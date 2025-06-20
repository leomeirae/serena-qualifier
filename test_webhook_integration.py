#!/usr/bin/env python3
"""
Script de teste para validar integração WhatsApp → Webhook → Kestra
"""
import requests
import json
import time
from datetime import datetime

# URLs de teste
WEBHOOK_URL = "http://localhost:8000"
KESTRA_URL = "http://localhost:8081"

def test_webhook_health():
    """Testa health check do webhook service"""
    try:
        response = requests.get(f"{WEBHOOK_URL}/", timeout=5)
        print(f"✅ Health Check: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health Check falhou: {e}")
        return False

def test_webhook_verification():
    """Testa verificação do webhook (challenge do WhatsApp)"""
    try:
        params = {
            "hub.mode": "subscribe",
            "hub.verify_token": "serena_webhook_verify_token",
            "hub.challenge": "test_challenge_123"
        }
        response = requests.get(f"{WEBHOOK_URL}/webhook", params=params, timeout=5)
        print(f"✅ Verificação Webhook: {response.status_code}")
        print(f"   Challenge retornado: {response.text}")
        return response.status_code == 200 and response.text == "test_challenge_123"
    except Exception as e:
        print(f"❌ Verificação falhou: {e}")
        return False

def test_message_processing():
    """Testa processamento de mensagem simulada"""
    try:
        # Simular payload do WhatsApp
        whatsapp_payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "5581999887766",
                            "type": "text",
                            "text": {
                                "body": "Olá! Quero saber sobre energia solar"
                            },
                            "timestamp": str(int(datetime.now().timestamp()))
                        }]
                    }
                }]
            }]
        }
        
        response = requests.post(
            f"{WEBHOOK_URL}/webhook",
            json=whatsapp_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"✅ Processamento Mensagem: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Phone: {data.get('phone')}")
            print(f"   Preview: {data.get('message_preview')}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Processamento falhou: {e}")
        return False

def test_kestra_connection():
    """Testa se Kestra está acessível"""
    try:
        response = requests.get(f"{KESTRA_URL}/api/v1/flows", timeout=5)
        print(f"✅ Kestra API: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Kestra não acessível: {e}")
        return False

def test_direct_kestra_webhook():
    """Testa webhook direto do Kestra"""
    try:
        payload = {
            "phone": "5581999887766",
            "message": "Teste direto para Kestra",
            "timestamp": str(int(datetime.now().timestamp()))
        }
        
        response = requests.post(
            f"{KESTRA_URL}/api/v1/executions/webhook/converse_production_lead",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"✅ Kestra Webhook Direto: {response.status_code}")
        if response.status_code in [200, 202]:
            data = response.json()
            print(f"   Execution ID: {data.get('id', 'N/A')}")
            
        return response.status_code in [200, 202]
    except Exception as e:
        print(f"❌ Webhook Kestra falhou: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🧪 INICIANDO TESTES DE INTEGRAÇÃO")
    print("=" * 50)
    
    tests = [
        ("Health Check Webhook", test_webhook_health),
        ("Verificação Webhook", test_webhook_verification),
        ("Conexão Kestra", test_kestra_connection),
        ("Webhook Direto Kestra", test_direct_kestra_webhook),
        ("Processamento Mensagem", test_message_processing),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)  # Pequena pausa entre testes
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO DOS TESTES:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 RESUMO: {passed}/{len(tests)} testes passaram")
    
    if passed == len(tests):
        print("🎉 TODOS OS TESTES PASSARAM! Integração funcionando!")
    else:
        print("⚠️  Alguns testes falharam. Verifique os serviços.")

if __name__ == "__main__":
    main()
