# =============================================================================
# SERENA SDR - CONFIGURAÇÃO DE TESTES
# =============================================================================

"""
Configuração de testes para o sistema Serena SDR

Este arquivo contém fixtures e configurações compartilhadas
para todos os testes de integração e end-to-end.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import pytest
import json
import os
from unittest.mock import Mock, patch
from typing import Dict, Any, Optional
import httpx
from datetime import datetime, timedelta


@pytest.fixture
def mock_supabase_mcp():
    """Mock do servidor MCP Supabase."""
    with patch('httpx.post') as mock_post:
        # Mock para execute_sql
        mock_post.return_value.json.return_value = {
            "result": {
                "data": [
                    {
                        "id": "test-lead-id",
                        "phone": "5581997498268",
                        "name": "Teste SDR",
                        "email": "teste@serena.com",
                        "status": "active",
                        "created_at": "2024-01-17T10:00:00Z"
                    }
                ]
            }
        }
        mock_post.return_value.status_code = 200
        yield mock_post


@pytest.fixture
def mock_serena_mcp():
    """Mock do servidor MCP Serena."""
    with patch('httpx.post') as mock_post:
        # Mock para validar_qualificacao_lead
        mock_post.return_value.json.return_value = {
            "result": {
                "qualificado": True,
                "score": 85,
                "motivo": "Consumo alto de energia",
                "valor_fatura": 350.50,
                "consumo_kwh": 450
            }
        }
        mock_post.return_value.status_code = 200
        yield mock_post


@pytest.fixture
def mock_whatsapp_mcp():
    """Mock do servidor MCP WhatsApp."""
    with patch('httpx.post') as mock_post:
        # Mock para sendTextMessage
        mock_post.return_value.json.return_value = {
            "result": {
                "message_id": "test-message-id",
                "status": "sent",
                "timestamp": datetime.now().isoformat()
            }
        }
        mock_post.return_value.status_code = 200
        yield mock_post


@pytest.fixture
def mock_whatsapp_media():
    """Mock para download de mídia do WhatsApp."""
    with patch('httpx.get') as mock_get:
        # Mock para download de imagem
        mock_get.return_value.content = b"fake_image_data"
        mock_get.return_value.status_code = 200
        yield mock_get


@pytest.fixture
def sample_webhook_payload():
    """Payload de exemplo para webhook WhatsApp."""
    return {
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
                                    "profile": {
                                        "name": "Teste SDR"
                                    },
                                    "wa_id": "5581997498268"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "5581997498268",
                                    "id": "test-message-id",
                                    "timestamp": "1705492800",
                                    "type": "text",
                                    "text": {
                                        "body": "Olá Silvia"
                                    }
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def sample_webhook_payload_with_image():
    """Payload de exemplo para webhook com imagem."""
    return {
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
                                    "profile": {
                                        "name": "Teste SDR"
                                    },
                                    "wa_id": "5581997498268"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "5581997498268",
                                    "id": "test-message-id",
                                    "timestamp": "1705492800",
                                    "type": "image",
                                    "image": {
                                        "id": "test-media-id",
                                        "mime_type": "image/jpeg",
                                        "sha256": "test-sha256",
                                        "filename": "fatura.jpg"
                                    }
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def sample_energy_bill_data():
    """Dados de exemplo de fatura de energia."""
    return {
        "classification": "energy_bill",
        "confidence": 0.95,
        "extracted_data": {
            "total_value": 350.50,
            "due_date": "2024-01-15",
            "consumption_kwh": 450,
            "utility_name": "ENEL SP",
            "customer_name": "João Silva",
            "customer_address": "Rua das Flores, 123 - São Paulo/SP"
        },
        "reasoning": "Documento identificado como fatura de energia elétrica"
    }


@pytest.fixture
def mock_openai_vision():
    """Mock para OpenAI Vision API."""
    with patch('openai.ChatCompletion.create') as mock_create:
        mock_create.return_value.choices[0].message.content = json.dumps({
            "classification": "energy_bill",
            "confidence": 0.95,
            "extracted_data": {
                "total_value": 350.50,
                "due_date": "2024-01-15",
                "consumption_kwh": 450,
                "utility_name": "ENEL SP"
            },
            "reasoning": "Documento identificado como fatura de energia elétrica"
        })
        yield mock_create


@pytest.fixture
def mock_openai_chat():
    """Mock para OpenAI Chat API."""
    with patch('openai.ChatCompletion.create') as mock_create:
        mock_create.return_value.choices[0].message.content = "Olá! Sou a Silvia, sua consultora de energia solar. Como posso ajudá-lo hoje?"
        yield mock_create


@pytest.fixture
def test_environment():
    """Configuração de ambiente de teste."""
    os.environ.update({
        "OPENAI_API_KEY": "test-openai-key",
        "SUPABASE_MCP_URL": "http://supabase-mcp-server:3000",
        "SERENA_MCP_URL": "http://serena-mcp-server:3001",
        "WHATSAPP_MCP_URL": "http://whatsapp-mcp-server:3003",
        "SERENA_API_TOKEN": "test-serena-token",
        "SERENA_API_BASE_URL": "https://api.serena.com.br",
        "WHATSAPP_API_TOKEN": "test-whatsapp-token",
        "WHATSAPP_PHONE_NUMBER_ID": "test-phone-id",
        "WHATSAPP_BUSINESS_ACCOUNT_ID": "test-business-id",
        "SECRET_SUPABASE_URL": "https://test.supabase.co",
        "SECRET_SUPABASE_KEY": "test-supabase-key"
    })


@pytest.fixture
def mock_kestra_workflow():
    """Mock para execução de workflow Kestra."""
    with patch('httpx.post') as mock_post:
        mock_post.return_value.json.return_value = {
            "id": "test-execution-id",
            "status": "RUNNING",
            "flowId": "2_sdr_conversation_flow",
            "namespace": "serena.production"
        }
        mock_post.return_value.status_code = 200
        yield mock_post


def assert_mcp_call(mock_mcp, expected_method: str, expected_params: Dict[str, Any]):
    """Helper para verificar chamadas MCP."""
    mock_mcp.assert_called()
    call_args = mock_mcp.call_args
    
    # Verificar URL
    assert expected_method in str(call_args)
    
    # Verificar parâmetros JSON-RPC
    if call_args[1].get('json'):
        json_data = call_args[1]['json']
        assert json_data['method'] == expected_method
        assert json_data['params'] == expected_params


def assert_supabase_log(log_data: Dict[str, Any], expected_type: str):
    """Helper para verificar logs no Supabase."""
    assert log_data['type'] == expected_type
    assert 'timestamp' in log_data
    assert 'phone_number' in log_data


def create_test_lead(phone: str = "5581997498268") -> Dict[str, Any]:
    """Helper para criar lead de teste."""
    return {
        "id": f"test-lead-{phone}",
        "phone": phone,
        "name": "Teste SDR",
        "email": "teste@serena.com",
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    } 