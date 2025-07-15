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
import json
import base64
import re
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from pythonjsonlogger import jsonlogger
import psycopg2

# Importar módulos especializados
from scripts.location_extractor import LocationExtractor
from scripts.conversation_context import ConversationContext

# Importar dependências existentes
try:
    from scripts.serena_api import SerenaAPI
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from scripts.serena_api import SerenaAPI

# A função de persistência será chamada a partir dos resultados, não diretamente aqui
# try:
#     from save_lead_to_supabase import save_qualified_lead
# except ImportError:
#     try:
#         sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#         from save_lead_to_supabase import save_qualified_lead
#     except ImportError:
#         def save_qualified_lead(data):
#             return {'success': False, 'error': 'Função não disponível'}

# Configure structured (JSON) logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logHandler = logging.StreamHandler()
# Example of a custom format
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s'
)
logHandler.setFormatter(formatter)
# Avoid adding duplicate handlers
if not logger.handlers:
    logger.addHandler(logHandler)

# Load environment variables
load_dotenv()


def normalize_phone(phone):
    """Normalizar número de telefone removendo caracteres especiais e código do país"""
    digits = re.sub(r'\D', '', phone)  # remove tudo que não for número
    if digits.startswith('55'):
        digits = digits[2:]  # remove o código do país
    return digits


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
            # Decodifica se estiver em base64 (Kestra/Coolify pode passar secrets assim)
            if self.openai_api_key and not self.openai_api_key.startswith('sk-'):
                try:
                    self.openai_api_key = base64.b64decode(self.openai_api_key).decode()
                except Exception:
                    pass  # já está em texto puro ou erro de decodificação
            
            # Limpar quebras de linha e espaços em branco
            if self.openai_api_key:
                self.openai_api_key = self.openai_api_key.strip()
            self.whatsapp_token = os.getenv('WHATSAPP_API_TOKEN')
            self.whatsapp_phone_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
            self.serena_token = os.getenv('SERENA_API_TOKEN')
            self.db_connection_string = self._get_db_connection_string()
            
            # Verificar variáveis obrigatórias com logs específicos
            missing_vars = []
            if not self.openai_api_key:
                missing_vars.append("OPENAI_API_KEY")
            if not self.whatsapp_token:
                missing_vars.append("WHATSAPP_API_TOKEN")
            if not self.whatsapp_phone_id:
                missing_vars.append("WHATSAPP_PHONE_NUMBER_ID")
            if not self.serena_token:
                missing_vars.append("SERENA_API_TOKEN")
            
            if missing_vars:
                error_msg = f"Variáveis de ambiente obrigatórias não configuradas: {', '.join(missing_vars)}"
                logger.error(f"❌ {error_msg}")
                raise ValueError(error_msg)
            
            # Inicializar clientes com tratamento de erro
            try:
                logger.info("🤖 Inicializando cliente OpenAI...")
                self.openai_client = OpenAI(
                    api_key=self.openai_api_key,
                    timeout=30.0,  # Timeout padrão de 30 segundos
                    max_retries=3   # Retry automático em caso de erro
                )
                logger.info("✅ Cliente OpenAI inicializado com sucesso")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar cliente OpenAI: {str(e)}")
                raise ValueError(f"Falha na inicialização do cliente OpenAI: {str(e)}")
            
            self.serena_api = SerenaAPI()
            
            # Inicializar módulos especializados
            self.location_extractor = LocationExtractor()
            self.conversation_context = ConversationContext()
            
            # Estratégias de processamento de mensagens em ordem de prioridade
            self._message_strategies = [
                self._process_energy_bill_image,
                self._process_location_message,
                self._process_initial_message,
            ]
            
            logger.info("✅ AIConversationHandler inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {str(e)}")
            raise
    
    def _get_db_connection_string(self) -> str:
        """Obtém a string de conexão do banco de dados."""
        encoded_conn_string = os.getenv('SECRET_DB_CONNECTION_STRING')
        if not encoded_conn_string:
            logger.warning("SECRET_DB_CONNECTION_STRING não encontrada")
            return ""
        
        try:
            # Decodifica a string de conexão (base64)
            db_connection_string = base64.b64decode(encoded_conn_string).decode('utf-8')
            logger.info("✅ String de conexão do banco decodificada com sucesso")
            return db_connection_string
        except Exception as e:
            logger.error(f"❌ Erro ao decodificar string de conexão: {str(e)}")
            return ""
    
    def _get_lead_data(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Recupera dados do lead do banco de dados via SECRET_DB_CONNECTION_STRING."""
        try:
            # Normalizar número de telefone
            normalized_phone = normalize_phone(phone_number)
            
            # Buscar dados do lead no banco
            if not self.db_connection_string:
                logger.warning("String de conexão do banco não disponível")
                return None
            conn = psycopg2.connect(self.db_connection_string)
            cur = conn.cursor()
            query = "SELECT id, phone_number, name, email, invoice_amount, additional_data, created_at FROM leads WHERE phone_number = %s ORDER BY created_at DESC LIMIT 1"
            cur.execute(query, (normalized_phone,))
            result = cur.fetchone()
            cur.close()
            conn.close()
            if result:
                lead_data = {
                    'id': result[0],
                    'phone_number': result[1],
                    'name': result[2],
                    'email': result[3],
                    'invoice_amount': result[4],
                    'additional_data': json.loads(result[5]) if result[5] else {},
                    'created_at': result[6]
                }
                logger.info(f"✅ Dados do lead recuperados para {phone_number}: {lead_data['name']}")
                return lead_data
            else:
                logger.warning(f"❌ Lead não encontrado para {phone_number}")
                return None
        except Exception as e:
            logger.error(f"❌ Erro ao recuperar dados do lead: {str(e)}")
            return None
    
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
            phone_number = normalize_phone(phone_number)
            logger.info(f"📱 Processando mensagem de {phone_number}: {message[:100]}...")
            
            # Verificar se conversa já foi finalizada
            if self.conversation_context.is_conversation_completed(phone_number):
                return self._handle_completed_conversation(phone_number)
            
            # Iterar sobre as estratégias de processamento
            for strategy in self._message_strategies:
                result = strategy(
                    phone_number, message, media_id=media_id,
                    ai_model=ai_model, max_tokens=max_tokens, temperature=temperature
                )
                if result is not None:
                    return result

            # Se nenhuma estratégia for aplicável (fallback, embora improvável)
            return {
                "success": False,
                "error": "Nenhuma estratégia de processamento aplicável.",
                "phone_number": phone_number
            }
            
        except Exception as e:
            logger.error(f"💥 Erro no processamento: {str(e)}")
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}",
                "phone_number": phone_number
            }
    
    def _process_energy_bill_image(
        self, phone_number: str, message: str, media_id: Optional[str], 
        ai_model: str, max_tokens: int, temperature: float
    ) -> Optional[Dict[str, Any]]:
        """Processa imagem da conta de energia usando GPT-4o diretamente."""
        # Verificar se há mídia anexada
        if not media_id:
            return None
        
        # Verificar se a mensagem indica que é uma conta de energia
        energy_keywords = ["conta", "fatura", "energia", "light", "cemig", "copel", "cpfl"]
        if not any(keyword in message.lower() for keyword in energy_keywords):
            return None

        logger.info(f"🔍 Processando imagem da conta de energia - Media ID: {media_id}")
        
        try:
            # Obter URL da imagem do WhatsApp
            image_url = self._get_whatsapp_media_url(media_id)
            if not image_url:
                return self._handle_image_error(phone_number, "Não consegui acessar a imagem")
            
            # Usar GPT-4o para processar a imagem diretamente
            prompt = """Analise esta imagem de conta de energia elétrica e extraia os seguintes dados:
            - Valor da conta (apenas números)
            - Nome do cliente
            - Endereço completo
            - Cidade e estado
            - Concessionária/distribuidora
            - Consumo em kWh
            
            Responda apenas com os dados extraídos em formato JSON, sem explicações adicionais."""
            
            response = self.openai_client.chat.completions.create(
                model=ai_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.3  # Baixa temperatura para extração precisa
            )
            
            extracted_text = response.choices[0].message.content
            
            # Gerar resposta final personalizada
            final_response = f"""✅ Analisei sua conta de energia!

Dados extraídos:
{extracted_text}

Agora vou buscar as melhores opções de energia solar para você. Me informe sua cidade e estado para encontrar as promoções disponíveis na sua região."""
            
            # Enviar resposta
            whatsapp_result = self._send_whatsapp_message(phone_number, final_response)
            
            if whatsapp_result['success']:
                # Salvar contexto completo
                self.conversation_context.save_context(
                    phone_number,
                    extracted_data={"raw_text": extracted_text},
                    conversation_completed=False  # Ainda precisa da localização
                )
                
                return {
                    "success": True,
                    "ai_response": final_response,
                    "whatsapp_message_id": whatsapp_result['message_id'],
                    "phone_number": phone_number,
                    "model_used": ai_model,
                    "has_media": True,
                    "media_processed": True,
                    "extracted_data": {"raw_text": extracted_text},
                    "conversation_completed": False
                }
            else:
                return {
                    "success": False,
                    "error": f"Falha no envio WhatsApp: {whatsapp_result['error']}",
                    "ai_response": final_response,
                    "phone_number": phone_number,
                    "has_media": True,
                    "media_processed": True
                }
                
        except Exception as e:
            logger.error(f"💥 Erro no processamento da imagem: {str(e)}")
            return self._handle_image_error(phone_number, f"Erro interno: {str(e)}")
    
    def _get_whatsapp_media_url(self, media_id: str) -> Optional[str]:
        """Obter URL da mídia do WhatsApp."""
        try:
            # Primeiro, obter informações da mídia
            media_info_url = f"https://graph.facebook.com/v18.0/{media_id}"
            headers = {"Authorization": f"Bearer {self.whatsapp_token}"}
            
            response = requests.get(media_info_url, headers=headers)
            if response.status_code != 200:
                logger.error(f"Erro ao obter info da mídia: {response.status_code}")
                return None
            
            media_info = response.json()
            media_url = media_info.get("url")
            
            if not media_url:
                return None
            
            # Obter o arquivo da mídia
            media_response = requests.get(media_url, headers=headers)
            if media_response.status_code != 200:
                logger.error(f"Erro ao baixar mídia: {media_response.status_code}")
                return None
            
            # Converter para base64 para usar com OpenAI
            import base64
            media_base64 = base64.b64encode(media_response.content).decode()
            return f"data:image/jpeg;base64,{media_base64}"
            
        except Exception as e:
            logger.error(f"Erro ao obter URL da mídia: {str(e)}")
            return None
    
    def _process_location_message(
        self, phone_number: str, message: str, media_id: Optional[str],
        ai_model: str, max_tokens: int, temperature: float
    ) -> Optional[Dict[str, Any]]:
        """Processa mensagem com localização detectada, se aplicável."""
        location = self.location_extractor.extract_location_from_message(message)
        if not location:
            return None

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
            
            # Gerar e enviar resposta
            ai_response = self._generate_ai_response(
                prompt, ai_model, max_tokens, temperature
            )
            whatsapp_result = self._send_whatsapp_message(phone_number, ai_response)
            
            # Salvar contexto
            if whatsapp_result['success']:
                self.conversation_context.save_context(
                    phone_number,
                    city=city,
                    state=state,
                    promotions=promotions
                )

            return {
                "success": whatsapp_result['success'],
                "ai_response": ai_response,
                "whatsapp_message_id": whatsapp_result.get('message_id'),
                "phone_number": phone_number,
                "model_used": ai_model,
                "detected_location": (city, state)
            }
            
        except Exception as e:
            logger.error(f"💥 Erro no processamento da localização: {str(e)}")
            return {
                "success": False,
                "error": f"Erro interno ao processar localização: {str(e)}",
                "phone_number": phone_number,
                "detected_location": (city, state)
            }

    def _process_initial_message(
        self, phone_number: str, message: str, media_id: Optional[str],
        ai_model: str, max_tokens: int, temperature: float
    ) -> Dict[str, Any]:
        """Processa mensagem inicial que não se encaixa em outras estratégias."""
        logger.info("📝 Processando como mensagem inicial (sem localização ou imagem de conta)")
        
        try:
            # Recuperar dados do lead do banco de dados
            lead_data = self._get_lead_data(phone_number)
            
            # Gerar resposta personalizada baseada nos dados do lead
            if lead_data:
                # Usar dados do lead para personalizar a resposta
                prompt = f"""
                Você é um assistente da Serena Energia especializado em energia solar.
                
                Dados do lead:
                - Nome: {lead_data['name']}
                - Email: {lead_data['email']}
                - Valor da conta: R$ {lead_data['invoice_amount']}
                
                O lead enviou a mensagem: "{message}"
                
                Responda de forma amigável e personalizada, usando o nome do lead.
                Pergunte sobre a cidade e estado onde mora para poder mostrar os planos disponíveis.
                Mantenha o foco em energia solar e economia na conta de luz.
                """
            else:
                # Fallback para mensagem genérica
                prompt = self.location_extractor.get_initial_response_prompt(message)
            
            ai_response = self._generate_ai_response(prompt, ai_model, max_tokens, temperature)
            whatsapp_result = self._send_whatsapp_message(phone_number, ai_response)

            # Salvar contexto inicial com dados do lead
            if whatsapp_result['success']:
                self.conversation_context.save_context(
                    phone_number, 
                    extracted_data=lead_data
                )

            return {
                "success": whatsapp_result['success'],
                "ai_response": ai_response,
                "whatsapp_message_id": whatsapp_result.get('message_id'),
                "phone_number": phone_number,
                "model_used": ai_model,
                "lead_data": lead_data
            }
        
        except Exception as e:
            logger.error(f"💥 Erro no processamento inicial: {str(e)}")
            return {
                "success": False,
                "error": f"Erro interno ao processar mensagem inicial: {str(e)}",
                "phone_number": phone_number,
            }

    def _handle_completed_conversation(self, phone_number: str) -> Dict[str, Any]:
        """Lida com mensagens recebidas após a conversa ser finalizada."""
        logger.info(f"✅ Conversa com {phone_number} já finalizada. Enviando resposta padrão.")
        response_text = "Nossa conversa sobre sua fatura já foi concluída! Se precisar de uma nova análise ou tiver outra dúvida, basta me enviar uma nova mensagem."
        self._send_whatsapp_message(phone_number, response_text)
        return {
            "success": True,
            "status": "conversation_already_completed",
            "ai_response": response_text,
            "phone_number": phone_number,
        }

    def _handle_image_error(self, phone_number: str, error_message: str) -> Dict[str, Any]:
        """Lida com erros durante o processamento de imagem."""
        logger.warning(f"⚠️ Erro de imagem para {phone_number}: {error_message}")
        response_text = f"Ocorreu um problema ao analisar a imagem da sua conta: {error_message}. Poderia tentar enviar novamente? Se o erro persistir, me informe sua cidade, estado e o valor médio da sua conta."
        self._send_whatsapp_message(phone_number, response_text)
        return {
            "success": False,
            "error": error_message,
            "ai_response": response_text,
            "phone_number": phone_number,
            "has_media": True,
            "media_processed": False,
        }

    def _save_to_supabase(self, phone_number: str, extracted_data: Dict[str, Any], model_used: str):
        """Prepara e envia os dados para serem salvos no Supabase."""
        logger.info(f"💾 Preparando para salvar dados do lead {phone_number} no Supabase...")
        try:
            # Esta função agora retorna um dicionário que pode ser usado por uma task Kestra
            # para chamar o script `save_lead_to_supabase.py`.
            # A lógica de salvamento direto foi removida para desacoplar.
            
            lead_data = {
                "phone_number": phone_number,
                "name": extracted_data.get('nome_cliente', 'N/A'),
                "city": extracted_data.get('cidade', 'N/A'),
                "state": extracted_data.get('estado', 'N/A'),
                "invoice_amount": extracted_data.get('valor_total', 0.0),
                "distributor": extracted_data.get('distribuidora', 'N/A'),
                "consumption_kwh": extracted_data.get('consumo_kwh', 0),
                "client_type": "PJ" if extracted_data.get('tipo_cliente') == 'juridica' else "PF",
                "additional_data": {
                    "model_used": model_used,
                    "full_extracted_data": extracted_data
                }
            }
            logger.info(f"✅ Dados do lead {phone_number} prontos para serem persistidos.")
            # No ambiente Kestra, este dicionário seria o output da task.
            # O salvamento real ocorre em outra task.
            # save_qualified_lead(lead_data) # Chamada removida
        except Exception as e:
            logger.error(f"❌ Erro ao preparar dados para Supabase: {str(e)}")


    def _generate_ai_response(
        self, prompt: str, model: str, max_tokens: int, temperature: float
    ) -> str:
        """Gera resposta usando OpenAI com tratamento robusto de erros."""
        logger.info(f"🤖 Iniciando chamada para OpenAI")
        logger.info(f"📝 Modelo: {model}")
        logger.info(f"🎯 Max tokens: {max_tokens}")
        logger.info(f"🌡️ Temperature: {temperature}")
        logger.info(f"🔑 API Key configurada: {'✅' if self.openai_api_key else '❌'}")
        
        try:
            # Verificar se a API key está configurada
            if not self.openai_api_key:
                logger.error("❌ OPENAI_API_KEY não está configurada")
                return "Erro de configuração: API Key da OpenAI não encontrada."
            
            logger.info(f"📤 Enviando requisição para OpenAI...")
            
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=30  # Timeout de 30 segundos
            )
            
            logger.info(f"📥 Resposta recebida da OpenAI")
            logger.info(f"✅ Status: Sucesso")
            
            content = response.choices[0].message.content
            if content:
                logger.info(f"📊 Resposta gerada: {len(content)} caracteres")
                return content.strip()
            else:
                logger.warning("⚠️ Resposta da OpenAI está vazia")
                return "Desculpe, não consegui gerar uma resposta."
                
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            
            logger.error(f"❌ Erro na OpenAI: {error_type}")
            logger.error(f"📄 Mensagem: {error_msg}")
            
            # Tratamento específico para diferentes tipos de erro
            if "connection" in error_msg.lower() or "network" in error_msg.lower():
                logger.error("🌐 Problema de conexão de rede")
                return "Desculpe, tive um problema de conexão. Tente novamente em alguns minutos."
            elif "timeout" in error_msg.lower():
                logger.error("⏰ Timeout na requisição")
                return "Desculpe, a resposta demorou muito. Tente novamente."
            elif "rate limit" in error_msg.lower() or "429" in error_msg:
                logger.error("🚫 Rate limit excedido")
                return "Desculpe, muitas requisições. Aguarde um momento e tente novamente."
            elif "401" in error_msg or "authentication" in error_msg.lower():
                logger.error("🔐 Erro de autenticação - verifique OPENAI_API_KEY")
                return "Erro de autenticação com a OpenAI. Verifique a configuração."
            elif "400" in error_msg or "bad request" in error_msg.lower():
                logger.error("📝 Erro na requisição - parâmetros inválidos")
                return "Erro na requisição. Verifique os parâmetros."
            else:
                logger.error(f"❓ Erro não identificado: {error_type}")
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
    # Normalizar telefone antes da busca
    normalized_phone = normalize_phone(phone_number)
    
    handler = get_handler()
    return handler.process_message(normalized_phone, message, media_id, ai_model, max_tokens, temperature)


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