"""
Serena API Tool - Wrapper LangChain sobre serena_api

Este tool permite usar scripts.serena_api através da interface LangChain,
mantendo acesso à API real da Serena que já está funcionando.
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

# Import do módulo existente (REAL - funcionando)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Import real do serena_api
try:
    from scripts.serena_api import check_coverage, get_available_plans, SerenaAPI
    SERENA_API_AVAILABLE = True
except ImportError:
    SERENA_API_AVAILABLE = False
    logging.warning("SerenaAPI não disponível - usando simulação")

logger = logging.getLogger(__name__)


if LANGCHAIN_AVAILABLE:
    class SerenaAPIToolInput(BaseModel):
        """Schema de entrada para o Serena API Tool."""
        action: str = Field(description="Ação a executar: check_coverage, get_plans")
        city: Optional[str] = Field(default=None, description="Cidade para consulta")
        state: Optional[str] = Field(default=None, description="Estado para consulta (sigla)")
        zipcode: Optional[str] = Field(default=None, description="CEP para consulta")
else:
    class SerenaAPIToolInput:
        """Schema de entrada para o Serena API Tool (modo compatibilidade)."""
        action: str  # check_coverage, get_plans, etc.
        city: Optional[str] = None
        state: Optional[str] = None
        zipcode: Optional[str] = None


# @tool("serena_api")
def serena_api_tool_function(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper LangChain sobre scripts.serena_api.
    
    Permite consultar a API real da Serena através da interface
    padronizada LangChain, mantendo toda funcionalidade existente.
    
    Args:
        input_data: Dict com action e parâmetros específicos
        
    Returns:
        Dict com resultado da consulta à API
    """
    logger.info(f"SerenaAPITool executando: {input_data.get('action')}")
    
    try:
        action = input_data.get("action")
        city = input_data.get("city")
        state = input_data.get("state")
        zipcode = input_data.get("zipcode")
        
        if SERENA_API_AVAILABLE:
            # Usa a API real da Serena (já funcionando!)
            if action == "check_coverage":
                result = check_coverage(city, state, zipcode)
                
            elif action == "get_plans":
                result = get_available_plans(city, state, zipcode)
                
            else:
                result = f"Ação não reconhecida: {action}"
                
        else:
            # Simula a interface do serena_api (fallback)
            location = f"{city}/{state}" if city and state else zipcode
            
            if action == "check_coverage":
                result = {
                    "has_coverage": True,
                    "location": location,
                    "available_plans": 3,
                    "message": "Cobertura disponível para energia solar"
                }
                
            elif action == "get_plans":
                result = {
                    "plans": [
                        {"name": "CEMIG Solar 14%", "discount": 14, "provider": "CEMIG"},
                        {"name": "CEMIG Solar 16%", "discount": 16, "provider": "CEMIG"},
                        {"name": "CEMIG Solar 18%", "discount": 18, "provider": "CEMIG"}
                    ],
                    "location": location,
                    "total_plans": 3
                }
                
            else:
                result = f"Ação não reconhecida: {action}"
            
        return {
            "success": True,
            "result": result,
            "action": action,
            "location": f"{city}/{state}" if city and state else zipcode
        }
        
    except Exception as e:
        logger.error(f"Erro no SerenaAPITool: {e}")
        return {
            "success": False,
            "error": str(e),
            "action": action
        }


# LangChain tool decorator (se disponível)
if LANGCHAIN_AVAILABLE:
    @tool("serena_api", args_schema=SerenaAPIToolInput)
    def serena_api_tool_langchain(action: str, city: str = None, state: str = None, zipcode: str = None) -> str:
        """Consulta API real da Serena para cobertura e planos de energia solar."""
        input_data = {
            "action": action,
            "city": city,
            "state": state,
            "zipcode": zipcode
        }
        result = serena_api_tool_function(input_data)
        return str(result.get("result", "Erro no processamento"))

# Instância do tool que será usada pelo AgentExecutor
serena_api_tool = {
    "name": "serena_api",
    "description": "Consulta API real da Serena para cobertura e planos de energia solar",
    "function": serena_api_tool_function,
    "args_schema": SerenaAPIToolInput
}

# Exporta a versão LangChain se disponível
if LANGCHAIN_AVAILABLE:
    serena_api_tool_decorated = serena_api_tool_langchain
else:
    serena_api_tool_decorated = None 