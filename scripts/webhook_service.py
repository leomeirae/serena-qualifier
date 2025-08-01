#!/usr/bin/env python3
"""
WhatsApp Webhook Service for Kestra Integration (v1.1.0 - Corrected)

Este serviço FastAPI atua como ponte entre WhatsApp Business API e Kestra workflows.
Recebe webhooks do WhatsApp na raiz (/) e aciona o workflow de conversação.

Funcionalidades:
- Endpoint GET / combinado para Health Check e verificação de webhook.
- Endpoint POST / para recebimento de mensagens.
- Acionamento do workflow 2_sdr_conversation_flow_updated no Kestra.
- Logs detalhados e validação de segurança.

Author: Serena-Coder AI Agent & Gemini
Version: 1.1.0 (Definitive Fix)
Created: 2025-08-01
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

# Configure logging
logger = logging.getLogger(__name__)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
logHandler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(logHandler)

# FastAPI app
app = FastAPI(
    title="WhatsApp Webhook Service",
    description="Bridge between WhatsApp Business API and Kestra workflows",
    version="1.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# --- CONFIGURAÇÃO CORRETA ---
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "serena_webhook_verify_token")
WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "")
KESTRA_BASE_URL = os.getenv("KESTRA_API_URL", "http://kestra:8081")
# CORREÇÃO DA URL DO KESTRA: Apontando para o workflow correto
KESTRA_WEBHOOK_URL = f"{KESTRA_BASE_URL}/api/v1/executions/webhook/serena.production/2_sdr_conversation_flow_updated/converse_sdr_silvia"
CHATWOOT_WEBHOOK_URL = os.getenv("CHATWOOT_WEBHOOK_URL")

class WhatsAppMessage(BaseModel):
    phone: str
    message: str
    media_id: Optional[str] = None
    timestamp: Optional[str] = None
    type: Optional[str] = "text"

# Funções auxiliares (verify_webhook_signature, extract_whatsapp_message, etc.)
# ... (COLE AQUI AS FUNÇÕES 'verify_webhook_signature', 'extract_whatsapp_message', 'trigger_kestra_workflow' e 'forward_to_chatwoot' DO SEU ARQUIVO ORIGINAL, ELAS ESTÃO CORRETAS) ...
# Para garantir, aqui estão elas novamente:

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    if not WHATSAPP_APP_SECRET:
        logger.warning("⚠️ WHATSAPP_APP_SECRET não configurado - pulando verificação")
        return True
    try:
        expected_signature = hmac.new(WHATSAPP_APP_SECRET.encode(), payload, hashlib.sha256).hexdigest()
        if signature.startswith('sha256='):
            signature = signature[7:]
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logger.error(f"❌ Erro na verificação de assinatura: {str(e)}")
        return False

def extract_whatsapp_message(webhook_data: Dict[str, Any]) -> Optional[WhatsAppMessage]:
    try:
        entry = webhook_data.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})
        message = value.get('messages', [{}])[0]
        
        if not message:
             logger.info("Webhook sem conteúdo de mensagem (provavelmente status de entrega)")
             return None

        phone_number = message.get('from', '')
        message_type = message.get('type', 'text')
        timestamp = message.get('timestamp', str(int(datetime.now().timestamp())))
        
        message_text = ""
        media_id = None
        
        if message_type == 'text':
            message_text = message.get('text', {}).get('body', '')
        elif message_type == 'image':
            media_id = message.get('image', {}).get('id', '')
            message_text = message.get('image', {}).get('caption', '[Imagem recebida]')
        # Adicione outros tipos de mensagem se necessário
        else:
            message_text = f"[Mensagem do tipo '{message_type}' recebida]"

        return WhatsAppMessage(phone=phone_number, message=message_text, media_id=media_id, timestamp=timestamp, type=message_type)
    except (IndexError, KeyError) as e:
        logger.error(f"Estrutura de webhook inesperada: {e} | Payload: {json.dumps(webhook_data)}")
        return None

async def trigger_kestra_workflow(message: WhatsAppMessage):
    # (Esta função do seu arquivo original está correta, pode mantê-la)
    payload = message.dict()
    logger.info(f"🚀 Acionando Kestra: {KESTRA_WEBHOOK_URL} com payload: {payload}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(KESTRA_WEBHOOK_URL, json=payload, timeout=30)
            if 200 <= response.status_code < 300:
                logger.info(f"✅ Workflow acionado com sucesso: {response.json()}")
            else:
                logger.error(f"❌ Erro no Kestra: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"💥 Erro ao acionar Kestra: {str(e)}")


# --- CORREÇÃO DOS ENDPOINTS ---

@app.get("/")
async def health_check():
    """
    Health check endpoint para o Docker healthcheck.
    """
    logger.info("Health check recebido na raiz.")
    return {
        "status": "healthy",
        "service": "whatsapp-webhook-service",
        "version": "1.1.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/webhook")
async def health_check_and_verify(request: Request):
    """
    Endpoint combinado para health check e verificação do webhook do WhatsApp.
    """
    if "hub.mode" in request.query_params and "hub.verify_token" in request.query_params:
        logger.info("Recebendo requisição de verificação do WhatsApp...")
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")

        if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
            logger.info("✅ Webhook verificado com sucesso!")
            return PlainTextResponse(content=challenge)
        else:
            logger.error("❌ Verificação do Webhook falhou. Token inválido.")
            raise HTTPException(status_code=403, detail="Token de verificação inválido.")
    else:
        logger.info("Recebendo health check.")
        return {
            "status": "healthy",
            "service": "whatsapp-webhook-service",
            "version": "1.1.0",
            "timestamp": datetime.now().isoformat(),
            "kestra_target_url": KESTRA_WEBHOOK_URL
        }

@app.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Recebe webhooks de mensagens do WhatsApp no path /webhook.
    """
    logger.info("Webhook POST recebido no path '/webhook'")
    payload_bytes = await request.body()
    
    # Verificação de assinatura
    signature = request.headers.get("x-hub-signature-256", "")
    if not verify_webhook_signature(payload_bytes, signature):
        logger.error("❌ Assinatura do webhook inválida.")
        raise HTTPException(status_code=403, detail="Assinatura inválida")
    
    try:
        webhook_data = json.loads(payload_bytes)
        logger.info(f"Payload recebido: {json.dumps(webhook_data, indent=2)}")
        
        message_obj = extract_whatsapp_message(webhook_data)
        
        if message_obj:
            background_tasks.add_task(trigger_kestra_workflow, message_obj)
            return {"status": "received_and_processing"}
        else:
            return {"status": "received_no_action"}
            
    except json.JSONDecodeError:
        logger.error("❌ Erro: Payload não é um JSON válido.")
        raise HTTPException(status_code=400, detail="Payload JSON inválido.")
    except Exception as e:
        logger.error(f"💥 Erro inesperado no processamento do webhook: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor.")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando WhatsApp Webhook Service...")
    uvicorn.run(app, host="0.0.0.0", port=8001)