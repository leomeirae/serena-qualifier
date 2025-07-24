#!/usr/bin/env python3
"""
WhatsApp Webhook Service for Kestra Integration

Este serviço FastAPI atua como ponte entre WhatsApp Business API e Kestra workflows.
Recebe webhooks do WhatsApp e aciona o workflow de conversação com IA.

Funcionalidades:
- Verificação de webhook do WhatsApp (challenge)
- Processamento de mensagens recebidas
- Acionamento do workflow converse_production_lead no Kestra
- Logs detalhados para debug
- Validação de segurança

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-20
"""

import os
import sys
import json
import logging
import requests
import httpx
import hashlib
import hmac
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pythonjsonlogger import jsonlogger
import uuid

# Load environment variables
load_dotenv()

# Configure structured (JSON) logging
logger = logging.getLogger(__name__)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
logHandler = logging.StreamHandler()
# Example of a custom format
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s %(trace_id)s'
)
logHandler.setFormatter(formatter)
# Avoid adding duplicate handlers
if not logger.handlers:
    logger.addHandler(logHandler)

# FastAPI app
app = FastAPI(
    title="WhatsApp Webhook Service",
    description="Bridge between WhatsApp Business API and Kestra workflows",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "serena_webhook_verify_token")
WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "")
KESTRA_BASE_URL = os.getenv("KESTRA_API_URL", "http://kestra:8081")
KESTRA_WEBHOOK_URL = f"{KESTRA_BASE_URL}/api/v1/executions/webhook/serena.production/3_ai_conversation_optimized/converse_production_optimized"
CHATWOOT_WEBHOOK_URL = os.getenv("CHATWOOT_WEBHOOK_URL")

