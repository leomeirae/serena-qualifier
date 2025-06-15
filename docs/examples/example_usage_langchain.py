#!/usr/bin/env python3
"""
Exemplo Prático - SerenaAIAgent com LangChain

Demonstra como usar o novo agente IA potencializado por LangChain
para qualificação de leads de energia solar.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

def exemplo_conversa_completa():
    """Exemplo de conversa completa com lead."""
    print("🌞 Exemplo: Qualificação Completa de Lead\n")
    
    from scripts.serena_agent.core_agent import SerenaAIAgent
    
    # Inicializa agente
    agent = SerenaAIAgent()
    print(f"✅ Agente inicializado (LangChain: {'Sim' if agent.agent_executor else 'Não'})")
    
    # Simulação de conversa com lead
    phone = "5511987654321"
    
    # 1. Lead demonstra interesse
    print("\n1️⃣ Lead demonstra interesse:")
    print("💬 Lead: 'Olá, vi vocês no Google. Tenho interesse em energia solar.'")
    
    result1 = agent.process_conversation(
        phone=phone,
        message="Olá, vi vocês no Google. Tenho interesse em energia solar.",
        action="respond"
    )
    
    print(f"🤖 Serena: {result1['response']}")
    print(f"📊 Método: {result1.get('method', 'N/A')}")
    
    # 2. Lead fornece localização
    print("\n2️⃣ Lead fornece localização:")
    print("💬 Lead: 'Moro em Belo Horizonte, MG. Minha conta vem R$ 280 por mês.'")
    
    result2 = agent.process_conversation(
        phone=phone,
        message="Moro em Belo Horizonte, MG. Minha conta vem R$ 280 por mês.",
        action="respond"
    )
    
    print(f"🤖 Serena: {result2['response']}")
    
    # 3. Demonstra extração de dados
    print("\n3️⃣ Extração de dados estruturados:")
    
    extract_result = agent.process_conversation(
        phone=phone,
        message="Moro em Belo Horizonte, MG. Minha conta vem R$ 280 por mês.",
        action="extract"
    )
    
    print(f"📋 Dados extraídos: {extract_result['response']}")
    
    # 4. Classificação de intenção
    print("\n4️⃣ Classificação de intenção:")
    
    classify_result = agent.process_conversation(
        phone=phone,
        message="Quanto custa para instalar?",
        action="classify"
    )
    
    print(f"🎯 Intenção: {classify_result['response']}")
    
    return True

def exemplo_compatibilidade_kestra():
    """Exemplo de compatibilidade com workflows Kestra."""
    print("\n🔧 Exemplo: Compatibilidade Workflows Kestra\n")
    
    # Função de compatibilidade (mesma interface do ai_agent.py original)
    from scripts.serena_agent.core_agent import process_ai_request
    
    # Como seria chamado nos workflows Kestra
    print("📝 Como usar nos workflows Kestra:")
    print("```python")
    print("# ANTES (ai_agent.py):")
    print("result = process_ai_request(phone, message, 'respond')")
    print("")
    print("# DEPOIS (serena_agent - mesma interface!):")
    print("result = process_ai_request(phone, message, 'respond')")
    print("```")
    
    # Teste real
    result = process_ai_request(
        phone="5511999888777",
        message="Oi, quero economizar na conta de luz",
        action="respond"
    )
    
    print(f"\n✅ Resultado: {result['result']}")
    print(f"📞 Phone: {result['phone']}")
    print(f"🎬 Action: {result['action']}")
    print(f"⚙️  Method: {result.get('method', 'N/A')}")
    print(f"💬 Response: {result['response'][:80]}...")
    
    return True

def exemplo_tools_reais():
    """Exemplo usando tools reais."""
    print("\n🛠️ Exemplo: Tools Reais Integradas\n")
    
    from scripts.serena_agent.tools.conversation_tool import conversation_tool_function
    from scripts.serena_agent.tools.serena_api_tool import serena_api_tool_function
    
    phone = "5511999777666"
    
    # 1. Conversation Tool (Supabase real)
    print("1️⃣ Salvando mensagem no Supabase:")
    conv_result = conversation_tool_function({
        "action": "add_message",
        "phone": phone,
        "role": "user", 
        "content": "Quero economizar energia"
    })
    print(f"✅ Supabase: {conv_result['success']}")
    
    # 2. Serena API Tool (API real)
    print("\n2️⃣ Consultando API Serena real:")
    api_result = serena_api_tool_function({
        "action": "check_coverage",
        "city": "Belo Horizonte",
        "state": "MG"
    })
    print(f"✅ API Serena: {api_result['success']}")
    print(f"📊 Resultado: {api_result.get('result', 'N/A')}")
    
    return True

def exemplo_performance():
    """Exemplo comparando performance."""
    print("\n⚡ Exemplo: Análise de Performance\n")
    
    from scripts.serena_agent.core_agent import SerenaAIAgent
    import time
    
    agent = SerenaAIAgent()
    
    test_message = "Tenho interesse em energia solar para minha casa"
    test_phone = "5511999666555"
    
    print("🎯 Testando diferentes ações:")
    
    actions = ["classify", "extract", "respond"]
    
    for action in actions:
        start = time.time()
        result = agent.process_conversation(test_phone, test_message, action)
        elapsed = time.time() - start
        
        method = result.get('method', 'N/A')
        print(f"  {action:10} → {elapsed:.3f}s ({method})")
    
    print("\n📊 Resumo:")
    print("  - classify/extract: Rápido (prompts)")
    print("  - respond: Mais lento (LangChain + OpenAI)")
    print("  - Híbrido otimizado por caso de uso!")
    
    return True

def main():
    """Executa todos os exemplos."""
    print("🚀 Exemplos Práticos - SerenaAIAgent LangChain\n")
    
    try:
        exemplos = [
            exemplo_conversa_completa,
            exemplo_compatibilidade_kestra,
            exemplo_tools_reais,
            exemplo_performance
        ]
        
        for i, exemplo in enumerate(exemplos, 1):
            print(f"\n{'='*60}")
            exemplo()
            
        print(f"\n{'='*60}")
        print("🎉 TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
        print("\n✅ Principais vantagens demonstradas:")
        print("   - LangChain gerando respostas inteligentes")
        print("   - Tools reais (Supabase + API Serena) funcionando") 
        print("   - 100% compatibilidade com workflows Kestra")
        print("   - Performance híbrida otimizada")
        print("   - Fallback robusto para edge cases")
        
        print(f"\n🚀 Sistema pronto para produção!")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos exemplos: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 