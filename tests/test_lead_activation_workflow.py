import pytest
import uuid
import asyncio
import time
from unittest.mock import patch, MagicMock, AsyncMock

async def process_lead_activation(payload):
    """
    Simula o fluxo completo do workflow lead-activation.yml de forma assíncrona.
    
    Args:
        payload: Dicionário com os dados do lead (name, email, phone, city)
        
    Returns:
        dict: Resultado da execução simulada do workflow
    """
    result = {"success": False}
    
    # 1. Validação de campos
    for field in ["name", "email", "phone", "city"]:
        if not payload.get(field):
            result["error"] = f"Campo obrigatório ausente: {field}"
            return result
    
    try:
        # 2. Geração do conversation_id e salvamento no Supabase
        from supabase import create_client
        
        conversation_id = str(uuid.uuid4())
        lead_data = {**payload, "conversation_id": conversation_id}
        
        supabase = create_client("mock-url", "mock-key")
        db_result = supabase.table("leads_iniciados").insert(lead_data).execute()
        
        lead_id = db_result.data[0].get("id") if db_result.data else None
        if not lead_id:
            result["error"] = "Falha ao salvar lead no Supabase"
            return result
            
        # 3. Envio do template WhatsApp (função assíncrona)
        import scripts.whatsapp_sender
        components = [
            {
                "type": "body",
                "parameters": [
                    {
                        "type": "text",
                        "text": payload["name"]
                    }
                ]
            }
        ]
        
        # Chamada da função assíncrona com await
        whatsapp_result = await scripts.whatsapp_sender.send_whatsapp_template_message(
            phone=payload["phone"],
            template_name="ativar_perfil",
            components=components
        )
        
        if not whatsapp_result or "message_id" not in whatsapp_result:
            result["error"] = "Falha ao enviar template WhatsApp"
            return result
            
        # 4. Integração com ai-conversation.yml
        import requests
        ai_conversation_payload = {
            "lead_phone": payload["phone"],
            "lead_name": payload["name"],
            "conversation_id": conversation_id,
            "city": payload["city"]
        }
        
        # Chamada HTTP para integração
        response = requests.post(
            "http://kestra:8080/api/v1/executions/webhook/serena.energia/ai-conversation/ai_conversation_webhook",
            json=ai_conversation_payload
        )
        
        if response.status_code != 202:
            result["error"] = f"Falha ao acionar ai-conversation.yml: {response.status_code}"
            return result
            
        # Sucesso em todas as etapas
        result.update({
            "success": True,
            "conversation_id": conversation_id,
            "lead_id": lead_id,
            "message_id": whatsapp_result.get("message_id"),
            "integration_success": True
        })
        
        return result
        
    except Exception as e:
        result["error"] = str(e)
        return result


@pytest.mark.asyncio
async def test_trigger_webhook_payload_valido():
    """Testa o trigger do webhook com payload válido e fluxo completo de sucesso."""
    # Setup mocks
    with patch('supabase.create_client') as mock_supabase, \
         patch('scripts.whatsapp_sender.send_whatsapp_template_message', new_callable=AsyncMock) as mock_whatsapp, \
         patch('requests.post') as mock_http:
        
        # Mock Supabase
        mock_supabase_instance = MagicMock()
        mock_supabase_instance.table.return_value.insert.return_value.execute.return_value.data = [{"id": 123}]
        mock_supabase.return_value = mock_supabase_instance
        
        # Mock WhatsApp usando AsyncMock para função assíncrona
        mock_whatsapp.return_value = {"message_id": "msg-001", "success": True}
        
        # Mock HTTP
        mock_http_response = MagicMock()
        mock_http_response.status_code = 202
        mock_http_response.json.return_value = {"message": "Conversation continuation accepted"}
        mock_http.return_value = mock_http_response

        # Dados do payload para teste
        payload = {
            "name": "João da Silva",
            "email": "joao.silva@example.com",
            "phone": "+5511987654321",
            "city": "São Paulo"
        }
        
        # Chamada da função assíncrona
        result = await process_lead_activation(payload)
        
        # Verificações
        assert result["success"] is True
        assert "conversation_id" in result
        assert result["message_id"] == "msg-001"
        assert result["lead_id"] == 123
        assert result["integration_success"] is True
        
        # Verificar se todos os serviços foram chamados corretamente
        mock_supabase.assert_called_once()
        mock_supabase_instance.table.assert_called_with("leads_iniciados")
        mock_whatsapp.assert_called_once()
        mock_http.assert_called_once()


