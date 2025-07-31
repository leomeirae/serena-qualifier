#!/usr/bin/env python3
"""
MCP Supabase Integration for Serena Qualifier

Este módulo integra o projeto Serena Qualifier com o MCP Server Supabase,
substituindo as conexões diretas PostgreSQL por chamadas MCP padronizadas.

Funcionalidades:
- Consulta de leads via MCP
- Salvamento e atualização de leads
- Upload de imagens de contas de energia
- Geração de URLs assinadas
- Gestão de metadados de imagens

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-30
"""

import os
import json
import re
import requests
import logging
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from langchain_core.tools import tool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPSupabaseClient:
    """Cliente para comunicação com o MCP Server Supabase"""
    
    def __init__(self, base_url: str = None):
        """
        Inicializa o cliente MCP Supabase.
        
        Args:
            base_url (str): URL base do MCP Server. Se None, usa a URL padrão.
        """
        self.base_url = base_url or "http://egkccc8ow4ww4kw40gokgkw0.157.180.32.249.sslip.io"
        self.mcp_endpoint = f"{self.base_url}/mcp"
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def _make_mcp_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Faz uma requisição para o MCP Server.
        
        Args:
            method (str): Método MCP a ser chamado
            params (Dict[str, Any]): Parâmetros do método
            
        Returns:
            Dict[str, Any]: Resposta do MCP Server
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        try:
            response = requests.post(
                self.mcp_endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "error" in result:
                    logger.error(f"MCP Error: {result['error']}")
                    raise Exception(f"MCP Error: {result['error']}")
                return result.get("result", {})
            else:
                raise Exception(f"HTTP Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise
    
    def execute_sql(self, query: str) -> List[Dict[str, Any]]:
        """
        Executa uma query SQL via MCP Server.
        
        Args:
            query (str): Query SQL a ser executada
            
        Returns:
            List[Dict[str, Any]]: Resultados da query
        """
        return self._make_mcp_request("execute_sql", {"query": query})
    
    def list_tables(self, schemas: List[str] = None) -> List[Dict[str, Any]]:
        """
        Lista tabelas do banco via MCP Server.
        
        Args:
            schemas (List[str]): Schemas a serem listados
            
        Returns:
            List[Dict[str, Any]]: Lista de tabelas
        """
        params = {}
        if schemas:
            params["schemas"] = schemas
        return self._make_mcp_request("list_tables", params)

# Instância global do cliente MCP
mcp_client = MCPSupabaseClient()

@tool
def consultar_dados_lead_mcp(phone_number: str) -> str:
    """
    Consulta os dados de um lead existente no banco de dados usando o MCP Server.
    Use esta ferramenta no início de cada conversa para carregar o contexto do lead.
    
    Args:
        phone_number (str): Número de telefone do lead
        
    Returns:
        str: Dados do lead em formato JSON
    """
    try:
        # Normaliza o número de telefone para busca
        digits_only = re.sub(r'\D', '', phone_number)
        
        # Cria uma lista de possíveis formatos de telefone para busca
        possible_formats = []
        
        # Se começar com código do país (55)
        if digits_only.startswith('55'):
            without_country = digits_only[2:]  # Remove o 55
            possible_formats.append(without_country)  # Formato sem o 55
            
            # Se tiver o 9 após o DDD (formato novo)
            if len(without_country) >= 9 and without_country[2] == '9':
                possible_formats.append(without_country[:2] + without_country[3:])  # Remove o 9
            
            # Se não tiver o 9 (formato antigo)
            if len(without_country) == 8:
                possible_formats.append(without_country[:2] + '9' + without_country[2:])  # Adiciona o 9
        else:
            possible_formats.append(digits_only)
        
        # Adiciona outros formatos possíveis
        if len(digits_only) == 11:
            possible_formats.append(digits_only[-10:])
            possible_formats.append(digits_only[-8:])
        
        possible_formats.append(digits_only)
        possible_formats = list(set(possible_formats))
        
        logger.info(f"Tentando formatos de telefone: {possible_formats}")
        
        # Tenta cada formato via MCP
        for format_to_try in possible_formats:
            query = """
                SELECT name, city, state, invoice_amount, client_type, phone_number 
                FROM leads 
                WHERE phone_number = %s
            """
            
            try:
                result = mcp_client.execute_sql(query, [format_to_try])
                if result and len(result) > 0:
                    row = result[0]
                    lead_data = {
                        "name": row["name"],
                        "city": row["city"],
                        "state": row["state"],
                        "invoice_amount": float(row["invoice_amount"]) if row["invoice_amount"] is not None else 0.0,
                        "client_type": row["client_type"],
                        "phone_format": format_to_try
                    }
                    return json.dumps(lead_data)
            except Exception as e:
                logger.warning(f"Erro ao tentar formato {format_to_try}: {str(e)}")
                continue
        
        # Tenta busca por LIKE com últimos 8 dígitos
        if len(digits_only) >= 8:
            last_8_digits = digits_only[-8:]
            query = """
                SELECT name, city, state, invoice_amount, client_type, phone_number 
                FROM leads 
                WHERE phone_number LIKE %s
                LIMIT 1
            """
            
            try:
                result = mcp_client.execute_sql(query, [f"%{last_8_digits}"])
                if result and len(result) > 0:
                    row = result[0]
                    lead_data = {
                        "name": row["name"],
                        "city": row["city"],
                        "state": row["state"],
                        "invoice_amount": float(row["invoice_amount"]) if row["invoice_amount"] is not None else 0.0,
                        "client_type": row["client_type"],
                        "phone_format": row["phone_number"]
                    }
                    return json.dumps(lead_data)
            except Exception as e:
                logger.warning(f"Erro na busca LIKE: {str(e)}")
        
        return "Lead não encontrado no banco de dados."
        
    except Exception as e:
        logger.error(f"Erro ao consultar lead: {str(e)}")
        return f"Erro ao consultar lead: {str(e)}"

@tool
def salvar_ou_atualizar_lead_mcp(dados_lead: str) -> str:
    """
    Salva ou atualiza dados de um lead no banco de dados via MCP Server.
    
    Args:
        dados_lead (str): Dados do lead em formato JSON
        
    Returns:
        str: Resultado da operação
    """
    try:
        lead_data = json.loads(dados_lead)
        
        # Query de upsert
        query = """
            INSERT INTO leads
                (phone_number, name, invoice_amount, client_type, city, state, additional_data, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (phone_number) DO UPDATE
                SET name            = EXCLUDED.name,
                    invoice_amount  = EXCLUDED.invoice_amount,
                    client_type     = EXCLUDED.client_type,
                    city            = EXCLUDED.city,
                    state           = EXCLUDED.state,
                    additional_data = EXCLUDED.additional_data,
                    updated_at      = NOW()
            RETURNING id, phone_number, name
        """
        
        additional_data = {
            "source": "mcp_integration",
            "updated_by": "silvia_agent"
        }
        
        params = [
            lead_data["phone_number"],
            lead_data["name"],
            float(lead_data.get("invoice_amount", 0)),
            lead_data.get("client_type", "residencial"),
            lead_data.get("city", ""),
            lead_data.get("state", ""),
            json.dumps(additional_data)
        ]
        
        result = mcp_client.execute_sql(query, params)
        
        if result and len(result) > 0:
            row = result[0]
            return json.dumps({
                "success": True,
                "lead_id": row["id"],
                "phone_number": row["phone_number"],
                "name": row["name"],
                "message": "Lead salvo/atualizado com sucesso"
            })
        else:
            return json.dumps({
                "success": False,
                "message": "Erro ao salvar lead"
            })
            
    except Exception as e:
        logger.error(f"Erro ao salvar lead: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })

@tool
def listar_tabelas_mcp() -> str:
    """
    Lista todas as tabelas do banco de dados via MCP Server.
    
    Returns:
        str: Lista de tabelas em formato JSON
    """
    try:
        tables = mcp_client.list_tables()
        return json.dumps({
            "success": True,
            "tables": tables
        })
    except Exception as e:
        logger.error(f"Erro ao listar tabelas: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })

@tool
def verificar_status_mcp() -> str:
    """
    Verifica o status do MCP Server Supabase.
    
    Returns:
        str: Status do servidor
    """
    try:
        response = requests.get(f"{mcp_client.base_url}/status", timeout=10)
        if response.status_code == 200:
            return json.dumps({
                "success": True,
                "status": "online",
                "response": response.json()
            })
        else:
            return json.dumps({
                "success": False,
                "status": "error",
                "status_code": response.status_code
            })
    except Exception as e:
        logger.error(f"Erro ao verificar status: {str(e)}")
        return json.dumps({
            "success": False,
            "status": "offline",
            "error": str(e)
        })

# Função para migração gradual
def migrate_to_mcp():
    """
    Função para migração gradual das ferramentas existentes para MCP.
    """
    logger.info("Iniciando migração para MCP Server...")
    
    # Verifica status do MCP Server
    status = verificar_status_mcp()
    status_data = json.loads(status)
    
    if not status_data["success"]:
        logger.error("MCP Server não está disponível. Mantendo conexão direta.")
        return False
    
    logger.info("MCP Server está online. Migração pode prosseguir.")
    return True

if __name__ == "__main__":
    # Teste das funcionalidades
    print("=== Teste MCP Supabase Integration ===")
    
    # Verifica status
    status = verificar_status_mcp()
    print(f"Status: {status}")
    
    # Lista tabelas
    tables = listar_tabelas_mcp()
    print(f"Tabelas: {tables}") 