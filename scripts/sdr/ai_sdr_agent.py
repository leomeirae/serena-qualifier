# =============================================================================
# SERENA SDR - AI AGENT
# =============================================================================

"""
Serena SDR AI Agent

Este script implementa o agente conversacional principal do sistema Serena SDR,
utilizando OpenAI Function Calling para interagir com leads via WhatsApp.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import os
import json
import time
import openai
from typing import Dict, Any, Optional, List
from datetime import datetime

# Importar utilitários
from utils.config import get_config, is_qualified_lead
from utils.logger import get_agent_logger, log_ai_conversation, log_lead_created, log_lead_qualified
from utils.mcp_client import call_mcp_tool, get_mcp_client

# Importar ferramentas
from agent_tools.supabase_tools import SupabaseTools
from agent_tools.serena_tools import SerenaTools
from agent_tools.whatsapp_tools import WhatsAppTools
from agent_tools.ocr_tools import OCRTools

logger = get_agent_logger()


class SerenaSDRAgent:
    """Agente conversacional principal do Serena SDR."""
    
    def __init__(self):
        """Inicializa o agente SDR."""
        self.config = get_config()
        openai.api_key = self.config.openai_api_key
        
        # Inicializar ferramentas
        self.supabase_tools = SupabaseTools()
        self.serena_tools = SerenaTools()
        self.whatsapp_tools = WhatsAppTools()
        self.ocr_tools = OCRTools()
        
        # Configurar OpenAI
        self.model = self.config.openai_model
        self.max_tokens = self.config.openai_max_tokens
        self.temperature = self.config.openai_temperature
        self.max_retries = self.config.max_retries
        
        # Definir funções disponíveis para OpenAI Function Calling
        self.functions = self._define_functions()
        
        logger.info("Agente Serena SDR inicializado", 
                   model=self.model, max_tokens=self.max_tokens, temperature=self.temperature)
    
    def _define_functions(self) -> List[Dict[str, Any]]:
        """Define as funções disponíveis para OpenAI Function Calling."""
        return [
    {
        "name": "get_lead_data",
                "description": "Busca dados do lead no Supabase",
        "parameters": {
            "type": "object",
            "properties": {
                        "phone_number": {
                            "type": "string",
                            "description": "Número de telefone do lead"
                        }
            },
                    "required": ["phone_number"]
        }
    },
    {
                "name": "create_or_update_lead",
                "description": "Cria ou atualiza lead no Supabase",
        "parameters": {
            "type": "object",
            "properties": {
                        "lead_data": {
                            "type": "object",
                            "description": "Dados do lead para salvar"
                        }
                    },
                    "required": ["lead_data"]
                }
            },
            {
                "name": "process_energy_bill",
                "description": "Processa imagem de fatura de energia via OCR",
        "parameters": {
            "type": "object",
            "properties": {
                        "image_url": {
                            "type": "string",
                            "description": "URL da imagem da fatura"
                        }
            },
            "required": ["image_url"]
        }
    },
            {
                "name": "validate_lead_qualification",
                "description": "Valida se lead está qualificado para energia solar",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cidade": {
                            "type": "string",
                            "description": "Cidade do lead"
                        },
                        "estado": {
                            "type": "string",
                            "description": "Estado do lead"
                        },
                        "tipo_pessoa": {
                            "type": "string",
                            "description": "Tipo de pessoa (natural ou juridical)"
                        },
                        "valor_conta": {
                            "type": "number",
                            "description": "Valor da conta de energia"
                        }
                    },
                    "required": ["cidade", "estado", "tipo_pessoa", "valor_conta"]
                }
            },
            {
                "name": "get_energy_plans",
                "description": "Obtém planos de energia disponíveis para a região",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cidade": {
                            "type": "string",
                            "description": "Cidade do lead"
                        },
                        "estado": {
                            "type": "string",
                            "description": "Estado do lead"
                        }
                    },
                    "required": ["cidade", "estado"]
        }
    },
    {
        "name": "send_whatsapp_message",
                "description": "Envia mensagem via WhatsApp",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {
                            "type": "string",
                            "description": "Número de telefone"
                        },
                        "message": {
                            "type": "string",
                            "description": "Conteúdo da mensagem"
                        }
                    },
                    "required": ["to", "message"]
                }
            },
            {
                "name": "send_welcome_message",
                "description": "Envia mensagem de boas-vindas personalizada",
        "parameters": {
            "type": "object",
            "properties": {
                        "to": {
                            "type": "string",
                            "description": "Número de telefone"
                        },
                        "lead_name": {
                            "type": "string",
                            "description": "Nome do lead (opcional)"
                        }
                    },
                    "required": ["to"]
                }
            },
            {
                "name": "send_qualification_message",
                "description": "Envia mensagem de qualificação com planos",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {
                            "type": "string",
                            "description": "Número de telefone"
                        },
                        "lead_name": {
                            "type": "string",
                            "description": "Nome do lead"
                        },
                        "cidade": {
                            "type": "string",
                            "description": "Cidade do lead"
                        },
                        "invoice_amount": {
                            "type": "number",
                            "description": "Valor da conta de energia"
                        }
                    },
                    "required": ["to", "lead_name", "cidade", "invoice_amount"]
                }
            },
            {
                "name": "send_plans_message",
                "description": "Envia mensagem com planos disponíveis",
        "parameters": {
            "type": "object",
            "properties": {
                        "to": {
                            "type": "string",
                            "description": "Número de telefone"
                        },
                        "lead_name": {
                            "type": "string",
                            "description": "Nome do lead"
                        },
                        "plans": {
                            "type": "array",
                            "description": "Lista de planos disponíveis"
                        }
                    },
                    "required": ["to", "lead_name", "plans"]
                }
            },
            {
                "name": "update_lead_conversation_state",
                "description": "Atualiza estado da conversa do lead",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone_number": {
                            "type": "string",
                            "description": "Número de telefone"
                        },
                        "state": {
                            "type": "string",
                            "description": "Novo estado da conversa"
                        },
                        "additional_data": {
                            "type": "object",
                            "description": "Dados adicionais para atualizar"
                        }
                    },
                    "required": ["phone_number", "state"]
                }
            }
        ]
    
    def _call_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma função específica baseada no nome."""
        try:
            logger.debug(f"Executando função: {function_name}", function=function_name, arguments=arguments)
            
            if function_name == "get_lead_data":
                phone = arguments.get("phone_number")
                result = self.supabase_tools.get_lead_by_phone(phone)
                return {"success": True, "lead_data": result}
            
            elif function_name == "create_or_update_lead":
                lead_data = arguments.get("lead_data")
                result = self.supabase_tools.create_or_update_lead(lead_data)
                return result
            
            elif function_name == "process_energy_bill":
                image_url = arguments.get("image_url")
                result = self.ocr_tools.process_energy_bill_image(image_url)
                return result
            
            elif function_name == "validate_lead_qualification":
                result = self.serena_tools.validar_qualificacao_lead(
                    cidade=arguments.get("cidade"),
                    estado=arguments.get("estado"),
                    tipo_pessoa=arguments.get("tipo_pessoa"),
                    valor_conta=arguments.get("valor_conta")
                )
                return result
            
            elif function_name == "get_energy_plans":
                result = self.serena_tools.obter_planos_gd(
                    cidade=arguments.get("cidade"),
                    estado=arguments.get("estado")
                )
                return result
            
            elif function_name == "send_whatsapp_message":
                result = self.whatsapp_tools.send_text_message(
                    to=arguments.get("to"),
                    message=arguments.get("message")
                )
                return result
            
            elif function_name == "send_welcome_message":
                result = self.whatsapp_tools.send_welcome_message(
                    to=arguments.get("to"),
                    lead_name=arguments.get("lead_name")
                )
                return result
            
            elif function_name == "send_qualification_message":
                result = self.whatsapp_tools.send_qualification_message(
                    to=arguments.get("to"),
                    lead_name=arguments.get("lead_name"),
                    city=arguments.get("cidade"),
                    invoice_amount=arguments.get("invoice_amount")
                )
                return result
            
            elif function_name == "send_plans_message":
                result = self.whatsapp_tools.send_plans_message(
                    to=arguments.get("to"),
                    lead_name=arguments.get("lead_name"),
                    plans=arguments.get("plans")
                )
                return result
            
            elif function_name == "update_lead_conversation_state":
                result = self.supabase_tools.update_lead_conversation_state(
                    phone_number=arguments.get("phone_number"),
                    state=arguments.get("state"),
                    additional_data=arguments.get("additional_data")
                )
                return result
            
        else:
                raise ValueError(f"Função desconhecida: {function_name}")
                
        except Exception as e:
            logger.error(f"Erro ao executar função {function_name}: {str(e)}", 
                        function=function_name, error=str(e))
            return {"success": False, "error": str(e)}
    
    def run_agent(self, lead_id: str = None, user_message: str = None, 
                  message_type: str = "text", media_id: str = None, 
                  lead_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executa o agente conversacional.
        
        Args:
            lead_id: ID do lead
            user_message: Mensagem do usuário
            message_type: Tipo da mensagem (text, image, etc.)
            media_id: ID da mídia (se aplicável)
            lead_data: Dados do lead (se disponível)
            
        Returns:
            Dict: Resposta do agente
        """
        start_time = datetime.now()
        
        try:
            logger.info("Iniciando processamento do agente", 
                       lead_id=lead_id, message_type=message_type, media_id=media_id)
            
            # Construir prompt do sistema
            system_prompt = self._build_system_prompt(lead_data)
            
            # Construir mensagens
        messages = [
            {"role": "system", "content": system_prompt}
        ]
            
            # Adicionar contexto do lead se disponível
            if lead_data:
                messages.append({
                    "role": "system", 
                    "content": f"Contexto do lead: {json.dumps(lead_data, ensure_ascii=False)}"
                })
            
            # Adicionar mensagem do usuário
        if user_message:
            messages.append({"role": "user", "content": user_message})
            
        # Loop de function calling
            response = self._process_function_calling(messages)
            
            # Calcular tempo de processamento
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Log da conversa
            if lead_id and user_message:
                log_ai_conversation(lead_id, lead_data.get('phone_number', ''), user_message, response, processing_time)
            
            logger.info("Processamento do agente concluído", 
                       lead_id=lead_id, processing_time=processing_time)
            
            return {
                "response": response,
                "success": True,
                "processing_time": processing_time,
                "lead_id": lead_id
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento do agente: {str(e)}", 
                        lead_id=lead_id, error=str(e))
            return {
                "response": "Desculpe, ocorreu um erro interno. Tente novamente em alguns minutos.",
                "success": False,
                "error": str(e),
                "lead_id": lead_id
            }
    
    def _build_system_prompt(self, lead_data: Dict[str, Any] = None) -> str:
        """Constrói o prompt do sistema."""
        prompt = """Você é Sílvia, agente virtual de pré-vendas da Serena Energia. 

MISSÃO: Ajudar leads a economizar até 95% na conta de luz com energia solar.

PERSONALIDADE:
- Amigável, profissional e empática
- Fala de forma clara e objetiva
- Usa emojis moderadamente para tornar a conversa mais leve
- Sempre oferece ajuda concreta

FLUXO DE CONVERSA:
1. PRIMEIRO CONTATO: Cumprimente calorosamente e peça foto da conta de energia
2. PROCESSAMENTO: Se receber imagem, processe via OCR e extraia valor
3. QUALIFICAÇÃO: Se conta >= R$ 200, qualifique o lead
4. APRESENTAÇÃO: Se qualificado, apresente planos disponíveis
5. FECHAMENTO: Se interesse, registre dados e crie contrato

REGRAS IMPORTANTES:
- SEMPRE peça foto da conta de energia no primeiro contato
- Só qualifique leads com conta >= R$ 200
- Use as funções disponíveis para buscar dados e enviar mensagens
- Se não souber algo, seja honesto e ofereça contato humano
- Mantenha conversa focada em energia solar e economia

FUNÇÕES DISPONÍVEIS:
- get_lead_data: Busca dados do lead
- create_or_update_lead: Salva dados do lead
- process_energy_bill: Processa imagem de fatura
- validate_lead_qualification: Valida qualificação
- get_energy_plans: Obtém planos disponíveis
- send_whatsapp_message: Envia mensagem
- send_welcome_message: Envia boas-vindas
- send_qualification_message: Envia qualificação
- send_plans_message: Envia planos
- update_lead_conversation_state: Atualiza estado

Lembre-se: Seja Sílvia, a consultora virtual que ajuda a economizar com energia solar! 🌞"""
        
        return prompt
    
    def _process_function_calling(self, messages: List[Dict[str, str]]) -> str:
        """Processa o loop de function calling."""
        max_iterations = 10  # Evitar loop infinito
        iteration = 0
        
        while iteration < max_iterations:
            try:
                # Chamar OpenAI
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    functions=self.functions,
                    function_call="auto",
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                
                message = response.choices[0].message
                
                # Se não há function call, retornar resposta final
                if not message.get("function_call"):
                    return message["content"]
                
                # Executar function call
                function_call = message["function_call"]
                function_name = function_call["name"]
                function_args = json.loads(function_call["arguments"])
                
                logger.debug(f"Executando function call: {function_name}", 
                           function=function_name, arguments=function_args)
                
                # Executar função
                function_result = self._call_function(function_name, function_args)
                
                # Adicionar resultado à conversa
                messages.append(message)
                messages.append({
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(function_result, ensure_ascii=False)
                })
                
                iteration += 1
                
            except Exception as e:
                logger.error(f"Erro no function calling: {str(e)}", error=str(e))
                return f"Desculpe, ocorreu um erro técnico: {str(e)}"
        
        return "Desculpe, o processamento demorou muito. Tente novamente."
    
    def process_image_message(self, image_url: str, lead_id: str = None) -> Dict[str, Any]:
        """Processa mensagem com imagem (fatura de energia)."""
        try:
            logger.info("Processando imagem de fatura", image_url=image_url, lead_id=lead_id)
            
            # Processar imagem via OCR
            ocr_result = self.ocr_tools.process_energy_bill_image(image_url)
            
            if not ocr_result["success"]:
                return {
                    "success": False,
                    "error": "Não foi possível processar a imagem da fatura",
                    "response": "Desculpe, não consegui ler sua fatura de energia. Pode enviar uma foto mais clara?"
                }
            
            # Extrair dados
            extracted_data = ocr_result["dados_extraidos"]
            valor_conta = ocr_result["valor_conta"]
            confianca = ocr_result["confianca"]
            
            # Validar se é uma fatura válida
            validation = self.ocr_tools.validate_energy_bill(extracted_data)
            
            if not validation["is_valid"]:
                return {
                    "success": False,
                    "error": "Fatura inválida",
                    "response": "Não consegui identificar uma fatura de energia válida. Pode enviar uma foto mais clara da sua conta de luz?"
                }
            
            # Extrair informações do lead
            lead_info = self.ocr_tools.extract_lead_info_from_bill(extracted_data)
            
            # Verificar qualificação
            is_qualified = is_qualified_lead(valor_conta)
            
            # Construir resposta
            if is_qualified:
                response = f"""✅ Perfeito! Analisei sua fatura de energia:

💰 Valor: R$ {valor_conta:.2f}
📊 Consumo: {extracted_data.get('consumo_kwh', 0):.0f} kWh
🏢 Distribuidora: {extracted_data.get('distribuidora', 'N/A')}

🎉 ÓTIMA NOTÍCIA! Você está QUALIFICADO para nossa solução de energia solar!

Com energia solar, você pode economizar até 95% na sua conta de luz! 🌞

Gostaria que eu te apresente os planos disponíveis para sua região?

Responda "SIM" que te mostro as opções! 💚"""
            else:
                response = f"""✅ Analisei sua fatura de energia:

💰 Valor: R$ {valor_conta:.2f}
📊 Consumo: {extracted_data.get('consumo_kwh', 0):.0f} kWh

Infelizmente, para nossa solução de energia solar, precisamos de contas com valor mínimo de R$ 200,00.

Mas não se preocupe! Vou te manter informado sobre outras soluções de economia de energia que podem te ajudar! 💡

Obrigada pelo interesse! 💚"""
            
            return {
                "success": True,
                "response": response,
                "extracted_data": extracted_data,
                "valor_conta": valor_conta,
                "is_qualified": is_qualified,
                "confidence": confianca
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar imagem: {str(e)}", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "response": "Desculpe, ocorreu um erro ao processar sua fatura. Tente novamente."
            }


# Função principal para uso no workflow
def main():
    """Função principal para execução via linha de comando."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Serena SDR AI Agent')
    parser.add_argument('--lead-id', required=True, help='ID do lead')
    parser.add_argument('--message', required=True, help='Mensagem do usuário')
    parser.add_argument('--message-type', default='text', help='Tipo da mensagem')
    parser.add_argument('--media-id', help='ID da mídia (se aplicável)')
    
    args = parser.parse_args()
    
    # Criar agente e executar
    agent = SerenaSDRAgent()
    result = agent.run_agent(
        lead_id=args.lead_id,
        user_message=args.message,
        message_type=args.message_type,
        media_id=args.media_id
    )
    
    # Exibir resultado
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()