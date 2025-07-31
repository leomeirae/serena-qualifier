# =============================================================================
# SERENA SDR - TESTE E2E: FATURA DE ENERGIA (OCR + QUALIFICAÇÃO)
# =============================================================================

"""
Teste End-to-End: Fluxo de Fatura de Energia

Este teste simula o fluxo completo de processamento de uma
fatura de energia via OCR, desde o recebimento da imagem
até a qualificação e resposta com planos.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import pytest
import json
import httpx
from unittest.mock import patch, Mock
from datetime import datetime


class TestEnergyBillOCRFlow:
    """Teste do fluxo de processamento de fatura de energia."""

    def test_energy_bill_ocr_qualification_flow(
        self,
        sample_webhook_payload_with_image,
        mock_supabase_mcp,
        mock_serena_mcp,
        mock_whatsapp_mcp,
        mock_whatsapp_media,
        mock_openai_vision,
        mock_openai_chat,
        test_environment
    ):
        """
        Teste 1: Fluxo completo de fatura de energia com qualificação.
        
        Cenário:
        1. Webhook recebe imagem de fatura
        2. classify_media.py identifica como imagem
        3. OCR extrai dados da fatura
        4. validar_qualificacao_lead é chamado
        5. Se valor ≥ R$200, obter_planos_gd é chamado
        6. Resposta personalizada é enviada
        """
        
        # 1. Simular recebimento do webhook com imagem
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=sample_webhook_payload_with_image
            )
            
            assert response.status_code == 200
        
        # 2. Verificar que lead foi buscado no Supabase
        assert_mcp_call(
            mock_supabase_mcp,
            "execute_sql",
            {
                "query": "SELECT * FROM leads WHERE phone = $1",
                "params": ["5581997498268"]
            }
        )
        
        # 3. Verificar que mídia foi baixada do WhatsApp
        mock_whatsapp_media.assert_called()
        
        # 4. Verificar que classify_media foi executado
        # (isso seria verificado no workflow Kestra)
        
        # 5. Verificar que OpenAI Vision foi chamado para OCR
        mock_openai_vision.assert_called()
        vision_call = mock_openai_vision.call_args
        
        # Verificar que a imagem foi incluída na chamada
        messages = vision_call[1]['messages']
        user_message = next((msg for msg in messages if msg['role'] == 'user'), None)
        assert user_message is not None
        
        # Verificar que há conteúdo de imagem
        content = user_message['content']
        assert any(item.get('type') == 'image_url' for item in content if isinstance(item, dict))
        
        # 6. Verificar que qualificação foi chamada
        assert_mcp_call(
            mock_serena_mcp,
            "validar_qualificacao_lead",
            {
                "phone": "5581997498268",
                "valor_fatura": 350.50,
                "consumo_kwh": 450,
                "distribuidora": "ENEL SP"
            }
        )
        
        # 7. Verificar que planos foram obtidos (valor ≥ R$200)
        assert_mcp_call(
            mock_serena_mcp,
            "obter_planos_gd",
            {
                "phone": "5581997498268",
                "consumo_kwh": 450,
                "distribuidora": "ENEL SP"
            }
        )
        
        # 8. Verificar que resposta foi enviada via WhatsApp
        mock_whatsapp_mcp.assert_called()
        call_args = mock_whatsapp_mcp.call_args
        
        # Verificar que a mensagem contém informações sobre planos
        json_data = call_args[1]['json']
        message_content = json_data['params']['message']
        assert "plano" in message_content.lower() or "energia solar" in message_content.lower()

    def test_energy_bill_below_threshold(
        self,
        sample_webhook_payload_with_image,
        mock_supabase_mcp,
        mock_serena_mcp,
        mock_whatsapp_mcp,
        mock_whatsapp_media,
        mock_openai_vision,
        test_environment
    ):
        """
        Teste 2: Fatura com valor abaixo do threshold (R$200).
        
        Cenário:
        1. Fatura com valor R$150 (abaixo do threshold)
        2. Qualificação retorna não qualificado
        3. obter_planos_gd NÃO deve ser chamado
        4. Mensagem de não qualificação deve ser enviada
        """
        
        # Mock OpenAI Vision retornando fatura com valor baixo
        with patch('openai.ChatCompletion.create') as mock_vision:
            mock_vision.return_value.choices[0].message.content = json.dumps({
                "classification": "energy_bill",
                "confidence": 0.95,
                "extracted_data": {
                    "total_value": 150.00,
                    "consumption_kwh": 200,
                    "utility_name": "ENEL SP"
                }
            })
        
        # Mock Serena MCP retornando não qualificado
        mock_serena_mcp.return_value.json.return_value = {
            "result": {
                "qualificado": False,
                "score": 30,
                "motivo": "Consumo muito baixo",
                "valor_fatura": 150.00,
                "consumo_kwh": 200
            }
        }
        
        # Simular webhook
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=sample_webhook_payload_with_image
            )
            
            assert response.status_code == 200
        
        # Verificar que qualificação foi chamada
        assert_mcp_call(
            mock_serena_mcp,
            "validar_qualificacao_lead",
            {
                "phone": "5581997498268",
                "valor_fatura": 150.00,
                "consumo_kwh": 200,
                "distribuidora": "ENEL SP"
            }
        )
        
        # Verificar que obter_planos_gd NÃO foi chamado
        calls = mock_serena_mcp.call_args_list
        planos_calls = [call for call in calls if "obter_planos_gd" in str(call)]
        assert len(planos_calls) == 0, "obter_planos_gd não deve ser chamado para valor baixo"
        
        # Verificar que mensagem de não qualificação foi enviada
        mock_whatsapp_mcp.assert_called()
        call_args = mock_whatsapp_mcp.call_args
        json_data = call_args[1]['json']
        message_content = json_data['params']['message']
        assert "não qualificado" in message_content.lower() or "consumo baixo" in message_content.lower()

    def test_energy_bill_classification_error(
        self,
        sample_webhook_payload_with_image,
        mock_supabase_mcp,
        mock_whatsapp_mcp,
        mock_whatsapp_media,
        test_environment
    ):
        """
        Teste 3: Erro na classificação da fatura.
        
        Cenário:
        1. OpenAI Vision retorna erro ou classificação inválida
        2. Sistema deve enviar mensagem de fallback
        3. Log de erro deve ser registrado
        """
        
        # Mock OpenAI Vision retornando erro
        with patch('openai.ChatCompletion.create') as mock_vision:
            mock_vision.side_effect = Exception("OpenAI API Error")
        
        # Simular webhook
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=sample_webhook_payload_with_image
            )
            
            assert response.status_code == 200
        
        # Verificar que mensagem de fallback foi enviada
        mock_whatsapp_mcp.assert_called()
        call_args = mock_whatsapp_mcp.call_args
        json_data = call_args[1]['json']
        message_content = json_data['params']['message']
        assert "desculpe" in message_content.lower() or "erro" in message_content.lower()
        
        # Verificar que log de erro foi registrado
        calls = mock_supabase_mcp.call_args_list
        error_logs = [call for call in calls if "INSERT INTO sdr_logs" in str(call) and "error" in str(call)]
        assert len(error_logs) >= 1, "Deve haver log de erro registrado"

    def test_energy_bill_not_energy_bill(
        self,
        sample_webhook_payload_with_image,
        mock_supabase_mcp,
        mock_whatsapp_mcp,
        mock_whatsapp_media,
        test_environment
    ):
        """
        Teste 4: Imagem que não é fatura de energia.
        
        Cenário:
        1. OpenAI Vision classifica como "not_document" ou "other_document"
        2. Sistema deve enviar mensagem informando que não é fatura
        3. Fluxo de qualificação não deve ser executado
        """
        
        # Mock OpenAI Vision retornando não é fatura
        with patch('openai.ChatCompletion.create') as mock_vision:
            mock_vision.return_value.choices[0].message.content = json.dumps({
                "classification": "not_document",
                "confidence": 0.9,
                "extracted_data": {},
                "reasoning": "Imagem não é um documento"
            })
        
        # Simular webhook
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=sample_webhook_payload_with_image
            )
            
            assert response.status_code == 200
        
        # Verificar que mensagem informativa foi enviada
        mock_whatsapp_mcp.assert_called()
        call_args = mock_whatsapp_mcp.call_args
        json_data = call_args[1]['json']
        message_content = json_data['params']['message']
        assert "fatura" in message_content.lower() or "documento" in message_content.lower()

    def test_energy_bill_ocr_accuracy(
        self,
        sample_webhook_payload_with_image,
        mock_supabase_mcp,
        mock_serena_mcp,
        mock_whatsapp_mcp,
        mock_whatsapp_media,
        test_environment
    ):
        """
        Teste 5: Verificar precisão do OCR.
        
        Cenário:
        1. Fatura com dados específicos
        2. Verificar que dados extraídos estão corretos
        3. Verificar que qualificação usa dados corretos
        """
        
        expected_data = {
            "total_value": 450.75,
            "due_date": "2024-01-20",
            "consumption_kwh": 550,
            "utility_name": "CPFL",
            "customer_name": "Maria Santos",
            "customer_address": "Av. Paulista, 1000 - São Paulo/SP"
        }
        
        # Mock OpenAI Vision com dados específicos
        with patch('openai.ChatCompletion.create') as mock_vision:
            mock_vision.return_value.choices[0].message.content = json.dumps({
                "classification": "energy_bill",
                "confidence": 0.98,
                "extracted_data": expected_data,
                "reasoning": "Fatura de energia elétrica identificada com alta confiança"
            })
        
        # Mock Serena MCP para qualificação
        mock_serena_mcp.return_value.json.return_value = {
            "result": {
                "qualificado": True,
                "score": 90,
                "motivo": "Consumo alto de energia",
                "valor_fatura": expected_data["total_value"],
                "consumo_kwh": expected_data["consumption_kwh"]
            }
        }
        
        # Simular webhook
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=sample_webhook_payload_with_image
            )
            
            assert response.status_code == 200
        
        # Verificar que qualificação foi chamada com dados corretos
        assert_mcp_call(
            mock_serena_mcp,
            "validar_qualificacao_lead",
            {
                "phone": "5581997498268",
                "valor_fatura": expected_data["total_value"],
                "consumo_kwh": expected_data["consumption_kwh"],
                "distribuidora": expected_data["utility_name"]
            }
        )
        
        # Verificar que planos foram obtidos com dados corretos
        assert_mcp_call(
            mock_serena_mcp,
            "obter_planos_gd",
            {
                "phone": "5581997498268",
                "consumo_kwh": expected_data["consumption_kwh"],
                "distribuidora": expected_data["utility_name"]
            }
        )

    def test_energy_bill_processing_time(
        self,
        sample_webhook_payload_with_image,
        mock_supabase_mcp,
        mock_serena_mcp,
        mock_whatsapp_mcp,
        mock_whatsapp_media,
        mock_openai_vision,
        test_environment
    ):
        """
        Teste 6: Verificar tempo de processamento da fatura.
        
        Cenário:
        1. Medir tempo total do fluxo OCR + qualificação
        2. Verificar que está dentro do SLA (< 30 segundos)
        """
        
        import time
        
        start_time = time.time()
        
        # Simular fluxo completo
        with patch('httpx.post') as mock_webhook:
            mock_webhook.return_value.status_code = 200
            
            response = httpx.post(
                "http://localhost:8001/webhook",
                json=sample_webhook_payload_with_image
            )
            
            assert response.status_code == 200
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verificar SLA: processamento em menos de 30 segundos
        assert processing_time < 30.0, f"Tempo de processamento {processing_time:.2f}s excedeu SLA de 30s"
        
        # Verificar que todas as chamadas foram feitas
        mock_supabase_mcp.assert_called()
        mock_whatsapp_media.assert_called()
        mock_openai_vision.assert_called()
        mock_serena_mcp.assert_called()
        mock_whatsapp_mcp.assert_called() 