#!/bin/bash

# Script de Diagnóstico de Autenticação do Kestra v0.24.0
# Data: $(date)

echo "🔍 Diagnóstico de Autenticação do Kestra v0.24.0"
echo "================================================"
echo ""

# Configurações
KESTRA_URL="https://kestra.darwinai.com.br"
USERNAME="leonardo@darwinai.com.br"
PASSWORD="@Atjlc151523"

# 1. Teste de conectividade básica
echo "1. Testando conectividade básica..."
echo "   URL: $KESTRA_URL"
echo ""

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$KESTRA_URL" 2>/dev/null)

if [ "$HTTP_STATUS" = "401" ]; then
    echo "   ✅ Serviço respondendo (401 = Autenticação requerida - NORMAL)"
elif [ "$HTTP_STATUS" = "200" ]; then
    echo "   ⚠️  Serviço respondendo sem autenticação (200)"
elif [ "$HTTP_STATUS" = "000" ]; then
    echo "   ❌ Serviço não acessível (timeout/conexão recusada)"
else
    echo "   ⚠️  Status HTTP: $HTTP_STATUS"
fi

echo ""

# 2. Teste de autenticação
echo "2. Testando autenticação..."
echo "   Username: $USERNAME"
echo "   Password: ${PASSWORD:0:3}***"
echo ""

AUTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -u "$USERNAME:$PASSWORD" "$KESTRA_URL" 2>/dev/null)

if [ "$AUTH_STATUS" = "200" ]; then
    echo "   ✅ Autenticação funcionando (200)"
elif [ "$AUTH_STATUS" = "401" ]; then
    echo "   ❌ Credenciais inválidas (401)"
elif [ "$AUTH_STATUS" = "000" ]; then
    echo "   ❌ Erro de conexão"
else
    echo "   ⚠️  Status HTTP: $AUTH_STATUS"
fi

echo ""

# 3. Teste de resposta do conteúdo
echo "3. Verificando resposta do conteúdo..."
echo ""

CONTENT=$(curl -s "$KESTRA_URL" 2>/dev/null | head -20)

if echo "$CONTENT" | grep -q -i "kestra"; then
    echo "   ✅ Página do Kestra detectada"
elif echo "$CONTENT" | grep -q -i "login\|auth"; then
    echo "   ✅ Página de login detectada"
else
    echo "   ⚠️  Conteúdo não reconhecido"
    echo "   Primeiras linhas:"
    echo "$CONTENT" | head -5
fi

echo ""

# 4. Teste com autenticação e conteúdo
echo "4. Testando acesso autenticado..."
echo ""

AUTH_CONTENT=$(curl -s -u "$USERNAME:$PASSWORD" "$KESTRA_URL" 2>/dev/null | head -20)

if echo "$AUTH_CONTENT" | grep -q -i "kestra"; then
    echo "   ✅ Acesso autenticado funcionando"
    echo "   ✅ Kestra v0.24.0 está operacional"
elif echo "$AUTH_CONTENT" | grep -q -i "error\|exception"; then
    echo "   ❌ Erro detectado na resposta"
    echo "   Conteúdo:"
    echo "$AUTH_CONTENT" | head -10
else
    echo "   ⚠️  Resposta não reconhecida"
    echo "   Conteúdo:"
    echo "$AUTH_CONTENT" | head -5
fi

echo ""
echo "================================================"
echo "📋 Resumo do Diagnóstico:"
echo ""

if [ "$HTTP_STATUS" = "401" ] && [ "$AUTH_STATUS" = "200" ]; then
    echo "✅ TUDO FUNCIONANDO CORRETAMENTE!"
    echo "   - Kestra v0.24.0 está operacional"
    echo "   - Autenticação básica funcionando"
    echo "   - Use as credenciais para acessar a interface"
elif [ "$HTTP_STATUS" = "401" ] && [ "$AUTH_STATUS" = "401" ]; then
    echo "❌ PROBLEMA DE CREDENCIAIS"
    echo "   - Serviço está funcionando"
    echo "   - Credenciais estão incorretas"
    echo "   - Verifique as variáveis no Coolify"
else
    echo "⚠️  PROBLEMA DE CONECTIVIDADE"
    echo "   - Verifique se o serviço está rodando"
    echo "   - Verifique logs no Coolify"
fi

echo ""
echo "🔧 Próximos passos:"
echo "   1. Verificar variáveis no Coolify"
echo "   2. Verificar logs do container kestra"
echo "   3. Testar em modo incógnito"
echo "   4. Se necessário, reiniciar o serviço"
