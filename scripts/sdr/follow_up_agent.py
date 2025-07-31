# =============================================================================
# SERENA SDR - FOLLOW-UP AGENT
# =============================================================================

"""
Follow-up Agent para Serena SDR

Este script é responsável por gerar e enviar lembretes automáticos
quando o lead não responde dentro de 2 horas.

Funcionalidades:
- Gera mensagem de follow-up personalizada
- Envia via WhatsApp MCP
- Registra tentativa de follow-up
- Tratamento de erros

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import os
import json
import logging
import openai
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Importar utilitários
from utils.config import get_config, get_follow_up_delay
from utils.logger import get_logger, log_message_sent

# Importar ferramentas
from agent_tools.whatsapp_tools import WhatsAppTools
from agent_tools.supabase_tools import SupabaseTools

logger = get_logger("serena_sdr.follow_up")


class FollowUpAgent:
    """Agente para geração e envio de follow-ups automáticos."""
    
    def __init__(self):
        """Inicializa o agente de follow-up."""
        self.config = get_config()
        openai.api_key = self.config.openai_api_key
        
        # Inicializar ferramentas
        self.whatsapp_tools = WhatsAppTools()
        self.supabase_tools = SupabaseTools()
        
        # Configurar OpenAI
        self.model = "gpt-4o"
        self.max_tokens = 150
        self.temperature = 0.7
        
        logger.info("Follow-up Agent inicializado")
    
    def generate_follow_up_message(self, lead_data: Dict[str, Any]) -> str:
        """
        Gera mensagem de follow-up personalizada usando OpenAI.
        
        Args:
            lead_data: Dados do lead do Supabase
            
        Returns:
            str: Mensagem de follow-up personalizada
        """
        try:
            # Preparar contexto do lead
            lead_name = lead_data.get('name', 'Cliente')
            lead_city = lead_data.get('city', 'sua cidade')
            invoice_amount = lead_data.get('invoice_amount', 0)
            
            # Prompt para geração do follow-up
            system_prompt = """
            Você é a Sílvia, agente virtual de pré-vendas da Serena Energia.
            
            O lead não respondeu à nossa mensagem inicial. Gere uma mensagem de follow-up:
            - Amigável e não intrusiva
            - Mencione os benefícios da energia solar
            - Ofereça ajuda para economizar na conta de luz
            - Inclua call-to-action para resposta
            - Máximo 200 caracteres
            
            Use os dados do lead para personalizar a mensagem.
            """
            
            user_prompt = f"""
            Lead: {lead_name}
            Cidade: {lead_city}
            Valor da conta: R$ {invoice_amount}
            
            Gere uma mensagem de follow-up persuasiva e personalizada.
            """
            
            # Chamar OpenAI
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            follow_up_message = response.choices[0].message.content.strip()
            logger.info(f"Follow-up gerado: {follow_up_message}")
            
            return follow_up_message
            
        except Exception as e:
            logger.error(f"Erro ao gerar follow-up: {str(e)}")
            # Mensagem de fallback
            return f"Oi {lead_name}! 😊 Só passando para lembrar que temos uma proposta especial de energia solar para você em {lead_city}. Quer economizar até 95% na sua conta de luz? Responda aqui que te ajudo! 🌞"
    
    def send_follow_up_whatsapp(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Envia follow-up via WhatsApp MCP.
        
        Args:
            phone_number: Número do WhatsApp
            message: Mensagem de follow-up
            
        Returns:
            Dict: Resultado do envio
        """
        try:
            result = self.whatsapp_tools.send_text_message(phone_number, message)
            
            if result["success"]:
                logger.info(f"Follow-up enviado com sucesso: {result}")
                log_message_sent(phone_number, message, True)
                return {
                    "success": True,
                    "message_id": result.get("message_id", "N/A"),
                    "response": result
                }
            else:
                logger.error(f"Erro ao enviar follow-up: {result}")
                log_message_sent(phone_number, message, False, result.get("error"))
                return {
                    "success": False,
                    "error": result.get("error", "Erro desconhecido")
                }
                
        except Exception as e:
            logger.error(f"Erro inesperado ao enviar follow-up: {str(e)}")
            log_message_sent(phone_number, message, False, str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_lead_follow_up_status(self, lead_id: str, follow_up_sent: bool) -> Dict[str, Any]:
        """
        Atualiza status de follow-up no Supabase.
        
        Args:
            lead_id: ID do lead
            follow_up_sent: Se o follow-up foi enviado
            
        Returns:
            Dict: Resultado da atualização
        """
        try:
            # Preparar dados para atualização
            additional_data = {
                "follow_up_sent": follow_up_sent,
                "follow_up_timestamp": datetime.now().isoformat()
            }
            
            # Atualizar estado da conversa
            result = self.supabase_tools.update_lead_conversation_state(
                phone_number=lead_id,  # Usar phone como lead_id
                state="FOLLOW_UP_SENT" if follow_up_sent else "FOLLOW_UP_FAILED",
                additional_data=additional_data
            )
            
            if result["success"]:
                logger.info(f"Status de follow-up atualizado: {result}")
                return {
                    "success": True,
                    "response": result
                }
            else:
                logger.error(f"Erro ao atualizar status: {result}")
                return {
                    "success": False,
                    "error": result.get("error", "Erro desconhecido")
                }
                
        except Exception as e:
            logger.error(f"Erro ao atualizar status de follow-up: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_follow_up(self, lead_id: str, phone_number: str, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera e envia follow-up completo.
        
        Args:
            lead_id: ID do lead
            phone_number: Número do WhatsApp
            lead_data: Dados do lead
            
        Returns:
            Dict: Resultado completo do follow-up
        """
        logger.info(f"Iniciando follow-up para lead {lead_id}")
        
        try:
            # 1. Gerar mensagem de follow-up
            follow_up_message = self.generate_follow_up_message(lead_data)
            
            # 2. Enviar via WhatsApp
            whatsapp_result = self.send_follow_up_whatsapp(phone_number, follow_up_message)
            
            # 3. Atualizar status no Supabase
            status_result = self.update_lead_follow_up_status(lead_id, whatsapp_result["success"])
            
            # 4. Preparar resultado final
            result = {
                "success": whatsapp_result["success"],
                "message": follow_up_message,
                "whatsapp_result": whatsapp_result,
                "status_result": status_result,
                "lead_id": lead_id,
                "phone_number": phone_number,
                "timestamp": datetime.now().isoformat()
            }
            
            if whatsapp_result["success"]:
                logger.info(f"✅ Follow-up enviado com sucesso para {phone_number}")
            else:
                logger.error(f"❌ Falha no envio do follow-up para {phone_number}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro geral no follow-up: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "lead_id": lead_id,
                "phone_number": phone_number,
                "timestamp": datetime.now().isoformat()
            }
    
    def should_send_follow_up(self, lead_data: Dict[str, Any]) -> bool:
        """
        Verifica se deve enviar follow-up baseado nos dados do lead.
        
        Args:
            lead_data: Dados do lead
            
        Returns:
            bool: True se deve enviar follow-up
        """
        try:
            # Verificar se já foi enviado follow-up
            additional_data = lead_data.get('additional_data', {})
            if additional_data.get('follow_up_sent'):
                logger.info("Follow-up já foi enviado anteriormente")
                return False
            
            # Verificar se lead está qualificado
            qualification_status = lead_data.get('qualification_status', 'NEW')
            if qualification_status == 'DISQUALIFIED':
                logger.info("Lead desqualificado, não enviar follow-up")
                return False
            
            # Verificar se lead demonstrou interesse
            conversation_state = lead_data.get('conversation_state', 'INITIAL')
            if conversation_state in ['INTERESTED', 'CONTRACT_CREATED']:
                logger.info("Lead já demonstrou interesse, não enviar follow-up")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar se deve enviar follow-up: {str(e)}")
            return False
    
    def get_follow_up_delay_seconds(self) -> int:
        """
        Retorna o delay para follow-up em segundos.
        
        Returns:
            int: Delay em segundos
        """
        return get_follow_up_delay()


def main():
    """
    Função principal para teste e execução via linha de comando.
    
    Exemplo de uso:
    python follow_up_agent.py --lead-id "123" --phone "+5581999887766" --name "João Silva"
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerar e enviar follow-up automático')
    parser.add_argument('--lead-id', required=True, help='ID do lead')
    parser.add_argument('--phone', required=True, help='Número de telefone')
    parser.add_argument('--name', required=True, help='Nome do lead')
    parser.add_argument('--city', required=True, help='Cidade do lead')
    parser.add_argument('--invoice-amount', type=float, default=0, help='Valor da conta')
    
    args = parser.parse_args()
    
    # Dados do lead
    lead_data = {
        "name": args.name,
        "city": args.city,
        "invoice_amount": args.invoice_amount
    }
    
    # Criar agente e executar follow-up
    agent = FollowUpAgent()
    result = agent.generate_follow_up(
        lead_id=args.lead_id,
        phone_number=args.phone,
        lead_data=lead_data
    )
    
    # Exibir resultado
    if result['success']:
        print(f"✅ Follow-up enviado com sucesso!")
        print(f"📱 Phone: {result['phone_number']}")
        print(f"💬 Message: {result['message']}")
        print(f"📧 Message ID: {result['whatsapp_result']['message_id']}")
    else:
        print(f"❌ Erro no follow-up:")
        print(f"📱 Phone: {result['phone_number']}")
        print(f"💥 Erro: {result.get('error', 'Erro desconhecido')}")


if __name__ == "__main__":
    main() 