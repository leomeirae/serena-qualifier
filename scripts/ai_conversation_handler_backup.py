#!/usr/bin/env python3
"""
AI Conversation Handler - Orquestrador Principal.

Este módulo orquestra o fluxo de conversas com leads, utilizando módulos especializados
para extração de localização, processamento de imagem e gerenciamento de contexto.

Author: Serena-Coder AI Agent
Version: 2.0.0 - Refatoração Task-331 (Orquestrador)
"""

import os
import sys
import logging
import requests
from typing import Dict, Any, Optional, List, Tuple
from openai import OpenAI

# Importar módulos especializados
from location_extractor import LocationExtractor
from vision_processor import VisionProcessor
from conversation_context import ConversationContextManager
from serena_api import SerenaAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIConversationHandler:
    """
    Orquestrador principal para conversas com IA.
    
    Coordena todos os módulos especializados para processar mensagens de leads,
    extrair informações, buscar promoções e gerenciar o fluxo da conversa.
    """
    
    def __init__(self):
        """Inicializa o orquestrador com todos os módulos especializados."""
        try:
            # Inicializar módulos especializados
            self.location_extractor = LocationExtractor()
            self.vision_processor = VisionProcessor()
            self.context_manager = ConversationContextManager()
            self.serena_api = SerenaAPI()
            
            # Configurar OpenAI
            self.openai_api_key = os.getenv('OPENAI_API_KEY')
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY não encontrada")
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            
            # Configurar WhatsApp
            self.whatsapp_token = os.getenv("WHATSAPP_API_TOKEN")
            self.whatsapp_phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
            
            logger.info("🚀 AIConversationHandler inicializado com sucesso")
            
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
        Processa uma mensagem do lead (ponto de entrada principal).
        
        Args:
            phone_number (str): Número do lead
            message (str): Mensagem enviada
            media_id (Optional[str]): ID da mídia (se houver imagem)
            ai_model (str): Modelo da OpenAI
            max_tokens (int): Máximo de tokens
            temperature (float): Temperatura da IA
            
        Returns:
            Dict[str, Any]: Resultado do processamento
        """
        try:
            phone_number = self._normalize_phone_number(phone_number)
            logger.info(f"📱 Processando mensagem de {phone_number}: {message[:100]}...")
            
            # 1. Verificar se é imagem de conta de energia
            if media_id and self.vision_processor.is_energy_bill_image(message):
                return self._handle_energy_bill_image(phone_number, message, media_id)
            
            # 2. Tentar extrair localização
            location = self.location_extractor.extract_location_from_message(message)
            if location:
                return self._handle_location_detected(phone_number, message, location)
            
            # 3. Gerar resposta padrão
            return self._handle_general_message(phone_number, message, ai_model, max_tokens, temperature)
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento: {str(e)}")
            return self._create_error_response(str(e))
    
    def _handle_energy_bill_image(
        self, 
        phone_number: str, 
        message: str, 
        media_id: str
    ) -> Dict[str, Any]:
        """
        Processa imagem de conta de energia.
        
        Args:
            phone_number (str): Número do lead
            message (str): Mensagem do lead
            media_id (str): ID da mídia
            
        Returns:
            Dict[str, Any]: Resultado do processamento
        """
        try:
            logger.info(f"🔍 Processando conta de energia para {phone_number}")
            
            # Obter contexto atual
            context = self.context_manager.get_conversation_context(phone_number)
            promotions = context.get('promotions', [])
            
            # Processar imagem com Vision API
            result = self.vision_processor.process_energy_bill_image(
                media_id, message, promotions
            )
            
            if result.get('success'):
                # Salvar dados extraídos no contexto
                self.context_manager.save_extracted_data(
                    phone_number, 
                    result['extracted_data']
                )
                
                # Atualizar estágio da conversa
                self.context_manager.update_conversation_stage(
                    phone_number, 
                    'energy_bill_processed'
                )
                
                # Salvar lead qualificado no Supabase
                self._save_qualified_lead(phone_number, result['extracted_data'])
                
                # Enviar resposta
                response_sent = self._send_whatsapp_message(
                    phone_number, 
                    result['final_response']
                )
                
                return {
                    "success": True,
                    "message": "Conta de energia processada com sucesso",
                    "extracted_data": result['extracted_data'],
                    "response_sent": response_sent,
                    "stage": "completed"
                }
            else:
                # Erro no processamento
                error_response = self._handle_image_processing_error(
                    phone_number, 
                    result.get('error', 'Erro desconhecido')
                )
                return error_response
                
        except Exception as e:
            logger.error(f"❌ Erro no processamento da imagem: {str(e)}")
            return self._handle_image_processing_error(phone_number, str(e))
    
    def _handle_location_detected(
        self, 
        phone_number: str, 
        message: str, 
        location: Tuple[str, str]
    ) -> Dict[str, Any]:
        """
        Processa localização detectada.
        
        Args:
            phone_number (str): Número do lead
            message (str): Mensagem original
            location (Tuple[str, str]): (cidade, estado)
            
        Returns:
            Dict[str, Any]: Resultado do processamento
        """
        try:
            city, state = location
            logger.info(f"📍 Localização detectada: {city}/{state}")
            
            # Buscar promoções na API Serena
            promotions = self.serena_api.get_promotions_by_location(city, state)
            
            # Salvar no contexto
            self.context_manager.save_conversation_context(
                phone_number,
                city=city,
                state=state,
                promotions=promotions
            )
            
            # Gerar resposta com promoções
            ai_response = self._generate_ai_response(
                message, city, state, promotions
            )
            
            # Enviar resposta
            response_sent = self._send_whatsapp_message(phone_number, ai_response)
            
            return {
                "success": True,
                "message": "Localização processada e promoções encontradas",
                "location": {"city": city, "state": state},
                "promotions": promotions,
                "ai_response": ai_response,
                "response_sent": response_sent
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento da localização: {str(e)}")
            return self._create_error_response(str(e))
    
    def _handle_general_message(
        self, 
        phone_number: str, 
        message: str, 
        ai_model: str, 
        max_tokens: int, 
        temperature: float
    ) -> Dict[str, Any]:
        """
        Processa mensagem geral (sem localização ou imagem).
        
        Args:
            phone_number (str): Número do lead
            message (str): Mensagem do lead
            ai_model (str): Modelo da OpenAI
            max_tokens (int): Máximo de tokens
            temperature (float): Temperatura
            
        Returns:
            Dict[str, Any]: Resultado do processamento
        """
        try:
            # Verificar se já tem contexto
            context = self.context_manager.get_conversation_context(phone_number)
            
            if context.get('city') and context.get('state'):
                # Já tem localização, gerar resposta contextual
                ai_response = self._generate_ai_response(
                    message, 
                    context.get('city'), 
                    context.get('state'),
                    context.get('promotions', []),
                    ai_model, max_tokens, temperature
                )
            else:
                # Primeira interação, solicitar localização
                ai_response = self._get_initial_response_prompt(message)
                ai_response = self._generate_openai_response(
                    ai_response, ai_model, max_tokens, temperature
                )
            
            # Enviar resposta
            response_sent = self._send_whatsapp_message(phone_number, ai_response)
            
            return {
                "success": True,
                "message": "Mensagem geral processada",
                "ai_response": ai_response,
                "response_sent": response_sent,
                "has_context": bool(context)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na mensagem geral: {str(e)}")
            return self._create_error_response(str(e))
    
    def _save_qualified_lead(self, phone_number: str, extracted_data: Dict[str, Any]) -> None:
        """
        Salva lead qualificado no Supabase.
        
        Args:
            phone_number (str): Número do lead
            extracted_data (Dict[str, Any]): Dados extraídos da conta
        """
        try:
            # Importar função de persistência
            from save_lead_to_supabase import save_qualified_lead
            
            # Obter contexto completo
            context = self.context_manager.get_conversation_context(phone_number)
            
            # Chamar função de persistência
            save_qualified_lead(
                phone_number=phone_number,
                location_data={
                    'city': context.get('city'),
                    'state': context.get('state')
                },
                energy_bill_data=extracted_data,
                promotions_data=context.get('promotions', []),
                conversation_state=context
            )
            
            logger.info(f"💾 Lead qualificado salvo no Supabase: {phone_number}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar lead qualificado: {str(e)}")
            # Não interrompe o fluxo se a persistência falhar
    
    def _generate_ai_response(
        self, 
        lead_message: str, 
        city: Optional[str] = None,
        state: Optional[str] = None,
        promotions: Optional[List[Dict[str, Any]]] = None,
        model: str = "gpt-4o-mini",
        max_tokens: int = 400,
        temperature: float = 0.7
    ) -> str:
        """
        Gera resposta da IA baseada no contexto.
        
        Args:
            lead_message (str): Mensagem do lead
            city (Optional[str]): Cidade
            state (Optional[str]): Estado
            promotions (Optional[List[Dict[str, Any]]]): Promoções
            model (str): Modelo OpenAI
            max_tokens (int): Máximo de tokens
            temperature (float): Temperatura
            
        Returns:
            str: Resposta gerada
        """
        try:
            if city and state and promotions:
                prompt = self._get_promotions_response_prompt(
                    lead_message, city, state, promotions
                )
            else:
                prompt = self._get_initial_response_prompt(lead_message)
            
            return self._generate_openai_response(prompt, model, max_tokens, temperature)
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de resposta: {str(e)}")
            return "Obrigada pelo seu interesse! Em breve um especialista entrará em contato. 😊"
    
    def _generate_openai_response(
        self, 
        prompt: str, 
        model: str = "gpt-4o-mini",
        max_tokens: int = 400,
        temperature: float = 0.7
    ) -> str:
        """
        Gera resposta usando OpenAI.
        
        Args:
            prompt (str): Prompt para a IA
            model (str): Modelo a usar
            max_tokens (int): Máximo de tokens
            temperature (float): Temperatura
            
        Returns:
            str: Resposta gerada
        """
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
            return "Obrigada pelo contato! Um especialista entrará em contato em breve. 😊"
    
    def _get_initial_response_prompt(self, lead_message: str) -> str:
        """Gera prompt para primeira resposta."""
        return f"""Você é a Serena, assistente virtual da SRna Energia. Um lead interessado em economizar na conta de luz acabou de enviar a mensagem: "{lead_message}"

