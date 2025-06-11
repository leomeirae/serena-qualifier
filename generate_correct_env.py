#!/usr/bin/env python3
"""
Gerador de arquivo .env corrigido
================================
"""

# Conteúdo correto para o .env
correct_env_content = """WHATSAPP_API_TOKEN=EAAPR0FG5sq8BO9M7rCnpNZC4Vk0SGab3VLdsIrwuzP0ePYODHDNI7kBaUNBSSQkfTh1DvZBzZCk3VyLZCAQRUjcB4hIyhNhZCD77EXKhvzI5sm1ZB7rX13RSoZCcocOUZBRe97fnmPk1PlS2mcVTsXnyyOUlpjtINpJLwFpzgBluaEUYuSqSUaWsjCZCJW3m0Jpuu5QZDZD
WHATSAPP_PHONE_NUMBER_ID=599096403294262
WHATSAPP_BUSINESS_ID=1097835408776820
WHATSAPP_WELCOME_TEMPLATE_NAME=prosseguir_com_solicitacao
OPENAI_API_KEY=sk-proj-dRtmXog4czlQzGkhLXXkLQ-SoVGGd8eFdQGmRzpGG01vHV49P9XsBEYecVSkUJRy_ih-Nom3ZyT3BlbkFJfTw
SUPABASE_URL=https://sua-instancia.supabase.co
SUPABASE_ANON_KEY=sua-chave-anon-supabase-aqui"""

print("🔧 Gerando arquivo .env corrigido...")

with open('.env.new', 'w') as f:
    f.write(correct_env_content.strip())

print("✅ Arquivo .env.new criado!")
print("\n📝 Para aplicar a correção:")
print("mv .env.new .env")
print("\n⚠️  Você ainda precisa configurar:")
print("• SUPABASE_URL=https://sua-instancia-real.supabase.co")
print("• SUPABASE_ANON_KEY=sua-chave-anon-real")
print("\n🧪 Teste depois:")
print("python test_credentials.py") 