class WhatsAppMessage(BaseModel):
    """Modelo para mensagem do WhatsApp"""
    phone: str
    message: str
    media_id: Optional[str] = None
    timestamp: Optional[str] = None
    type: Optional[str] = "text"  # Adicionado campo type


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verifica assinatura do webhook do WhatsApp para segurança.
    
    Args:
        payload (bytes): Payload da requisição
        signature (str): Assinatura SHA256 do WhatsApp
        
    Returns:
        bool: True se assinatura válida
    """
    if not WHATSAPP_APP_SECRET:
        logger.warning("⚠️ WHATSAPP_APP_SECRET não configurado - pulando verificação")
        return True
    
    try:
        expected_signature = hmac.new(
            WHATSAPP_APP_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Remover prefixo 'sha256=' se presente
        if signature.startswith('sha256='):
            signature = signature[7:]
            
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logger.error(f"❌ Erro na verificação de assinatura: {str(e)}")
        return False


def extract_whatsapp_message(webhook_data: Dict[str, Any], trace_id: str = "") -> Optional[WhatsAppMessage]:
    """
    Extrai dados da mensagem do payload do WhatsApp de forma robusta.
    """
    try:
        entry = webhook_data.get('entry', [])
        if not entry or not entry[0].get('changes'):
            logger.warning(f"[TRACE {trace_id}] entry vazio ou sem changes", extra={"trace_id": trace_id})
            return None
            
        value = entry[0]['changes'][0].get('value', {})
        messages = value.get('messages', [])
        
        if not messages:
            logger.info(f"[TRACE {trace_id}] 📡 Webhook recebido sem mensagens (provavelmente um status de entrega)", extra={"trace_id": trace_id})
            return None
            
        message = messages[0]
        phone_number = message.get('from', '')
        message_type = message.get('type', '')
        timestamp = message.get('timestamp', str(int(datetime.now().timestamp())))
        
        message_text = ""
        media_id = None
        
        if message_type == 'text':
            message_text = message.get('text', {}).get('body', '')
        elif message_type == 'image':
            media_id = message.get('image', {}).get('id', '')
            message_text = message.get('image', {}).get('caption', 'Imagem enviada')
        elif message_type == 'audio':
            media_id = message.get('audio', {}).get('id', '')
            message_text = "Áudio recebido"
        elif message_type == 'video':
            media_id = message.get('video', {}).get('id', '')
            message_text = "Vídeo recebido"
        elif message_type == 'document':
            media_id = message.get('document', {}).get('id', '')
            message_text = "Documento recebido"
        elif message_type == 'interactive':
            interactive = message.get('interactive', {})
            if 'button_reply' in interactive:
                message_text = interactive['button_reply'].get('title', 'Botão Interativo')
            elif 'list_reply' in interactive:
                message_text = interactive['list_reply'].get('title', 'Item de Lista')
            else:
                message_text = 'Interação desconhecida'
            logger.info(f"[TRACE {trace_id}] 🔘 Interativo pressionado, texto extraído: '{message_text}'", extra={"trace_id": trace_id})
        elif message_type == 'button':
            reply = message.get('button', {})
            message_text = (
                reply.get('payload') or
                reply.get('text') or
                "Mensagem de botão vazia"
            )
            logger.info(f"[TRACE {trace_id}] 🔘 Botão de Template pressionado, texto extraído: '{message_text}'", extra={"trace_id": trace_id})
            logger.info(f"[TRACE {trace_id}] [DEBUG] Mensagem extraída do WhatsApp: {message_text}", extra={"trace_id": trace_id})
        else:
            message_text = f"Mensagem do tipo '{message_type}' não suportado recebida"

        if not phone_number:
            logger.warning(f"[TRACE {trace_id}] ⚠️ phone_number vazio na mensagem recebida! Estrutura possivelmente inválida.", extra={"trace_id": trace_id})

        logger.info(f"[TRACE {trace_id}] 📱 Mensagem final extraída para {phone_number}: '{message_text[:100]}'", extra={"trace_id": trace_id})
        
        return WhatsAppMessage(
            phone=phone_number,
            message=message_text,
            media_id=media_id,
            timestamp=timestamp
        )
        
    except Exception as e:
        logger.error(f"[TRACE {trace_id}] ❌ Erro crítico ao extrair mensagem do webhook: {str(e)}", extra={"trace_id": trace_id})
        return None


async def trigger_kestra_workflow(message: WhatsAppMessage) -> Dict[str, Any]:
    """
    Aciona o workflow converse_production_lead no Kestra.
    
    Args:
        message (WhatsAppMessage): Dados da mensagem
        
    Returns:
        Dict: Resultado do acionamento
    """
    try:
        # Payload para o Kestra
        payload = {
            "phone": message.phone,
            "message": message.message,
            "timestamp": message.timestamp,
            "type": message.type or "text"
        }
        
        if message.media_id:
            payload["media_id"] = message.media_id
        
        logger.info(f"🚀 Acionando Kestra workflow: {KESTRA_WEBHOOK_URL}")
        logger.info(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        # Fazer requisição para o Kestra
        response = requests.post(
            KESTRA_WEBHOOK_URL,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "WhatsApp-Webhook-Service/1.0.0"
            },
            timeout=30
        )
        
        if response.status_code in [200, 202]:
            response_data = response.json() if response.content else {}
            execution_id = response_data.get('id', 'N/A')
            
            logger.info(f"✅ Workflow acionado com sucesso! Execution ID: {execution_id}")
            
            return {
                "success": True,
                "execution_id": execution_id,
                "kestra_response": response_data,
                "phone_number": message.phone
            }
        else:
            error_msg = f"Kestra retornou status {response.status_code}"
            logger.error(f"❌ Erro no Kestra: {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "status_code": response.status_code,
                "phone_number": message.phone
            }
            
    except requests.exceptions.Timeout:
        logger.error("⏰ Timeout na comunicação com Kestra")
        return {
            "success": False,
            "error": "Timeout na comunicação com Kestra",
            "phone_number": message.phone
        }
        
    except Exception as e:
        logger.error(f"💥 Erro inesperado: {str(e)}")
        return {
            "success": False,
            "error": f"Erro inesperado: {str(e)}",
            "phone_number": message.phone
        }


async def forward_to_chatwoot(payload: bytes, headers: dict):
    """
    Encaminha o payload bruto do webhook para o Chatwoot.
    
    Args:
        payload: Payload bruto do webhook WhatsApp
        headers: Headers da requisição original
    """
    if not CHATWOOT_WEBHOOK_URL:
        logger.warning("⚠️ CHATWOOT_WEBHOOK_URL não configurado. Pulando encaminhamento.")
        return

    try:
        # Replicar os cabeçalhos relevantes do WhatsApp
        forward_headers = {
            'Content-Type': headers.get('Content-Type', 'application/json'),
            'X-Hub-Signature-256': headers.get('X-Hub-Signature-256', '')
        }

        logger.info(f"📤 Encaminhando webhook para o Chatwoot: {CHATWOOT_WEBHOOK_URL}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                CHATWOOT_WEBHOOK_URL,
                content=payload,
                headers=forward_headers
            )

        if 200 <= response.status_code < 300:
            logger.info(f"✅ Webhook encaminhado para Chatwoot com sucesso. Status: {response.status_code}")
        else:
            logger.error(f"❌ Erro ao encaminhar para Chatwoot: {response.status_code} - {response.text}")

    except httpx.TimeoutException:
        logger.error("⏱️ Timeout ao encaminhar para Chatwoot")
    except Exception as e:
        logger.error(f"💥 Erro inesperado no encaminhamento para Chatwoot: {str(e)}")


@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "whatsapp-webhook-service",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "kestra_url": KESTRA_WEBHOOK_URL,
        "chatwoot_url": CHATWOOT_WEBHOOK_URL,
        "chatwoot_enabled": bool(CHATWOOT_WEBHOOK_URL)
    }


@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Verificação do webhook do WhatsApp (challenge).
    
    O WhatsApp envia um GET com challenge para verificar o endpoint.
    """
    try:
        # Parâmetros de verificação
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        logger.info(f"🔐 Verificação webhook: mode={mode}, token={token}, challenge={challenge}")
        logger.info(f"🔐 Token esperado: {WHATSAPP_VERIFY_TOKEN}")
        
        # Verificar se todos os parâmetros foram recebidos
        if not mode or not token or not challenge:
            logger.error(f"❌ Parâmetros faltando: mode={mode}, token={token}, challenge={challenge}")
            raise HTTPException(status_code=400, detail="Parâmetros hub.mode, hub.verify_token e hub.challenge são obrigatórios")
        
        # Verificar se é o token correto
        if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
            logger.info("✅ Webhook verificado com sucesso!")
            return PlainTextResponse(challenge)
        else:
            logger.warning(f"❌ Token inválido: esperado={WHATSAPP_VERIFY_TOKEN}, recebido={token}")
            raise HTTPException(status_code=403, detail="Token inválido")
            
    except HTTPException:
        # Re-raise HTTPException para não ser capturada pelo except genérico
        raise
    except Exception as e:
        logger.error(f"💥 Erro na verificação: {str(e)}")
        logger.error(f"💥 Tipo do erro: {type(e)}")
        import traceback
        logger.error(f"💥 Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Erro interno")


