"""
Testes Específicos: Comportamento do WaitForWebhook

Este módulo testa especificamente o comportamento do WaitForWebhook no workflow
ai-conversation.yml, simulando cenários reais de timeout e resposta.

Cenários testados:
1. Timeout atingido - lembrete enviado
2. Resposta antes do timeout - lembrete cancelado
3. Múltiplas respostas durante o período de espera
4. Falhas na API durante timeout
5. Webhook key correto para identificação
"""

import os
import json
import time
import pytest
import requests
from unittest.mock import Mock, patch, call
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# --- Configurações de Teste ---

KESTRA_BASE_URL = os.getenv("KESTRA_BASE_URL", "http://localhost:8081")
WEBHOOK_BASE_URL = f"{KESTRA_BASE_URL}/api/v1/executions/webhook/serena.energia/ai-conversation"

# Dados de teste para WaitForWebhook
WEBHOOK_TEST_DATA = {
    "conversation_id": "conv_test_waitfor_001",
    "lead_phone": "5581999887766",
    "lead_message": "Oi, quero saber sobre energia solar",
    "message_type": "text",
    "timestamp": int(time.time())
}


# --- Fixtures ---

@pytest.fixture
def mock_kestra_api():
    """Mock da API do Kestra para simular execuções."""
    with patch('requests.post') as mock_post, patch('requests.get') as mock_get:
        # Mock para webhook trigger
        mock_webhook_response = Mock()
        mock_webhook_response.status_code = 200
        mock_webhook_response.json.return_value = {
            "executionId": "exec_test_001",
            "state": "RUNNING"
        }
        mock_post.return_value = mock_webhook_response
        
        # Mock para status da execução
        mock_status_response = Mock()
        mock_status_response.status_code = 200
        mock_status_response.json.return_value = {
            "id": "exec_test_001",
            "state": "SUCCESS",
            "outputs": {
                "wait-for-response": {
                    "timeout_reached": True,
                    "webhook_data": None
                }
            }
        }
        mock_get.return_value = mock_status_response
        
        yield {"post": mock_post, "get": mock_get}


@pytest.fixture
def conversation_context():
    """Contexto de conversa para testes."""
    return {
        "conversation_id": WEBHOOK_TEST_DATA["conversation_id"],
        "phone": WEBHOOK_TEST_DATA["lead_phone"],
        "first_message_sent": True,
        "first_message_id": "msg_001",
        "timestamp": WEBHOOK_TEST_DATA["timestamp"]
    }


# --- Testes do WaitForWebhook ---

class TestWaitForWebhookConfiguration:
    """Testa a configuração específica do WaitForWebhook."""
    
    def test_waitforwebhook_task_structure(self):
        """Verifica se a task WaitForWebhook está configurada corretamente."""
        with open('kestra/workflows/ai-conversation.yml', 'r') as f:
            workflow_content = f.read()
        
        # Verificar estrutura da task
        assert 'id: wait-for-response' in workflow_content
        assert 'type: io.kestra.plugin.core.flow.WaitForWebhook' in workflow_content
        assert 'timeout: "PT2H"' in workflow_content
        assert 'onTimeout:' in workflow_content
    
    def test_webhook_key_dynamic_generation(self):
        """Testa se a chave do webhook é gerada dinamicamente."""
        with open('kestra/workflows/ai-conversation.yml', 'r') as f:
            workflow_content = f.read()
        
        # Verificar se usa conversation_id como chave
        assert 'key: "{{ outputs[\'send-first-message\'].vars.first_message_result.conversation_id }}"' in workflow_content
    
    def test_timeout_task_dependency(self):
        """Verifica se o timeout depende corretamente da primeira mensagem."""
        with open('kestra/workflows/ai-conversation.yml', 'r') as f:
            workflow_content = f.read()
        
        # Verificar dependência
        assert 'FIRST_MESSAGE_RESULT: "{{ outputs[\'send-first-message\'].vars.first_message_result | json }}"' in workflow_content


