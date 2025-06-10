#!/usr/bin/env python3
"""
Teste do Endpoint FastAPI para Template "prosseguir_com_solicitacao"
Testa o endpoint POST /whatsapp/send_prosseguir
"""

import requests
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_prosseguir_api_endpoint():
    """
    Testa o endpoint FastAPI para enviar template prosseguir_com_solicitacao
    """
    
    # URL do servidor FastAPI (assumindo que está rodando na porta 8000)
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/whatsapp/send_prosseguir"
    
    # Configurações do teste
    test_phone = input("Digite o número de telefone para teste (com código do país, ex: +5511999999999): ").strip()
    if not test_phone:
        test_phone = "+5511999999999"
    
    lead_name = input("Digite o nome do lead para teste (ou pressione Enter para usar 'Maria Santos'): ").strip()
    if not lead_name:
        lead_name = "Maria Santos"
    
    print(f"\n🧪 TESTE DO ENDPOINT: POST /whatsapp/send_prosseguir")
    print(f"🌐 URL: {endpoint}")
    print(f"📱 Telefone: {test_phone}")
    print(f"👤 Nome do Lead: {lead_name}")
    
    # Payload para o endpoint
    payload = {
        "phone": test_phone,
        "lead_name": lead_name
    }
    
    print(f"\n📋 Payload:")
    print(json.dumps(payload, indent=2))
    
    confirm = input(f"\n❓ Confirma o teste do endpoint? (s/N): ").strip().lower()
    if confirm not in ['s', 'sim', 'y', 'yes']:
        print("❌ Teste cancelado pelo usuário")
        return
    
    try:
        print(f"\n🚀 Enviando request para {endpoint}...")
        
        # Fazer request POST
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📊 RESULTADO DO TESTE:")
        print(f"🔢 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso: {result.get('success', False)}")
            print(f"📧 Mensagem: {result.get('message', 'N/A')}")
            print(f"📱 Telefone: {result.get('phone', 'N/A')}")
            print(f"🆔 Message ID: {result.get('message_id', 'N/A')}")
            
            print(f"\n📋 Resposta completa:")
            print(json.dumps(result, indent=2))
            
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            try:
                error_detail = response.json()
                print(f"📋 Detalhes do erro:")
                print(json.dumps(error_detail, indent=2))
            except:
                print(f"📋 Resposta raw: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print(f"❌ Erro de conexão - Verifique se o servidor FastAPI está rodando")
        print(f"💡 Para iniciar o servidor: uvicorn scripts.whatsapp_sender:app --host 0.0.0.0 --port 8000")
    except requests.exceptions.Timeout:
        print(f"❌ Timeout na requisição")
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_health_endpoint():
    """Testa se o servidor está rodando"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor FastAPI está rodando")
            return True
        else:
            print(f"⚠️  Servidor respondeu com status {response.status_code}")
            return False
    except:
        print("❌ Servidor FastAPI não está respondendo")
        print("💡 Inicie com: uvicorn scripts.whatsapp_sender:app --host 0.0.0.0 --port 8000")
        return False

async def main():
    """Função principal do teste"""
    print(f"🧪 TESTE DO ENDPOINT API - Template 'prosseguir_com_solicitacao'")
    print(f"=" * 70)
    
    # Verificar se servidor está rodando
    print(f"🔍 Verificando servidor...")
    if not await test_health_endpoint():
        return
    
    # Executar teste do endpoint
    await test_prosseguir_api_endpoint()

if __name__ == "__main__":
    asyncio.run(main()) 