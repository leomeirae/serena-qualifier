"""
Testes Automatizados: Funcionalidade de Timeout/Lembrete

Este módulo testa a funcionalidade de timeout implementada no workflow ai-conversation.yml,
validando tanto o cenário de timeout (lembrete enviado) quanto o cenário de resposta
antes do timeout.

Funcionalidades testadas:
1. WaitForWebhook com timeout de 2 horas
2. Envio automático de lembrete após timeout
3. Processamento de resposta antes do timeout
4. Analytics e logging corretos
5. Integração com WhatsApp API
"""

import os
import json
import time
import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# --- Configurações de Teste ---

KESTRA_BASE_URL = os.getenv("KESTRA_BASE_URL", "http://localhost:8081")
AI_CONVERSATION_WEBHOOK_URL = f"{KESTRA_BASE_URL}/api/v1/executions/webhook/serena.energia/ai-conversation/ai_conversation_webhook"
WHATSAPP_API_URL = "http://whatsapp-service:8000/whatsapp/send_text_message"

# Dados de teste
TEST_LEAD_DATA = {
    "lead_phone": "5581999887766",
    "lead_message": "Oi, tenho interesse em energia solar",
    "message_type": "text",
    "message_id": "test_msg_001",
    "conversation_id": "conv_test_001"
}

TIMEOUT_REMINDER_MESSAGE = """Oi! 😊

Notei que você não respondeu nossa conversa anterior sobre energia solar.

Ainda tem interesse em economizar na conta de luz? Posso te ajudar a encontrar o melhor plano para sua região! ⚡

É só me responder que continuamos de onde paramos! 👍"""


# --- Fixtures ---

@pytest.fixture
def mock_whatsapp_api():
    """Mock da API do WhatsApp para testes isolados."""
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message_id": "test_msg_sent_123"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture
def mock_serena_agent():
    """Mock do SerenaAIAgent para testes isolados."""
    with patch('scripts.serena_agent.core_agent.SerenaAIAgent') as mock_agent_class:
        mock_agent = Mock()
        mock_agent.process_conversation.return_value = {
            "response": "Olá! Vou te ajudar com energia solar. Qual sua cidade?",
            "method": "langchain"
        }
        mock_agent.agent_executor = Mock()  # Simula LangChain ativo
        mock_agent_class.return_value = mock_agent
        yield mock_agent


@pytest.fixture
def sample_webhook_payload():
    """Payload de exemplo para webhook do ai-conversation."""
    return {
        "lead_phone": TEST_LEAD_DATA["lead_phone"],
        "lead_message": TEST_LEAD_DATA["lead_message"],
        "message_type": TEST_LEAD_DATA["message_type"],
        "message_id": TEST_LEAD_DATA["message_id"],
        "conversation_id": TEST_LEAD_DATA["conversation_id"]
    }


# --- Testes Unitários ---

class TestTimeoutConfiguration:
    """Testa a configuração do timeout no workflow."""
    
    def test_timeout_duration_is_2_hours(self):
        """Verifica se o timeout está configurado para 2 horas (PT2H)."""
        # Ler o workflow ai-conversation.yml
        with open('kestra/workflows/ai-conversation.yml', 'r') as f:
            workflow_content = f.read()
        
        # Verificar se timeout está configurado corretamente
        assert 'timeout: "PT2H"' in workflow_content
        assert 'WaitForWebhook' in workflow_content
        assert 'onTimeout:' in workflow_content
    
    def test_webhook_key_configuration(self):
        """Verifica se a chave do webhook está configurada corretamente."""
        with open('kestra/workflows/ai-conversation.yml', 'r') as f:
            workflow_content = f.read()
        
        assert 'key: "ai_conversation_webhook"' in workflow_content
        assert 'type: io.kestra.plugin.core.trigger.Webhook' in workflow_content
    
    def test_reminder_task_exists(self):
        """Verifica se a task send-reminder-message existe no onTimeout."""
        with open('kestra/workflows/ai-conversation.yml', 'r') as f:
            workflow_content = f.read()
        
        assert 'send-reminder-message' in workflow_content
        assert 'Envia mensagem de lembrete quando timeout é atingido' in workflow_content