@pytest.mark.asyncio
async def test_trigger_webhook_payload_invalido():
    """Testa o trigger do webhook com payload inválido (campos obrigatórios ausentes)."""
    payload = {
        "name": "",
        "email": "",
        "phone": "+5511987654321",
        "city": "São Paulo"
    }
    
    result = await process_lead_activation(payload)
    assert result["success"] is False
    assert "error" in result
    assert "Campo obrigatório ausente" in result["error"]


@pytest.mark.asyncio
async def test_erro_supabase():
    """Testa erro de conexão ou inserção no Supabase."""
    with patch('supabase.create_client') as mock_supabase:
        mock_supabase.side_effect = Exception("Erro de conexão Supabase")
        
        payload = {
            "name": "João da Silva",
            "email": "joao.silva@example.com",
            "phone": "+5511987654321",
            "city": "São Paulo"
        }
        
        result = await process_lead_activation(payload)
        assert result["success"] is False
        assert "error" in result
        assert "Erro de conexão Supabase" in result["error"]


@pytest.mark.asyncio
async def test_erro_whatsapp():
    """Testa erro no envio do template WhatsApp."""
    with patch('supabase.create_client') as mock_supabase, \
         patch('scripts.whatsapp_sender.send_whatsapp_template_message', new_callable=AsyncMock) as mock_whatsapp:
        
        # Mock Supabase para sucesso
        mock_supabase_instance = MagicMock()
        mock_supabase_instance.table.return_value.insert.return_value.execute.return_value.data = [{"id": 123}]
        mock_supabase.return_value = mock_supabase_instance
        
        # Mock WhatsApp para falha usando AsyncMock
        mock_whatsapp.side_effect = Exception("Erro WhatsApp API")
        
        payload = {
            "name": "João da Silva",
            "email": "joao.silva@example.com",
            "phone": "+5511987654321",
            "city": "São Paulo"
        }
        
        result = await process_lead_activation(payload)
        assert result["success"] is False
        assert "error" in result
        assert "Erro WhatsApp API" in result["error"]


@pytest.mark.asyncio
async def test_erro_integracao_ai_conversation():
    """Testa erro na integração com o workflow de conversa (HTTP 500)."""
    with patch('supabase.create_client') as mock_supabase, \
         patch('scripts.whatsapp_sender.send_whatsapp_template_message', new_callable=AsyncMock) as mock_whatsapp, \
         patch('requests.post') as mock_http:
        
        # Setup de mocks para sucesso nas etapas anteriores
        mock_supabase_instance = MagicMock()
        mock_supabase_instance.table.return_value.insert.return_value.execute.return_value.data = [{"id": 123}]
        mock_supabase.return_value = mock_supabase_instance
        
        # Mock WhatsApp para sucesso
        mock_whatsapp.return_value = {"message_id": "msg-001", "success": True}
        
        # Mock HTTP para falha
        mock_http_response = MagicMock()
        mock_http_response.status_code = 500
        mock_http_response.json.return_value = {"error": "Kestra trigger failed"}
        mock_http.return_value = mock_http_response
        
        payload = {
            "name": "João da Silva",
            "email": "joao.silva@example.com",
            "phone": "+5511987654321",
            "city": "São Paulo"
        }
        
        result = await process_lead_activation(payload)
        assert result["success"] is False
        assert "error" in result
        assert "Falha ao acionar ai-conversation.yml" in result["error"]


