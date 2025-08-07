#!/usr/bin/env python3
# =============================================================================
# SERENA SDR - INTEGRAÇÃO MCP SERENA
# =============================================================================

"""
Integração com MCP Server Serena para o projeto Serena Qualifier.

Este módulo fornece ferramentas para comunicação com a API Serena via protocolo MCP,
incluindo consulta de planos, qualificação de leads e criação de contratos.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-30
"""

import os
import json
import requests
import logging
from typing import Dict, Any, List, Optional
from langchain.tools import tool

# Configurar logging
logger = logging.getLogger(__name__)

# Configurações MCP
SERENA_MCP_URL = os.getenv('SERENA_MCP_URL', 'http://mwc8k8wk0wg8o8s4k0w8scc4.157.180.32.249.sslip.io')
SERENA_MCP_ENDPOINT = f"{SERENA_MCP_URL.rstrip('/')}/mcp"

class MCPSerenaClient:
    """Cliente para comunicação com MCP Server Serena."""
    
    def __init__(self, base_url: str = None):
        """Inicializa o cliente MCP Serena."""
        self.base_url = base_url or SERENA_MCP_URL
        self.mcp_endpoint = f"{self.base_url.rstrip('/')}/mcp"
        self.timeout = 30
        self.max_retries = 3
    
    def _make_mcp_request(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Faz requisição JSON-RPC para o MCP Server."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fazendo requisição MCP Serena: {tool_name} (tentativa {attempt + 1})")
                response = requests.post(
                    self.mcp_endpoint,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "result" in result:
                        return result["result"]
                    elif "error" in result:
                        raise Exception(f"Erro MCP: {result['error']}")
                    else:
                        return result
                else:
                    logger.error(f"Erro HTTP {response.status_code}: {response.text}")
                    if attempt == self.max_retries - 1:
                        raise Exception(f"Erro HTTP {response.status_code}: {response.text}")
                        
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro de conexão (tentativa {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise Exception(f"Falha na conexão com MCP Serena: {str(e)}")
                    
        raise Exception("Máximo de tentativas excedido")
    
    def check_health(self) -> Dict[str, Any]:
        """Verifica a saúde do MCP Server."""
        try:
            health_url = f"{self.base_url.rstrip('/')}/health"
            response = requests.get(health_url, timeout=10)
            if response.status_code == 200:
                return {"status": "online", "data": response.json()}
            else:
                return {"status": "offline", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "offline", "error": str(e)}

# Instância global do cliente
mcp_client = MCPSerenaClient()

def test_mcp_connection() -> bool:
    """Testa a conexão com o MCP Server."""
    try:
        health_status = mcp_client.check_health()
        return health_status["status"] == "online"
    except Exception:
        return False

@tool
def consultar_areas_operacao_mcp(cidade: str = None, estado: str = None) -> str:
    """
    Consulta áreas de operação para Geração Distribuída via MCP Serena.
    
    Args:
        cidade: Nome da cidade (opcional)
        estado: Sigla do estado (opcional)
    
    Returns:
        JSON string com as áreas de operação disponíveis
    """
    try:
        arguments = {}
        if cidade:
            arguments["cidade"] = cidade
        if estado:
            arguments["estado"] = estado
            
        result = mcp_client._make_mcp_request("consultar_areas_operacao_gd", arguments)
        
        logger.info(f"Áreas de operação consultadas: {len(result.get('areas', []))} encontradas")
        return json.dumps({
            "success": True,
            "areas": result.get("areas", []),
            "count": len(result.get("areas", []))
        }, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Erro ao consultar áreas de operação: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "areas": []
        })

@tool
def obter_planos_mcp(cidade: str = None, estado: str = None, id_distribuidora: str = None) -> str:
    """
    Obtém planos de energia disponíveis via MCP Serena.
    
    Args:
        cidade: Nome da cidade (opcional)
        estado: Sigla do estado (opcional)
        id_distribuidora: ID da distribuidora (opcional)
    
    Returns:
        JSON string com os planos disponíveis
    """
    try:
        arguments = {}
        if cidade:
            arguments["cidade"] = cidade
        if estado:
            arguments["estado"] = estado
        if id_distribuidora:
            arguments["id_distribuidora"] = id_distribuidora
            
        result = mcp_client._make_mcp_request("obter_planos_gd", arguments)
        
        logger.info(f"Planos obtidos: {len(result.get('planos', []))} encontrados")
        return json.dumps({
            "success": True,
            "planos": result.get("planos", []),
            "count": len(result.get("planos", []))
        }, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Erro ao obter planos: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "planos": []
        })

@tool
def validar_qualificacao_lead_mcp(cidade: str, estado: str, tipo_pessoa: str, valor_conta: float) -> str:
    """
    Valida a qualificação de um lead via MCP Serena.
    
    Args:
        cidade: Nome da cidade
        estado: Sigla do estado
        tipo_pessoa: Tipo de pessoa (natural ou juridica)
        valor_conta: Valor da conta de energia
    
    Returns:
        JSON string com o resultado da validação
    """
    try:
        arguments = {
            "cidade": cidade,
            "estado": estado,
            "tipo_pessoa": tipo_pessoa,
            "valor_conta": valor_conta
        }
        
        result = mcp_client._make_mcp_request("validar_qualificacao_lead", arguments)
        
        logger.info(f"Lead validado: qualificado={result.get('qualificado', False)}")
        return json.dumps({
            "success": True,
            "qualificado": result.get("qualificado", False),
            "score": result.get("score", 0),
            "motivo": result.get("motivo", ""),
            "detalhes": result
        }, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Erro ao validar qualificação: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "qualificado": False
        })

