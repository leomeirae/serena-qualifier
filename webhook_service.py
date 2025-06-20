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
import hashlib
import hmac
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
KESTRA_BASE_URL = os.getenv("KESTRA_API_URL", "http://kestra-minimal:8080")
KESTRA_WEBHOOK_URL = f"{KESTRA_BASE_URL}/api/v1/executions/webhook/converse_production_lead"

class WhatsAppMessage(BaseModel):
    """Modelo para mensagem do WhatsApp"""
    phone: str
    message: str
    media_id: Optional[str] = None
    timestamp: Optional[str] = None


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


def extract_whatsapp_message(webhook_data: Dict[str, Any]) -> Optional[WhatsAppMessage]:
    """
    Extrai dados da mensagem do payload do WhatsApp.
    
    Args:
        webhook_data (Dict): Payload do webhook
        
    Returns:
        Optional[WhatsAppMessage]: Dados da mensagem ou None
    """
    try:
        entry = webhook_data.get('entry', [])
        if not entry:
            return None
            
        changes = entry[0].get('changes', [])
        if not changes:
            return None
            
        value = changes[0].get('value', {})
        messages = value.get('messages', [])
        
        if not messages:
            logger.info("📭 Webhook recebido sem mensagens (status update)")
            return None
            
        message = messages[0]
        
        # Extrair dados da mensagem
        phone_number = message.get('from', '')
        message_type = message.get('type', '')
        timestamp = message.get('timestamp', str(int(datetime.now().timestamp())))
        
        # Processar diferentes tipos de mensagem
        message_text = ""
        media_id = None
        
        if message_type == 'text':
            message_text = message.get('text', {}).get('body', '')
        elif message_type == 'image':
            media_id = message.get('image', {}).get('id', '')
            message_text = message.get('image', {}).get('caption', 'Imagem enviada')
        elif message_type == 'interactive':
            button_reply = message.get('interactive', {}).get('button_reply', {})
            message_text = button_reply.get('title', '')
        else:
            message_text = f"Mensagem do tipo {message_type} recebida"
        
        logger.info(f"📱 Mensagem extraída: {phone_number} -> {message_text[:100]}")
        
        return WhatsAppMessage(
            phone=phone_number,
            message=message_text,
            media_id=media_id,
            timestamp=timestamp
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao extrair mensagem: {str(e)}")
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
            "timestamp": message.timestamp
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


@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "whatsapp-webhook-service",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "kestra_url": KESTRA_WEBHOOK_URL
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
        
        logger.info(f"🔐 Verificação webhook: mode={mode}, token={token}")
        
        # Verificar se é o token correto
        if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
            logger.info("✅ Webhook verificado com sucesso!")
            return PlainTextResponse(challenge)
        else:
            logger.warning(f"❌ Token inválido: esperado={WHATSAPP_VERIFY_TOKEN}, recebido={token}")
            raise HTTPException(status_code=403, detail="Token inválido")
            
    except Exception as e:
        logger.error(f"💥 Erro na verificação: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")


@app.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Recebe webhooks do WhatsApp com mensagens dos leads.
    
    Processa a mensagem e aciona o workflow Kestra em background.
    """
    try:
        # Ler payload
        payload = await request.body()
        
        # Verificar assinatura (se configurada)
        signature = request.headers.get("X-Hub-Signature-256", "")
        if not verify_webhook_signature(payload, signature):
            logger.warning("❌ Assinatura inválida")
            raise HTTPException(status_code=403, detail="Assinatura inválida")
        
        # Parsear JSON
        webhook_data = json.loads(payload.decode())
        
        logger.info(f"📨 Webhook recebido: {json.dumps(webhook_data, indent=2)}")
        
        # Extrair mensagem
        message = extract_whatsapp_message(webhook_data)
        
        if message:
            # Processar em background para resposta rápida
            background_tasks.add_task(trigger_kestra_workflow, message)
            
            logger.info(f"✅ Mensagem processada: {message.phone} -> {message.message[:50]}...")
            
            return {
                "status": "received",
                "phone": message.phone,
                "message_preview": message.message[:100],
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.info("📭 Webhook sem mensagem relevante")
            return {"status": "acknowledged"}
            
    except json.JSONDecodeError:
        logger.error("❌ Payload JSON inválido")
        raise HTTPException(status_code=400, detail="JSON inválido")
        
    except Exception as e:
        logger.error(f"💥 Erro no processamento: {str(e)}")
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