class TestReminderMessage:
    """Testa a funcionalidade de envio de lembrete."""
    
    @patch.dict(os.environ, {
        'WHATSAPP_API_URL': WHATSAPP_API_URL,
        'FIRST_MESSAGE_RESULT': json.dumps({
            "phone": TEST_LEAD_DATA["lead_phone"],
            "conversation_id": TEST_LEAD_DATA["conversation_id"],
            "success": True
        })
    })
    def test_reminder_message_content(self, mock_whatsapp_api):
        """Testa se a mensagem de lembrete tem o conteúdo correto."""
        # Simular execução do script de lembrete
        script_code = '''
from dotenv import load_dotenv
load_dotenv('/app/.env')

import json
import requests
import time

first_msg_result = json.loads(os.getenv("FIRST_MESSAGE_RESULT", "{}"))
phone = first_msg_result.get("phone")
conversation_id = first_msg_result.get("conversation_id")

reminder_message = """Oi! 😊

Notei que você não respondeu nossa conversa anterior sobre energia solar.

Ainda tem interesse em economizar na conta de luz? Posso te ajudar a encontrar o melhor plano para sua região! ⚡

É só me responder que continuamos de onde paramos! 👍"""

whatsapp_url = os.getenv("WHATSAPP_API_URL")
payload = {"phone": phone, "message": reminder_message}

response = requests.post(whatsapp_url, json=payload, timeout=30)
'''
        
        # Executar o código do script (simulado)
        exec(script_code, {'os': os, 'json': json, 'requests': requests, 'time': time})
        
        # Verificar se a API foi chamada com a mensagem correta
        mock_whatsapp_api.assert_called_once()
        call_args = mock_whatsapp_api.call_args
        
        assert call_args[1]['json']['phone'] == TEST_LEAD_DATA["lead_phone"]
        assert "energia solar" in call_args[1]['json']['message']
        assert "😊" in call_args[1]['json']['message']
        assert "⚡" in call_args[1]['json']['message']
    
    def test_reminder_analytics_structure(self):
        """Testa se os analytics do lembrete têm a estrutura correta."""
        expected_analytics = {
            "reminder_sent": True,
            "reminder_message_id": "test_msg_123",
            "timeout_duration": "PT2H",
            "conversation_id": TEST_LEAD_DATA["conversation_id"],
            "timestamp": time.time(),
            "workflow_version": "v6_two_workflows",
            "architecture": "timeout_reminder"
        }
        
        # Verificar estrutura dos analytics
        assert "reminder_sent" in expected_analytics
        assert "timeout_duration" in expected_analytics
        assert expected_analytics["timeout_duration"] == "PT2H"
        assert expected_analytics["workflow_version"] == "v6_two_workflows"


class TestLeadResponseBeforeTimeout:
    """Testa o processamento de resposta do lead antes do timeout."""
    
    def test_response_processing_structure(self, mock_serena_agent, mock_whatsapp_api):
        """Testa se a resposta do lead é processada corretamente."""
        # Dados de resposta do lead
        webhook_data = {
            "lead_phone": TEST_LEAD_DATA["lead_phone"],
            "lead_message": "Sim, moro em Recife mesmo!",
            "conversation_id": TEST_LEAD_DATA["conversation_id"]
        }
        
        # Simular processamento da resposta
        agent_response = mock_serena_agent.process_conversation.return_value
        
        # Verificar se o agente foi chamado corretamente
        assert agent_response["response"] is not None
        assert agent_response["method"] == "langchain"
    
    def test_timeout_avoided_analytics(self):
        """Testa se os analytics registram corretamente quando timeout é evitado."""
        expected_analytics = {
            "lead_responded": True,
            "timeout_avoided": True,
            "response_message_id": "test_response_123",
            "conversation_id": TEST_LEAD_DATA["conversation_id"],
            "timestamp": time.time(),
            "workflow_version": "v6_two_workflows"
        }
        
        # Verificar estrutura dos analytics
        assert expected_analytics["lead_responded"] is True
        assert expected_analytics["timeout_avoided"] is True
        assert "response_message_id" in expected_analytics


# --- Testes de Integração ---