@app.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    trace_id = str(uuid.uuid4())
    logger.info(f"[TRACE {trace_id}] Nova requisição recebida", extra={"trace_id": trace_id})
    try:
        # Ler payload
        payload = await request.body()
        
        # Encaminhar para Chatwoot em background (se configurado)
        if CHATWOOT_WEBHOOK_URL:
            background_tasks.add_task(forward_to_chatwoot, payload, dict(request.headers))
        
        # Verificar assinatura (se configurada)
        signature = request.headers.get("X-Hub-Signature-256", "")
        if not verify_webhook_signature(payload, signature):
            logger.warning(f"[TRACE {trace_id}] ❌ Assinatura inválida", extra={"trace_id": trace_id})
            raise HTTPException(status_code=403, detail="Assinatura inválida")
        
        # Parsear JSON
        webhook_data = json.loads(payload.decode())
        logger.info(f"[TRACE {trace_id}] 🔍 PAYLOAD BRUTO DO WHATSAPP: {json.dumps(webhook_data, indent=2)}", extra={"trace_id": trace_id})
        logger.info(f"[TRACE {trace_id}] 📨 Webhook recebido: {json.dumps(webhook_data, indent=2)}", extra={"trace_id": trace_id})

        # Extrai o tipo de mensagem principal
        entry = webhook_data.get('entry', [])
        if not entry or not entry[0].get('changes'):
            logger.warning(f"[TRACE {trace_id}] entry vazio ou sem changes", extra={"trace_id": trace_id})
            return {"status": "ignored", "reason": "entry vazio ou sem changes", "trace_id": trace_id}
        value = entry[0]['changes'][0].get('value', {})
        messages = value.get('messages', [])
        if not messages:
            logger.info(f"[TRACE {trace_id}] 📡 Webhook recebido sem mensagens (provavelmente um status de entrega)", extra={"trace_id": trace_id})
            return {"status": "ignored", "reason": "sem mensagens", "trace_id": trace_id}

        # Chama o parser universal para texto E botão!
        message_obj = extract_whatsapp_message(webhook_data, trace_id=trace_id)
        if not message_obj:
            logger.info(f"[TRACE {trace_id}] 📭 Webhook sem mensagem relevante", extra={"trace_id": trace_id})
            return {"status": "acknowledged", "trace_id": trace_id}

        # Garante o type correto
        message_type = messages[0].get('type', '')
        message_obj.type = message_type

        background_tasks.add_task(trigger_kestra_workflow, message_obj)
        logger.info(f"[TRACE {trace_id}] ✅ Mensagem processada: {message_obj.phone} -> {message_obj.message[:100]}...", extra={"trace_id": trace_id})
        return {
            "status": "received",
            "phone": message_obj.phone,
            "message_preview": message_obj.message[:100],
            "timestamp": datetime.now().isoformat(),
            "trace_id": trace_id
        }
    except json.JSONDecodeError:
        logger.error(f"[TRACE {trace_id}] ❌ Payload JSON inválido", extra={"trace_id": trace_id})
        raise HTTPException(status_code=400, detail="JSON inválido")
    except Exception as e:
        logger.error(f"[TRACE {trace_id}] 💥 Erro no processamento: {str(e)}", extra={"trace_id": trace_id})
        raise HTTPException(status_code=500, detail="Erro interno")


@app.post("/test")
async def test_webhook(message: WhatsAppMessage):
    """
    Endpoint de teste para simular mensagem do WhatsApp.
    
    Útil para testes e debug.
    """
    try:
        logger.info(f"🧪 TESTE - Simulando mensagem: {message.phone} -> {message.message}")
        
        result = await trigger_kestra_workflow(message)
        
        return {
            "test_mode": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"💥 Erro no teste: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro no teste: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Iniciando WhatsApp Webhook Service...")
    logger.info(f"🔗 Kestra URL: {KESTRA_WEBHOOK_URL}")
    logger.info(f"🔐 Verify Token: {WHATSAPP_VERIFY_TOKEN}")
    
    uvicorn.run(
        "webhook_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 