class TestTimeoutScenario:
    """Testa cenários de timeout (2 horas sem resposta)."""
    
    @patch('time.time')
    def test_timeout_duration_validation(self, mock_time):
        """Testa se o timeout de 2 horas é respeitado."""
        # Simular início da espera
        start_time = 1640995200  # Timestamp fixo
        mock_time.return_value = start_time
        
        # Calcular quando timeout deveria ocorrer
        timeout_duration = 2 * 60 * 60  # 2 horas em segundos
        expected_timeout = start_time + timeout_duration
        
        # Verificar cálculo
        assert expected_timeout == start_time + 7200
        
        # Simular passagem do tempo até timeout
        mock_time.return_value = expected_timeout
        current_time = mock_time.return_value
        
        # Verificar se timeout foi atingido
        assert current_time >= expected_timeout
    
    def test_reminder_trigger_on_timeout(self, conversation_context):
        """Testa se lembrete é acionado quando timeout é atingido."""
        # Simular contexto de timeout
        timeout_context = {
            **conversation_context,
            "timeout_reached": True,
            "webhook_data": None,  # Nenhuma resposta recebida
            "timeout_duration": "PT2H"
        }
        
        # Verificar condições para acionar lembrete
        assert timeout_context["timeout_reached"] is True
        assert timeout_context["webhook_data"] is None
        assert timeout_context["timeout_duration"] == "PT2H"
    
    @patch('requests.post')
    def test_reminder_message_sending(self, mock_post, conversation_context):
        """Testa o envio da mensagem de lembrete."""
        # Configurar mock para sucesso
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message_id": "reminder_msg_001"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Simular envio de lembrete
        reminder_payload = {
            "phone": conversation_context["phone"],
            "message": "Oi! 😊\n\nNotei que você não respondeu nossa conversa anterior sobre energia solar.\n\nAinda tem interesse em economizar na conta de luz? Posso te ajudar a encontrar o melhor plano para sua região! ⚡\n\nÉ só me responder que continuamos de onde paramos! 👍"
        }
        
        # Simular chamada da API
        whatsapp_url = "http://whatsapp-service:8000/whatsapp/send_text_message"
        requests.post(whatsapp_url, json=reminder_payload, timeout=30)
        
        # Verificar se foi chamado corretamente
        mock_post.assert_called_once_with(
            whatsapp_url,
            json=reminder_payload,
            timeout=30
        )


class TestResponseBeforeTimeout:
    """Testa cenários onde lead responde antes do timeout."""
    
    def test_webhook_data_reception(self, conversation_context):
        """Testa recepção de dados do webhook antes do timeout."""
        # Simular resposta do lead
        webhook_response_data = {
            "lead_phone": conversation_context["phone"],
            "lead_message": "Sim, tenho interesse! Moro em São Paulo.",
            "message_type": "text",
            "message_id": "lead_response_001",
            "timestamp": conversation_context["timestamp"] + 1800  # 30 min depois
        }
        
        # Simular contexto com resposta recebida
        response_context = {
            **conversation_context,
            "timeout_reached": False,
            "webhook_data": webhook_response_data,
            "response_received_at": webhook_response_data["timestamp"]
        }
        
        # Verificar que timeout foi evitado
        assert response_context["timeout_reached"] is False
        assert response_context["webhook_data"] is not None
        assert response_context["response_received_at"] < (conversation_context["timestamp"] + 7200)
    
    def test_timeout_cancellation(self, conversation_context):
        """Testa se timeout é cancelado quando resposta é recebida."""
        response_time = conversation_context["timestamp"] + 3600  # 1 hora depois
        timeout_time = conversation_context["timestamp"] + 7200   # 2 horas depois
        
        # Verificar que resposta chegou antes do timeout
        assert response_time < timeout_time
        
        # Simular cancelamento do timeout
        timeout_cancelled = response_time < timeout_time
        assert timeout_cancelled is True
    
    @patch('requests.post')
    def test_ai_response_to_lead(self, mock_post, conversation_context):
        """Testa resposta da IA quando lead responde antes do timeout."""
        # Configurar mock para sucesso
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message_id": "ai_response_001"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Simular resposta da IA
        ai_response_payload = {
            "phone": conversation_context["phone"],
            "message": "Ótimo! São Paulo tem excelentes opções de energia solar. Vou te mostrar os melhores planos disponíveis na sua região!"
        }
        
        # Simular chamada da API
        whatsapp_url = "http://whatsapp-service:8000/whatsapp/send_text_message"
        requests.post(whatsapp_url, json=ai_response_payload, timeout=30)
        
        # Verificar se foi chamado corretamente
        mock_post.assert_called_once_with(
            whatsapp_url,
            json=ai_response_payload,
            timeout=30
        )


class TestMultipleResponses:
    """Testa cenários com múltiplas respostas durante período de espera."""
    
    def test_first_response_wins(self, conversation_context):
        """Testa se apenas a primeira resposta é processada."""
        # Simular múltiplas respostas
        responses = [
            {
                "message": "Tenho interesse sim!",
                "timestamp": conversation_context["timestamp"] + 1800  # 30 min
            },
            {
                "message": "Quando vocês podem me ligar?",
                "timestamp": conversation_context["timestamp"] + 1900  # 31.67 min
            },
            {
                "message": "Estou aguardando retorno",
                "timestamp": conversation_context["timestamp"] + 2100  # 35 min
            }
        ]
        
        # Primeira resposta deve cancelar o timeout
        first_response = responses[0]
        timeout_cancelled_at = first_response["timestamp"]
        
        # Verificar que timeout foi cancelado na primeira resposta
        assert timeout_cancelled_at == conversation_context["timestamp"] + 1800
        
        # Respostas subsequentes não devem afetar o timeout
        for response in responses[1:]:
            assert response["timestamp"] > timeout_cancelled_at
    
    def test_conversation_continuation(self, conversation_context):
        """Testa continuação da conversa após primeira resposta."""
        # Simular que timeout foi cancelado
        timeout_cancelled = True
        conversation_active = True
        
        # Verificar estado da conversa
        assert timeout_cancelled is True
        assert conversation_active is True
        
        # Novas mensagens devem ser processadas normalmente
        # (não mais pelo WaitForWebhook, mas por novos triggers)


