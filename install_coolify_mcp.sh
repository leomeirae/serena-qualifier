#!/bin/bash

# Script de instalação do Coolify MCP Server
# Autor: Serena Qualifier Team
# Data: Janeiro 2025

set -e

echo "🚀 Instalando Coolify MCP Server..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 é necessário mas não está instalado."
    exit 1
fi

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 é necessário mas não está instalado."
    exit 1
fi

echo "✅ Python e pip encontrados"

# Instalar dependências
echo "📦 Instalando dependências..."
pip3 install -r mcp_coolify_requirements.txt

# Verificar se o arquivo de configuração existe
if [ ! -f "coolify_mcp_config.json" ]; then
    echo "❌ Arquivo de configuração coolify_mcp_config.json não encontrado!"
    exit 1
fi

# Solicitar configuração do usuário
echo ""
echo "🔧 Configuração do Coolify MCP Server"
echo "======================================"

# Solicitar URL base
read -p "Digite a URL base do seu Coolify (ex: https://coolify.darwinai.com.br): " BASE_URL
if [ -z "$BASE_URL" ]; then
    echo "❌ URL base é obrigatória!"
    exit 1
fi

# Solicitar token
read -p "Digite seu token da API do Coolify: " TOKEN
if [ -z "$TOKEN" ]; then
    echo "❌ Token da API é obrigatório!"
    exit 1
fi

# Atualizar arquivo de configuração
echo "📝 Atualizando configuração..."
sed -i.bak "s|YOUR_COOLIFY_TOKEN_HERE|$TOKEN|g" coolify_mcp_config.json
sed -i.bak "s|https://coolify.darwinai.com.br|$BASE_URL|g" coolify_mcp_config.json

# Remover arquivo de backup
rm coolify_mcp_config.json.bak

# Tornar o servidor executável
chmod +x mcp_coolify_server.py

# Teste de conectividade
echo "🔍 Testando conectividade..."
export COOLIFY_BASE_URL="$BASE_URL"
export COOLIFY_TOKEN="$TOKEN"

# Criar script de teste simples
cat > test_coolify_connection.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
import httpx
import json

base_url = os.getenv("COOLIFY_BASE_URL", "").rstrip('/')
token = os.getenv("COOLIFY_TOKEN", "")

if not base_url or not token:
    print("❌ Configuração inválida")
    sys.exit(1)

api_base = f"{base_url}/api/v1"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

try:
    response = httpx.get(f"{api_base}/health", headers=headers, timeout=10)
    response.raise_for_status()
    print("✅ Conectividade com Coolify OK!")
except httpx.HTTPStatusError as e:
    print(f"❌ Erro HTTP {e.response.status_code}: {e.response.text}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro de conexão: {str(e)}")
    sys.exit(1)
EOF

python3 test_coolify_connection.py

# Limpar arquivo de teste
rm test_coolify_connection.py

echo ""
echo "🎉 Instalação concluída com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "==================="
echo "1. Para testar localmente: python3 mcp_coolify_server.py"
echo "2. Para integrar com Cursor:"
echo "   - Copie o conteúdo de coolify_mcp_config.json para sua configuração MCP"
echo "   - Ou adicione o servidor ao seu arquivo de configuração existente"
echo "3. Para integrar com Claude Desktop:"
echo "   - Adicione a configuração ao seu claude_desktop_config.json"
echo ""
echo "📖 Leia o COOLIFY_MCP_SERVER_README.md para mais detalhes"
echo ""
echo "🔧 Configuração salva em coolify_mcp_config.json"
echo "   Base URL: $BASE_URL"
echo "   Token: ${TOKEN:0:10}..."
echo ""
echo "✨ Servidor MCP do Coolify pronto para uso!" 