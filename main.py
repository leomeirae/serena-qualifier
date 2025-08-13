#!/usr/bin/env python3
"""
Serena SDR WhatsApp Webhook Microservice

Este serviço FastAPI processa mensagens do WhatsApp em tempo real,
mantém contexto de conversa e integra com o agente de IA.

Author: Serena SDR System
Version: 2.0.0
"""

import os
import json
import logging
import hmac
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

# Importar o agente e ferramentas
from scripts.ai_sdr_agent import SerenaSDRAgent
from scripts.agent_tools.supabase_tools import SupabaseTools
from scripts.agent_tools.whatsapp_tools import WhatsAppTools

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "serena_webhook_verify_token")
WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "")

# Instâncias globais
sdr_agent = None
supabase_tools = None
whatsapp_tools = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação."""
    global sdr_agent, supabase_tools, whatsapp_tools
    
    logger.info("Inicializando Serena SDR Webhook Service...")
    
    try:
        # Inicializar ferramentas
        sdr_agent = SerenaSDRAgent()
        supabase_tools = SupabaseTools()
        whatsapp_tools = WhatsAppTools()
        logger.info("Ferramentas inicializadas com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar ferramentas: {str(e)}")
        raise
    
    yield
    
    logger.info("Encerrando Serena SDR Webhook Service...")

# Criar aplicação FastAPI
app = FastAPI(
    title="Serena SDR Webhook Service",
    description="Processa mensagens WhatsApp e mantém conversas contextualizadas",
    version="2.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WebhookPayload(BaseModel):
    """Modelo para payload do webhook."""
    entry: list = []

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verifica assinatura do webhook WhatsApp."""
    if not WHATSAPP_APP_SECRET:
        logger.warning("WHATSAPP_APP_SECRET não configurado - pulando verificação")
        return True
    
    try:
        expected_signature = hmac.new(
            WHATSAPP_APP_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        if signature.startswith('sha256='):
            signature = signature[7:]
        
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logger.error(f"Erro na verificação de assinatura: {str(e)}")
        return False

def extract_message_data(webhook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extrai dados da mensagem do payload do webhook."""
    try:
        entry = webhook_data.get('entry', [])[0] if webhook_data.get('entry') else {}
        changes = entry.get('changes', [])[0] if entry.get('changes') else {}
        value = changes.get('value', {})
        
        # Verificar se há mensagens
        messages = value.get('messages', [])
        if not messages:
            return None
        
        message = messages[0]
        phone_number = message.get('from', '')
        message_type = message.get('type', 'text')
        timestamp = message.get('timestamp', str(int(datetime.now().timestamp())))
        
        # Extrair conteúdo baseado no tipo
        message_text = ""
        media_id = None
        
        if message_type == 'text':
            message_text = message.get('text', {}).get('body', '')
        elif message_type == 'interactive':
            interactive = message.get('interactive', {})
            if 'button_reply' in interactive:
                message_text = interactive['button_reply'].get('title', '')
            elif 'list_reply' in interactive:
                message_text = interactive['list_reply'].get('title', '')
        elif message_type == 'image':
            media_id = message.get('image', {}).get('id', '')
            message_text = message.get('image', {}).get('caption', '[Imagem recebida]')
        
        return {
            'phone_number': phone_number,
            'message_text': message_text,
            'message_type': message_type,
            'media_id': media_id,
            'timestamp': timestamp
        }
        
    except Exception as e:
        logger.error(f"Erro ao extrair dados da mensagem: {str(e)}")
        return None

async def process_message_async(message_data: Dict[str, Any]):
    """Processa mensagem de forma assíncrona."""
    phone_number = message_data['phone_number']
    user_message = message_data['message_text']
    message_type = message_data['message_type']
    media_id = message_data.get('media_id')
    
    try:
        logger.info(f"Processando mensagem de {phone_number}: {user_message[:50]}...")
        
        # Registrar mensagem do usuário
        await supabase_tools.record_message(
            phone_number=phone_number,
            direction='user',
            content=user_message,
            message_type=message_type,
            media_id=media_id
        )
        
        # Recuperar dados e estado do lead
        lead_data = await supabase_tools.get_lead_by_phone(phone_number)
        
        if not lead_data:
            # Criar lead se não existir
            lead_data = {
                'phone_number': phone_number,
                'name': 'Lead WhatsApp',
                'conversation_state': 'INITIAL',
                'created_at': datetime.now().isoformat()
            }
            await supabase_tools.create_or_update_lead(lead_data)
        
        # Executar agente
        agent_response = await sdr_agent.run_agent(
            lead_id=phone_number,
            user_message=user_message,
            message_type=message_type,
            media_id=media_id,
            conversation_state=lead_data.get('conversation_state', 'INITIAL')
        )
        
        if agent_response.get('success'):
            response_text = agent_response.get('response')
            
            # Enviar resposta via WhatsApp
            await whatsapp_tools.send_text_message(phone_number, response_text)
            
            # Registrar resposta do bot
            await supabase_tools.record_message(
                phone_number=phone_number,
                direction='bot',
                content=response_text,
                message_type='text'
            )
            
            # Atualizar última mensagem no lead
            await supabase_tools.update_lead_last_message(phone_number)
            
            logger.info(f"Resposta enviada com sucesso para {phone_number}")
        else:
            # Enviar mensagem de erro genérica
            error_message = "Desculpe, tive um problema técnico. Por favor, tente novamente em alguns instantes."
            await whatsapp_tools.send_text_message(phone_number, error_message)
            logger.error(f"Falha no agente para {phone_number}: {agent_response.get('error')}")
            
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}")
        try:
            await whatsapp_tools.send_text_message(
                phone_number,
                "Desculpe, ocorreu um erro. Nossa equipe foi notificada e resolveremos em breve."
            )
        except:
            pass

@app.get("/")
async def health_check_and_verify(request: Request):
    """Health check e verificação do webhook WhatsApp."""
    # Verificar se é requisição de verificação do WhatsApp
    if "hub.mode" in request.query_params and "hub.verify_token" in request.query_params:
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
            logger.info("Webhook WhatsApp verificado com sucesso")
            return PlainTextResponse(content=challenge)
        else:
            logger.error("Falha na verificação do webhook - token inválido")
            raise HTTPException(status_code=403, detail="Token de verificação inválido")
    
    # Health check padrão
    return {
        "status": "healthy",
        "service": "serena-sdr-webhook",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "sdr_agent": sdr_agent is not None,
            "supabase_tools": supabase_tools is not None,
            "whatsapp_tools": whatsapp_tools is not None
        }
    }

@app.post("/webhook/whatsapp")
async def handle_whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Recebe e processa webhooks do WhatsApp."""
    # Verificar assinatura
    payload_bytes = await request.body()
    signature = request.headers.get("x-hub-signature-256", "")
    
    if not verify_webhook_signature(payload_bytes, signature):
        logger.error("Assinatura do webhook inválida")
        raise HTTPException(status_code=403, detail="Assinatura inválida")
    
    try:
        # Parse do payload
        payload = json.loads(payload_bytes)
        logger.debug(f"Webhook recebido: {json.dumps(payload, indent=2)}")
        
        # Extrair dados da mensagem
        message_data = extract_message_data(payload)
        
        if message_data:
            # Processar mensagem em background
            background_tasks.add_task(process_message_async, message_data)
            return {"status": "received", "queued": True}
        else:
            # Não é uma mensagem de usuário (pode ser status, etc)
            return {"status": "received", "queued": False}
            
    except json.JSONDecodeError:
        logger.error("Payload não é JSON válido")
        raise HTTPException(status_code=400, detail="Payload inválido")
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/health")
async def health():
    """Endpoint de health check."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics")
async def metrics():
    """Endpoint de métricas básicas."""
    try:
        # Buscar métricas do Supabase
        metrics = await supabase_tools.get_conversation_metrics()
        return {
            "status": "ok",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
