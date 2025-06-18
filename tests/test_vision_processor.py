#!/usr/bin/env python3
"""
Testes para o módulo VisionProcessor

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

from vision_processor import VisionProcessor


class TestEnergyBillImageDetection:
    """Testes para detecção de imagem de conta de energia."""
    
    def setup_method(self):
        """Setup para cada teste."""
        # Mock do cliente OpenAI e token WhatsApp
        mock_client = MagicMock()
        self.processor = VisionProcessor(mock_client, "test_token")
    
    def test_is_energy_bill_image_with_keywords(self):
        """Testa detecção de conta de energia com palavras-chave."""
        test_cases = [
            ("Aqui está minha conta de luz", True),
            ("Enviando a fatura da CEMIG", True),
            ("Minha conta da CELPE", True),
            ("Fatura de energia elétrica", True),
            ("Conta da distribuidora", True),
            ("[FATURA_ENVIADA: conta_energia.pdf]", True),
            ("[DOCUMENTO_ENVIADO: fatura.jpg]", True)
        ]
        
        for message, expected in test_cases:
            result = self.processor.is_energy_bill_image(message)
            assert result == expected, f"Falhou para: {message}"
    
    def test_is_energy_bill_image_short_messages(self):
        """Testa detecção com mensagens curtas (só imagem)."""
        test_cases = [
            ("", True),      # Mensagem vazia (só imagem)
            (".", True),     # Mensagem muito curta
            ("Aqui", True),  # Mensagem curta
        ]
        
        for message, expected in test_cases:
            result = self.processor.is_energy_bill_image(message)
            assert result == expected, f"Falhou para: {message}"
    
    def test_is_energy_bill_image_negative_cases(self):
        """Testa casos que NÃO devem ser detectados como conta de energia."""
        test_cases = [
            ("Como funciona o desconto solar?", False),
            ("Quanto custa o sistema fotovoltaico?", False),
            ("Tenho dúvidas sobre painéis solares", False),
            ("Quero informações sobre o serviço", False),
            ("Explique como funciona o processo", False)
        ]
        
        for message, expected in test_cases:
            result = self.processor.is_energy_bill_image(message)
            assert result == expected, f"Falhou para: {message}"


class TestVisionAPIExtraction:
    """Testes para extração de dados usando Vision API."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.mock_client = MagicMock()
        self.processor = VisionProcessor(self.mock_client, "test_token")
    
    def test_extract_bill_data_with_vision_success(self):
        """Testa extração bem-sucedida de dados da conta."""
        # Mock da resposta da Vision API
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "cliente_nome": "João Silva",
            "valor_total": "R$ 245,67",
            "consumo_kwh": "380 kWh",
            "distribuidora": "CEMIG",
            "vencimento": "15/02/2025",
            "endereco": "Rua das Flores, 123",
            "numero_instalacao": "12345678"
        }
        '''
        self.mock_client.chat.completions.create.return_value = mock_response
        
        image_url = "https://example.com/conta.jpg"
        result = self.processor.extract_bill_data_with_vision(image_url)
        
        assert result["success"] is True
        assert result["data"]["cliente_nome"] == "João Silva"
        assert result["data"]["valor_total"] == "R$ 245,67"
        assert result["data"]["distribuidora"] == "CEMIG"
        
        # Verificar se o payload multimodal foi construído corretamente
        call_args = self.mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert len(messages[0]["content"]) == 2
        assert messages[0]["content"][0]["type"] == "text"
        assert messages[0]["content"][1]["type"] == "image_url"
        assert messages[0]["content"][1]["image_url"]["url"] == image_url
    
    def test_extract_bill_data_with_vision_invalid_json(self):
        """Testa tratamento de resposta com JSON inválido."""
        # Mock da resposta com JSON malformado
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Resposta sem JSON válido"
        self.mock_client.chat.completions.create.return_value = mock_response
        
        image_url = "https://example.com/conta.jpg"
        result = self.processor.extract_bill_data_with_vision(image_url)
        
        assert result["success"] is False
        assert "JSON não encontrado" in result["error"]
        assert "raw_response" in result
    
    def test_extract_bill_data_with_vision_api_error(self):
        """Testa tratamento de erro na API."""
        # Mock de erro na API
        self.mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        image_url = "https://example.com/conta.jpg"
        result = self.processor.extract_bill_data_with_vision(image_url)
        
        assert result["success"] is False
        assert "API Error" in result["error"]
    
    def test_validate_extracted_data_valid(self):
        """Testa validação de dados válidos."""
        valid_data = {
            "cliente_nome": "Maria Santos",
            "valor_total": "R$ 156,89",
            "distribuidora": "ENEL",
            "consumo_kwh": "280 kWh",
            "vencimento": "20/02/2025"
        }
        
        result = self.processor.validate_extracted_data(valid_data)
        assert result is True
    
    def test_validate_extracted_data_missing_required_fields(self):
        """Testa validação com campos obrigatórios ausentes."""
        invalid_cases = [
            # Sem nome do cliente
            {
                "cliente_nome": "NÃO_IDENTIFICADO",
                "valor_total": "R$ 156,89",
                "distribuidora": "ENEL"
            },
            # Sem valor total
            {
                "cliente_nome": "Maria Santos",
                "valor_total": "NÃO_IDENTIFICADO",
                "distribuidora": "ENEL"
            },
            # Sem distribuidora
            {
                "cliente_nome": "Maria Santos",
                "valor_total": "R$ 156,89",
                "distribuidora": "NÃO_IDENTIFICADO"
            }
        ]
        
        for invalid_data in invalid_cases:
            result = self.processor.validate_extracted_data(invalid_data)
            assert result is False
    
    def test_validate_extracted_data_invalid_values(self):
        """Testa validação com valores inválidos."""
        invalid_cases = [
            # Valor total inválido
            {
                "cliente_nome": "Maria Santos",
                "valor_total": "valor inválido",
                "distribuidora": "ENEL"
            },
            # Nome muito curto
            {
                "cliente_nome": "AB",
                "valor_total": "R$ 156,89",
                "distribuidora": "ENEL"
            }
        ]
        
        for invalid_data in invalid_cases:
            result = self.processor.validate_extracted_data(invalid_data)
            assert result is False


class TestFinalConversationResponse:
    """Testes para geração da resposta final da conversa."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.mock_client = MagicMock()
        self.processor = VisionProcessor(self.mock_client, "test_token")
    
    def test_generate_final_conversation_response_success(self):
        """Testa geração da resposta final com dados válidos."""
        # Mock da resposta da OpenAI
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "✅ Perfeito! Analisei sua conta da CEMIG..."
        self.mock_client.chat.completions.create.return_value = mock_response
        
        extracted_data = {
            "success": True,
            "data": {
                "cliente_nome": "João Silva",
                "valor_total": "R$ 245,67",
                "distribuidora": "CEMIG"
            }
        }
        
        result = self.processor.generate_final_conversation_response(extracted_data)
        
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Verificar se o prompt contém os dados extraídos
        call_args = self.mock_client.chat.completions.create.call_args
        prompt = call_args[1]["messages"][0]["content"]
        
        assert "João Silva" in prompt
        assert "R$ 245,67" in prompt
        assert "CEMIG" in prompt
        assert "Etapa 6" in prompt
    
    def test_generate_final_conversation_response_api_error(self):
        """Testa geração da resposta final com erro na API."""
        # Mock de erro na API
        self.mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        extracted_data = {
            "success": True,
            "data": {
                "cliente_nome": "João Silva",
                "valor_total": "R$ 245,67",
                "distribuidora": "CEMIG"
            }
        }
        
        result = self.processor.generate_final_conversation_response(extracted_data)
        
        # Deve retornar resposta de fallback
        assert isinstance(result, str)
        assert "Obrigada por enviar sua conta" in result
        assert "24 horas" in result
    
    def test_create_error_response(self):
        """Testa criação de resposta de erro amigável."""
        error_message = "Erro técnico qualquer"
        result = self.processor.create_error_response(error_message)
        
        assert isinstance(result, str)
        assert "Desculpe" in result
        assert "📸" in result  # Deve conter dicas com emojis
        assert "PDF" in result


class TestWhatsAppMediaAPI:
    """Testes para integração com WhatsApp Media API."""
    
    def setup_method(self):
        """Setup para cada teste."""
        mock_client = MagicMock()
        self.processor = VisionProcessor(mock_client, "test_whatsapp_token")
    
    @patch('vision_processor.requests.get')
    def test_get_whatsapp_media_url_success(self, mock_get):
        """Testa obtenção bem-sucedida de URL da mídia."""
        # Mock da resposta do WhatsApp
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "url": "https://example.com/media/image.jpg"
        }
        mock_get.return_value = mock_response
        
        media_id = "media_123"
        result = self.processor.get_whatsapp_media_url(media_id)
        
        assert result == "https://example.com/media/image.jpg"
        
        # Verificar se a chamada foi feita corretamente
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert f"/{media_id}" in call_args[0][0]
        assert "Authorization" in call_args[1]["headers"]
        assert "Bearer test_whatsapp_token" in call_args[1]["headers"]["Authorization"]
    
    @patch('vision_processor.requests.get')
    def test_get_whatsapp_media_url_error(self, mock_get):
        """Testa tratamento de erro na API do WhatsApp."""
        # Mock de erro na resposta
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_get.return_value = mock_response
        
        media_id = "media_invalid"
        result = self.processor.get_whatsapp_media_url(media_id)
        
        assert result is None
    
    @patch('vision_processor.requests.get')
    def test_get_whatsapp_media_url_exception(self, mock_get):
        """Testa tratamento de exceção na chamada da API."""
        # Mock de exceção
        mock_get.side_effect = Exception("Network error")
        
        media_id = "media_123"
        result = self.processor.get_whatsapp_media_url(media_id)
        
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
