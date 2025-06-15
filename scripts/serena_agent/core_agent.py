"""
Core Agent - Orquestrador Principal LangChain

Este módulo serve como ponto de entrada principal para o agente IA,
integrando com os workflows Kestra existentes mantendo interface compatível.
"""

from typing import Dict, Any, Optional, List
import logging
import os
from dotenv import load_dotenv

# LangChain imports
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool

# Import tools locais
from .tools.conversation_tool import conversation_tool_function, conversation_tool_decorated
from .tools.serena_api_tool import serena_api_tool_function, serena_api_tool_decorated
from .tools.ocr_tool import ocr_tool_function
from .tools.rag_tool import rag_tool
from .prompts.classification import get_classification_prompt
from .prompts.extraction import get_extraction_prompt
from .prompts.conversation import get_conversation_prompt

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class SerenaAIAgent:
    """
    Orquestrador principal do agente IA Serena.
    
    Substitui process_ai_request() dos workflows mantendo interface idêntica.
    Usa LangChain internamente para melhor consistência e estrutura.
    """
    
    def __init__(self):
        """Inicializa o agente com tools e prompts."""
        logger.info("Inicializando SerenaAIAgent...")
        
        self.llm = None
        self.agent_executor = None
        self.tools = []
        
        # Setup LangChain
        if os.getenv("OPENAI_API_KEY"):
            self._setup_langchain()
        else:
            logger.warning("OPENAI_API_KEY não encontrada. LangChain não será inicializado.")
    
    def _setup_langchain(self):
        """Configura LangChain com tools e AgentExecutor."""
        try:
            # Inicializa modelo OpenAI
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                api_key=os.getenv("OPENAI_API_KEY")
            )
            
            # Cria tools LangChain
            self.tools = self._create_tools()
            
            # Prompt para o agente
            system_prompt = """Você é um especialista em energia solar da Serena Energia.

Suas responsabilidades:
1. Classificar intenções de mensagens dos leads
2. Extrair dados estruturados das conversas
3. Gerar respostas conversacionais adequadas
4. Usar as tools disponíveis para acessar dados e APIs
5. Solicitar e processar contas de energia para qualificação

Tools disponíveis:
- conversation_manager: Para gerenciar histórico de conversas
- serena_api: Para consultar planos e cobertura da Serena
- ocr_processor: Para processar faturas enviadas pelos leads com extração estruturada
- rag_tool: Para responder dúvidas gerais sobre energia solar, financiamento e benefícios

FLUXO DE QUALIFICAÇÃO COM OCR:

1. QUANDO SOLICITAR CONTA DE ENERGIA:
   - Após interesse inicial confirmado
   - Quando lead pergunta sobre economia/valores
   - Para calcular proposta personalizada
   - Se lead menciona valor alto da conta atual

2. COMO SOLICITAR:
   "Para calcular sua economia exata, preciso analisar sua conta de energia. 
   Pode enviar uma foto da sua última fatura? Vou extrair os dados automaticamente 
   e mostrar quanto você pode economizar com energia solar."

3. PROCESSAMENTO OCR:
   - Use ocr_processor com action="process_image" quando receber imagem
   - Extraia: nome, distribuidora, valor, consumo, endereço
   - Valide automaticamente os dados extraídos
   - Qualifique o lead (mínimo R$ 200/mês)

4. APÓS PROCESSAMENTO:
   - Confirme dados extraídos com o lead
   - Use serena_api para consultar planos disponíveis
   - Apresente proposta personalizada com economia

IMPORTANTE: 
- Use rag_tool para dúvidas gerais sobre energia solar
- Use serena_api para consultas específicas de planos e cobertura
- Use ocr_processor para processar faturas e qualificar leads
- Sempre confirme dados extraídos antes de prosseguir

Mantenha tom profissional, foque em energia solar e economia."""

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}")
            ])
            
            # Cria o agente
            agent = create_openai_tools_agent(self.llm, self.tools, prompt)
            self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
            
            logger.info("✅ LangChain AgentExecutor configurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar LangChain: {e}")
            self.agent_executor = None
    
    def _create_tools(self):
        """Cria e retorna lista de tools LangChain."""
        tools = []
        
        # Conversation tool
        if conversation_tool_decorated:
            tools.append(conversation_tool_decorated)
        else:
            tools.append(Tool(
                name="conversation_manager",
                description="Gerencia conversas e histórico de mensagens com leads",
                func=lambda x: conversation_tool_function(eval(x) if isinstance(x, str) else x)
            ))
        
        # Serena API tool
        if serena_api_tool_decorated:
            tools.append(serena_api_tool_decorated)
        else:
            tools.append(Tool(
                name="serena_api",
                description="Consulta API real da Serena para cobertura e planos de energia solar",
                func=lambda x: serena_api_tool_function(eval(x) if isinstance(x, str) else x)
            ))
        
        # OCR tool melhorada com extração estruturada
        tools.append(Tool(
            name="ocr_processor", 
            description="""Processa faturas de energia via OCR com extração estruturada avançada.
            
            Ações disponíveis:
            - process_image: Processa imagem da fatura (requer media_id e phone_number)
            - extract_fields: Extrai campos estruturados de texto OCR (requer ocr_text)
            - validate_invoice: Valida dados extraídos (requer ocr_data)
            - identify_distributor: Identifica distribuidora (requer ocr_text)
            - validate_structured: Validação robusta (requer ocr_data)
            - get_supported_distributors: Lista distribuidoras suportadas
            
            Extrai automaticamente: nome_cliente, distribuidora, valor_conta, consumo_kwh, 
            endereco, vencimento, CPF/CNPJ. Qualifica leads baseado em valor mínimo R$ 200.
            Suporta 20+ distribuidoras brasileiras (CEMIG, ENEL, LIGHT, CPFL, etc.)""",
            func=lambda x: ocr_tool_function(eval(x) if isinstance(x, str) else x)
        ))
        
        # RAG tool para dúvidas gerais
        tools.append(rag_tool)
        
        return tools
    
    def process_conversation(
        self, 
        phone: str, 
        message: str, 
        action: str = "respond",
        media_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Interface principal compatível com workflows Kestra.
        
        Args:
            phone: Número do telefone do lead
            message: Mensagem recebida
            action: Ação a ser executada (classify, extract, respond)
            media_id: ID da mídia se imagem foi enviada
            
        Returns:
            Dict com resultado da ação, compatível com scripts existentes
        """
        logger.info(f"Processando conversa para {phone}, ação: {action}")
        
        try:
            # Detecta se é uma imagem de conta de energia
            if media_id and self._is_energy_bill_context(message):
                logger.info(f"🔍 Detectada imagem de conta de energia para {phone}")
                result = self._process_energy_bill_image(phone, message, media_id)
            elif self.agent_executor and action == "respond":
                # Usa LangChain para resposta conversacional
                result = self._process_with_langchain(phone, message, action)
            else:
                # Usa modo compatibilidade para outras ações ou fallback
                result = self._process_with_prompts(phone, message, action)
                
            return {
                "action": action,
                "phone": phone,
                "message": message,
                "result": "success",
                "response": result.get("response", "Processado com sucesso"),
                "data": result.get("data", {}),
                "method": result.get("method", "langchain" if self.agent_executor and action == "respond" else "prompts"),
                "media_processed": media_id is not None
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento: {e}")
            return {
                "action": action,
                "phone": phone,
                "message": message,
                "result": "error",
                "error": str(e),
                "method": "fallback"
            }
    
    def _is_energy_bill_context(self, message: str) -> bool:
        """
        Detecta se o contexto indica que uma imagem de conta de energia foi enviada.
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            bool: True se parece ser contexto de conta de energia
        """
        message_lower = message.lower()
        
        # Palavras que indicam especificamente conta/fatura
        bill_keywords = [
            "conta", "fatura", "boleto", "luz", "cemig", "enel", "light", 
            "cpfl", "distribuidora", "kwh", "consumo", "valor"
        ]
        
        # Frases que NÃO são contexto de conta (mesmo tendo "energia")
        non_bill_phrases = [
            "energia solar", "sobre energia", "como funciona", "quanto custa",
            "quero saber", "vocês atendem", "instalação"
        ]
        
        # Se contém frases que não são de conta, retorna False
        if any(phrase in message_lower for phrase in non_bill_phrases):
            return False
        
        # Se contém palavras específicas de conta/fatura, retorna True
        if any(keyword in message_lower for keyword in bill_keywords):
            return True
        
        # Se mensagem muito curta (provavelmente só imagem), retorna True
        return len(message.strip()) < 10
    
    def _process_energy_bill_image(self, phone: str, message: str, media_id: str) -> Dict[str, Any]:
        """
        Processa imagem de conta de energia usando OCR melhorado.
        
        Args:
            phone: Número do telefone
            message: Mensagem do usuário
            media_id: ID da mídia enviada
            
        Returns:
            Dict com resultado do processamento OCR
        """
        logger.info(f"📸 Processando conta de energia via OCR para {phone}")
        
        try:
            # Chama OCR tool para processar imagem
            ocr_input = {
                "action": "process_image",
                "media_id": media_id,
                "phone_number": phone
            }
            
            ocr_result = ocr_tool_function(ocr_input)
            
            if ocr_result.get("success"):
                extracted_data = ocr_result.get("extracted_data", {})
                validation = ocr_result.get("validation", {})
                is_qualified = ocr_result.get("is_qualified", False)
                
                # Gera resposta baseada nos dados extraídos
                response = self._generate_ocr_response(extracted_data, validation, is_qualified)
                
                return {
                    "response": response,
                    "data": {
                        "ocr_processed": True,
                        "extracted_data": extracted_data,
                        "validation": validation,
                        "is_qualified": is_qualified
                    },
                    "method": "ocr_structured"
                }
            else:
                return {
                    "response": "Não consegui processar a imagem da conta. Pode tentar enviar uma foto mais clara?",
                    "data": {"ocr_error": True},
                    "method": "ocr_error"
                }
                
        except Exception as e:
            logger.error(f"Erro no processamento OCR: {e}")
            return {
                "response": "Houve um problema ao processar sua conta. Pode tentar novamente?",
                "data": {"ocr_exception": str(e)},
                "method": "ocr_fallback"
            }
    
    def _generate_ocr_response(self, extracted_data: Dict, validation: Dict, is_qualified: bool) -> str:
        """
        Gera resposta personalizada baseada nos dados extraídos da conta.
        
        Args:
            extracted_data: Dados extraídos da conta
            validation: Dados de validação
            is_qualified: Se o lead está qualificado
            
        Returns:
            str: Resposta personalizada
        """
        nome = extracted_data.get("nome_cliente", "")
        distribuidora = extracted_data.get("distribuidora", "")
        valor = extracted_data.get("total_a_pagar", "")
        consumo = extracted_data.get("consumo_kwh", "")
        
        if is_qualified:
            response = f"✅ Perfeito! Analisei sua conta da {distribuidora}.\n\n"
            response += f"📊 **Dados extraídos:**\n"
            if nome: response += f"• Cliente: {nome}\n"
            if valor: response += f"• Valor atual: {valor}\n"
            if consumo: response += f"• Consumo: {consumo} kWh\n"
            response += f"\n🎯 **Ótima notícia!** Com esse perfil de consumo, você pode economizar significativamente com energia solar.\n\n"
            response += f"Vou consultar os planos disponíveis na sua região para mostrar sua economia potencial. Um momento..."
        else:
            response = f"📋 Analisei sua conta da {distribuidora}.\n\n"
            if valor: response += f"Valor atual: {valor}\n"
            response += f"\n💡 Para energia solar ser mais vantajosa, recomendamos contas a partir de R$ 200/mês.\n"
            response += f"Mas posso te ajudar com informações sobre nossos planos e financiamento!"
        
        return response
    
    def _process_with_langchain(self, phone: str, message: str, action: str) -> Dict[str, Any]:
        """Processa usando LangChain AgentExecutor."""
        input_text = f"Usuário {phone} enviou: '{message}'. Ação solicitada: {action}"
        
        try:
            response = self.agent_executor.invoke({"input": input_text})
            return {
                "response": response.get("output", "Resposta gerada via LangChain"),
                "data": {"langchain_used": True}
            }
        except Exception as e:
            logger.error(f"Erro no LangChain: {e}")
            # Fallback para modo prompts
            return self._process_with_prompts(phone, message, action)
    
    def _process_with_prompts(self, phone: str, message: str, action: str) -> Dict[str, Any]:
        """Processa usando prompts padronizados (modo compatibilidade)."""
        if action == "classify":
            prompt = get_classification_prompt(phone, message, "")
            response = "interest"  # Simulado - integrará com LLM
            
        elif action == "extract":
            prompt = get_extraction_prompt(phone, message, "")
            response = '{"phone": "' + phone + '", "message_analyzed": true}'
            
        elif action == "respond":
            prompt = get_conversation_prompt(message, "interest", "", "")
            response = "Obrigado pelo interesse! Vamos conversar sobre energia solar. Em qual cidade você mora?"
            
        else:
            response = f"Ação {action} processada via prompts padronizados"
        
        return {
            "response": response,
            "data": {"prompt_used": True, "action": action}
        }


def process_ai_request(phone: str, message: str, action: str, media_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Função de compatibilidade com workflows existentes.
    
    Wrapper que mantém interface idêntica ao ai_agent.py original,
    agora com suporte a processamento de imagens via OCR.
    
    Args:
        phone: Número do telefone do lead
        message: Mensagem recebida
        action: Ação a ser executada
        media_id: ID da mídia se imagem foi enviada
    """
    agent = SerenaAIAgent()
    return agent.process_conversation(phone, message, action, media_id) 