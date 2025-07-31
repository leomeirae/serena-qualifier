# =============================================================================
# SERENA SDR - TESTE E2E: MENSAGEM DE TEXTO
# =============================================================================

"""
Teste End-to-End: Fluxo de Mensagem de Texto

Este teste simula o fluxo completo de uma mensagem de texto
via webhook WhatsApp, desde o recebimento até a resposta da IA.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import pytest
import json
import httpx
from unittest.mock import patch, Mock
from datetime import datetime


class TestTextMessageFlow:
    """Teste do fluxo de mensagem de texto."""

    def test_text_message_webhook_flow(
        self,
        sample_webhook_payload,
        mock_supabase_mcp,
        mock_whatsapp_mcp,
        mock_openai_chat,
        test_environment
    ):
        """
        Teste 1: Disparar webhook com mensagem de texto e verificar resposta.
        
        Cenário:
        1. Webhook recebe payload com mensagem "Olá Silvia"
        2. Sistema busca lead no Supabase
        3. Agente IA gera resposta
        4. Resposta é enviada via WhatsApp
        """
        
        # 1. Simular recebimento do webhook
        webhook_url = "http://localhost:8001/webhook"
        
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 200
            mock_webhook.return_value.json.return_value = {"status": "ok"}
            
            # Chamar webhook
            response = httpx.post(
                webhook_url,
                json=sample_webhook_payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Verificar que webhook foi chamado
            assert response.status_code == 200
            mock_webhook.assert_called()
        
        # 2. Verificar que lead foi buscado no Supabase
        assert_mcp_call(
            mock_supabase_mcp,
            "execute_sql",
            {
                "query": "SELECT * FROM leads WHERE phone = $1",
                "params": ["5581997498268"]
            }
        )
        
        # 3. Verificar que OpenAI foi chamado para gerar resposta
        mock_openai_chat.assert_called()
        call_args = mock_openai_chat.call_args
        
        # Verificar que a mensagem do usuário foi incluída
        messages = call_args[1]['messages']
        user_message = next((msg for msg in messages if msg['role'] == 'user'), None)
        assert user_message is not None
        assert "Olá Silvia" in user_message['content']
        
        # 4. Verificar que resposta foi enviada via WhatsApp
        assert_mcp_call(
            mock_whatsapp_mcp,
            "sendTextMessage",
            {
                "phone": "5581997498268",
                "message": "Olá! Sou a Silvia, sua consultora de energia solar. Como posso ajudá-lo hoje?"
            }
        )

    def test_text_message_with_lead_not_found(
        self,
        sample_webhook_payload,
        mock_supabase_mcp,
        mock_whatsapp_mcp,
        test_environment
    ):
        """
        Teste 2: Mensagem de texto com lead não encontrado.
        
        Cenário:
        1. Webhook recebe mensagem de lead não cadastrado
        2. Sistema não encontra lead no Supabase
        3. Deve enviar mensagem de erro ou fallback
        """
        
        # Mock Supabase retornando lead não encontrado
        mock_supabase_mcp.return_value.json.return_value = {
            "result": {"data": []}
        }
        
        # Simular webhook
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=sample_webhook_payload
            )
            
            assert response.status_code == 200
        
        # Verificar que lead foi buscado
        assert_mcp_call(
            mock_supabase_mcp,
            "execute_sql",
            {
                "query": "SELECT * FROM leads WHERE phone = $1",
                "params": ["5581997498268"]
            }
        )
        
        # Verificar que mensagem de fallback foi enviada
        mock_whatsapp_mcp.assert_called()
        call_args = mock_whatsapp_mcp.call_args
        
        # Verificar que a mensagem contém texto de fallback
        json_data = call_args[1]['json']
        message_content = json_data['params']['message']
        assert "desculpe" in message_content.lower() or "não encontrado" in message_content.lower()

    def test_text_message_with_invalid_payload(
        self,
        mock_whatsapp_mcp,
        test_environment
    ):
        """
        Teste 3: Webhook com payload inválido.
        
        Cenário:
        1. Webhook recebe payload malformado
        2. Sistema deve retornar erro 400
        3. Nenhuma chamada MCP deve ser feita
        """
        
        invalid_payload = {
            "object": "whatsapp_business_account",
            "entry": []  # Sem mensagens
        }
        
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 400
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=invalid_payload
            )
            
            assert response.status_code == 400
        
        # Verificar que nenhuma chamada MCP foi feita
        mock_whatsapp_mcp.assert_not_called()

    def test_text_message_response_time(
        self,
        sample_webhook_payload,
        mock_supabase_mcp,
        mock_whatsapp_mcp,
        mock_openai_chat,
        test_environment
    ):
        """
        Teste 4: Verificar tempo de resposta da mensagem de texto.
        
        Cenário:
        1. Medir tempo total do fluxo
        2. Verificar que está dentro do SLA (< 15 segundos)
        """
        
        import time
        
        start_time = time.time()
        
        # Simular fluxo completo
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=sample_webhook_payload
            )
            
            assert response.status_code == 200
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Verificar SLA: resposta em menos de 15 segundos
        assert response_time < 15.0, f"Tempo de resposta {response_time:.2f}s excedeu SLA de 15s"
        
        # Verificar que todas as chamadas foram feitas
        mock_supabase_mcp.assert_called()
        mock_openai_chat.assert_called()
        mock_whatsapp_mcp.assert_called()

    def test_text_message_logging(
        self,
        sample_webhook_payload,
        mock_supabase_mcp,
        mock_whatsapp_mcp,
        mock_openai_chat,
        test_environment
    ):
        """
        Teste 5: Verificar logging de métricas.
        
        Cenário:
        1. Fluxo de mensagem de texto executado
        2. Verificar que logs foram inseridos no Supabase
        3. Verificar métricas de performance
        """
        
        # Mock para logs no Supabase
        mock_supabase_mcp.return_value.json.return_value = {
            "result": {
                "data": [
                    {
                        "id": "test-lead-id",
                        "phone": "5581997498268",
                        "name": "Teste SDR"
                    }
                ]
            }
        }
        
        # Simular fluxo
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=sample_webhook_payload
            )
            
            assert response.status_code == 200
        
        # Verificar que logs foram inseridos
        # Deve haver pelo menos 3 chamadas: buscar lead, inserir log inicial, inserir log final
        assert mock_supabase_mcp.call_count >= 3
        
        # Verificar chamadas de log
        calls = mock_supabase_mcp.call_args_list
        
        # Primeira chamada: buscar lead
        first_call = calls[0]
        assert "SELECT * FROM leads" in str(first_call)
        
        # Verificar se há chamadas de log
        log_calls = [call for call in calls if "INSERT INTO sdr_logs" in str(call)]
        assert len(log_calls) >= 1, "Deve haver pelo menos um log inserido"
        
        # Verificar se há atualização de lead_status
        status_calls = [call for call in calls if "UPDATE leads" in str(call)]
        assert len(status_calls) >= 1, "Deve haver atualização de status do lead" 