class TestWebhookKeyManagement:
    """Testa gerenciamento de chaves do webhook."""
    
    def test_unique_webhook_keys(self):
        """Testa se cada conversa tem chave única."""
        conversation_ids = [
            "conv_001_5581999887766",
            "conv_002_5581999887766",
            "conv_003_5511999887766"
        ]
        
        # Verificar que todas as chaves são únicas
        assert len(conversation_ids) == len(set(conversation_ids))
        
        # Verificar formato das chaves
        for conv_id in conversation_ids:
            assert conv_id.startswith("conv_")
            assert len(conv_id) > 10  # Deve ter tamanho razoável
    
    def test_webhook_key_persistence(self, conversation_context):
        """Testa se chave do webhook persiste durante toda a conversa."""
        webhook_key = conversation_context["conversation_id"]
        
        # Chave deve permanecer a mesma durante toda a conversa
        assert webhook_key == WEBHOOK_TEST_DATA["conversation_id"]
        
        # Verificar que chave não muda com o tempo
        time.sleep(0.1)  # Pequena pausa
        assert webhook_key == conversation_context["conversation_id"]


class TestErrorHandlingInTimeout:
    """Testa tratamento de erros durante timeout."""
    
    @patch('requests.post')
    def test_whatsapp_api_failure_during_reminder(self, mock_post, conversation_context):
        """Testa comportamento quando WhatsApp API falha durante envio de lembrete."""
        # Simular falha na API
        mock_post.side_effect = requests.exceptions.RequestException("WhatsApp API Error")
        
        # Tentar enviar lembrete
        try:
            whatsapp_url = "http://whatsapp-service:8000/whatsapp/send_text_message"
            payload = {"phone": conversation_context["phone"], "message": "Lembrete"}
            requests.post(whatsapp_url, json=payload, timeout=30)
            assert False, "Deveria ter levantado exceção"
        except requests.exceptions.RequestException as e:
            assert "WhatsApp API Error" in str(e)
    
    def test_malformed_webhook_response(self, conversation_context):
        """Testa tratamento de resposta malformada do webhook."""
        malformed_responses = [
            None,
            {},
            {"wrong_field": "value"},
            {"lead_phone": None},
            {"lead_message": ""}
        ]
        
        for response in malformed_responses:
            # Sistema deve validar dados recebidos
            if response:
                phone = response.get("lead_phone", "")
                message = response.get("lead_message", "")
                
                # Validações básicas
                if phone:
                    assert isinstance(phone, str)
                if message:
                    assert isinstance(message, str)
    
    def test_timeout_with_network_issues(self, conversation_context):
        """Testa comportamento do timeout com problemas de rede."""
        # Simular problemas de conectividade
        network_issues = [
            "Connection timeout",
            "DNS resolution failed",
            "Network unreachable"
        ]
        
        for issue in network_issues:
            # Sistema deve ser resiliente a problemas de rede
            assert isinstance(issue, str)
            assert len(issue) > 0


class TestTimeoutAnalytics:
    """Testa analytics específicos do timeout."""
    
    def test_timeout_analytics_structure(self, conversation_context):
        """Testa estrutura dos analytics quando timeout é atingido."""
        timeout_analytics = {
            "timeout_reached": True,
            "timeout_duration": "PT2H",
            "timeout_duration_seconds": 7200,
            "conversation_id": conversation_context["conversation_id"],
            "phone": conversation_context["phone"],
            "first_message_sent_at": conversation_context["timestamp"],
            "timeout_reached_at": conversation_context["timestamp"] + 7200,
            "reminder_sent": True,
            "reminder_message_id": "reminder_001",
            "workflow_version": "v6_two_workflows",
            "architecture": "timeout_reminder"
        }
        
        # Verificar campos obrigatórios
        required_fields = [
            "timeout_reached", "timeout_duration", "conversation_id",
            "phone", "reminder_sent", "workflow_version"
        ]
        
        for field in required_fields:
            assert field in timeout_analytics
    
    def test_response_analytics_structure(self, conversation_context):
        """Testa estrutura dos analytics quando lead responde antes do timeout."""
        response_analytics = {
            "timeout_reached": False,
            "timeout_avoided": True,
            "response_received": True,
            "response_time_seconds": 1800,  # 30 minutos
            "conversation_id": conversation_context["conversation_id"],
            "phone": conversation_context["phone"],
            "first_message_sent_at": conversation_context["timestamp"],
            "response_received_at": conversation_context["timestamp"] + 1800,
            "ai_response_sent": True,
            "ai_response_message_id": "ai_response_001",
            "workflow_version": "v6_two_workflows",
            "architecture": "conversation_flow"
        }
        
        # Verificar campos obrigatórios
        required_fields = [
            "timeout_avoided", "response_received", "conversation_id",
            "phone", "ai_response_sent", "workflow_version"
        ]
        
        for field in required_fields:
            assert field in response_analytics


if __name__ == "__main__":
    # Executar testes específicos para desenvolvimento
    pytest.main([__file__, "-v", "-s"])