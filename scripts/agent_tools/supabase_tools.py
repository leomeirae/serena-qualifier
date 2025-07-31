# =============================================================================
# SERENA SDR - SUPABASE TOOLS
# =============================================================================

"""
Supabase Tools Module

Este módulo contém todas as ferramentas para interação com o Supabase MCP Server.
Responsável por gerenciamento de leads, logs e persistência de dados.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import os
import json
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class SupabaseTools:
    """Ferramentas para interação com Supabase via MCP."""
    
    def __init__(self):
        """Inicializa as ferramentas do Supabase."""
        self.mcp_url = os.getenv('SUPABASE_MCP_URL')
        if not self.mcp_url:
            raise ValueError("SUPABASE_MCP_URL não encontrado")
        
        # Configurar timeout e retries
        self.timeout = 30
        self.max_retries = 3
    
    def _make_mcp_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Faz requisição para o MCP Server do Supabase.
        
        Args:
            method: Método MCP (tools/call)
            params: Parâmetros da requisição
            
        Returns:
            Dict: Resposta do MCP Server
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.mcp_url}/mcp",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                if "error" in result:
                    raise Exception(f"MCP Error: {result['error']}")
                
                return result.get("result", {})
                
            except Exception as e:
                logger.error(f"Tentativa {attempt + 1} falhou: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                continue
    
    def get_lead_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        Busca lead por número de telefone.
        
        Args:
            phone_number: Número de telefone do lead
            
        Returns:
            Dict: Dados do lead ou None se não encontrado
        """
        try:
            query = f"""
            SELECT * FROM leads 
            WHERE phone_number = '{phone_number}'
            ORDER BY created_at DESC 
            LIMIT 1
            """
            
            result = self._make_mcp_request("tools/call", {
                "name": "execute_sql",
                "arguments": {"query": query}
            })
            
            if result and "rows" in result and len(result["rows"]) > 0:
                return result["rows"][0]
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar lead por telefone: {str(e)}")
            return None
    
    def create_or_update_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria ou atualiza lead no Supabase.
        
        Args:
            lead_data: Dados do lead
            
        Returns:
            Dict: Resultado da operação
        """
        try:
            phone_number = lead_data.get('phone_number')
            if not phone_number:
                raise ValueError("phone_number é obrigatório")
            
            # Verificar se lead já existe
            existing_lead = self.get_lead_by_phone(phone_number)
            
            if existing_lead:
                # Atualizar lead existente
                query = f"""
                UPDATE leads 
                SET 
                    name = '{lead_data.get('name', existing_lead.get('name', ''))}',
                    city = '{lead_data.get('city', existing_lead.get('city', ''))}',
                    state = '{lead_data.get('state', existing_lead.get('state', ''))}',
                    invoice_amount = {lead_data.get('invoice_amount', existing_lead.get('invoice_amount', 0))},
                    client_type = '{lead_data.get('client_type', existing_lead.get('client_type', 'RESIDENTIAL'))}',
                    qualification_status = '{lead_data.get('qualification_status', existing_lead.get('qualification_status', 'NEW'))}',
                    conversation_state = '{lead_data.get('conversation_state', existing_lead.get('conversation_state', 'INITIAL'))}',
                    additional_data = '{json.dumps(lead_data.get('additional_data', {}))}'::jsonb,
                    updated_at = CURRENT_TIMESTAMP
                WHERE phone_number = '{phone_number}'
                RETURNING *
                """
            else:
                # Criar novo lead
                query = f"""
                INSERT INTO leads (
                    phone_number, name, city, state, invoice_amount, 
                    client_type, qualification_status, conversation_state, additional_data
                ) VALUES (
                    '{phone_number}',
                    '{lead_data.get('name', '')}',
                    '{lead_data.get('city', '')}',
                    '{lead_data.get('state', '')}',
                    {lead_data.get('invoice_amount', 0)},
                    '{lead_data.get('client_type', 'RESIDENTIAL')}',
                    '{lead_data.get('qualification_status', 'NEW')}',
                    '{lead_data.get('conversation_state', 'INITIAL')}',
                    '{json.dumps(lead_data.get('additional_data', {}))}'::jsonb
                ) RETURNING *
                """
            
            result = self._make_mcp_request("tools/call", {
                "name": "execute_sql",
                "arguments": {"query": query}
            })
            
            if result and "rows" in result and len(result["rows"]) > 0:
                return {
                    "success": True,
                    "lead": result["rows"][0],
                    "action": "updated" if existing_lead else "created"
                }
            
            return {"success": False, "error": "Falha ao salvar lead"}
            
        except Exception as e:
            logger.error(f"Erro ao criar/atualizar lead: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def update_lead_conversation_state(self, phone_number: str, state: str, additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Atualiza estado da conversa do lead.
        
        Args:
            phone_number: Número do telefone
            state: Novo estado da conversa
            additional_data: Dados adicionais para atualizar
            
        Returns:
            Dict: Resultado da atualização
        """
        try:
            # Preparar dados adicionais
            additional_json = json.dumps(additional_data or {})
            
            query = f"""
            UPDATE leads 
            SET 
                conversation_state = '{state}',
                additional_data = additional_data || '{additional_json}'::jsonb,
                updated_at = CURRENT_TIMESTAMP
            WHERE phone_number = '{phone_number}'
            RETURNING *
            """
            
            result = self._make_mcp_request("tools/call", {
                "name": "execute_sql",
                "arguments": {"query": query}
            })
            
            if result and "rows" in result and len(result["rows"]) > 0:
                return {
                    "success": True,
                    "lead": result["rows"][0]
                }
            
            return {"success": False, "error": "Lead não encontrado"}
            
        except Exception as e:
            logger.error(f"Erro ao atualizar estado da conversa: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def save_energy_bill(self, lead_id: int, phone: str, image_path: str, extracted_data: str) -> Dict[str, Any]:
        """
        Salva dados de conta de energia processada.
        
        Args:
            lead_id: ID do lead
            phone: Número do telefone
            image_path: Caminho da imagem
            extracted_data: Dados extraídos da imagem
            
        Returns:
            Dict: Resultado da operação
        """
        try:
            query = f"""
            INSERT INTO energy_bills (lead_id, phone, image_path, extracted_data)
            VALUES ({lead_id}, '{phone}', '{image_path}', '{extracted_data}')
            RETURNING *
            """
            
            result = self._make_mcp_request("tools/call", {
                "name": "execute_sql",
                "arguments": {"query": query}
            })
            
            if result and "rows" in result and len(result["rows"]) > 0:
                return {
                    "success": True,
                    "energy_bill": result["rows"][0]
                }
            
            return {"success": False, "error": "Falha ao salvar conta de energia"}
            
        except Exception as e:
            logger.error(f"Erro ao salvar conta de energia: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def log_sdr_activity(self, lead_id: str, task_name: str, success: bool, message: str, additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Registra atividade do SDR no log.
        
        Args:
            lead_id: ID do lead
            task_name: Nome da tarefa
            success: Se a tarefa foi bem-sucedida
            message: Mensagem de log
            additional_data: Dados adicionais
            
        Returns:
            Dict: Resultado da operação
        """
        try:
            # Criar tabela de logs se não existir
            create_table_query = """
            CREATE TABLE IF NOT EXISTS sdr_logs (
                id SERIAL PRIMARY KEY,
                lead_id VARCHAR(255),
                task_name VARCHAR(255),
                success BOOLEAN,
                message TEXT,
                additional_data JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            self._make_mcp_request("tools/call", {
                "name": "execute_sql",
                "arguments": {"query": create_table_query}
            })
            
            # Inserir log
            additional_json = json.dumps(additional_data or {})
            insert_query = f"""
            INSERT INTO sdr_logs (lead_id, task_name, success, message, additional_data)
            VALUES ('{lead_id}', '{task_name}', {success}, '{message}', '{additional_json}'::jsonb)
            RETURNING *
            """
            
            result = self._make_mcp_request("tools/call", {
                "name": "execute_sql",
                "arguments": {"query": insert_query}
            })
            
            if result and "rows" in result and len(result["rows"]) > 0:
                return {
                    "success": True,
                    "log_entry": result["rows"][0]
                }
            
            return {"success": False, "error": "Falha ao salvar log"}
            
        except Exception as e:
            logger.error(f"Erro ao salvar log SDR: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_lead_conversation_history(self, phone_number: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca histórico de conversas do lead.
        
        Args:
            phone_number: Número do telefone
            limit: Limite de registros
            
        Returns:
            List: Histórico de conversas
        """
        try:
            query = f"""
            SELECT * FROM sdr_logs 
            WHERE lead_id = '{phone_number}'
            ORDER BY created_at DESC 
            LIMIT {limit}
            """
            
            result = self._make_mcp_request("tools/call", {
                "name": "execute_sql",
                "arguments": {"query": query}
            })
            
            if result and "rows" in result:
                return result["rows"]
            
            return []
            
        except Exception as e:
            logger.error(f"Erro ao buscar histórico: {str(e)}")
            return []
    
    def update_lead_qualification(self, phone_number: str, qualification_status: str, invoice_amount: float = None) -> Dict[str, Any]:
        """
        Atualiza qualificação do lead.
        
        Args:
            phone_number: Número do telefone
            qualification_status: Status da qualificação
            invoice_amount: Valor da conta (opcional)
            
        Returns:
            Dict: Resultado da atualização
        """
        try:
            # Construir query dinamicamente
            update_fields = [f"qualification_status = '{qualification_status}'"]
            
            if invoice_amount is not None:
                update_fields.append(f"invoice_amount = {invoice_amount}")
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            
            query = f"""
            UPDATE leads 
            SET {', '.join(update_fields)}
            WHERE phone_number = '{phone_number}'
            RETURNING *
            """
            
            result = self._make_mcp_request("tools/call", {
                "name": "execute_sql",
                "arguments": {"query": query}
            })
            
            if result and "rows" in result and len(result["rows"]) > 0:
                return {
                    "success": True,
                    "lead": result["rows"][0]
                }
            
            return {"success": False, "error": "Lead não encontrado"}
            
        except Exception as e:
            logger.error(f"Erro ao atualizar qualificação: {str(e)}")
            return {"success": False, "error": str(e)} 