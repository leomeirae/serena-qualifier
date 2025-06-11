"""
Conversation Tool - Wrapper LangChain sobre conversation_manager

Este tool permite usar utils.conversation_manager através da interface
LangChain, mantendo toda funcionalidade existente.
"""

from typing import Dict, Any, Optional
import logging
import sys
import os

# LangChain imports
try:
    from langchain.tools import tool
    from pydantic import BaseModel, Field
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Import do módulo existente (será preservado)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Import real do conversation_manager
try:
    from utils.conversation_manager import ConversationManager
    CONVERSATION_MANAGER_AVAILABLE = True
except ImportError:
    CONVERSATION_MANAGER_AVAILABLE = False
    logging.warning("ConversationManager não disponível - usando simulação")

logger = logging.getLogger(__name__)


if LANGCHAIN_AVAILABLE:
    class ConversationToolInput(BaseModel):
        """Schema de entrada para o Conversation Tool."""
        action: str = Field(description="Ação a executar: add_message, get_history, update_step")
        phone: str = Field(description="Número do telefone do lead")
        role: Optional[str] = Field(default=None, description="Papel na conversa: user, assistant")
        content: Optional[str] = Field(default=None, description="Conteúdo da mensagem")
        step: Optional[str] = Field(default=None, description="Step atual da conversa")
        execution_id: Optional[str] = Field(default=None, description="ID da execução Kestra")
else:
    class ConversationToolInput:
        """Schema de entrada para o Conversation Tool (modo compatibilidade)."""
        action: str  # add_message, get_history, update_step, etc.
        phone: str
        role: Optional[str] = None  # user, assistant
        content: Optional[str] = None
        step: Optional[str] = None
        execution_id: Optional[str] = None


# @tool("conversation_manager")
def conversation_tool_function(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper LangChain sobre utils.conversation_manager.
    
    Permite usar todas as funcionalidades do conversation_manager
    através da interface padronizada LangChain.
    
    Args:
        input_data: Dict com action, phone e parâmetros específicos
        
    Returns:
        Dict com resultado da operação
    """
    logger.info(f"ConversationTool executando: {input_data.get('action')}")
    
    try:
        action = input_data.get("action")
        phone = input_data.get("phone")
        
        if CONVERSATION_MANAGER_AVAILABLE:
            # Usa o conversation_manager real
            cm = ConversationManager()
            
            if action == "add_message":
                role = input_data.get("role", "user")
                content = input_data.get("content", "")
                result = cm.add_message(phone, role, content)
                
            elif action == "get_history":
                result = cm.get_conversation_history(phone)
                
            elif action == "update_step":
                step = input_data.get("step")
                execution_id = input_data.get("execution_id")
                result = cm.update_conversation_step(phone, step, execution_id)
                
            else:
                result = f"Ação não reconhecida: {action}"
                
        else:
            # Simula a interface do conversation_manager (fallback)
            if action == "add_message":
                role = input_data.get("role", "user")
                content = input_data.get("content", "")
                result = f"Mensagem adicionada: {role} - {content}"
                
            elif action == "get_history":
                result = f"Histórico recuperado para {phone}"
                
            elif action == "update_step":
                step = input_data.get("step")
                execution_id = input_data.get("execution_id")
                result = f"Step atualizado para {step}"
                
            else:
                result = f"Ação não reconhecida: {action}"
            
        return {
            "success": True,
            "result": result,
            "phone": phone,
            "action": action
        }
        
    except Exception as e:
        logger.error(f"Erro no ConversationTool: {e}")
        return {
            "success": False,
            "error": str(e),
            "phone": phone,
            "action": action
        }


# LangChain tool decorator (se disponível)
if LANGCHAIN_AVAILABLE:
    @tool("conversation_manager", args_schema=ConversationToolInput)
    def conversation_tool_langchain(action: str, phone: str, role: str = None, content: str = None, step: str = None, execution_id: str = None) -> str:
        """Gerencia conversas e histórico de mensagens com leads."""
        input_data = {
            "action": action,
            "phone": phone,
            "role": role,
            "content": content,
            "step": step,
            "execution_id": execution_id
        }
        result = conversation_tool_function(input_data)
        return str(result.get("result", "Erro no processamento"))

# Instância do tool que será usada pelo AgentExecutor
conversation_tool = {
    "name": "conversation_manager",
    "description": "Gerencia conversas e histórico de mensagens com leads",
    "function": conversation_tool_function,
    "args_schema": ConversationToolInput
}

# Exporta a versão LangChain se disponível
if LANGCHAIN_AVAILABLE:
    conversation_tool_decorated = conversation_tool_langchain
else:
    conversation_tool_decorated = None 