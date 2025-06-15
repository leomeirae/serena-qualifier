"""
Testes para integração real com API WhatsApp Business v23.0
Testa a função send_template_message e integração com API oficial da Meta
"""

import pytest
import json
import os
from unittest.mock import patch, Mock, MagicMock
from requests.exceptions import RequestException, Timeout, ConnectionError
import sys
import logging

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from whatsapp_sender import send_template_message


@pytest.fixture
def mock_env_vars():
    """Mock das variáveis de ambiente necessárias"""
    with patch.dict(os.environ, {
        'WHATSAPP_API_TOKEN': 'EAAD_test_token_12345',
        'WHATSAPP_PHONE_NUMBER_ID': '599096403294262',
        'WHATSAPP_WELCOME_TEMPLATE_NAME': 'prosseguir_com_solicitacao'
    }):
        yield

@pytest.fixture
def mock_successful_response():
    """Mock de resposta bem-sucedida da API WhatsApp v23.0"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "messaging_product": "whatsapp",
        "contacts": [{
            "input": "5581997498268",
            "wa_id": "5581997498268"
        }],
        "messages": [{
            "id": "wamid.HBgLNTU4MTk5NzQ5ODI2OBUCABIYFjNBMDJCMDk2QzAyRjdGNzU4RTI1Qjk"
        }]
    }
    return mock_response

@pytest.fixture
def mock_error_response():
    """Mock de resposta de erro da API WhatsApp v23.0"""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
        "error": {
            "message": "Invalid phone number format",
            "type": "OAuthException",
            "code": 100,
            "fbtrace_id": "ABC123"
        }
    }
    return mock_response


class TestWhatsAppRealAPIIntegration:
    """Testes para integração real com API WhatsApp Business v23.0"""


class TestSendTemplateMessageSuccess:
    """Testes de casos de sucesso"""
    
    @patch('whatsapp_sender.requests.post')
    def test_send_template_message_success_basic(self, mock_post, mock_env_vars, mock_successful_response):
        """Teste básico de envio bem-sucedido"""
        mock_post.return_value = mock_successful_response
        
        result = send_template_message("5581997498268", "João Silva")
        
        assert result["success"] is True
        assert result["message"] == "Template message sent successfully"
        assert "wamid.HBgLNTU4MTk5NzQ5ODI2OBUCABIYFjNBMDJCMDk2QzAyRjdGNzU4RTI1Qjk" in result["message_id"]
        assert result["phone"] == "+555581997498268"
        assert result["personalized_name"] == "João"
        
        # Verificar chamada para API v23.0
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "https://graph.facebook.com/v23.0/599096403294262/messages" in call_args[1]["url"]
        assert call_args[1]["headers"]["Authorization"] == "Bearer EAAD_test_token_12345"
        assert call_args[1]["headers"]["Content-Type"] == "application/json"
    
    @patch('whatsapp_sender.requests.post')
    def test_send_template_message_phone_formatting(self, mock_post, mock_env_vars, mock_successful_response):
        """Teste de formatação automática de telefone"""
        mock_post.return_value = mock_successful_response
        
        # Teste com telefone sem código do país
        result = send_template_message("81997498268", "Maria Santos")
        
        assert result["success"] is True
        assert result["phone"] == "+5581997498268"
        
        # Verificar payload enviado
        call_args = mock_post.call_args
        payload = json.loads(call_args[1]["data"])
        assert payload["to"] == "+5581997498268"
    
    @patch('whatsapp_sender.requests.post')
    def test_send_template_message_name_personalization(self, mock_post, mock_env_vars, mock_successful_response):
        """Teste de personalização com primeiro nome"""
        mock_post.return_value = mock_successful_response
        
        result = send_template_message("+5511999887766", "Ana Carolina Silva Santos")
        
        assert result["success"] is True
        assert result["personalized_name"] == "Ana"
        
        # Verificar template personalizado no payload
        call_args = mock_post.call_args
        payload = json.loads(call_args[1]["data"])
        assert payload["template"]["components"][0]["parameters"][0]["text"] == "Ana"
    
    @patch('whatsapp_sender.requests.post')
    def test_send_template_message_correct_payload_structure(self, mock_post, mock_env_vars, mock_successful_response):
        """Teste da estrutura correta do payload para API v23.0"""
        mock_post.return_value = mock_successful_response
        
        send_template_message("+5511987654321", "Pedro")
        
        call_args = mock_post.call_args
        payload = json.loads(call_args[1]["data"])
        
        # Verificar estrutura do payload
        assert payload["messaging_product"] == "whatsapp"
        assert payload["recipient_type"] == "individual"
        assert payload["to"] == "+5511987654321"
        assert payload["type"] == "template"
        
        # Verificar template
        template = payload["template"]
        assert template["name"] == "prosseguir_com_solicitacao"
        assert template["language"]["code"] == "pt_BR"
        
        # Verificar componentes
        components = template["components"]
        assert len(components) == 1
        assert components[0]["type"] == "body"
        assert components[0]["parameters"][0]["type"] == "text"
        assert components[0]["parameters"][0]["text"] == "Pedro"


class TestSendTemplateMessageValidation:
    """Testes de validação de entrada"""
    
    def test_send_template_message_missing_phone(self, mock_env_vars):
        """Teste com telefone ausente"""
        result = send_template_message("", "João")
        
        assert result["success"] is False
        assert "Phone number is required" in result["message"]
        assert result["error_type"] == "validation_error"
    
    def test_send_template_message_missing_name(self, mock_env_vars):
        """Teste com nome ausente"""
        result = send_template_message("+5511999887766", "")
        
        assert result["success"] is False
        assert "Name is required" in result["message"]
        assert result["error_type"] == "validation_error"
    
    def test_send_template_message_invalid_phone_type(self, mock_env_vars):
        """Teste com tipo de telefone inválido"""
        result = send_template_message(None, "João")
        
        assert result["success"] is False
        assert "Phone number is required" in result["message"]
        assert result["error_type"] == "validation_error"
    
    def test_send_template_message_invalid_name_type(self, mock_env_vars):
        """Teste com tipo de nome inválido"""
        result = send_template_message("+5511999887766", None)
        
        assert result["success"] is False
        assert "Name is required" in result["message"]
        assert result["error_type"] == "validation_error"
    
    def test_send_template_message_phone_too_short(self, mock_env_vars):
        """Teste com telefone muito curto"""
        result = send_template_message("123", "João")
        
        assert result["success"] is False
        assert "Invalid Brazilian phone number format" in result["message"]
        assert result["error_type"] == "validation_error"
    
    def test_send_template_message_phone_too_long(self, mock_env_vars):
        """Teste com telefone muito longo"""
        result = send_template_message("+55119998877661234567890", "João")
        
        assert result["success"] is False
        assert "Invalid Brazilian phone number format" in result["message"]
        assert result["error_type"] == "validation_error"


class TestSendTemplateMessageEnvironmentValidation:
    """Testes de validação de variáveis de ambiente"""
    
    def test_send_template_message_missing_token(self):
        """Teste com token ausente"""
        with patch.dict(os.environ, {
            'WHATSAPP_PHONE_NUMBER_ID': '599096403294262',
            'WHATSAPP_WELCOME_TEMPLATE_NAME': 'prosseguir_com_solicitacao'
        }, clear=True):
            result = send_template_message("+5511999887766", "João")
            
            assert result["success"] is False
            assert "WHATSAPP_API_TOKEN not found" in result["error"]
            assert result["error_type"] == "configuration_error"
    
    def test_send_template_message_missing_phone_id(self):
        """Teste com phone number ID ausente"""
        with patch.dict(os.environ, {
            'WHATSAPP_API_TOKEN': 'EAAD_test_token',
            'WHATSAPP_WELCOME_TEMPLATE_NAME': 'prosseguir_com_solicitacao'
        }, clear=True):
            result = send_template_message("+5511999887766", "João")
            
            assert result["success"] is False
            assert "WHATSAPP_PHONE_NUMBER_ID not found" in result["error"]
            assert result["error_type"] == "configuration_error"
    
    def test_send_template_message_missing_template_name(self):
        """Teste com nome do template ausente"""
        with patch.dict(os.environ, {
            'WHATSAPP_API_TOKEN': 'EAAD_test_token',
            'WHATSAPP_PHONE_NUMBER_ID': '599096403294262'
        }, clear=True):
            result = send_template_message("+5511999887766", "João")
            
            assert result["success"] is False
            assert "WHATSAPP_WELCOME_TEMPLATE_NAME not found" in result["error"]
            assert result["error_type"] == "configuration_error"


class TestSendTemplateMessageAPIErrors:
    """Testes de tratamento de erros da API"""
    
    @patch('whatsapp_sender.requests.post')
    def test_send_template_message_400_bad_request(self, mock_post, mock_env_vars):
        """Teste de erro 400 - Bad Request"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {
                "message": "Invalid phone number format",
                "type": "OAuthException",
                "code": 100
            }
        }
        mock_post.return_value = mock_response
        
        result = send_template_message("+5511999887766", "João")
        
        assert result["success"] is False
        assert result["error_type"] == "api_error"
        assert result["status_code"] == 400
        assert "Invalid phone number format" in result["message"]
    
    @patch('whatsapp_sender.requests.post')
    def test_send_template_message_401_unauthorized(self, mock_post, mock_env_vars):
        """Teste de erro 401 - Unauthorized"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": {
                "message": "Invalid access token",
                "type": "OAuthException",
                "code": 190
            }
        }
        mock_post.return_value = mock_response
        
        result = send_template_message("+5511999887766", "João")
        
        assert result["success"] is False
        assert result["error_type"] == "authentication_error"
        assert result["status_code"] == 401
        assert "Invalid access token" in result["message"]
    
    @patch('whatsapp_sender.requests.post')
    def test_send_template_message_403_forbidden(self, mock_post, mock_env_vars):
        """Teste de erro 403 - Forbidden"""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {
            "error": {
                "message": "Insufficient permissions",
                "type": "OAuthException",
                "code": 200
            }
        }
        mock_post.return_value = mock_response
        
        result = send_template_message("+5511999887766", "João")
        
        assert result["success"] is False
        assert result["error_type"] == "permission_error"
        assert result["status_code"] == 403
        assert "Insufficient permissions" in result["message"]
    
    @patch('whatsapp_sender.requests.post')
    def test_send_template_message_429_rate_limit(self, mock_post, mock_env_vars):
        """Teste de erro 429 - Rate Limit"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "error": {
                "message": "Rate limit exceeded",
                "type": "OAuthException",
                "code": 613
            }
        }
        mock_post.return_value = mock_response
        
        result = send_template_message("+5511999887766", "João")
        
        assert result["success"] is False
        assert result["error_type"] == "rate_limit_error"
        assert result["status_code"] == 429
        assert "Rate limit exceeded" in result["message"]
    
    @patch('whatsapp_sender.requests.post')
    def test_send_template_message_500_server_error(self, mock_post, mock_env_vars):
        """Teste de erro 500 - Server Error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "error": {
                "message": "Internal server error",
                "type": "OAuthException",
                "code": 1
            }
        }
        mock_post.return_value = mock_response
        
        result = send_template_message("+5511999887766", "João")
        
        assert result["success"] is False
        assert result["error_type"] == "server_error"
        assert result["status_code"] == 500
        assert "Internal server error" in result["message"]


class TestSendTemplateMessageNetworkErrors:
    """Testes de tratamento de erros de rede"""
    
    @patch('whatsapp_sender.requests.post')
    def test_send_template_message_timeout_error(self, mock_post, mock_env_vars):
        """Teste de erro de timeout"""
        mock_post.side_effect = Timeout("Request timeout")
        
        result = send_template_message("+5511999887766", "João")
        
        assert result["success"] is False
        assert result["error_type"] == "timeout_error"
        assert "Request timeout" in result["message"]
    
    @patch('whatsapp_sender.requests.post')
    def test_send_template_message_connection_error(self, mock_post, mock_env_vars):
        """Teste de erro de conexão"""
        mock_post.side_effect = ConnectionError("Connection failed")
        
        result = send_template_message("+5511999887766", "João")
        
        assert result["success"] is False
        assert result["error_type"] == "connection_error"
        assert "Connection failed" in result["message"]
    
    @patch('whatsapp_sender.requests.post')
    def test_send_template_message_generic_request_exception(self, mock_post, mock_env_vars):
        """Teste de exceção genérica de request"""
        mock_post.side_effect = RequestException("Generic request error")
        
        result = send_template_message("+5511999887766", "João")
        
        assert result["success"] is False
        assert result["error_type"] == "request_error"
        assert "Generic request error" in result["message"]


class TestSendTemplateMessageLogging:
    """Testes de logging"""
    
    @patch('whatsapp_sender.requests.post')
    @patch('whatsapp_sender.logger')
    def test_send_template_message_success_logging(self, mock_logger, mock_post, mock_env_vars, mock_successful_response):
        """Teste de logging em caso de sucesso"""
        mock_post.return_value = mock_successful_response
        
        send_template_message("+5511999887766", "João")
        
        # Verificar logs de debug
        mock_logger.debug.assert_any_call("📱 Sending WhatsApp template to +555511999887766 for João")
        mock_logger.debug.assert_any_call("🔧 Using template: prosseguir_com_solicitacao")
        mock_logger.info.assert_any_call("✅ WhatsApp template sent successfully to +555511999887766")
    
    @patch('whatsapp_sender.requests.post')
    @patch('whatsapp_sender.logger')
    def test_send_template_message_error_logging(self, mock_logger, mock_post, mock_env_vars):
        """Teste de logging em caso de erro"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "Test error"}}
        mock_post.return_value = mock_response
        
        send_template_message("+5511999887766", "João")
        
        # Verificar logs de erro
        mock_logger.error.assert_any_call("❌ WhatsApp API error (400): Test error")


