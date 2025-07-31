# =============================================================================
# SERENA SDR - MCP CLIENT UTILS
# =============================================================================

"""
MCP Client Utilities

Este módulo fornece cliente padronizado para comunicação com servidores MCP
usando protocolo JSON-RPC.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import json
import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

from .config import get_config
from .logger import get_logger

logger = get_logger("serena_sdr.mcp_client")


class MCPClient:
    """Cliente para comunicação com servidores MCP."""
    
    def __init__(self, base_url: str, timeout: int = 30, max_retries: int = 3):
        """
        Inicializa o cliente MCP.
        
        Args:
            base_url: URL base do servidor MCP
            timeout: Timeout em segundos
            max_retries: Número máximo de tentativas
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
        # Configurar headers padrão
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Serena-SDR-MCP-Client/1.0.0'
        })
    
    def _make_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Faz requisição JSON-RPC para o servidor MCP.
        
        Args:
            method: Método MCP (tools/list, tools/call, etc.)
            params: Parâmetros da requisição
            
        Returns:
            Dict: Resposta do servidor
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method
        }
        
        if params:
            payload["params"] = params
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Fazendo requisição MCP: {method}", 
                           service=self.base_url, method=method, attempt=attempt + 1)
                
                response = self.session.post(
                    f"{self.base_url}/mcp",
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Verificar se há erro na resposta
                if "error" in result:
                    error_msg = result["error"]
                    logger.error(f"Erro MCP: {error_msg}", 
                               service=self.base_url, method=method, error=error_msg)
                    raise Exception(f"MCP Error: {error_msg}")
                
                logger.debug(f"Requisição MCP bem-sucedida: {method}", 
                           service=self.base_url, method=method)
                
                return result.get("result", {})
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout na tentativa {attempt + 1} para {method}", 
                             service=self.base_url, method=method, attempt=attempt + 1)
                if attempt == self.max_retries - 1:
                    raise Exception(f"Timeout após {self.max_retries} tentativas")
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro de requisição na tentativa {attempt + 1}: {str(e)}", 
                           service=self.base_url, method=method, error=str(e))
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro inesperado na tentativa {attempt + 1}: {str(e)}", 
                           service=self.base_url, method=method, error=str(e))
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(1)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        Lista ferramentas disponíveis no servidor MCP.
        
        Returns:
            List: Lista de ferramentas disponíveis
        """
        try:
            result = self._make_request("tools/list")
            tools = result.get("tools", [])
            logger.info(f"Ferramentas listadas: {len(tools)}", 
                       service=self.base_url, tools_count=len(tools))
            return tools
        except Exception as e:
            logger.error(f"Erro ao listar ferramentas: {str(e)}", 
                        service=self.base_url, error=str(e))
            raise
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chama uma ferramenta específica no servidor MCP.
        
        Args:
            name: Nome da ferramenta
            arguments: Argumentos da ferramenta
            
        Returns:
            Dict: Resultado da chamada da ferramenta
        """
        try:
            params = {
                "name": name,
                "arguments": arguments
            }
            
            result = self._make_request("tools/call", params)
            
            logger.info(f"Ferramenta chamada: {name}", 
                       service=self.base_url, tool=name, arguments=arguments)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao chamar ferramenta {name}: {str(e)}", 
                        service=self.base_url, tool=name, error=str(e))
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """
        Verifica a saúde do servidor MCP.
        
        Returns:
            Dict: Status de saúde do servidor
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro no health check: {str(e)}", 
                        service=self.base_url, error=str(e))
            raise


class MCPClientManager:
    """Gerenciador de clientes MCP para diferentes serviços."""
    
    def __init__(self):
        """Inicializa o gerenciador de clientes."""
        self.config = get_config()
        self.clients = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Inicializa clientes para todos os serviços MCP."""
        services = {
            'supabase': self.config.supabase_mcp_url,
            'serena': self.config.serena_mcp_url,
            'whatsapp': self.config.whatsapp_mcp_url
        }
        
        for service, url in services.items():
            try:
                self.clients[service] = MCPClient(
                    base_url=url,
                    timeout=self.config.request_timeout,
                    max_retries=self.config.max_retries
                )
                logger.info(f"Cliente MCP inicializado: {service}", service=service, url=url)
            except Exception as e:
                logger.error(f"Erro ao inicializar cliente MCP {service}: {str(e)}", 
                           service=service, error=str(e))
    
    def get_client(self, service: str) -> MCPClient:
        """
        Retorna cliente MCP para um serviço específico.
        
        Args:
            service: Nome do serviço (supabase, serena, whatsapp)
            
        Returns:
            MCPClient: Cliente para o serviço
        """
        if service not in self.clients:
            raise ValueError(f"Serviço MCP não encontrado: {service}")
        
        return self.clients[service]
    
    def call_service_tool(self, service: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chama uma ferramenta em um serviço específico.
        
        Args:
            service: Nome do serviço
            tool_name: Nome da ferramenta
            arguments: Argumentos da ferramenta
            
        Returns:
            Dict: Resultado da chamada
        """
        client = self.get_client(service)
        return client.call_tool(tool_name, arguments)
    
    def list_service_tools(self, service: str) -> List[Dict[str, Any]]:
        """
        Lista ferramentas disponíveis em um serviço.
        
        Args:
            service: Nome do serviço
            
        Returns:
            List: Lista de ferramentas
        """
        client = self.get_client(service)
        return client.list_tools()
    
    def health_check_all(self) -> Dict[str, Any]:
        """
        Verifica saúde de todos os serviços MCP.
        
        Returns:
            Dict: Status de saúde de todos os serviços
        """
        health_status = {}
        
        for service, client in self.clients.items():
            try:
                health_status[service] = {
                    "status": "healthy",
                    "details": client.health_check()
                }
            except Exception as e:
                health_status[service] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        return health_status


# Instância global do gerenciador de clientes
mcp_manager = MCPClientManager()


# Funções de conveniência
def get_mcp_client(service: str) -> MCPClient:
    """Retorna cliente MCP para um serviço específico."""
    return mcp_manager.get_client(service)


def call_mcp_tool(service: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Chama uma ferramenta MCP em um serviço específico."""
    return mcp_manager.call_service_tool(service, tool_name, arguments)


def list_mcp_tools(service: str) -> List[Dict[str, Any]]:
    """Lista ferramentas disponíveis em um serviço MCP."""
    return mcp_manager.list_service_tools(service)


def check_mcp_health() -> Dict[str, Any]:
    """Verifica saúde de todos os serviços MCP."""
    return mcp_manager.health_check_all()


# Clientes específicos para cada serviço
class SupabaseMCPClient:
    """Cliente específico para Supabase MCP."""
    
    def __init__(self):
        self.client = get_mcp_client('supabase')
    
    def execute_sql(self, query: str) -> Dict[str, Any]:
        """Executa SQL no Supabase."""
        return self.client.call_tool("execute_sql", {"query": query})
    
    def list_tables(self, schemas: List[str] = None) -> Dict[str, Any]:
        """Lista tabelas no Supabase."""
        arguments = {}
        if schemas:
            arguments["schemas"] = schemas
        return self.client.call_tool("list_tables", arguments)
    
    def get_lead_by_phone(self, phone: str) -> Dict[str, Any]:
        """Busca lead por telefone."""
        query = f"SELECT * FROM leads WHERE phone_number = '{phone}' ORDER BY created_at DESC LIMIT 1"
        return self.execute_sql(query)


class SerenaMCPClient:
    """Cliente específico para Serena MCP."""
    
    def __init__(self):
        self.client = get_mcp_client('serena')
    
    def consultar_areas_operacao_gd(self, cidade: str = None, estado: str = None) -> Dict[str, Any]:
        """Consulta áreas de operação GD."""
        arguments = {}
        if cidade:
            arguments["cidade"] = cidade
        if estado:
            arguments["estado"] = estado
        return self.client.call_tool("consultar_areas_operacao_gd", arguments)
    
    def obter_planos_gd(self, cidade: str = None, estado: str = None) -> Dict[str, Any]:
        """Obtém planos GD."""
        arguments = {}
        if cidade:
            arguments["cidade"] = cidade
        if estado:
            arguments["estado"] = estado
        return self.client.call_tool("obter_planos_gd", arguments)
    
    def validar_qualificacao_lead(self, cidade: str, estado: str, tipo_pessoa: str, valor_conta: float) -> Dict[str, Any]:
        """Valida qualificação de lead."""
        arguments = {
            "cidade": cidade,
            "estado": estado,
            "tipo_pessoa": tipo_pessoa,
            "valor_conta": valor_conta
        }
        return self.client.call_tool("validar_qualificacao_lead", arguments)


class WhatsAppMCPClient:
    """Cliente específico para WhatsApp MCP."""
    
    def __init__(self):
        self.client = get_mcp_client('whatsapp')
    
    def send_text_message(self, to: str, message: str) -> Dict[str, Any]:
        """Envia mensagem de texto."""
        return self.client.call_tool("sendTextMessage", {
            "to": to,
            "message": message
        })
    
    def send_template_message(self, to: str, template_name: str, language: str = "pt_BR", components: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Envia mensagem de template."""
        arguments = {
            "to": to,
            "templateName": template_name,
            "language": language
        }
        if components:
            arguments["components"] = components
        return self.client.call_tool("sendTemplateMessage", arguments)
    
    def send_image_message(self, to: str, image_url: str, caption: str = None) -> Dict[str, Any]:
        """Envia mensagem com imagem."""
        arguments = {
            "to": to,
            "imageUrl": image_url
        }
        if caption:
            arguments["caption"] = caption
        return self.client.call_tool("sendImageMessage", arguments) 