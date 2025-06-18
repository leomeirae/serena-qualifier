#!/usr/bin/env python3
"""
AI Conversation Handler - Orquestrador Principal

Este módulo atua como orquestrador principal, integrando os módulos especializados
para processar conversas de leads de energia solar.

Author: Serena-Coder AI Agent
Version: 2.0.0 - Refatoração para modularização
Created: 2025-01-17
"""

import os
import sys
import logging
import requests
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Importar módulos especializados
from location_extractor import LocationExtractor
from vision_processor import VisionProcessor
from conversation_context import ConversationContext

# Importar dependências existentes
try:
    from serena_api import SerenaAPI
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from serena_api import SerenaAPI

# Importar função de persistência
try:
    from save_lead_to_supabase import save_qualified_lead
except ImportError:
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from save_lead_to_supabase import save_qualified_lead
    except ImportError:
        def save_qualified_lead(data):
            return {'success': False, 'error': 'Função não disponível'}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class AIConversationHandler:
    """
    Orquestrador principal para processamento de conversas de leads.
    
    Integra os módulos especializados:
    - LocationExtractor: Detecção de localização
    - VisionProcessor: Processamento de imagens
    - ConversationContext: Gerenciamento de estado
    - SerenaAPI: Consulta de promoções
    """
    
    def __init__(self):
        """Inicializa o orquestrador e seus componentes."""
        try:
            # Configurar variáveis de ambiente
            self.openai_api_key = os.getenv('OPENAI_API_KEY')
            self.whatsapp_token = os.getenv('WHATSAPP_API_TOKEN')
            self.whatsapp_phone_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
            self.serena_token = os.getenv('SERENA_API_TOKEN')
            
            if not all([self.openai_api_key, self.whatsapp_token, self.whatsapp_phone_id, self.serena_token]):
                raise ValueError("Variáveis de ambiente obrigatórias não configuradas")
            
            # Inicializar clientes
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            self.serena_api = SerenaAPI()
            
            # Inicializar módulos especializados
            self.location_extractor = LocationExtractor()
            self.vision_processor = VisionProcessor(self.openai_client, self.whatsapp_token)
            self.conversation_context = ConversationContext()
            
            logger.info("✅ AIConversationHandler inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {str(e)}")
            raise
    
    def process_message(
        self, 
        phone_number: str, 
        message: str,
        media_id: Optional[str] = None,
        ai_model: str = "gpt-4o-mini",
        max_tokens: int = 400,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Processa mensagem do lead e orquestra o fluxo da conversa.
        
        Args:
            phone_number (str): Número do lead
            message (str): Mensagem recebida
            media_id (Optional[str]): ID da mídia (se houver imagem)
            ai_model (str): Modelo OpenAI
            max_tokens (int): Máximo de tokens
            temperature (float): Temperatura da IA
            
        Returns:
            Dict[str, Any]: Resultado do processamento
        """
        try:
            phone_number = self._normalize_phone_number(phone_number)
            logger.info(f"📱 Processando mensagem de {phone_number}: {message[:100]}...")
            
            # Verificar se conversa já foi finalizada
            if self.conversation_context.is_conversation_completed(phone_number):
                return self._handle_completed_conversation(phone_number)
            
            # Fluxo de processamento de imagem
            if media_id and self.vision_processor.is_energy_bill_image(message):
                return self._process_energy_bill_image(
                    phone_number, message, media_id, ai_model, max_tokens, temperature
                )
            
            # Fluxo de detecção de localização
            location = self.location_extractor.extract_location_from_message(message)
            if location:
                return self._process_location_message(
                    phone_number, message, location, ai_model, max_tokens, temperature
                )
            
            # Fluxo de mensagem inicial (sem localização)
            return self._process_initial_message(
                phone_number, message, ai_model, max_tokens, temperature
            )
            
        except Exception as e:
            logger.error(f"💥 Erro no processamento: {str(e)}")
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}",
                "phone_number": phone_number
            }
    
    def _process_energy_bill_image(
        self, phone_number: str, message: str, media_id: str, 
        ai_model: str, max_tokens: int, temperature: float
    ) -> Dict[str, Any]:
        """Processa imagem da conta de energia."""
        logger.info(f"🔍 Processando imagem da conta de energia - Media ID: {media_id}")
        
        try:
            # Obter URL da imagem
            image_url = self.vision_processor.get_whatsapp_media_url(media_id)
            if not image_url:
                return self._handle_image_error(phone_number, "Não consegui acessar a imagem")
            
            # Extrair dados da conta
            extracted_data = self.vision_processor.extract_bill_data_with_vision(
                image_url, ai_model, max_tokens, 0.3
            )
            
            if not extracted_data.get('success'):
                return self._handle_image_error(phone_number, "Não consegui ler os dados da conta")
            
            # Gerar resposta final
            final_response = self.vision_processor.generate_final_conversation_response(
                extracted_data, ai_model, max_tokens, temperature
            )
            
            # Enviar resposta
            whatsapp_result = self._send_whatsapp_message(phone_number, final_response)
            
            if whatsapp_result['success']:
                # Salvar contexto completo
                self.conversation_context.save_context(
                    phone_number,
                    extracted_data=extracted_data,
                    conversation_completed=True
                )
                
                # Persistir no Supabase
                self._save_to_supabase(phone_number, extracted_data, ai_model)
                
                return {
                    "success": True,
                    "ai_response": final_response,
                    "whatsapp_message_id": whatsapp_result['message_id'],
                    "phone_number": phone_number,
                    "model_used": ai_model,
                    "has_media": True,
                    "media_processed": True,
                    "extracted_data": extracted_data,
                    "conversation_completed": True,
                    "supabase_saved": True
                }
            else:
                return {
                    "success": False,
                    "error": f"Falha no envio WhatsApp: {whatsapp_result['error']}",
                    "ai_response": final_response,
                    "phone_number": phone_number,
                    "has_media": True,
                    "media_processed": True,
                    "extracted_data": extracted_data
                }
                
        except Exception as e:
            logger.error(f"💥 Erro no processamento da imagem: {str(e)}")
            return self._handle_image_error(phone_number, f"Erro interno: {str(e)}")
    
    def _process_location_message(
        self, phone_number: str, message: str, location: tuple,
        ai_model: str, max_tokens: int, temperature: float
    ) -> Dict[str, Any]:
        """Processa mensagem com localização detectada."""
        city, state = location
        logger.info(f"📍 Localização detectada: {city}/{state}")
        
        try:
            # Consultar promoções na API Serena
            promotions = []
            try:
                promotions = self.serena_api.get_plans_by_city(city, state)
                logger.info(f"🎯 Encontradas {len(promotions)} promoções para {city}/{state}")
            except Exception as e:
                logger.warning(f"⚠️ Erro na API Serena: {str(e)}")
            
            # Gerar resposta personalizada
            if promotions:
                prompt = self.location_extractor.get_promotions_response_prompt(
                    message, city, state, promotions
                )
            else:
                prompt = self.location_extractor.get_promotions_response_prompt(
                    message, city, state, []
                )
            
            ai_response = self._generate_ai_response(prompt, ai_model, max_tokens, temperature)
            
            # Enviar resposta
            whatsapp_result = self._send_whatsapp_message(phone_number, ai_response)
            
            if whatsapp_result['success']:
                # Salvar contexto
                self.conversation_context.save_context(
                    phone_number, city=city, state=state, promotions=promotions
                )
                
                return {
                    "success": True,
                    "ai_response": ai_response,
                    "whatsapp_message_id": whatsapp_result['message_id'],
                    "phone_number": phone_number,
                    "model_used": ai_model,
                    "has_media": False,
                    "location_detected": True,
                    "city": city,
                    "state": state,
                    "promotions_found": len(promotions),
                    "promotions": promotions
                }
            else:
                return {
                    "success": False,
                    "error": f"Falha no envio WhatsApp: {whatsapp_result['error']}",
                    "ai_response": ai_response,
                    "phone_number": phone_number,
                    "location_detected": True,
                    "city": city,
                    "state": state,
                    "promotions_found": len(promotions)
                }
                
        except Exception as e:
            logger.error(f"💥 Erro no processamento de localização: {str(e)}")
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}",
                "phone_number": phone_number,
                "location_detected": True,
                "city": city,
                "state": state
            }
    
    def _process_initial_message(
        self, phone_number: str, message: str,
        ai_model: str, max_tokens: int, temperature: float
    ) -> Dict[str, Any]:
        """Processa mensagem inicial (sem localização)."""
        logger.info(f"💬 Processando mensagem inicial")
        
        try:
            # Gerar prompt inicial
            prompt = self.location_extractor.get_initial_response_prompt(message)
            ai_response = self._generate_ai_response(prompt, ai_model, max_tokens, temperature)
            
            # Enviar resposta
            whatsapp_result = self._send_whatsapp_message(phone_number, ai_response)
            
            if whatsapp_result['success']:
                return {
                    "success": True,
                    "ai_response": ai_response,
                    "whatsapp_message_id": whatsapp_result['message_id'],
                    "phone_number": phone_number,
                    "model_used": ai_model,
                    "has_media": False,
                    "location_detected": False,
                    "requesting_location": True
                }
            else:
                return {
                    "success": False,
                    "error": f"Falha no envio WhatsApp: {whatsapp_result['error']}",
                    "ai_response": ai_response,
                    "phone_number": phone_number,
                    "location_detected": False,
                    "requesting_location": True
                }
                
        except Exception as e:
            logger.error(f"💥 Erro no processamento inicial: {str(e)}")
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}",
                "phone_number": phone_number,
                "location_detected": False
            }
    
    def _handle_completed_conversation(self, phone_number: str) -> Dict[str, Any]:
        """Trata tentativa de interação com conversa já finalizada."""
        return {
            "success": True,
            "message": "Conversa já foi finalizada",
            "phone_number": phone_number,
            "conversation_completed": True
        }
    
    def _handle_image_error(self, phone_number: str, error_message: str) -> Dict[str, Any]:
        """Trata erros no processamento de imagem."""
        try:
            friendly_message = self.vision_processor.create_error_response(error_message)
            whatsapp_result = self._send_whatsapp_message(phone_number, friendly_message)
            
            return {
                "success": False,
                "error": error_message,
                "ai_response": friendly_message,
                "phone_number": phone_number,
                "has_media": True,
                "media_processed": False,
                "whatsapp_sent": whatsapp_result.get('success', False),
                "whatsapp_message_id": whatsapp_result.get('message_id')
            }
        except Exception as e:
            logger.error(f"❌ Erro ao tratar erro de imagem: {str(e)}")
            return {
                "success": False,
                "error": f"Erro duplo: {error_message} + {str(e)}",
                "phone_number": phone_number,
                "has_media": True,
                "media_processed": False
            }
    
    def _save_to_supabase(self, phone_number: str, extracted_data: Dict[str, Any], model_used: str):
        """Salva lead qualificado no Supabase."""
        try:
            # Preparar dados consolidados
            context = self.conversation_context.get_context(phone_number)
            lead_data = {
                "phone_number": phone_number,
                "extracted_data": extracted_data,
                "conversation_completed": True,
                "model_used": model_used,
                "media_processed": True,
                "city": context.get('city'),
                "state": context.get('state'),
                "promotions": context.get('promotions', [])
            }
            
            save_result = save_qualified_lead(lead_data)
            if save_result['success']:
                logger.info(f"💾 Lead qualificado salvo no Supabase: {save_result.get('lead_id')}")
            else:
                logger.warning(f"⚠️ Falha ao salvar lead no Supabase: {save_result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Erro crítico ao salvar lead no Supabase: {str(e)}")
    
    def _generate_ai_response(
        self, prompt: str, model: str, max_tokens: int, temperature: float
    ) -> str:
        """Gera resposta usando OpenAI."""
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"❌ Erro na OpenAI: {str(e)}")
            return "Desculpe, tive um problema técnico. Pode tentar novamente?"
    
    def _normalize_phone_number(self, phone: str) -> str:
        """Normaliza número de telefone."""
        phone = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not phone.startswith("+"):
            if phone.startswith("55"):
                phone = "+" + phone
            else:
                phone = "+55" + phone
        return phone
    
    def _send_whatsapp_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Envia mensagem via WhatsApp API."""
        try:
            url = f"https://graph.facebook.com/v23.0/{self.whatsapp_phone_id}/messages"
            headers = {
                "Authorization": f"Bearer {self.whatsapp_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {"body": message}
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                response_data = response.json()
                message_id = response_data.get("messages", [{}])[0].get("id", "unknown")
                logger.info(f"✅ Mensagem enviada para {phone_number}: {message_id}")
                return {"success": True, "message_id": message_id}
            else:
                error_msg = response.json().get("error", {}).get("message", "Erro desconhecido")
                logger.error(f"❌ Falha no WhatsApp API: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            logger.error(f"❌ Erro no envio WhatsApp: {str(e)}")
            return {"success": False, "error": str(e)}


# Funções de compatibilidade para uso externo
def get_handler() -> AIConversationHandler:
    """Obtém instância singleton do handler."""
    if not hasattr(get_handler, '_instance'):
        get_handler._instance = AIConversationHandler()
    return get_handler._instance


def handle_lead_message(
    phone_number: str,
    message: str,
    media_id: Optional[str] = None,
    ai_model: str = "gpt-4o-mini",
    max_tokens: int = 400,
    temperature: float = 0.7
) -> Dict[str, Any]:
    """Função wrapper para processamento de mensagens."""
    handler = get_handler()
    return handler.process_message(phone_number, message, media_id, ai_model, max_tokens, temperature)


def main():
    """Função principal para teste."""
    try:
        handler = AIConversationHandler()
        logger.info("🚀 AI Conversation Handler iniciado com sucesso!")
        
        # Teste básico
        test_result = handler.process_message(
            "+5511999887766",
            "Oi, quero economizar na conta de luz"
        )
        
        logger.info(f"📊 Resultado do teste: {test_result}")
        
    except Exception as e:
        logger.error(f"💥 Erro na execução: {str(e)}")


if __name__ == "__main__":
    main() 