#!/usr/bin/env python3
"""
WhatsApp Real API Sender
Integração real com a API Cloud da Meta para envio de mensagens de template
"""

import os
import json
import requests
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()


def send_template_message(phone_number: str, customer_name: str) -> Dict[str, Any]:
    """
    Envia mensagem de template WhatsApp usando a API Cloud da Meta
    
    Args:
        phone_number: Número de telefone do destinatário (ex: +5581997498268)
        customer_name: Nome do cliente para personalização do template
    
    Returns:
        Dict contendo status da operação e detalhes da resposta
    
    Raises:
        ValueError: Se variáveis de ambiente obrigatórias estiverem ausentes
        requests.RequestException: Se houver erro na requisição HTTP
    """
    
    # Passo 3a: Ler variáveis de ambiente obrigatórias
    whatsapp_token = os.getenv("WHATSAPP_API_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    template_name = os.getenv("WHATSAPP_WELCOME_TEMPLATE_NAME")
    
    # Validar se variáveis existem
    if not whatsapp_token:
        error_msg = "WHATSAPP_API_TOKEN não encontrado no arquivo .env"
        logger.error(f"❌ Erro de configuração: {error_msg}")
        raise ValueError(error_msg)
    
    if not phone_number_id:
        error_msg = "WHATSAPP_PHONE_NUMBER_ID não encontrado no arquivo .env"
        logger.error(f"❌ Erro de configuração: {error_msg}")
        raise ValueError(error_msg)
    
    if not template_name:
        error_msg = "WHATSAPP_WELCOME_TEMPLATE_NAME não encontrado no arquivo .env"
        logger.error(f"❌ Erro de configuração: {error_msg}")
        raise ValueError(error_msg)
    
    logger.info(f"📱 Iniciando envio de template WhatsApp para {phone_number}")
    logger.info(f"👤 Cliente: {customer_name}")
    logger.info(f"📋 Template: {template_name}")
    
    # Passo 3b: Formatar phone_number para padrão E.164 sem o +
    # Remove caracteres especiais e espaços
    phone_clean = phone_number.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
    
    # Garantir que tenha código do país Brasil (55) se não tiver
    if not phone_clean.startswith("55"):
        phone_clean = f"55{phone_clean}"
    
    logger.info(f"📞 Telefone formatado E.164: {phone_clean}")
    
    # Passo 3c: Montar payload JSON para API da Meta
    # Extrair primeiro nome para personalização
    first_name = customer_name.split()[0] if customer_name else "Cliente"
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_clean,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": "pt_BR"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": first_name
                        }
                    ]
                }
            ]
        }
    }
    
    # Passo 3d: Configurar endpoint e headers
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json"
    }
    
    logger.info(f"🌐 Endpoint: {url}")
    logger.debug(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Passo 3d: Enviar requisição POST
        logger.info("📤 Enviando requisição para API da Meta...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # Passo 3e: Registrar resposta e tratar erros
        logger.info(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Sucesso
            response_data = response.json()
            message_id = response_data.get("messages", [{}])[0].get("id", "N/A")
            
            logger.info(f"✅ Mensagem enviada com sucesso!")
            logger.info(f"🆔 Message ID: {message_id}")
            logger.info(f"📱 Destinatário: {phone_clean}")
            logger.info(f"👤 Personalização: {first_name}")
            
            return {
                "success": True,
                "message": "Template WhatsApp enviado com sucesso",
                "phone_number": phone_clean,
                "customer_name": customer_name,
                "first_name": first_name,
                "message_id": message_id,
                "template_name": template_name,
                "response": response_data
            }
            
        elif response.status_code in [400, 401, 403, 404]:
            # Erros 4xx - Problema com a requisição
            try:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", "Erro desconhecido")
                error_code = error_data.get("error", {}).get("code", "N/A")
                
                logger.error(f"❌ Erro 4xx da API WhatsApp:")
                logger.error(f"   Status: {response.status_code}")
                logger.error(f"   Código: {error_code}")
                logger.error(f"   Mensagem: {error_message}")
                
                return {
                    "success": False,
                    "message": f"Erro na requisição: {error_message}",
                    "phone_number": phone_clean,
                    "customer_name": customer_name,
                    "error_code": error_code,
                    "status_code": response.status_code,
                    "error_details": error_data
                }
                
            except json.JSONDecodeError:
                logger.error(f"❌ Erro {response.status_code}: Resposta não é JSON válido")
                logger.error(f"   Resposta bruta: {response.text}")
                
                return {
                    "success": False,
                    "message": f"Erro HTTP {response.status_code}",
                    "phone_number": phone_clean,
                    "customer_name": customer_name,
                    "status_code": response.status_code,
                    "raw_response": response.text
                }
                
        elif response.status_code >= 500:
            # Erros 5xx - Problema no servidor da Meta
            logger.error(f"❌ Erro 5xx do servidor Meta:")
            logger.error(f"   Status: {response.status_code}")
            logger.error(f"   Resposta: {response.text}")
            
            return {
                "success": False,
                "message": f"Erro interno do servidor Meta (HTTP {response.status_code})",
                "phone_number": phone_clean,
                "customer_name": customer_name,
                "status_code": response.status_code,
                "raw_response": response.text
            }
            
        else:
            # Outros status codes
            logger.error(f"❌ Status code inesperado: {response.status_code}")
            logger.error(f"   Resposta: {response.text}")
            
            return {
                "success": False,
                "message": f"Status code inesperado: {response.status_code}",
                "phone_number": phone_clean,
                "customer_name": customer_name,
                "status_code": response.status_code,
                "raw_response": response.text
            }
            
    except requests.exceptions.Timeout:
        error_msg = "Timeout na requisição para API da Meta (30s)"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "message": error_msg,
            "phone_number": phone_clean,
            "customer_name": customer_name,
            "error_type": "timeout"
        }
        
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Erro de conexão com API da Meta: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "message": error_msg,
            "phone_number": phone_clean,
            "customer_name": customer_name,
            "error_type": "connection_error"
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Erro na requisição HTTP: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "message": error_msg,
            "phone_number": phone_clean,
            "customer_name": customer_name,
            "error_type": "request_error"
        }


def main():
    """Função principal para teste do script"""
    import sys
    
    if len(sys.argv) != 3:
        print("Uso: python whatsapp_real_sender.py <phone_number> <customer_name>")
        print("Exemplo: python whatsapp_real_sender.py +5581997498268 'João Silva'")
        sys.exit(1)
    
    phone = sys.argv[1]
    name = sys.argv[2]
    
    try:
        result = send_template_message(phone, name)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result["success"]:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Erro fatal: {str(e)}")
        print(json.dumps({
            "success": False,
            "message": f"Erro fatal: {str(e)}",
            "phone_number": phone,
            "customer_name": name
        }, indent=2, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main() 