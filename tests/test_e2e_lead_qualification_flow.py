"""
Teste End-to-End: Fluxo Completo de Qualificação de Lead

Este teste simula a jornada completa de um lead, interagindo com o sistema
exclusivamente através de APIs e webhooks, como um usuário real.

Fluxo:
1.  POST para o webhook do Kestra simulando o envio de um formulário.
2.  Espera para o sistema processar e enviar a primeira mensagem.
3.  POST para o webhook do WhatsApp simulando a resposta do lead.
4.  Espera para a IA processar a conversa e gerar uma resposta.
5.  Valida no Supabase se a resposta da IA foi registrada corretamente.
"""

import os
import requests
import time
import json
import pytest
from dotenv import load_dotenv
from supabase import create_client, Client

# --- Configuração do Teste ---
load_dotenv()

# Endpoints da aplicação (assumindo que rodam localmente)
KESTRA_WEBHOOK_URL = "http://localhost:8080/api/v1/executions/webhook/serena.energia/full-lead-qualification-workflow/serena-capture-webhook"
WHATSAPP_WEBHOOK_URL = "http://localhost:8001/webhook" # Porta do whatsapp-service

# Dados do Lead (extraídos do formulário)
LEAD_DATA = {
    "lead_name": "Leonardo Franca",
    "lead_email": "lelecomeiralins@gmail.com",
    "lead_phone": "5581997498268", # Formato internacional
    "valor_conta_luz": "500",
    "tipo_cliente": "empresa",
    "cidade": "Recife"
}

# Resposta simulada do Lead
LEAD_RESPONSE_MESSAGE = "Isso mesmo! Moro em Recife, Pernambuco."

# Configuração do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- Teste ---

@pytest.fixture(scope="module")
def supabase_client() -> Client:
    """Cria um cliente Supabase para o módulo de teste."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        pytest.fail("Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY são necessárias.")
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Limpar conversas anteriores para este número de telefone antes do teste
    phone_number = LEAD_DATA["lead_phone"]
    print(f"🧹 Limpando conversas antigas para o número {phone_number}...")
    client.table("messages").delete().eq("phone_number", phone_number).execute()
    client.table("active_conversations").delete().eq("phone_number", phone_number).execute()
    print("✅ Limpeza concluída.")
    
    return client

def test_full_lead_qualification_journey(supabase_client: Client):
    """
    Executa o teste de ponta a ponta para a jornada de qualificação do lead.
    """
    # ETAPA 1: Simular envio do formulário para o Kestra
    print(f"\n🚀 ETAPA 1: Enviando dados do formulário para o Kestra...")
    try:
        response_kestra = requests.post(KESTRA_WEBHOOK_URL, json=LEAD_DATA, timeout=15)
        response_kestra.raise_for_status()
        print(f"✅ Sucesso! Kestra respondeu com status {response_kestra.status_code}.")
        assert response_kestra.status_code == 200
        execution_id = response_kestra.json().get("executionId")
        print(f"🆔 ID da Execução Kestra: {execution_id}")

    except requests.exceptions.RequestException as e:
        pytest.fail(f"❌ Falha ao acionar o webhook do Kestra. O ambiente está de pé? Erro: {e}")

    # ETAPA 2: Aguardar o envio da mensagem de boas-vindas
    print("\n⏳ ETAPA 2: Aguardando 20 segundos para o workflow enviar a mensagem de boas-vindas...")
    time.sleep(20)

    # ETAPA 3: Simular resposta do usuário no WhatsApp
    print(f"💬 ETAPA 3: Simulando resposta do lead via webhook do WhatsApp...")
    whatsapp_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "BOT_PHONE_NUMBER",
                        "phone_number_id": "BOT_PHONE_NUMBER_ID"
                    },
                    "contacts": [{ "profile": { "name": LEAD_DATA["lead_name"] }, "wa_id": LEAD_DATA["lead_phone"] }],
                    "messages": [{
                        "from": LEAD_DATA["lead_phone"],
                        "id": "wamid.TEST_MESSAGE_ID",
                        "timestamp": str(int(time.time())),
                        "text": { "body": LEAD_RESPONSE_MESSAGE },
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }

    try:
        response_whatsapp = requests.post(WHATSAPP_WEBHOOK_URL, json=whatsapp_payload, timeout=15)
        response_whatsapp.raise_for_status()
        print(f"✅ Sucesso! Webhook do WhatsApp respondeu com status {response_whatsapp.status_code}.")
        assert response_whatsapp.status_code == 200

    except requests.exceptions.RequestException as e:
        pytest.fail(f"❌ Falha ao acionar o webhook do WhatsApp. O serviço está de pé? Erro: {e}")

    # ETAPA 4: Aguardar processamento da IA
    print("\n🧠 ETAPA 4: Aguardando 45 segundos para o agente IA processar e responder...")
    time.sleep(45)

    # ETAPA 5: Validar resultado no Supabase
    print("📊 ETAPA 5: Validando o resultado no banco de dados Supabase...")
    try:
        # Buscar as últimas 3 mensagens para verificar a conversa
        messages_response = supabase_client.table("messages") \
            .select("role, content") \
            .eq("phone_number", LEAD_DATA["lead_phone"]) \
            .order("created_at", desc=False) \
            .execute()

        assert len(messages_response.data) > 1, "A conversa deveria ter pelo menos a mensagem do usuário e a resposta da IA."
        
        print("\n--- Histórico da Conversa Salvo ---")
        for msg in messages_response.data:
            print(f"[{msg['role']}] {msg['content']}")
        print("-----------------------------------")

        # A última mensagem deve ser do assistente
        last_message = messages_response.data[-1]
        assert last_message['role'] == 'assistant', "A última mensagem no histórico deveria ser do 'assistant'."
        
        # A resposta da IA deve ser contextual e conter informações sobre os planos
        ai_response_content = last_message['content'].lower()
        assert "plano" in ai_response_content or "desconto" in ai_response_content, \
            "A resposta da IA deveria mencionar 'plano' ou 'desconto'."
        assert "recife" in ai_response_content, "A resposta da IA deveria confirmar a cidade 'Recife'."

        print("\n✅ Validação no Supabase concluída com sucesso!")
        print("🎉 Teste End-to-End finalizado com sucesso!")

    except Exception as e:
        pytest.fail(f"❌ Falha na validação do Supabase. Erro: {e}") 