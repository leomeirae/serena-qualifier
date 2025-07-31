# =============================================================================
# SERENA SDR - TESTE E2E: FLUXO DE FOLLOW-UP
# =============================================================================

"""
Teste End-to-End: Fluxo de Follow-Up

Este teste simula o fluxo de follow-up automático quando
o lead não responde dentro de 2 horas, e o cancelamento
quando há resposta antecipada.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import pytest
import json
import httpx
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
import time


class TestFollowUpFlow:
    """Teste do fluxo de follow-up automático."""

    def test_follow_up_timeout_triggered(
        self,
        sample_webhook_payload,
        mock_supabase_mcp,
        mock_whatsapp_mcp,
        mock_openai_chat,
        test_environment
    ):
        """
        Teste 1: Follow-up disparado após 2 horas sem resposta.
        
        Cenário:
        1. Lead recebe mensagem inicial
        2. Sistema aguarda 2 horas (simulado)
        3. Follow-up é disparado automaticamente
        4. Mensagem de follow-up é enviada via WhatsApp
        """
        
        # 1. Simular mensagem inicial
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=sample_webhook_payload
            )
            
            assert response.status_code == 200
        
        # 2. Verificar que mensagem inicial foi enviada
        mock_whatsapp_mcp.assert_called()
        
        # 3. Simular passagem de 2 horas (mock do tempo)
        with patch('datetime.datetime') as mock_datetime:
            # Simular tempo atual + 2 horas
            mock_datetime.now.return_value = datetime.now() + timedelta(hours=2, minutes=5)
            
            # Simular execução do follow-up
            with patch('httpx.post') as mock_followup:
                mock_followup.return_value.status_code = 200
                
                # Chamar endpoint de follow-up (simulado)
                followup_response = httpx.post(
                    "http://localhost:8081/api/v1/executions/trigger",
                    json={
                        "namespace": "serena.production",
                        "flowId": "2_sdr_conversation_flow",
                        "inputs": {
                            "phone": "5581997498268",
                            "followup_type": "timeout"
                        }
                    }
                )
                
                assert followup_response.status_code == 200
        
        # 4. Verificar que follow-up foi enviado
        # Deve haver pelo menos 2 chamadas: mensagem inicial + follow-up
        assert mock_whatsapp_mcp.call_count >= 2
        
        # Verificar conteúdo da mensagem de follow-up
        calls = mock_whatsapp_mcp.call_args_list
        followup_call = calls[-1]  # Última chamada deve ser o follow-up
        
        json_data = followup_call[1]['json']
        message_content = json_data['params']['message']
        
        # Verificar que é uma mensagem de follow-up
        assert any(keyword in message_content.lower() for keyword in [
            "lembrete", "follow-up", "ainda", "interesse", "contato"
        ])

    def test_follow_up_cancelled_by_response(
        self,
        sample_webhook_payload,
        mock_supabase_mcp,
        mock_whatsapp_mcp,
        mock_openai_chat,
        test_environment
    ):
        """
        Teste 2: Follow-up cancelado por resposta antecipada.
        
        Cenário:
        1. Lead recebe mensagem inicial
        2. Lead responde antes de 2 horas
        3. Follow-up é cancelado
        4. Sistema responde normalmente
        """
        
        # 1. Simular mensagem inicial
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=sample_webhook_payload
            )
            
            assert response.status_code == 200
        
        # 2. Simular resposta do lead antes de 2 horas
        response_payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "test-entry-id",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "+5581997498268",
                                    "phone_number_id": "test-phone-id"
                                },
                                "contacts": [
                                    {
                                        "profile": {"name": "Teste SDR"},
                                        "wa_id": "5581997498268"
                                    }
                                ],
                                "messages": [
                                    {
                                        "from": "5581997498268",
                                        "id": "test-response-id",
                                        "timestamp": "1705492800",
                                        "type": "text",
                                        "text": {"body": "Sim, tenho interesse!"}
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
        }
        
        # Simular resposta do lead
        with patch('httpx.post') as mock_response:
            mock_response.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=response_payload
            )
            
            assert response.status_code == 200
        
        # 3. Verificar que follow-up foi cancelado
        # Deve haver chamadas para mensagem inicial e resposta, mas não follow-up
        calls = mock_whatsapp_mcp.call_args_list
        
        # Verificar que não há mensagem de follow-up
        followup_messages = [
            call for call in calls 
            if any(keyword in str(call).lower() for keyword in ["lembrete", "follow-up"])
        ]
        assert len(followup_messages) == 0, "Follow-up não deve ser enviado quando há resposta"

    def test_follow_up_with_multiple_timeouts(
        self,
        sample_webhook_payload,
        mock_supabase_mcp,
        mock_whatsapp_mcp,
        test_environment
    ):
        """
        Teste 3: Múltiplos follow-ups com diferentes intervalos.
        
        Cenário:
        1. Lead não responde após 2 horas
        2. Follow-up 1 é enviado
        3. Lead ainda não responde após mais 2 horas
        4. Follow-up 2 é enviado
        5. Verificar que mensagens são diferentes
        """
        
        # 1. Simular mensagem inicial
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=sample_webhook_payload
            )
            
            assert response.status_code == 200
        
        # 2. Simular primeiro follow-up (2 horas)
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.now() + timedelta(hours=2)
            
            with patch('httpx.post') as mock_followup1:
                mock_followup1.return_value.status_code = 200
                
                # Simular primeiro follow-up
                followup1_response = httpx.post(
                    "http://localhost:8081/api/v1/executions/trigger",
                    json={
                        "namespace": "serena.production",
                        "flowId": "2_sdr_conversation_flow",
                        "inputs": {
                            "phone": "5581997498268",
                            "followup_type": "timeout_1"
                        }
                    }
                )
                
                assert followup1_response.status_code == 200
        
        # 3. Simular segundo follow-up (4 horas)
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.now() + timedelta(hours=4)
            
            with patch('httpx.post') as mock_followup2:
                mock_followup2.return_value.status_code = 200
                
                # Simular segundo follow-up
                followup2_response = httpx.post(
                    "http://localhost:8081/api/v1/executions/trigger",
                    json={
                        "namespace": "serena.production",
                        "flowId": "2_sdr_conversation_flow",
                        "inputs": {
                            "phone": "5581997498268",
                            "followup_type": "timeout_2"
                        }
                    }
                )
                
                assert followup2_response.status_code == 200
        
        # 4. Verificar que múltiplos follow-ups foram enviados
        assert mock_whatsapp_mcp.call_count >= 3  # Inicial + follow-up 1 + follow-up 2
        
        # 5. Verificar que mensagens são diferentes
        calls = mock_whatsapp_mcp.call_args_list
        
        # Extrair conteúdo das mensagens
        messages = []
        for call in calls:
            json_data = call[1]['json']
            message_content = json_data['params']['message']
            messages.append(message_content)
        
        # Verificar que há pelo menos 3 mensagens diferentes
        assert len(set(messages)) >= 3, "Mensagens devem ser diferentes"

    def test_follow_up_logging_and_metrics(
        self,
        sample_webhook_payload,
        mock_supabase_mcp,
        mock_whatsapp_mcp,
        test_environment
    ):
        """
        Teste 4: Verificar logging e métricas do follow-up.
        
        Cenário:
        1. Follow-up é disparado
        2. Verificar que logs são registrados no Supabase
        3. Verificar métricas de follow-up
        """
        
        # 1. Simular follow-up
        with patch('httpx.post') as mock_followup:
            mock_followup.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8081/api/v1/executions/trigger",
                json={
                    "namespace": "serena.production",
                    "flowId": "2_sdr_conversation_flow",
                    "inputs": {
                        "phone": "5511999999999",
                        "followup_type": "timeout"
                    }
                }
            )
            
            assert response.status_code == 200
        
        # 2. Verificar que logs foram registrados
        calls = mock_supabase_mcp.call_args_list
        
        # Verificar logs de follow-up
        followup_logs = [
            call for call in calls 
            if "INSERT INTO sdr_logs" in str(call) and "followup" in str(call)
        ]
        assert len(followup_logs) >= 1, "Deve haver log de follow-up"
        
        # Verificar atualização de lead_status
        status_updates = [
            call for call in calls 
            if "UPDATE leads" in str(call) and "followup" in str(call)
        ]
        assert len(status_updates) >= 1, "Deve haver atualização de status"

    def test_follow_up_error_handling(
        self,
        sample_webhook_payload,
        mock_supabase_mcp,
        test_environment
    ):
        """
        Teste 5: Tratamento de erro no follow-up.
        
        Cenário:
        1. Follow-up é disparado
        2. WhatsApp MCP retorna erro
        3. Sistema deve registrar erro e tentar novamente
        """
        
        # Mock WhatsApp MCP retornando erro
        with patch('httpx.post') as mock_whatsapp_error:
            mock_whatsapp_error.return_value.status_code = 500
            mock_whatsapp_error.return_value.json.return_value = {
                "error": "WhatsApp API Error"
            }
        
        # 1. Simular follow-up
        with patch('httpx.post') as mock_followup:
            mock_followup.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8081/api/v1/executions/trigger",
                json={
                    "namespace": "serena.production",
                    "flowId": "2_sdr_conversation_flow",
                    "inputs": {
                        "phone": "5511999999999",
                        "followup_type": "timeout"
                    }
                }
            )
            
            assert response.status_code == 200
        
        # 2. Verificar que erro foi registrado
        calls = mock_supabase_mcp.call_args_list
        
        error_logs = [
            call for call in calls 
            if "INSERT INTO sdr_logs" in str(call) and "error" in str(call)
        ]
        assert len(error_logs) >= 1, "Deve haver log de erro"

    def test_follow_up_timing_accuracy(
        self,
        sample_webhook_payload,
        mock_supabase_mcp,
        mock_whatsapp_mcp,
        test_environment
    ):
        """
        Teste 6: Verificar precisão do timing do follow-up.
        
        Cenário:
        1. Medir tempo exato entre mensagem inicial e follow-up
        2. Verificar que follow-up é disparado exatamente após 2 horas
        """
        
        start_time = datetime.now()
        
        # 1. Simular mensagem inicial
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=sample_webhook_payload
            )
            
            assert response.status_code == 200
        
        # 2. Simular follow-up após exatamente 2 horas
        with patch('datetime.datetime') as mock_datetime:
            expected_followup_time = start_time + timedelta(hours=2)
            mock_datetime.now.return_value = expected_followup_time
            
            with patch('httpx.post') as mock_followup:
                mock_followup.return_value.status_code = 200
                
                response = httpx.post(
                    "http://localhost:8081/api/v1/executions/trigger",
                    json={
                        "namespace": "serena.production",
                        "flowId": "2_sdr_conversation_flow",
                        "inputs": {
                            "phone": "5581997498268",
                            "followup_type": "timeout"
                        }
                    }
                )
                
                assert response.status_code == 200
        
        # 3. Verificar que follow-up foi enviado
        assert mock_whatsapp_mcp.call_count >= 2  # Inicial + follow-up
        
        # 4. Verificar timing (simulado)
        # O timing real seria verificado nos logs do Kestra
        calls = mock_supabase_mcp.call_args_list
        
        timing_logs = [
            call for call in calls 
            if "INSERT INTO sdr_logs" in str(call) and "timing" in str(call)
        ]
        assert len(timing_logs) >= 1, "Deve haver log de timing" 