class TestSendTemplateMessageEdgeCases:
    """Testes de casos extremos"""
    
    @patch('whatsapp_sender.requests.post')
    def test_send_template_message_special_characters_name(self, mock_post, mock_env_vars, mock_successful_response):
        """Teste com caracteres especiais no nome"""
        mock_post.return_value = mock_successful_response
        
        result = send_template_message("+5511999887766", "José da Silva-Santos")
        
        assert result["success"] is True
        assert result["personalized_name"] == "José"
    
    @patch('whatsapp_sender.requests.post')
    def test_send_template_message_single_name(self, mock_post, mock_env_vars, mock_successful_response):
        """Teste com nome único (sem sobrenome)"""
        mock_post.return_value = mock_successful_response
        
        result = send_template_message("+5511999887766", "João")
        
        assert result["success"] is True
        assert result["personalized_name"] == "João"
    
    @patch('whatsapp_sender.requests.post')
    def test_send_template_message_phone_with_spaces(self, mock_post, mock_env_vars, mock_successful_response):
        """Teste com telefone contendo espaços"""
        mock_post.return_value = mock_successful_response
        
        result = send_template_message(" +55 11 99988-7766 ", "João")
        
        assert result["success"] is True
        assert result["phone"] == "+5511999887766"
    
    @patch('whatsapp_sender.requests.post')
    def test_send_template_message_malformed_json_response(self, mock_post, mock_env_vars):
        """Teste com resposta JSON malformada"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Invalid response"
        mock_post.return_value = mock_response
        
        result = send_template_message("+5511999887766", "João")
        
        assert result["success"] is False
        assert result["error_type"] == "response_parsing_error"
        assert "Failed to parse API response" in result["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 