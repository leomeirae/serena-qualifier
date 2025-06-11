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
try:
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.tools import Tool
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain não disponível. Usando modo compatibilidade.")

# Import tools locais
from .tools.conversation_tool import conversation_tool_function, conversation_tool_decorated
from .tools.serena_api_tool import serena_api_tool_function, serena_api_tool_decorated
from .tools.ocr_tool import ocr_tool_function
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
        
        # Setup LangChain se disponível
        if LANGCHAIN_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self._setup_langchain()
        else:
            logger.warning("Usando modo compatibilidade sem LangChain")
    
    def _setup_langchain(self):
        """Configura LangChain com tools e AgentExecutor."""
        try:
            # Inicializa modelo OpenAI
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                api_key=os.getenv("OPENAI_API_KEY")
            )
            
            # Cria tools LangChain (usa decoradas se disponíveis)
            self.tools = []
            
            # Conversation tool
            if conversation_tool_decorated:
                self.tools.append(conversation_tool_decorated)
            else:
                self.tools.append(Tool(
                    name="conversation_manager",
                    description="Gerencia conversas e histórico de mensagens com leads",
                    func=lambda x: conversation_tool_function(eval(x) if isinstance(x, str) else x)
                ))
            
            # Serena API tool
            if serena_api_tool_decorated:
                self.tools.append(serena_api_tool_decorated)
            else:
                self.tools.append(Tool(
                    name="serena_api",
                    description="Consulta API real da Serena para cobertura e planos de energia solar",
                    func=lambda x: serena_api_tool_function(eval(x) if isinstance(x, str) else x)
                ))
            
            # OCR tool (ainda em modo compatibilidade)
            self.tools.append(Tool(
                name="ocr_processor", 
                description="Processa faturas de energia via OCR para extrair valores e validar documentos",
                func=lambda x: ocr_tool_function(eval(x) if isinstance(x, str) else x)
            ))
            
            # Prompt para o agente
            system_prompt = """Você é um especialista em energia solar da Serena Energia.

Suas responsabilidades:
1. Classificar intenções de mensagens dos leads
2. Extrair dados estruturados das conversas
3. Gerar respostas conversacionais adequadas
4. Usar as tools disponíveis para acessar dados e APIs

Tools disponíveis:
- conversation_manager: Para gerenciar histórico de conversas
- serena_api: Para consultar planos e cobertura da Serena
- ocr_processor: Para processar faturas enviadas pelos leads

Mantenha sempre tom profissional, foque em energia solar e economia."""

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
    
    def process_conversation(
        self, 
        phone: str, 
        message: str, 
        action: str = "respond"
    ) -> Dict[str, Any]:
        """
        Interface principal compatível com workflows Kestra.
        
        Args:
            phone: Número do telefone do lead
            message: Mensagem recebida
            action: Ação a ser executada (classify, extract, respond)
            
        Returns:
            Dict com resultado da ação, compatível com scripts existentes
        """
        logger.info(f"Processando conversa para {phone}, ação: {action}")
        
        try:
            if self.agent_executor and action == "respond":
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
                "method": "langchain" if self.agent_executor and action == "respond" else "prompts"
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


def process_ai_request(phone: str, message: str, action: str) -> Dict[str, Any]:
    """
    Função de compatibilidade com workflows existentes.
    
    Wrapper que mantém interface idêntica ao ai_agent.py original.
    """
    agent = SerenaAIAgent()
    return agent.process_conversation(phone, message, action) 