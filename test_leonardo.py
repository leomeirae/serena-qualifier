#!/usr/bin/env python3
"""
Teste Automatizado do Template WhatsApp "prosseguir_com_solicitacao"
Teste específico para Leonardo (+5581997498268)
"""

import asyncio
import json
import os
from dotenv import load_dotenv
import sys
sys.path.append('scripts')

from whatsapp_sender import send_whatsapp_template_message

# Load environment variables
load_dotenv()

async def test_leonardo_prosseguir():
    """
    Teste automatizado para Leonardo usando template prosseguir_com_solicitacao
    """
    
    # Dados do teste - Leonardo
    test_phone = "+5581997498268"
    lead_name = "Leonardo"
    
    print(f"🧪 TESTE DO TEMPLATE: prosseguir_com_solicitacao")
    print(f"📱 Telefone: {test_phone}")
    print(f"👤 Nome do Lead: {lead_name}")
    print(f"\n📝 Conteúdo do template que será enviado:")
    print(f"Olá, {lead_name}.")
    print(f"")
    print(f"Cadastro recebido! ✅")
    print(f"")
    print(f"Para ativar seu perfil, só precisamos confirmar alguns dados com você. É super rápido.")
    print(f"")
    print(f"Clique abaixo para dar o último passo.")
    
    try:
        # Configurar componentes do template com o nome do lead
        components = [
            {
                "type": "body",
                "parameters": [
                    {
                        "type": "text",
                        "text": lead_name
                    }
                ]
            }
        ]
        
        print(f"\n🚀 Enviando template 'prosseguir_com_solicitacao'...")
        print(f"📋 Components: {json.dumps(components, indent=2)}")
        
        # Enviar mensagem template
        result = await send_whatsapp_template_message(
            phone=test_phone,
            template_name="prosseguir_com_solicitacao",
            components=components
        )
        
        # Exibir resultado
        print(f"\n📊 RESULTADO DO TESTE:")
        print(f"✅ Sucesso: {result.get('success', False)}")
        
        if result.get('success'):
            print(f"🆔 Message ID: {result.get('message_id', 'N/A')}")
            print(f"📱 Enviado para: {test_phone}")
            print(f"👤 Nome usado: {lead_name}")
            print(f"✨ Template enviado com sucesso!")
            
            # Exibir resposta completa da API
            if result.get('response'):
                print(f"\n📋 Resposta completa da API:")
                print(json.dumps(result['response'], indent=2))
        else:
            print(f"❌ Erro: {result.get('error', 'Erro desconhecido')}")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

async def validate_environment():
    """Valida se as variáveis de ambiente estão configuradas"""
    required_vars = [
        "WHATSAPP_API_TOKEN",
        "WHATSAPP_PHONE_NUMBER_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variáveis de ambiente ausentes: {', '.join(missing_vars)}")
        print(f"📋 Configure no arquivo .env:")
        for var in missing_vars:
            print(f"   {var}=seu_valor_aqui")
        return False
    
    print(f"✅ Variáveis de ambiente configuradas")
    return True

async def main():
    """Função principal do teste"""
    print(f"🧪 TESTE AUTOMATIZADO - Leonardo - Template 'prosseguir_com_solicitacao'")
    print(f"=" * 70)
    
    # Validar environment
    if not await validate_environment():
        return
    
    # Executar teste
    await test_leonardo_prosseguir()

if __name__ == "__main__":
    asyncio.run(main()) 