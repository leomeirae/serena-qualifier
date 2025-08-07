#!/bin/bash

# Teste Final de Login do Kestra v0.24.0
# Data: $(date)

echo "🔍 Teste Final de Login do Kestra v0.24.0"
echo "=========================================="
echo ""

KESTRA_URL="https://kestra.darwinai.com.br"
USERNAME="leonardo@darwinai.com.br"
PASSWORD="@Atjlc151523"

echo "📋 Testando diferentes cenários de autenticação..."
echo ""

# Teste 1: Verificar se a configuração foi aplicada
echo "1. Verificando se a configuração foi aplicada..."
echo ""

# Testar se há WWW-Authenticate header
WWW_AUTH=$(curl -s -I "$KESTRA_URL/api/v1/flows" 2>/dev/null | grep -i "www-authenticate" | head -1)

if [ -n "$WWW_AUTH" ]; then
    echo "   ✅ WWW-Authenticate header encontrado:"
    echo "   $WWW_AUTH"
else
    echo "   ⚠️  WWW-Authenticate header não encontrado"
    echo "   Isso pode indicar que a autenticação não está configurada"
fi

echo ""

# Teste 2: Testar diferentes combinações de credenciais
echo "2. Testando diferentes combinações de credenciais..."
echo ""

# Credenciais originais
echo "   Teste 1: Credenciais originais..."
STATUS1=$(curl -s -o /dev/null -w "%{http_code}" -u "$USERNAME:$PASSWORD" "$KESTRA_URL/api/v1/flows" 2>/dev/null)
echo "   Status: $STATUS1"

# Senha sem @
echo "   Teste 2: Senha sem @..."
STATUS2=$(curl -s -o /dev/null -w "%{http_code}" -u "$USERNAME:Atjlc151523" "$KESTRA_URL/api/v1/flows" 2>/dev/null)
echo "   Status: $STATUS2"

# Username simplificado
echo "   Teste 3: Username simplificado..."
STATUS3=$(curl -s -o /dev/null -w "%{http_code}" -u "leonardo:$PASSWORD" "$KESTRA_URL/api/v1/flows" 2>/dev/null)
echo "   Status: $STATUS3"

# Sem autenticação
echo "   Teste 4: Sem autenticação..."
STATUS4=$(curl -s -o /dev/null -w "%{http_code}" "$KESTRA_URL/api/v1/flows" 2>/dev/null)
echo "   Status: $STATUS4"

echo ""

# Teste 3: Verificar se o container foi reiniciado
echo "3. Verificando se as mudanças foram aplicadas..."
echo ""

# Verificar se há diferença entre com e sem autenticação
if [ "$STATUS1" = "$STATUS4" ]; then
    echo "   ❌ PROBLEMA: Status igual com e sem autenticação"
    echo "   Isso indica que a autenticação não está funcionando"
    echo "   Possíveis causas:"
    echo "   1. Container não foi reiniciado"
    echo "   2. Configuração não foi aplicada"
    echo "   3. Variáveis de ambiente não estão corretas"
else
    echo "   ✅ Status diferente com e sem autenticação"
    echo "   Autenticação está funcionando"
fi

echo ""

# Teste 4: Verificar se conseguimos acessar o dashboard
echo "4. Testando acesso ao dashboard..."
echo ""

DASHBOARD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -u "$USERNAME:$PASSWORD" "$KESTRA_URL/ui/" 2>/dev/null)

if [ "$DASHBOARD_STATUS" = "200" ]; then
    echo "   ✅ Dashboard acessível com autenticação"
else
    echo "   ❌ Dashboard não acessível (Status: $DASHBOARD_STATUS)"
fi

echo ""

# Teste 5: Verificar se há Setup Page
echo "5. Verificando Setup Page..."
echo ""

SETUP_CONTENT=$(curl -s "$KESTRA_URL/ui/" 2>/dev/null | grep -i "setup\|welcome\|config\|admin" | head -3)

if [ -n "$SETUP_CONTENT" ]; then
    echo "   ✅ Setup Page detectada:"
    echo "$SETUP_CONTENT"
else
    echo "   ⚠️  Setup Page não detectada"
fi

echo ""
echo "=========================================="
echo "📋 Resumo dos Testes:"
echo ""

if [ "$STATUS1" = "200" ] || [ "$STATUS2" = "200" ] || [ "$STATUS3" = "200" ]; then
    echo "✅ LOGIN FUNCIONANDO!"
    if [ "$STATUS1" = "200" ]; then
        echo "   Use: $USERNAME / $PASSWORD"
    elif [ "$STATUS2" = "200" ]; then
        echo "   Use: $USERNAME / Atjlc151523"
    elif [ "$STATUS3" = "200" ]; then
        echo "   Use: leonardo / $PASSWORD"
    fi
elif [ "$STATUS1" = "$STATUS4" ]; then
    echo "❌ PROBLEMA DE CONFIGURAÇÃO"
    echo ""
    echo "🔧 Ações necessárias:"
    echo "   1. Verificar se o container foi reiniciado no Coolify"
    echo "   2. Verificar logs do container kestra"
    echo "   3. Verificar se as variáveis estão corretas"
    echo "   4. Aguardar mais tempo para reinicialização"
    echo ""
    echo "🌐 Para verificar no Coolify:"
    echo "   1. Acesse o painel do Coolify"
    echo "   2. Vá para o projeto serena-qualifier"
    echo "   3. Verifique se o container kestra foi reiniciado"
    echo "   4. Verifique os logs do container"
else
    echo "⚠️  STATUS INESPERADO"
    echo "   Verificar logs do container"
fi

echo ""
echo "🌐 URLs para testar:"
echo "   Dashboard: $KESTRA_URL/ui/"
echo "   API: $KESTRA_URL/api/v1/flows"
echo "   Login: $KESTRA_URL/ui/login"