Sua resposta deve:
1. Agradecer o interesse em economizar com a Serena Energia
2. Explicar brevemente que a Serena oferece energia solar sem instalação
3. Solicitar a cidade e estado do lead para verificar disponibilidade
4. Ser amigável, clara e concisa (máximo 2 parágrafos)
5. Usar emojis moderadamente para humanizar

Gere apenas a resposta que será enviada ao lead via WhatsApp:"""
    
    def _get_promotions_response_prompt(
        self, 
        lead_message: str, 
        city: str, 
        state: str, 
        promotions: List[Dict[str, Any]]
    ) -> str:
        """Gera prompt para resposta com promoções."""
        if promotions:
            promotions_text = []
            for i, promo in enumerate(promotions, 1):
                distributor = promo.get('energyUtilityName', 'Distribuidora')
                discount = promo.get('discountPercentage', 0)
                promotions_text.append(f"{i}. {distributor} - {discount}% de desconto")
            
            promotions_str = "\n".join(promotions_text)
            
            return f"""O lead enviou: "{lead_message}" e você identificou que mora em {city}/{state}.

ÓTIMA NOTÍCIA! Encontramos {len(promotions)} promoções disponíveis para {city}/{state}:

{promotions_str}

Sua resposta deve:
1. Confirmar a localização ({city}/{state})
2. Apresentar as promoções de forma clara e atrativa
3. Explicar que são descontos na conta de luz com energia solar sem instalação
4. Solicitar o envio da conta de energia para calcular economia exata
5. Ser entusiasmada e profissional