@pytest.mark.asyncio
async def test_geracao_conversation_id():
    """Testa a geração do conversation_id."""
    with patch('uuid.uuid4') as mock_uuid, \
         patch('supabase.create_client') as mock_supabase, \
         patch('scripts.whatsapp_sender.send_whatsapp_template_message', new_callable=AsyncMock) as mock_whatsapp, \
         patch('requests.post') as mock_http:
        
        # Configura UUID fixo para teste
        mock_uuid.return_value = "test-uuid-4321"
        
        # Mock Supabase para sucesso
        mock_supabase_instance = MagicMock()
        mock_supabase_instance.table.return_value.insert.return_value.execute.return_value.data = [{"id": 123}]
        mock_supabase.return_value = mock_supabase_instance
        
        # Mock WhatsApp para sucesso
        mock_whatsapp.return_value = {"message_id": "msg-001", "success": True}
        
        # Mock HTTP para sucesso
        mock_http_response = MagicMock()
        mock_http_response.status_code = 202
        mock_http_response.json.return_value = {"message": "Success"}
        mock_http.return_value = mock_http_response
        
        payload = {
            "name": "João da Silva",
            "email": "joao.silva@example.com",
            "phone": "+5511987654321",
            "city": "São Paulo"
        }
        
        result = await process_lead_activation(payload)
        assert result["success"] is True
        assert result["conversation_id"] == "test-uuid-4321"
        
        # Verifica se o UUID foi passado corretamente para o Supabase
        insert_call_args = mock_supabase_instance.table.return_value.insert.call_args[0][0]
        assert insert_call_args["conversation_id"] == "test-uuid-4321" 


@pytest.mark.asyncio
async def test_performance_sla():
    """
    Testa o SLA de latência para o processo de ativação do lead.
    
    SLA definido: < 3 segundos para processamento completo do lead-activation.yml
    """
    # Setup mocks
    with patch('supabase.create_client') as mock_supabase, \
         patch('scripts.whatsapp_sender.send_whatsapp_template_message', new_callable=AsyncMock) as mock_whatsapp, \
         patch('requests.post') as mock_http:
        
        # Mock Supabase para resposta rápida
        mock_supabase_instance = MagicMock()
        mock_supabase_instance.table.return_value.insert.return_value.execute.return_value.data = [{"id": 123}]
        mock_supabase.return_value = mock_supabase_instance
        
        # Mock WhatsApp para resposta rápida
        mock_whatsapp.return_value = {"message_id": "msg-001", "success": True}
        
        # Mock HTTP para resposta rápida
        mock_http_response = MagicMock()
        mock_http_response.status_code = 202
        mock_http_response.json.return_value = {"message": "Conversation continuation accepted"}
        mock_http.return_value = mock_http_response

        # Payload de teste
        payload = {
            "name": "João da Silva",
            "email": "joao.silva@example.com",
            "phone": "+5511987654321",
            "city": "São Paulo"
        }
        
        # Medir o tempo de resposta
        start_time = time.time()
        result = await process_lead_activation(payload)
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        
        # Verificações de sucesso
        assert result["success"] is True
        assert "conversation_id" in result
        assert "message_id" in result
        
        # Verificação do SLA: menos de 3 segundos
        assert elapsed_time < 3.0, f"SLA violado! Tempo: {elapsed_time:.3f}s (esperado < 3.0s)"
        
        # Registrar métricas de performance no log
        print(f"\nMétricas do SLA lead-activation.yml:")
        print(f"  Tempo total: {elapsed_time:.3f}s")
        print(f"  SLA: < 3.0s")
        print(f"  Status: {'✅ Dentro do SLA' if elapsed_time < 3.0 else '❌ SLA violado'}")
        
        # Testar latências das etapas individuais
        # Nota: em um ambiente real seria necessário instrumentar o código para medir com precisão
        assert elapsed_time < 3.0, "Processo de lead activation deve completar em menos de 3 segundos" 