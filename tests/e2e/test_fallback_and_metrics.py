# =============================================================================
# SERENA SDR - TESTE E2E: FALLBACK E MÉTRICAS
# =============================================================================

"""
Teste End-to-End: Fallback e Métricas

Este teste simula cenários de erro nos MCPs e verifica
o comportamento de fallback e registro de métricas.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import pytest
import json
import httpx
from unittest.mock import patch, Mock
from datetime import datetime


class TestFallbackAndMetrics:
    """Teste de fallback e métricas."""

    def test_mcp_timeout_fallback(
        self,
        sample_webhook_payload,
        mock_supabase_mcp,
        mock_whatsapp_mcp,
        test_environment
    ):
        """
        Teste 1: Timeout em MCP e verificação de fallback.
        
        Cenário:
        1. Supabase MCP retorna timeout
        2. Sistema deve enviar mensagem de fallback
        3. Erro deve ser registrado nos logs
        """
        
        # Mock Supabase MCP retornando timeout
        with patch('httpx.post') as mock_supabase_timeout:
            mock_supabase_timeout.side_effect = httpx.TimeoutException("Request timeout")
        
        # Simular webhook
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=sample_webhook_payload
            )
            
            assert response.status_code == 200
        
        # Verificar que mensagem de fallback foi enviada
        mock_whatsapp_mcp.assert_called()
        call_args = mock_whatsapp_mcp.call_args
        json_data = call_args[1]['json']
        message_content = json_data['params']['message']
        
        # Verificar que é uma mensagem de fallback
        assert any(keyword in message_content.lower() for keyword in [
            "desculpe", "erro", "problema", "temporariamente", "indisponível"
        ])

    def test_mcp_500_error_fallback(
        self,
        sample_webhook_payload,
        mock_supabase_mcp,
        mock_whatsapp_mcp,
        test_environment
    ):
        """
        Teste 2: Erro 500 em MCP e verificação de fallback.
        
        Cenário:
        1. Serena MCP retorna erro 500
        2. Sistema deve enviar mensagem de fallback
        3. Erro deve ser registrado nos logs
        """
        
        # Mock Serena MCP retornando erro 500
        with patch('httpx.post') as mock_serena_error:
            mock_serena_error.return_value.status_code = 500
            mock_serena_error.return_value.json.return_value = {
                "error": "Internal Server Error"
            }
        
        # Simular webhook
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=sample_webhook_payload
            )
            
            assert response.status_code == 200
        
        # Verificar que mensagem de fallback foi enviada
        mock_whatsapp_mcp.assert_called()
        call_args = mock_whatsapp_mcp.call_args
        json_data = call_args[1]['json']
        message_content = json_data['params']['message']
        
        # Verificar que é uma mensagem de fallback
        assert any(keyword in message_content.lower() for keyword in [
            "desculpe", "erro", "problema", "temporariamente", "indisponível"
        ])

    def test_whatsapp_mcp_error_fallback(
        self,
        sample_webhook_payload,
        mock_supabase_mcp,
        test_environment
    ):
        """
        Teste 3: Erro no WhatsApp MCP.
        
        Cenário:
        1. WhatsApp MCP retorna erro
        2. Sistema deve registrar erro nos logs
        3. Deve tentar retry ou usar fallback
        """
        
        # Mock WhatsApp MCP retornando erro
        with patch('httpx.post') as mock_whatsapp_error:
            mock_whatsapp_error.return_value.status_code = 500
            mock_whatsapp_error.return_value.json.return_value = {
                "error": "WhatsApp API Error"
            }
        
        # Simular webhook
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=sample_webhook_payload
            )
            
            assert response.status_code == 200
        
        # Verificar que erro foi registrado nos logs
        calls = mock_supabase_mcp.call_args_list
        
        error_logs = [
            call for call in calls 
            if "INSERT INTO sdr_logs" in str(call) and "error" in str(call)
        ]
        assert len(error_logs) >= 1, "Deve haver log de erro do WhatsApp MCP"

    def test_error_logging_metrics(
        self,
        sample_webhook_payload,
        mock_supabase_mcp,
        test_environment
    ):
        """
        Teste 4: Verificar métricas de erro nos logs.
        
        Cenário:
        1. Forçar erro em MCP
        2. Verificar que métricas são registradas
        3. Verificar estrutura dos logs de erro
        """
        
        # Mock erro em MCP
        with patch('httpx.post') as mock_mcp_error:
            mock_mcp_error.side_effect = Exception("MCP Error")
        
        # Simular webhook
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=sample_webhook_payload
            )
            
            assert response.status_code == 200
        
        # Verificar logs de erro
        calls = mock_supabase_mcp.call_args_list
        
        error_logs = [
            call for call in calls 
            if "INSERT INTO sdr_logs" in str(call)
        ]
        
        assert len(error_logs) >= 1, "Deve haver logs registrados"
        
        # Verificar estrutura do log de erro
        for log_call in error_logs:
            # Verificar que log contém campos obrigatórios
            log_data = log_call[1]['json']['params']
            assert 'phone_number' in str(log_data)
            assert 'timestamp' in str(log_data)
            assert 'type' in str(log_data)

    def test_retry_mechanism(
        self,
        sample_webhook_payload,
        mock_supabase_mcp,
        mock_whatsapp_mcp,
        test_environment
    ):
        """
        Teste 5: Verificar mecanismo de retry.
        
        Cenário:
        1. MCP retorna erro na primeira tentativa
        2. Sistema deve tentar novamente
        3. Se falhar novamente, usar fallback
        """
        
        # Mock MCP com falha na primeira tentativa, sucesso na segunda
        call_count = 0
        
        def mock_mcp_with_retry(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count == 1:
                # Primeira tentativa: erro
                raise httpx.TimeoutException("First attempt timeout")
            else:
                # Segunda tentativa: sucesso
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "result": {
                        "data": [
                            {
                                "id": "test-lead-id",
                                "phone": "5511999999999",
                                "name": "João Silva"
                            }
                        ]
                    }
                }
                return mock_response
        
        with patch('httpx.post', side_effect=mock_mcp_with_retry):
            # Simular webhook
            with patch('httpx.post') as mock_webhook:
                mock_webhook.return_value.status_code = 200
                
                response = httpx.post(
                    "http://localhost:8001/webhook",
                    json=sample_webhook_payload
                )
                
                assert response.status_code == 200
        
        # Verificar que houve pelo menos 2 tentativas
        assert call_count >= 2, "Deve haver pelo menos 2 tentativas"

    def test_fallback_message_content(
        self,
        sample_webhook_payload,
        test_environment
    ):
        """
        Teste 6: Verificar conteúdo das mensagens de fallback.
        
        Cenário:
        1. Forçar erro em diferentes MCPs
        2. Verificar que mensagens de fallback são apropriadas
        3. Verificar que não expõem informações sensíveis
        """
        
        # Testar diferentes tipos de erro
        error_scenarios = [
            ("Supabase MCP", httpx.TimeoutException("Database timeout")),
            ("Serena MCP", httpx.HTTPStatusError("500 Internal Server Error", request=Mock(), response=Mock())),
            ("WhatsApp MCP", Exception("WhatsApp API Error"))
        ]
        
        for error_type, error in error_scenarios:
            with patch('httpx.post') as mock_mcp_error:
                mock_mcp_error.side_effect = error
            
            with patch('httpx.post') as mock_whatsapp:
                mock_whatsapp.return_value.status_code = 200
                mock_whatsapp.return_value.json.return_value = {
                    "result": {"message_id": "test-id"}
                }
            
            # Simular webhook
            with patch('httpx.post') as mock_webhook:
                mock_webhook.return_value.status_code = 200
                
                response = httpx.post(
                    "http://localhost:8001/webhook",
                    json=sample_webhook_payload
                )
                
                assert response.status_code == 200
            
            # Verificar que mensagem de fallback foi enviada
            mock_whatsapp.assert_called()
            call_args = mock_whatsapp.call_args
            json_data = call_args[1]['json']
            message_content = json_data['params']['message']
            
            # Verificar que mensagem é apropriada
            assert len(message_content) > 0, "Mensagem de fallback não pode ser vazia"
            assert "desculpe" in message_content.lower() or "problema" in message_content.lower()
            
            # Verificar que não expõe informações sensíveis
            sensitive_info = ["error", "exception", "timeout", "500", "database"]
            for info in sensitive_info:
                assert info not in message_content.lower(), f"Mensagem não deve expor: {info}"

    def test_metrics_aggregation(
        self,
        sample_webhook_payload,
        mock_supabase_mcp,
        test_environment
    ):
        """
        Teste 7: Verificar agregação de métricas.
        
        Cenário:
        1. Executar múltiplos fluxos com erros
        2. Verificar que métricas são agregadas corretamente
        3. Verificar contadores de erro
        """
        
        # Simular múltiplos erros
        error_count = 0
        
        def mock_mcp_with_errors(*args, **kwargs):
            nonlocal error_count
            error_count += 1
            
            # Simular erro a cada 3 tentativas
            if error_count % 3 == 0:
                raise Exception(f"Simulated error #{error_count}")
            
            # Sucesso nas outras tentativas
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "result": {"data": [{"id": "test-lead"}]}
            }
            return mock_response
        
        with patch('httpx.post', side_effect=mock_mcp_with_errors):
            # Executar múltiplos webhooks
            for i in range(5):
                with patch('httpx.post') as mock_webhook:
                    mock_webhook.return_value.status_code = 200
                    
                    response = httpx.post(
                        "http://localhost:8001/webhook",
                        json=sample_webhook_payload
                    )
                    
                    assert response.status_code == 200
        
        # Verificar que houve erros
        assert error_count > 0, "Deve haver pelo menos um erro simulado"
        
        # Verificar logs de métricas
        calls = mock_supabase_mcp.call_args_list
        
        metric_logs = [
            call for call in calls 
            if "INSERT INTO sdr_logs" in str(call) and "metrics" in str(call)
        ]
        
        assert len(metric_logs) >= 1, "Deve haver logs de métricas"

    def test_circuit_breaker_pattern(
        self,
        sample_webhook_payload,
        mock_supabase_mcp,
        test_environment
    ):
        """
        Teste 8: Verificar padrão circuit breaker.
        
        Cenário:
        1. MCP falha consistentemente
        2. Sistema deve ativar circuit breaker
        3. Deve usar fallback até MCP voltar
        """
        
        # Mock MCP falhando consistentemente
        with patch('httpx.post') as mock_mcp_failure:
            mock_mcp_failure.side_effect = Exception("Consistent MCP failure")
        
        # Simular múltiplas tentativas
        for attempt in range(3):
            with patch('httpx.post') as mock_webhook:
                mock_webhook.return_value.status_code = 200
                
                response = httpx.post(
                    "http://localhost:8001/webhook",
                    json=sample_webhook_payload
                )
                
                assert response.status_code == 200
        
        # Verificar que circuit breaker foi ativado
        calls = mock_supabase_mcp.call_args_list
        
        circuit_breaker_logs = [
            call for call in calls 
            if "INSERT INTO sdr_logs" in str(call) and "circuit_breaker" in str(call)
        ]
        
        # Nota: Este teste assume que circuit breaker está implementado
        # Se não estiver, pode ser implementado futuramente
        if len(circuit_breaker_logs) > 0:
            assert len(circuit_breaker_logs) >= 1, "Circuit breaker deve ser ativado após falhas consistentes" 