@tool
def cadastrar_lead_mcp(dados_lead: str) -> str:
    """
    Cadastra um novo lead via MCP Serena.
    
    Args:
        dados_lead: JSON string com os dados do lead
    
    Returns:
        JSON string com o resultado do cadastro
    """
    try:
        # Parse dos dados do lead
        if isinstance(dados_lead, str):
            lead_data = json.loads(dados_lead)
        else:
            lead_data = dados_lead
            
        arguments = {
            "dados_lead": lead_data
        }
        
        result = mcp_client._make_mcp_request("cadastrar_lead", arguments)
        
        logger.info(f"Lead cadastrado: ID={result.get('id_lead', 'N/A')}")
        return json.dumps({
            "success": True,
            "id_lead": result.get("id_lead"),
            "status": result.get("status", "created"),
            "detalhes": result
        }, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Erro ao cadastrar lead: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "id_lead": None
        })

@tool
def criar_contrato_mcp(id_lead: str, plano: str) -> str:
    """
    Cria um contrato para um lead via MCP Serena.
    
    Args:
        id_lead: ID do lead
        plano: JSON string com os dados do plano
    
    Returns:
        JSON string com o resultado da criação do contrato
    """
    try:
        # Parse dos dados do plano
        if isinstance(plano, str):
            plano_data = json.loads(plano)
        else:
            plano_data = plano
            
        arguments = {
            "id_lead": id_lead,
            "plano": plano_data
        }
        
        result = mcp_client._make_mcp_request("criar_contrato", arguments)
        
        logger.info(f"Contrato criado: ID={result.get('id_contrato', 'N/A')}")
        return json.dumps({
            "success": True,
            "id_contrato": result.get("id_contrato"),
            "status": result.get("status", "created"),
            "detalhes": result
        }, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Erro ao criar contrato: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "id_contrato": None
        })

@tool
def verificar_status_serena_mcp() -> str:
    """
    Verifica o status e saúde do MCP Server Serena.
    
    Returns:
        JSON string com o status do servidor
    """
    try:
        health_status = mcp_client.check_health()
        
        # Tentar uma consulta simples para testar conectividade
        try:
            test_result = mcp_client._make_mcp_request("consultar_areas_operacao_gd", {})
            api_status = "connected" if test_result else "disconnected"
        except Exception:
            api_status = "disconnected"
        
        status_info = {
            "mcp_server": health_status["status"],
            "api_serena": api_status,
            "server_url": mcp_client.base_url,
            "timestamp": "now()"
        }
        
        if health_status["status"] == "offline":
            status_info["error"] = health_status.get("error", "Unknown error")
        
        logger.info(f"Status Serena MCP verificado: {status_info['mcp_server']}/{status_info['api_serena']}")
        return json.dumps(status_info, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Erro ao verificar status Serena MCP: {str(e)}")
        return json.dumps({
            "mcp_server": "error",
            "api_serena": "unknown", 
            "error": str(e),
            "server_url": mcp_client.base_url
        })

def get_serena_mcp_info() -> Dict[str, Any]:
    """Retorna informações sobre a configuração MCP Serena."""
    return {
        "server_url": mcp_client.base_url,
        "endpoint": mcp_client.mcp_endpoint,
        "available": test_mcp_connection()
    }

if __name__ == "__main__":
    # Teste básico quando executado diretamente
    print("=== Teste MCP Serena Integration ===")
    print(f"Server URL: {mcp_client.base_url}")
    
    # Teste de conectividade
    if test_mcp_connection():
        print("✅ MCP Server Serena online")
        
        # Teste de consulta de áreas
        try:
            areas_result = consultar_areas_operacao_mcp.invoke({"cidade": "São Paulo", "estado": "SP"})
            areas_data = json.loads(areas_result)
            if areas_data.get("success"):
                print(f"✅ Áreas encontradas: {areas_data['count']}")
            else:
                print(f"❌ Erro ao consultar áreas: {areas_data.get('error')}")
        except Exception as e:
            print(f"❌ Erro no teste de áreas: {str(e)}")
    else:
        print("❌ MCP Server Serena offline")
    
    print("=== Fim do Teste ===")