#!/usr/bin/env python3
"""
WhatsApp Template Sender for Lead Activation

Este script é responsável por enviar templates aprovados do WhatsApp
para leads que acabaram de se cadastrar no formulário de captura.

Funcionalidades:
- Envio de template "Ativar Perfil" personalizado
- Tratamento de erros da API WhatsApp
- Logging detalhado para debug
- Validação de número de telefone

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import os
import sys
import json
import logging
import requests
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def normalize_phone_number(phone: str) -> str:
    """
    Normaliza número de telefone para o formato WhatsApp API.
    
    Args:
        phone (str): Número de telefone em qualquer formato
        
    Returns:
        str: Número normalizado (+5581999887766)
    """
    # Remove todos os caracteres não numéricos
    clean_phone = re.sub(r'[^\d]', '', phone)
    
    # Se não começar com 55, adiciona código do Brasil
    if not clean_phone.startswith('55'):
        clean_phone = '55' + clean_phone
    
    # Adiciona o + no início
    if not clean_phone.startswith('+'):
        clean_phone = '+' + clean_phone
    
    logger.info(f"Phone normalized: {phone} -> {clean_phone}")
    return clean_phone


def send_activation_template(
    phone_number: str,
    lead_name: str,
    lead_city: str,  # NEW PARAMETER
    phone_number_id: str,
    template_name: str = "welcome_profile_site"  # Updated default template
) -> Dict[str, Any]:
    """
    Envia template de ativação do WhatsApp para o lead.
    
    Args:
        phone_number (str): Número do WhatsApp do lead
        lead_name (str): Nome do lead para personalização  
        phone_number_id (str): ID do número de telefone WhatsApp Business
        template_name (str): Nome do template aprovado
        
    Returns:
        Dict[str, Any]: Resultado do envio com status e dados
    """
    logger.info(f"Enviando template de ativação para {phone_number}")
    
    try:
        # Validações iniciais
        whatsapp_token = os.getenv("WHATSAPP_API_TOKEN")
        if not whatsapp_token:
            raise ValueError("WHATSAPP_API_TOKEN não encontrado nas variáveis de ambiente")
        
        if not phone_number_id:
            raise ValueError("WHATSAPP_PHONE_NUMBER_ID não fornecido")
            
        # Normaliza número de telefone
        normalized_phone = normalize_phone_number(phone_number)
        
        # URL da API WhatsApp
        api_url = f"https://graph.facebook.com/v23.0/{phone_number_id}/messages"
        
        # Headers da requisição
        headers = {
            "Authorization": f"Bearer {whatsapp_token}",
            "Content-Type": "application/json"
        }
        
        # Payload do template - UPDATED FOR TWO PARAMETERS
        payload = {
            "messaging_product": "whatsapp",
            "to": normalized_phone,
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
                                "text": lead_name  # {{1}} parameter
                            },
                            {
                                "type": "text", 
                                "text": lead_city  # {{2}} parameter
                            }
                        ]
                    }
                ]
            }
        }
        
        logger.info(f"Enviando payload: {json.dumps(payload, indent=2)}")
        
        # Faz a requisição para a API WhatsApp
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Processa resposta
        if response.status_code == 200:
            response_data = response.json()
            message_id = response_data.get('messages', [{}])[0].get('id', 'N/A')
            
            logger.info(f"✅ Template enviado com sucesso! Message ID: {message_id}")
            
            return {
                "success": True,
                "message_id": message_id,
                "phone_number": normalized_phone,
                "template_name": template_name,
                "response_data": response_data
            }
        else:
            error_data = response.json() if response.content else {}
            error_message = error_data.get('error', {}).get('message', 'Erro desconhecido')
            
            logger.error(f"❌ Erro ao enviar template: {response.status_code} - {error_message}")
            
            return {
                "success": False,
                "error": error_message,
                "status_code": response.status_code,
                "phone_number": normalized_phone,
                "response_data": error_data
            }
            
    except requests.exceptions.Timeout:
        logger.error("⏰ Timeout na requisição para WhatsApp API")
        return {
            "success": False,
            "error": "Timeout na requisição para WhatsApp API",
            "phone_number": phone_number
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"🌐 Erro de rede: {str(e)}")
        return {
            "success": False,
            "error": f"Erro de rede: {str(e)}",
            "phone_number": phone_number
        }
        
    except Exception as e:
        logger.error(f"💥 Erro inesperado: {str(e)}")
        return {
            "success": False,
            "error": f"Erro inesperado: {str(e)}",
            "phone_number": phone_number
        }


def main():
    """
    Função principal para teste e execução via linha de comando.
    
    Exemplo de uso:
    python send_whatsapp_template.py --phone "+5581999887766" --name "João Silva"
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Enviar template de ativação WhatsApp')
    parser.add_argument('--phone', required=True, help='Número de telefone do lead')
    parser.add_argument('--name', required=True, help='Nome do lead')
    parser.add_argument('--city', required=True, help='Cidade do lead')  # NEW PARAMETER
    parser.add_argument('--phone-id', help='ID do número WhatsApp Business')
    parser.add_argument('--template', default='welcome_profile_site', help='Nome do template')
    
    args = parser.parse_args()
    
    # Obtém phone_number_id do ambiente ou argumento
    phone_number_id = args.phone_id or os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    
    if not phone_number_id:
        logger.error("WHATSAPP_PHONE_NUMBER_ID não encontrado")
        sys.exit(1)
    
    # Envia template
    result = send_activation_template(
        phone_number=args.phone,
        lead_name=args.name,
        lead_city=args.city,  # NEW PARAMETER
        phone_number_id=phone_number_id,
        template_name=args.template
    )
    
    # Exibe resultado
    if result['success']:
        print(f"✅ Template enviado com sucesso!")
        print(f"📱 Phone: {result['phone_number']}")
        print(f"📧 Message ID: {result['message_id']}")
    else:
        print(f"❌ Erro ao enviar template:")
        print(f"📱 Phone: {result['phone_number']}")
        print(f"💥 Erro: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main() 