#!/usr/bin/env python3
"""
Verificador e corretor de formato .env
=====================================
"""

print("🔧 DIAGNÓSTICO DO ARQUIVO .env")
print("=" * 40)

# Tentar ler o arquivo .env atual
try:
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    print(f"📄 Arquivo .env encontrado com {len(lines)} linhas")
    print("\n🔍 Conteúdo atual (primeiras 10 linhas):")
    
    for i, line in enumerate(lines[:10], 1):
        # Mostrar caracteres especiais
        line_repr = repr(line.rstrip())
        print(f"  Linha {i}: {line_repr}")
        
        # Verificar problemas comuns
        problems = []
        if line.strip().startswith('#'):
            problems.append("Comentário")
        elif '=' not in line and line.strip():
            problems.append("Sem '='")
        elif line.count('=') > 1:
            problems.append("Múltiplos '='")
        elif line.startswith(' ') or line.startswith('\t'):
            problems.append("Espaço/tab inicial")
        
        if problems:
            print(f"    ⚠️  Problemas: {', '.join(problems)}")

except FileNotFoundError:
    print("❌ Arquivo .env não encontrado na pasta atual")
    print("📁 Pasta atual:", os.getcwd())

print("\n✅ FORMATO CORRETO DO .env:")
print("━" * 40)
print("OPENAI_API_KEY=sk-proj-sua-chave-aqui")
print("SUPABASE_URL=https://sua-instancia.supabase.co") 
print("SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
print("━" * 40)

print("\n🚫 FORMATOS INCORRETOS (evitar):")
print("❌ OPENAI_API_KEY = sk-chave  # com espaços")
print("❌ # OPENAI_API_KEY=sk-chave  # comentário")
print('❌ OPENAI_API_KEY="sk-chave"  # aspas desnecessárias')
print("❌ export OPENAI_API_KEY=sk-chave  # comando bash")

print("\n📝 REGRAS:")
print("• Uma variável por linha")
print("• Formato: NOME=valor")
print("• Sem espaços antes/depois do '='")
print("• Sem aspas (a menos que façam parte do valor)")
print("• Sem comentários na mesma linha")
print("• Sem comandos 'export'")

print("\n🔄 Para corrigir:")
print("1. Abra o arquivo .env no editor")
print("2. Remova espaços extras e comentários")
print("3. Use o formato exato mostrado acima")
print("4. Execute: python test_credentials.py")

import os 