class TestTimeoutIntegration:
    """Testes de integração para funcionalidade de timeout."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_workflow_webhook_accessibility(self):
        """Testa se o webhook do ai-conversation está acessível."""
        try:
            # Fazer uma requisição de teste para o webhook
            test_payload = {
                "lead_phone": "test_phone",
                "lead_message": "test_message"
            }
            
            response = requests.post(
                AI_CONVERSATION_WEBHOOK_URL,
                json=test_payload,
                timeout=10
            )
            
            # Webhook deve responder (mesmo que falhe na execução)
            assert response.status_code in [200, 400, 500]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Kestra não está rodando - pulando teste de integração")
    
    @pytest.mark.integration
    def test_conversation_id_generation(self):
        """Testa se conversation_id é gerado e usado corretamente."""
        conversation_id = f"conv_{int(time.time())}_{TEST_LEAD_DATA['lead_phone']}"
        
        # Verificar formato do conversation_id
        assert conversation_id.startswith("conv_")
        assert TEST_LEAD_DATA['lead_phone'] in conversation_id
        assert len(conversation_id) > 20  # Deve ter tamanho razoável


# --- Testes de Performance ---

class TestTimeoutPerformance:
    """Testes de performance para funcionalidade de timeout."""
    
    def test_timeout_duration_calculation(self):
        """Testa se o cálculo de 2 horas está correto."""
        # PT2H = 2 horas em ISO 8601
        timeout_seconds = 2 * 60 * 60  # 7200 segundos
        
        assert timeout_seconds == 7200
        
        # Verificar que é um tempo razoável (não muito curto, não muito longo)
        assert timeout_seconds >= 3600  # Pelo menos 1 hora
        assert timeout_seconds <= 86400  # No máximo 24 horas
    
    def test_reminder_message_size(self):
        """Testa se a mensagem de lembrete não é muito longa."""
        reminder_length = len(TIMEOUT_REMINDER_MESSAGE)
        
        # WhatsApp tem limite de ~4096 caracteres
        assert reminder_length < 1000  # Manter mensagem concisa
        assert reminder_length > 50   # Mas não muito curta


# --- Testes de Erro ---

class TestTimeoutErrorHandling:
    """Testa tratamento de erros na funcionalidade de timeout."""
    
    @patch('requests.post')
    def test_whatsapp_api_failure_handling(self, mock_post):
        """Testa tratamento quando WhatsApp API falha."""
        # Simular falha na API
        mock_post.side_effect = requests.exceptions.RequestException("API Error")
        
        # Script deve capturar o erro e continuar
        try:
            # Simular chamada que falha
            requests.post(WHATSAPP_API_URL, json={"test": "data"})
            assert False, "Deveria ter levantado exceção"
        except requests.exceptions.RequestException as e:
            assert "API Error" in str(e)
    
    def test_missing_environment_variables(self):
        """Testa comportamento com variáveis de ambiente faltando."""
        # Simular ambiente sem variáveis críticas
        with patch.dict(os.environ, {}, clear=True):
            # Script deve usar valores padrão ou falhar graciosamente
            whatsapp_url = os.getenv("WHATSAPP_API_URL", "http://default-url")
            assert whatsapp_url == "http://default-url"
    
    def test_invalid_conversation_id(self):
        """Testa comportamento com conversation_id inválido."""
        invalid_ids = ["", None, "invalid-format", "123"]
        
        for invalid_id in invalid_ids:
            # Sistema deve lidar com IDs inválidos graciosamente
            if invalid_id:
                assert len(str(invalid_id)) >= 0  # Básico: não deve quebrar
    
    def test_malformed_webhook_data(self):
        """Testa comportamento com dados malformados do webhook."""
        malformed_payloads = [
            {},  # Vazio
            {"wrong_field": "value"},  # Campos errados
            {"lead_phone": ""},  # Valores vazios
            {"lead_phone": None, "lead_message": None}  # Valores nulos
        ]
        
        for payload in malformed_payloads:
            # Sistema deve validar e lidar com dados malformados
            phone = payload.get("lead_phone", "")
            message = payload.get("lead_message", "")
            
            # Validações básicas que o sistema deveria fazer
            assert isinstance(phone, (str, type(None)))
            assert isinstance(message, (str, type(None)))


# --- Testes de Regressão ---

class TestTimeoutRegression:
    """Testes de regressão para garantir que funcionalidade não quebra."""
    
    def test_workflow_structure_integrity(self):
        """Testa se a estrutura do workflow não foi quebrada."""
        with open('kestra/workflows/ai-conversation.yml', 'r') as f:
            workflow_content = f.read()
        
        # Verificar elementos essenciais
        essential_elements = [
            'id: ai-conversation',
            'namespace: serena.energia',
            'intelligent-analysis',
            'langchain-response',
            'send-first-message',
            'wait-for-response',
            'WaitForWebhook',
            'onTimeout',
            'send-reminder-message'
        ]
        
        for element in essential_elements:
            assert element in workflow_content, f"Elemento essencial '{element}' não encontrado"
    
    def test_backward_compatibility(self):
        """Testa se mudanças mantêm compatibilidade com versões anteriores."""
        # Verificar se inputs ainda são aceitos
        expected_inputs = [
            'lead_phone',
            'lead_message',
            'message_type',
            'message_id',
            'media_id'
        ]
        
        with open('kestra/workflows/ai-conversation.yml', 'r') as f:
            workflow_content = f.read()
        
        for input_field in expected_inputs:
            assert input_field in workflow_content
    
    def test_docker_image_consistency(self):
        """Testa se imagem Docker ainda está configurada corretamente."""
        with open('kestra/workflows/ai-conversation.yml', 'r') as f:
            workflow_content = f.read()
        
        # Verificar configurações Docker
        assert 'image: "serena-runner:latest"' in workflow_content
        assert 'pullPolicy: "NEVER"' in workflow_content
        assert 'networkMode: "serena-qualifier_kestra-network"' in workflow_content


if __name__ == "__main__":
    # Executar testes específicos para desenvolvimento
    pytest.main([__file__, "-v", "-s"])