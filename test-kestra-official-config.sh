#!/bin/bash

# Teste da Configuração Oficial do Kestra v0.24.0
# Baseado na documentação oficial: https://kestra.io/docs/administrator-guide/basic-auth-troubleshooting
# Data: $(date)

echo "🔍 Teste da Configuração Oficial do Kestra v0.24.0"
echo "=================================================="
echo ""

KESTRA_URL="https://kestra.darwinai.com.br"
USERNAME="leonardo@darwinai.com.br"
PASSWORD="@Atjlc151523"

echo "📋 Configuração Aplicada (baseada na documentação oficial):"
echo "   kestra:"
echo "     server:"
echo "       basicAuth:"
echo "         username: $USERNAME"
echo "         password: $PASSWORD"
echo ""

echo "🔧 Mudanças Realizadas:"
echo "   1. Removida configuração incorreta do micronaut.server.basic-auth"
echo "   2. Adicionada configuração correta em kestra.server.basicAuth"
echo "   3. Removido flag 'enabled' (não é mais necessário na v0.24.0)"
echo ""

# Teste 1: Verificar se a configuração foi aplicada
echo "1. Verificando se a nova configuração foi aplicada..."
echo ""

# Aguardar um pouco para o container reiniciar
echo "   Aguardando reinicialização do container..."
sleep 10

# Testar se há WWW-Authenticate header
WWW_AUTH=$(curl -s -I "$KESTRA_URL/api/v1/flows" 2>/dev/null | grep -i "www-authenticate" | head -1)

if [ -n "$WWW_AUTH" ]; then
    echo "   ✅ WWW-Authenticate header encontrado:"
    echo "   $WWW_AUTH"
else
    echo "   ⚠️  WWW-Authenticate header não encontrado"
fi

echo ""

# Teste 2: Testar credenciais com a nova configuração
echo "2. Testando credenciais com a configuração oficial..."
echo ""

# Testar credenciais
AUTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -u "$USERNAME:$PASSWORD" "$KESTRA_URL/api/v1/flows" 2>/dev/null)

if [ "$AUTH_STATUS" = "200" ]; then
    echo "   ✅ LOGIN FUNCIONANDO! (Status: $AUTH_STATUS)"
    echo "   Credenciais aceitas com sucesso!"
elif [ "$AUTH_STATUS" = "401" ]; then
    echo "   ❌ Credenciais rejeitadas (Status: $AUTH_STATUS)"
    echo "   Verificar se o container foi reiniciado"
else
    echo "   ⚠️  Status inesperado: $AUTH_STATUS"
fi

echo ""

# Teste 3: Verificar acesso ao dashboard
echo "3. Testando acesso ao dashboard..."
echo ""

DASHBOARD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -u "$USERNAME:$PASSWORD" "$KESTRA_URL/ui/" 2>/dev/null)

if [ "$DASHBOARD_STATUS" = "200" ]; then
    echo "   ✅ Dashboard acessível com autenticação"
else
    echo "   ❌ Dashboard não acessível (Status: $DASHBOARD_STATUS)"
fi

echo ""

# Teste 4: Verificar Setup Page
echo "4. Verificando Setup Page..."
echo ""

SETUP_CONTENT=$(curl -s "$KESTRA_URL/ui/" 2>/dev/null | grep -i "setup\|welcome\|config\|admin" | head -3)

if [ -n "$SETUP_CONTENT" ]; then
    echo "   ✅ Setup Page detectada:"
    echo "$SETUP_CONTENT"
else
    echo "   ⚠️  Setup Page não detectada"
fi

echo ""
echo "=================================================="
echo "📋 Resumo dos Testes:"
echo ""

if [ "$AUTH_STATUS" = "200" ]; then
    echo "✅ CONFIGURAÇÃO OFICIAL FUNCIONANDO!"
    echo "   Login: $USERNAME"
    echo "   Senha: $PASSWORD"
    echo "   URL: $KESTRA_URL"
    echo ""
    echo "🎉 Problema resolvido com a configuração oficial!"
else
    echo "❌ AINDA HÁ PROBLEMAS"
    echo ""
    echo "🔧 Próximos passos:"
    echo "   1. Verificar se o container foi reiniciado no Coolify"
    echo "   2. Aguardar mais tempo para reinicialização (pode levar 2-3 minutos)"
    echo "   3. Verificar logs do container kestra"
    echo "   4. Se necessário, usar Setup Page para configurar credenciais"
    echo ""
    echo "📖 Documentação oficial:"
    echo "   https://kestra.io/docs/administrator-guide/basic-auth-troubleshooting"
fi

echo ""
echo "🌐 URLs para testar:"
echo "   Dashboard: $KESTRA_URL/ui/"
echo "   API: $KESTRA_URL/api/v1/flows"
echo "   Login: $KESTRA_URL/ui/login"