Gere apenas a resposta que será enviada ao lead via WhatsApp:"""
        else:
            return f"""O lead mora em {city}/{state} mas não encontramos promoções disponíveis no momento.

Sua resposta deve:
1. Confirmar a localização
2. Informar que não há promoções disponíveis no momento para essa região
3. Explicar que novas promoções surgem frequentemente
4. Oferecer para manter contato quando houver novidades
5. Ser empática e profissional

Gere apenas a resposta que será enviada ao lead via WhatsApp:"""
    
    def _send_whatsapp_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Envia mensagem via WhatsApp API.
        
        Args:
            phone_number (str): Número do destinatário
            message (str): Mensagem a enviar
            
        Returns:
            Dict[str, Any]: Resultado do envio
        """
        try:
            if not self.whatsapp_token or not self.whatsapp_phone_id:
                logger.error("❌ Credenciais WhatsApp não configuradas")
                return {"success": False, "error": "Credenciais não configuradas"}
            
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
                logger.info(f"✅ Mensagem enviada para {phone_number}")
                return {"success": True, "response": response.json()}
            else:
                logger.error(f"❌ Erro no envio: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"❌ Erro no WhatsApp: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _handle_image_processing_error(
        self, 
        phone_number: str, 
        error_message: str
    ) -> Dict[str, Any]:
        """
        Trata erros no processamento de imagem.
        
        Args:
            phone_number (str): Número do lead
            error_message (str): Mensagem de erro
            
        Returns:
            Dict[str, Any]: Resposta de erro
        """
        try:
            error_response = """Obrigada por enviar sua conta! 😊

Tive uma pequena dificuldade para analisar a imagem. Poderia tentar:

• Enviar uma foto mais clara da conta
• Verificar se todos os dados estão visíveis
• Ou me enviar sua cidade e estado para buscar as promoções disponíveis

Estou aqui para ajudar! 💡"""
            
            response_sent = self._send_whatsapp_message(phone_number, error_response)
            
            return {
                "success": False,
                "error": error_message,
                "recovery_message_sent": response_sent,
                "stage": "image_error_recovery"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no tratamento de erro: {str(e)}")
            return self._create_error_response(str(e))
    
    def _normalize_phone_number(self, phone: str) -> str:
        """
        Normaliza número de telefone.
        
        Args:
            phone (str): Número original
            
        Returns:
            str: Número normalizado
        """
        try:
            # Remove caracteres não numéricos
            clean_phone = ''.join(filter(str.isdigit, phone))
            
            # Adiciona código do país se necessário
            if len(clean_phone) == 11 and clean_phone.startswith('11'):
                clean_phone = '55' + clean_phone
            elif len(clean_phone) == 10:
                clean_phone = '5511' + clean_phone
            elif not clean_phone.startswith('55'):
                clean_phone = '55' + clean_phone
            
            return clean_phone
            
        except Exception as e:
            logger.error(f"❌ Erro na normalização: {str(e)}")
            return phone
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Cria resposta padronizada de erro.
        
        Args:
            error_message (str): Mensagem de erro
            
        Returns:
            Dict[str, Any]: Resposta de erro
        """
        return {
            "success": False,
            "error": error_message,
            "message": "Erro interno no processamento"
        }


# Instância global para compatibilidade
_global_handler = None


def get_handler() -> AIConversationHandler:
    """
    Retorna instância global do handler.
    
    Returns:
        AIConversationHandler: Instância do handler
    """
    global _global_handler
    if _global_handler is None:
        _global_handler = AIConversationHandler()
    return _global_handler


def handle_lead_message(
    phone_number: str,
    message: str,
    media_id: Optional[str] = None,
    ai_model: str = "gpt-4o-mini",
    max_tokens: int = 400,
    temperature: float = 0.7
) -> Dict[str, Any]:
    """
    Função de conveniência para processar mensagem de lead.
    
    Args:
        phone_number (str): Número do lead
        message (str): Mensagem enviada
        media_id (Optional[str]): ID da mídia
        ai_model (str): Modelo OpenAI
        max_tokens (int): Máximo de tokens
        temperature (float): Temperatura
        
    Returns:
        Dict[str, Any]: Resultado do processamento
    """
    try:
        handler = get_handler()
        return handler.process_message(
            phone_number, message, media_id, ai_model, max_tokens, temperature
        )
    except Exception as e:
        logger.error(f"❌ Erro na função de conveniência: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Erro na função handle_lead_message"
        }


def main():
    """Função principal para execução direta."""
    try:
        print("🚀 Iniciando AIConversationHandler...")
        handler = AIConversationHandler()
        
        # Teste básico
        test_result = handler.process_message(
            "5511999999999",
            "Olá, quero economizar na conta de luz"
        )
        
        print(f"Resultado do teste: {test_result}")
        print("✅ Handler inicializado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 