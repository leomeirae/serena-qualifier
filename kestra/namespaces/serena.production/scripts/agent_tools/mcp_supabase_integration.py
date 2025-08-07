#!/usr/bin/env python3
# =============================================================================
# SERENA SDR - INTEGRAÇÃO MCP SUPABASE
# =============================================================================

"""
Integração com MCP Server Supabase para o projeto Serena Qualifier.

Este módulo fornece ferramentas para comunicação com o Supabase via protocolo MCP,
com fallback automático para conexão direta PostgreSQL.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-07
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
MCP_SERVER_URL = os.getenv('SUPABASE_MCP_URL', 'http://hwg4ks4ooooc04wsosookoog.157.180.32.249.sslip.io')
MCP_ENDPOINT = f"{MCP_SERVER_URL.rstrip('/')}/mcp"

class MCPSupabaseClient:
    """Cliente para comunicação com MCP Server Supabase."""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or MCP_SERVER_URL
        self.mcp_endpoint = f"{self.base_url.rstrip('/')}/mcp"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Serena-SDR-Agent/1.0'
        })
    
    def _make_mcp_call(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Faz uma chamada JSON-RPC para o MCP Server."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        try:
            response = self.session.post(self.mcp_endpoint, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                logger.error(f"MCP Error: {result['error']}")
                raise Exception(f"MCP Error: {result['error']['message']}")
            
            return result.get("result", {})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MCP Request failed: {str(e)}")
            raise Exception(f"MCP Server não disponível: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"MCP Response parsing failed: {str(e)}")
            raise Exception(f"Resposta inválida do MCP Server: {str(e)}")
    
    def execute_sql(self, query: str) -> List[Dict[str, Any]]:
        """Executa query SQL via MCP Server."""
        return self._make_mcp_call("tools/call", {
            "name": "execute_sql",
            "arguments": {"query": query}
        })
    
    def list_tables(self, schemas: List[str] = None) -> List[Dict[str, Any]]:
        """Lista tabelas do banco via MCP Server."""
        params = {"name": "list_tables", "arguments": {}}
        if schemas:
            params["arguments"]["schemas"] = schemas
        
        return self._make_mcp_call("tools/call", params)
    
    def check_health(self) -> Dict[str, Any]:
        """Verifica saúde do MCP Server."""
        try:
            health_url = f"{self.base_url.rstrip('/')}/health"
            response = self.session.get(health_url, timeout=10)
            response.raise_for_status()
            return {"status": "online", "details": response.json()}
        except Exception as e:
            return {"status": "offline", "error": str(e)}

# Instância global do cliente MCP
mcp_client = MCPSupabaseClient()

# =============================================================================
# FERRAMENTAS LANGCHAIN PARA O AGENTE SÍLVIA
# =============================================================================

@tool
def consultar_dados_lead_mcp(phone_number: str) -> str:
    """
    Consulta dados de um lead pelo número de telefone via MCP Server.
    
    Args:
        phone_number: Número de telefone do lead (com ou sem código do país)
    
    Returns:
        JSON string com os dados do lead encontrado
    """
    try:
        # Normalizar número de telefone para diferentes formatos
        phone_variants = [
            phone_number,
            phone_number.replace("+", ""),
            phone_number.replace("+55", ""),
            f"+55{phone_number}" if not phone_number.startswith("+") else phone_number,
            f"55{phone_number}" if not phone_number.startswith("55") else phone_number
        ]
        
        for phone in phone_variants:
            query = f"""
            SELECT id, full_name, city, state, phone_number, email, 
                   person_type, monthly_bill, created_at, updated_at
            FROM leads 
            WHERE phone_number = '{phone}' 
            LIMIT 1
            """
            
            result = mcp_client.execute_sql(query)
            
            if result and len(result) > 0:
                lead_data = result[0]
                logger.info(f"Lead encontrado via MCP: {lead_data.get('full_name', 'N/A')}")
                return json.dumps(lead_data, ensure_ascii=False, default=str)
        
        logger.warning(f"Lead não encontrado via MCP para telefone: {phone_number}")
        return json.dumps({"error": "Lead não encontrado", "phone_searched": phone_number})
        
    except Exception as e:
        logger.error(f"Erro ao consultar lead via MCP: {str(e)}")
        return json.dumps({"error": f"Erro na consulta MCP: {str(e)}"})

@tool
def salvar_ou_atualizar_lead_mcp(dados_lead: str) -> str:
    """
    Salva ou atualiza dados de um lead via MCP Server.
    
    Args:
        dados_lead: JSON string com os dados do lead
    
    Returns:
        JSON string com o resultado da operação
    """
    try:
        lead_data = json.loads(dados_lead)
        
        # Campos obrigatórios
        required_fields = ['phone_number']
        for field in required_fields:
            if field not in lead_data:
                return json.dumps({"error": f"Campo obrigatório ausente: {field}"})
        
        phone = lead_data['phone_number']
        
        # Preparar dados para UPSERT
        fields = []
        values = []
        
        field_mapping = {
            'full_name': 'full_name',
            'city': 'city', 
            'state': 'state',
            'phone_number': 'phone_number',
            'email': 'email',
            'person_type': 'person_type',
            'monthly_bill': 'monthly_bill'
        }
        
        for json_key, db_field in field_mapping.items():
            if json_key in lead_data and lead_data[json_key] is not None:
                fields.append(db_field)
                if isinstance(lead_data[json_key], str):
                    values.append(f"'{lead_data[json_key]}'")
                else:
                    values.append(str(lead_data[json_key]))
        
        # Query UPSERT
        upsert_query = f"""
        INSERT INTO leads ({', '.join(fields)}, updated_at)
        VALUES ({', '.join(values)}, NOW())
        ON CONFLICT (phone_number) 
        DO UPDATE SET 
            {', '.join([f"{field} = EXCLUDED.{field}" for field in fields])},
            updated_at = NOW()
        RETURNING id, full_name, phone_number, updated_at
        """
        
        result = mcp_client.execute_sql(upsert_query)
        
        if result and len(result) > 0:
            saved_lead = result[0]
            logger.info(f"Lead salvo/atualizado via MCP: ID {saved_lead.get('id')}")
            return json.dumps({
                "success": True,
                "lead_id": saved_lead.get('id'),
                "message": "Lead salvo/atualizado com sucesso",
                "data": saved_lead
            }, ensure_ascii=False, default=str)
        else:
            return json.dumps({"error": "Falha ao salvar lead - nenhum resultado retornado"})
            
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON: {str(e)}")
        return json.dumps({"error": f"JSON inválido: {str(e)}"})
    except Exception as e:
        logger.error(f"Erro ao salvar lead via MCP: {str(e)}")
        return json.dumps({"error": f"Erro na operação MCP: {str(e)}"})

@tool
def listar_tabelas_mcp() -> str:
    """
    Lista todas as tabelas disponíveis no banco de dados via MCP Server.
    
    Returns:
        JSON string com a lista de tabelas
    """
    try:
        result = mcp_client.list_tables(["public"])
        
        if result:
            logger.info(f"Tabelas listadas via MCP: {len(result)} encontradas")
            return json.dumps({
                "success": True,
                "tables": result,
                "count": len(result)
            }, ensure_ascii=False)
        else:
            return json.dumps({"error": "Nenhuma tabela encontrada"})
            
    except Exception as e:
        logger.error(f"Erro ao listar tabelas via MCP: {str(e)}")
        return json.dumps({"error": f"Erro na listagem MCP: {str(e)}"})

@tool
def verificar_status_mcp() -> str:
    """
    Verifica o status e saúde do MCP Server Supabase.
    
    Returns:
        JSON string com o status do servidor
    """
    try:
        health_status = mcp_client.check_health()
        
        # Tentar uma query simples para testar conectividade
        test_query = "SELECT 1 as test_connection"
        try:
            query_result = mcp_client.execute_sql(test_query)
            database_status = "connected" if query_result else "disconnected"
        except Exception:
            database_status = "disconnected"
        
        status_info = {
            "mcp_server": health_status["status"],
            "database": database_status,
            "server_url": mcp_client.base_url,
            "timestamp": "now()"
        }
        
        if health_status["status"] == "offline":
            status_info["error"] = health_status.get("error", "Unknown error")
        
        logger.info(f"Status MCP verificado: {status_info['mcp_server']}/{status_info['database']}")
        return json.dumps(status_info, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Erro ao verificar status MCP: {str(e)}")
        return json.dumps({
            "mcp_server": "error",
            "database": "unknown", 
            "error": str(e),
            "server_url": mcp_client.base_url
        })

# =============================================================================
# FUNÇÕES DE UTILIDADE
# =============================================================================

def test_mcp_connection() -> bool:
    """Testa se a conexão MCP está funcionando."""
    try:
        health = mcp_client.check_health()
        return health["status"] == "online"
    except Exception:
        return False

def get_mcp_info() -> Dict[str, Any]:
    """Retorna informações sobre a configuração MCP."""
    return {
        "server_url": mcp_client.base_url,
        "endpoint": mcp_client.mcp_endpoint,
        "available": test_mcp_connection()
    }

if __name__ == "__main__":
    # Teste básico quando executado diretamente
    print("=== Teste MCP Supabase Integration ===")
    print(f"Server URL: {mcp_client.base_url}")
    
    # Teste de conectividade
    if test_mcp_connection():
        print("✅ MCP Server online")
        
        # Teste de listagem de tabelas
        try:
            tables_result = listar_tabelas_mcp.invoke({})
            tables_data = json.loads(tables_result)
            if tables_data.get("success"):
                print(f"✅ Tabelas encontradas: {tables_data['count']}")
            else:
                print(f"❌ Erro ao listar tabelas: {tables_data.get('error')}")
        except Exception as e:
            print(f"❌ Erro no teste de tabelas: {str(e)}")
    else:
        print("❌ MCP Server offline")
    
    print("=== Fim do Teste ===")