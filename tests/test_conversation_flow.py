#!/usr/bin/env python3
"""
Testes de Integração para o Fluxo Completo de Conversação

Este arquivo testa a integração entre todos os módulos refatorados:
- AIConversationHandler (orquestrador)
- LocationExtractor
- VisionProcessor  
- ConversationContext

Author: Serena-Coder AI Agent
Version: 1.0.0 - Refatoração para modularização
Created: 2025-01-17
"""

import pytest
import unittest.mock as mock
from unittest.mock import MagicMock, patch
import sys
import os

# Adicionar o diretório scripts ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from ai_conversation_handler import AIConversationHandler


class TestAIConversationHandlerInitialization:
    """Testes para inicialização do orquestrador."""
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_openai_key',
        'WHATSAPP_API_TOKEN': 'test_whatsapp_token',
        'WHATSAPP_PHONE_NUMBER_ID': 'test_phone_id',
        'SERENA_API_TOKEN': 'test_serena_token'
    })
    @patch('ai_conversation_handler.OpenAI')
    @patch('ai_conversation_handler.SerenaAPI')
    def test_initialization_success(self, mock_serena_api, mock_openai):
        """Testa inicialização bem-sucedida do handler."""
        # Mock das dependências
        mock_openai.return_value = MagicMock()
        mock_serena_api.return_value = MagicMock()
        
        handler = AIConversationHandler()
        
        # Verificar se as dependências foram inicializadas
        assert handler.openai_client is not None
        assert handler.serena_api is not None
        assert handler.location_extractor is not None
        assert handler.vision_processor is not None
        assert handler.conversation_context is not None
    
    def test_initialization_missing_env_vars(self):
        """Testa falha na inicialização por variáveis ausentes."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Variáveis de ambiente obrigatórias"):
                AIConversationHandler()


class TestLocationDetectionFlow:
    """Testes para o fluxo de detecção de localização."""
    
    def setup_method(self):
        """Setup para cada teste."""
        # Mock das variáveis de ambiente
        self.env_patch = patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test_openai_key',
            'WHATSAPP_API_TOKEN': 'test_whatsapp_token',
            'WHATSAPP_PHONE_NUMBER_ID': 'test_phone_id',
            'SERENA_API_TOKEN': 'test_serena_token'
        })
        self.env_patch.start()
        
        # Mock das dependências
        self.mock_openai = patch('ai_conversation_handler.OpenAI').start()
        self.mock_serena_api = patch('ai_conversation_handler.SerenaAPI').start()
        
        # Configurar mocks
        self.mock_openai.return_value = MagicMock()
        self.mock_serena_api.return_value = MagicMock()
        
        self.handler = AIConversationHandler()
    
    def teardown_method(self):
        """Cleanup após cada teste."""
        patch.stopall()
        self.env_patch.stop()
    
    @patch('ai_conversation_handler.requests.post')
    def test_process_location_message_with_promotions(self, mock_post):
        """Testa processamento de mensagem com localização e promoções."""
        # Mock da resposta do WhatsApp
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "messages": [{"id": "msg_123"}]
        }
        
        # Mock da API Serena retornando promoções
        self.handler.serena_api.get_plans_by_city.return_value = [
            {"energyUtilityName": "CEMIG", "discountPercentage": 16},
            {"energyUtilityName": "CEMIG", "discountPercentage": 18}
        ]
        
        # Mock da resposta da OpenAI
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "✅ Encontrei promoções em Belo Horizonte!"
        self.handler.openai_client.chat.completions.create.return_value = mock_response
        
        # Processar mensagem com localização
        result = self.handler.process_message(
            "+5511999887766",
            "Moro em Belo Horizonte, MG"
        )
        
        # Verificações
        assert result["success"] is True
        assert result["location_detected"] is True
        assert result["city"] == "Belo Horizonte"
        assert result["state"] == "MG"
        assert result["promotions_found"] == 2
        assert len(result["promotions"]) == 2
        assert result["whatsapp_message_id"] == "msg_123"
        
        # Verificar se o contexto foi salvo
        context = self.handler.conversation_context.get_context("+5511999887766")
        assert context["city"] == "Belo Horizonte"
        assert context["state"] == "MG"
        assert len(context["promotions"]) == 2
    
    @patch('ai_conversation_handler.requests.post')
    def test_process_location_message_no_promotions(self, mock_post):
        """Testa processamento de mensagem com localização sem promoções."""
        # Mock da resposta do WhatsApp
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "messages": [{"id": "msg_456"}]
        }
        
        # Mock da API Serena sem promoções
        self.handler.serena_api.get_plans_by_city.return_value = []
        
        # Mock da resposta da OpenAI
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Infelizmente não encontramos promoções..."
        self.handler.openai_client.chat.completions.create.return_value = mock_response
        
        # Processar mensagem
        result = self.handler.process_message(
            "+5511888777666",
            "Sou de São Paulo, SP"  # Usar localização válida
        )
        
        # Verificações
        assert result["success"] is True
        assert result["location_detected"] is True
        assert result["promotions_found"] == 0
        assert result["promotions"] == []


class TestImageProcessingFlow:
    """Testes para o fluxo de processamento de imagem."""
    
    def setup_method(self):
        """Setup para cada teste."""
        # Mock das variáveis de ambiente
        self.env_patch = patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test_openai_key',
            'WHATSAPP_API_TOKEN': 'test_whatsapp_token',
            'WHATSAPP_PHONE_NUMBER_ID': 'test_phone_id',
            'SERENA_API_TOKEN': 'test_serena_token'
        })
        self.env_patch.start()
        
        # Mock das dependências
        self.mock_openai = patch('ai_conversation_handler.OpenAI').start()
        self.mock_serena_api = patch('ai_conversation_handler.SerenaAPI').start()
        self.mock_save_lead = patch('ai_conversation_handler.save_qualified_lead').start()
        
        # Configurar mocks
        self.mock_openai.return_value = MagicMock()
        self.mock_serena_api.return_value = MagicMock()
        self.mock_save_lead.return_value = {"success": True, "lead_id": "lead_123"}
        
        self.handler = AIConversationHandler()
    
    def teardown_method(self):
        """Cleanup após cada teste."""
        patch.stopall()
        self.env_patch.stop()
    
    @patch('ai_conversation_handler.requests.post')
    @patch('ai_conversation_handler.requests.get')
    def test_process_energy_bill_image_success(self, mock_get, mock_post):
        """Testa processamento bem-sucedido de imagem da conta de energia."""
        # Mock da resposta do WhatsApp para obter URL da imagem
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "url": "https://example.com/conta.jpg"
        }
        
        # Mock da resposta do WhatsApp para enviar mensagem
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "messages": [{"id": "msg_789"}]
        }
        
        # Mock da Vision API retornando dados extraídos
        vision_response = MagicMock()
        vision_response.choices[0].message.content = '''
        {
            "cliente_nome": "João Silva",
            "valor_total": "R$ 245,67",
            "consumo_kwh": "380 kWh",
            "distribuidora": "CEMIG",
            "vencimento": "15/02/2025"
        }
        '''
        
        # Mock da resposta final da conversa
        final_response_mock = MagicMock()
        final_response_mock.choices[0].message.content = "✅ Perfeito! Analisei sua conta da CEMIG..."
        
        # Configurar sequência de chamadas da OpenAI
        self.handler.openai_client.chat.completions.create.side_effect = [
            vision_response,  # Primeira chamada: extração de dados
            final_response_mock  # Segunda chamada: resposta final
        ]
        
        # Processar imagem
        result = self.handler.process_message(
            "+5511999887766",
            "Aqui está minha conta de luz",
            media_id="media_123"
        )
        
        # Verificações
        assert result["success"] is True
        assert result["has_media"] is True
        assert result["media_processed"] is True
        assert result["conversation_completed"] is True
        assert result["supabase_saved"] is True
        assert result["whatsapp_message_id"] == "msg_789"
        
        # Verificar se os dados foram extraídos corretamente
        extracted_data = result["extracted_data"]
        assert extracted_data["success"] is True
        assert extracted_data["data"]["cliente_nome"] == "João Silva"
        assert extracted_data["data"]["valor_total"] == "R$ 245,67"
        assert extracted_data["data"]["distribuidora"] == "CEMIG"
        
        # Verificar se o contexto foi salvo como finalizado
        context = self.handler.conversation_context.get_context("+5511999887766")
        assert context["conversation_completed"] is True
        assert context["extracted_data"] == extracted_data
        
        # Verificar se a função de persistência foi chamada
        self.mock_save_lead.assert_called_once()
    
    @patch('ai_conversation_handler.requests.post')
    @patch('ai_conversation_handler.requests.get')
    def test_process_energy_bill_image_vision_error(self, mock_get, mock_post):
        """Testa tratamento de erro na Vision API."""
        # Mock da resposta do WhatsApp para obter URL da imagem
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "url": "https://example.com/conta.jpg"
        }
        
        # Mock da resposta do WhatsApp para enviar mensagem de erro
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "messages": [{"id": "msg_error"}]
        }
        
        # Mock de erro na Vision API
        self.handler.openai_client.chat.completions.create.side_effect = Exception("Vision API Error")
        
        # Processar imagem
        result = self.handler.process_message(
            "+5511999887766",
            "Aqui está minha conta de luz",
            media_id="media_123"
        )
        
        # Verificações
        assert result["success"] is False
        assert result["has_media"] is True
        assert result["media_processed"] is False
        assert result["whatsapp_sent"] is True
        assert result["whatsapp_message_id"] == "msg_error"


class TestInitialMessageFlow:
    """Testes para o fluxo de mensagem inicial."""
    
    def setup_method(self):
        """Setup para cada teste."""
        # Mock das variáveis de ambiente
        self.env_patch = patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test_openai_key',
            'WHATSAPP_API_TOKEN': 'test_whatsapp_token',
            'WHATSAPP_PHONE_NUMBER_ID': 'test_phone_id',
            'SERENA_API_TOKEN': 'test_serena_token'
        })
        self.env_patch.start()
        
        # Mock das dependências
        self.mock_openai = patch('ai_conversation_handler.OpenAI').start()
        self.mock_serena_api = patch('ai_conversation_handler.SerenaAPI').start()
        
        # Configurar mocks
        self.mock_openai.return_value = MagicMock()
        self.mock_serena_api.return_value = MagicMock()
        
        self.handler = AIConversationHandler()
    
    def teardown_method(self):
        """Cleanup após cada teste."""
        patch.stopall()
        self.env_patch.stop()
    
    @patch('ai_conversation_handler.requests.post')
    def test_process_initial_message(self, mock_post):
        """Testa processamento de mensagem inicial sem localização."""
        # Mock da resposta do WhatsApp
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "messages": [{"id": "msg_initial"}]
        }
        
        # Mock da resposta da OpenAI
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Olá! Sou a Serena, sua assistente..."
        self.handler.openai_client.chat.completions.create.return_value = mock_response
        
        # Processar mensagem inicial
        result = self.handler.process_message(
            "+5511999887766",
            "Oi, quero economizar na conta de luz"
        )
        
        # Verificações
        assert result["success"] is True
        assert result["location_detected"] is False
        assert result["requesting_location"] is True
        assert result["has_media"] is False
        assert result["whatsapp_message_id"] == "msg_initial"


class TestCompletedConversationFlow:
    """Testes para conversas já finalizadas."""
    
    def setup_method(self):
        """Setup para cada teste."""
        # Mock das variáveis de ambiente
        self.env_patch = patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test_openai_key',
            'WHATSAPP_API_TOKEN': 'test_whatsapp_token',
            'WHATSAPP_PHONE_NUMBER_ID': 'test_phone_id',
            'SERENA_API_TOKEN': 'test_serena_token'
        })
        self.env_patch.start()
        
        # Mock das dependências
        self.mock_openai = patch('ai_conversation_handler.OpenAI').start()
        self.mock_serena_api = patch('ai_conversation_handler.SerenaAPI').start()
        
        # Configurar mocks
        self.mock_openai.return_value = MagicMock()
        self.mock_serena_api.return_value = MagicMock()
        
        self.handler = AIConversationHandler()
    
    def teardown_method(self):
        """Cleanup após cada teste."""
        patch.stopall()
        self.env_patch.stop()
    
    def test_handle_completed_conversation(self):
        """Testa tratamento de conversa já finalizada."""
        phone = "+5511999887766"
        
        # Marcar conversa como finalizada
        self.handler.conversation_context.save_context(
            phone,
            conversation_completed=True
        )
        
        # Tentar processar nova mensagem
        result = self.handler.process_message(
            phone,
            "Tenho outra dúvida"
        )
        
        # Verificações
        assert result["success"] is True
        assert result["conversation_completed"] is True
        assert "já foi finalizada" in result["message"]


class TestIntegrationErrorHandling:
    """Testes para tratamento de erros na integração."""
    
    def setup_method(self):
        """Setup para cada teste."""
        # Mock das variáveis de ambiente
        self.env_patch = patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test_openai_key',
            'WHATSAPP_API_TOKEN': 'test_whatsapp_token',
            'WHATSAPP_PHONE_NUMBER_ID': 'test_phone_id',
            'SERENA_API_TOKEN': 'test_serena_token'
        })
        self.env_patch.start()
        
        # Mock das dependências
        self.mock_openai = patch('ai_conversation_handler.OpenAI').start()
        self.mock_serena_api = patch('ai_conversation_handler.SerenaAPI').start()
        
        # Configurar mocks
        self.mock_openai.return_value = MagicMock()
        self.mock_serena_api.return_value = MagicMock()
        
        self.handler = AIConversationHandler()
    
    def teardown_method(self):
        """Cleanup após cada teste."""
        patch.stopall()
        self.env_patch.stop()
    
    def test_openai_api_error(self):
        """Testa tratamento de erro na OpenAI API."""
        # Mock de erro na OpenAI
        self.handler.openai_client.chat.completions.create.side_effect = Exception("OpenAI Error")
        
        # Processar mensagem
        result = self.handler.process_message(
            "+5511999887766",
            "Quero economizar energia"
        )
        
        # Verificações
        assert result["success"] is False
        # O erro pode ser da OpenAI ou do WhatsApp dependendo de onde falha primeiro
        assert result["error"] is not None
    
    def test_serena_api_error(self):
        """Testa tratamento de erro na API Serena."""
        # Mock de erro na API Serena
        self.handler.serena_api.get_plans_by_city.side_effect = Exception("Serena API Error")
        
        # Mock da resposta da OpenAI (para não falhar)
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Resposta de fallback"
        self.handler.openai_client.chat.completions.create.return_value = mock_response
        
        # Mock do WhatsApp (para não falhar)
        with patch('ai_conversation_handler.requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "messages": [{"id": "msg_fallback"}]
            }
            
            # Processar mensagem com localização
            result = self.handler.process_message(
                "+5511999887766",
                "Moro em São Paulo, SP"
            )
            
            # Deve funcionar mesmo com erro na API Serena
            assert result["success"] is True
            assert result["location_detected"] is True
            assert result["promotions_found"] == 0  # Sem promoções devido ao erro


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 