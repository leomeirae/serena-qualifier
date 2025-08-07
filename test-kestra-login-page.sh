#!/bin/bash

# Teste da Página de Login do Kestra v0.24.0
# Data: $(date)

echo "🔍 Testando Página de Login do Kestra v0.24.0"
echo "=============================================="
echo ""

KESTRA_URL="https://kestra.darwinai.com.br"
LOGIN_URL="$KESTRA_URL/ui/login"

echo "📋 URLs de Teste:"
echo "   URL Principal: $KESTRA_URL"
echo "   URL de Login: $LOGIN_URL"
echo ""

# 1. Testar acesso à página de login
echo "1. Testando acesso à página de login..."
echo ""

LOGIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$LOGIN_URL" 2>/dev/null)

if [ "$LOGIN_STATUS" = "200" ]; then
    echo "   ✅ Página de login acessível (200)"
elif [ "$LOGIN_STATUS" = "401" ]; then
    echo "   ⚠️  Autenticação básica requerida (401)"
elif [ "$LOGIN_STATUS" = "302" ] || [ "$LOGIN_STATUS" = "307" ]; then
    echo "   ⚠️  Redirecionamento detectado ($LOGIN_STATUS)"
else
    echo "   ❌ Status inesperado: $LOGIN_STATUS"
fi

echo ""

# 2. Verificar conteúdo da página de login
echo "2. Verificando conteúdo da página de login..."
echo ""

LOGIN_CONTENT=$(curl -s "$LOGIN_URL" 2>/dev/null | head -50)

if echo "$LOGIN_CONTENT" | grep -q -i "login\|signin\|auth"; then
    echo "   ✅ Página de login detectada"
    echo "   Conteúdo encontrado:"
    echo "$LOGIN_CONTENT" | grep -i "login\|signin\|auth\|form" | head -3
elif echo "$LOGIN_CONTENT" | grep -q -i "kestra"; then
    echo "   ✅ Página do Kestra detectada"
else
    echo "   ⚠️  Conteúdo não reconhecido"
    echo "   Primeiras linhas:"
    echo "$LOGIN_CONTENT" | head -5
fi

echo ""

# 3. Testar redirecionamento da URL principal
echo "3. Testando redirecionamento da URL principal..."
echo ""

MAIN_RESPONSE=$(curl -s -I "$KESTRA_URL" 2>/dev/null | grep -E "(HTTP|Location)" | head -5)

echo "   Resposta da URL principal:"
echo "$MAIN_RESPONSE"

echo ""

# 4. Verificar se há formulário de login
echo "4. Verificando formulário de login..."
echo ""

FORM_DETECTED=$(echo "$LOGIN_CONTENT" | grep -i "form\|input\|password\|username" | head -3)

if [ -n "$FORM_DETECTED" ]; then
    echo "   ✅ Formulário de login detectado:"
    echo "$FORM_DETECTED"
else
    echo "   ⚠️  Formulário de login não detectado"
fi

echo ""

# 5. Testar credenciais via POST (se possível)
echo "5. Verificando se é possível fazer login via API..."
echo ""

# Tentar acessar a API para ver se precisa de autenticação
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$KESTRA_URL/api/v1/" 2>/dev/null)

if [ "$API_STATUS" = "401" ]; then
    echo "   ✅ API requer autenticação (401)"
elif [ "$API_STATUS" = "200" ]; then
    echo "   ⚠️  API não requer autenticação (200)"
else
    echo "   ⚠️  Status da API: $API_STATUS"
fi

echo ""
echo "=============================================="
echo "📋 Resumo do Diagnóstico:"
echo ""

if [ "$LOGIN_STATUS" = "200" ]; then
    echo "✅ PÁGINA DE LOGIN FUNCIONANDO!"
    echo "   Acesse: $LOGIN_URL"
    echo "   Use as credenciais:"
    echo "   - Username: leonardo@darwinai.com.br"
    echo "   - Password: @Atjlc151523"
else
    echo "❌ PROBLEMA COM PÁGINA DE LOGIN"
    echo "   Status: $LOGIN_STATUS"
    echo "   Verifique a configuração do Kestra"
fi

echo ""
echo "🌐 Para acessar:"
echo "   URL: $LOGIN_URL"
echo "   Ou: $KESTRA_URL (será redirecionado)"
echo ""
echo "🔧 Se não funcionar:"
echo "   1. Verificar configuração no docker-compose"
echo "   2. Reiniciar container kestra"
echo "   3. Verificar logs do container"
