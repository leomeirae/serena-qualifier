#!/bin/bash

# Script para Corrigir Autenticação do Kestra v0.24.0
# Data: $(date)

echo "🔧 Corrigindo Autenticação do Kestra v0.24.0"
echo "============================================="
echo ""

# Configurações
KESTRA_URL="https://kestra.darwinai.com.br"
USERNAME="leonardo@darwinai.com.br"
PASSWORD="@Atjlc151523"

echo "🔍 Diagnóstico Inicial..."
echo ""

# 1. Verificar se o serviço está respondendo
echo "1. Verificando conectividade..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$KESTRA_URL/ui/" 2>/dev/null)

if [ "$HTTP_STATUS" = "200" ]; then
    echo "   ✅ Serviço respondendo (200)"
elif [ "$HTTP_STATUS" = "401" ]; then
    echo "   ✅ Serviço respondendo (401 = Auth requerida)"
else
    echo "   ❌ Problema de conectividade (Status: $HTTP_STATUS)"
    exit 1
fi

echo ""

# 2. Testar diferentes combinações de credenciais
echo "2. Testando diferentes configurações de credenciais..."
echo ""

# Teste 1: Credenciais originais
echo "   Teste 1: Credenciais originais..."
AUTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -u "$USERNAME:$PASSWORD" "$KESTRA_URL/ui/" 2>/dev/null)
echo "   Status: $AUTH_STATUS"

# Teste 2: Sem @ na senha
echo "   Teste 2: Senha sem @..."
PASSWORD_NO_AT="Atjlc151523"
AUTH_STATUS2=$(curl -s -o /dev/null -w "%{http_code}" -u "$USERNAME:$PASSWORD_NO_AT" "$KESTRA_URL/ui/" 2>/dev/null)
echo "   Status: $AUTH_STATUS2"

# Teste 3: Username diferente
echo "   Teste 3: Username simplificado..."
USERNAME_SIMPLE="leonardo"
AUTH_STATUS3=$(curl -s -o /dev/null -w "%{http_code}" -u "$USERNAME_SIMPLE:$PASSWORD" "$KESTRA_URL/ui/" 2>/dev/null)
echo "   Status: $AUTH_STATUS3"

echo ""

# 3. Verificar se há Setup Page disponível
echo "3. Verificando Setup Page..."
echo ""

SETUP_CONTENT=$(curl -s "$KESTRA_URL/ui/" 2>/dev/null | grep -i "setup\|config\|admin" | head -3)

if [ -n "$SETUP_CONTENT" ]; then
    echo "   ✅ Setup Page detectada"
    echo "   Conteúdo encontrado:"
    echo "$SETUP_CONTENT"
else
    echo "   ⚠️  Setup Page não detectada"
fi

echo ""

# 4. Verificar logs do container (se possível)
echo "4. Verificando configuração atual..."
echo ""

echo "   📋 Variáveis de ambiente necessárias no Coolify:"
echo "   KESTRA_SERVER_BASICAUTH_USERNAME=leonardo@darwinai.com.br"
echo "   KESTRA_SERVER_BASICAUTH_PASSWORD=@Atjlc151523"
echo ""

echo "   🔧 Soluções possíveis:"
echo ""

if [ "$AUTH_STATUS" = "200" ]; then
    echo "   ✅ Credenciais originais funcionando!"
    echo "   Use: $USERNAME / $PASSWORD"
elif [ "$AUTH_STATUS2" = "200" ]; then
    echo "   ✅ Credenciais sem @ funcionando!"
    echo "   Use: $USERNAME / $PASSWORD_NO_AT"
elif [ "$AUTH_STATUS3" = "200" ]; then
    echo "   ✅ Username simplificado funcionando!"
    echo "   Use: $USERNAME_SIMPLE / $PASSWORD"
else
    echo "   ❌ Nenhuma combinação funcionou"
    echo ""
    echo "   🛠️  Ações necessárias:"
    echo "   1. Verificar variáveis no Coolify"
    echo "   2. Reiniciar o container kestra"
    echo "   3. Usar Setup Page para configurar credenciais"
    echo "   4. Verificar logs do container"
fi

echo ""
echo "============================================="
echo "📋 Resumo das Ações:"
echo ""

if [ "$AUTH_STATUS" = "200" ] || [ "$AUTH_STATUS2" = "200" ] || [ "$AUTH_STATUS3" = "200" ]; then
    echo "✅ CREDENCIAIS ENCONTRADAS!"
    echo "   Use as credenciais que retornaram status 200"
else
    echo "❌ PROBLEMA DE CONFIGURAÇÃO"
    echo ""
    echo "🔧 Próximos passos:"
    echo "   1. Acesse o painel do Coolify"
    echo "   2. Verifique as variáveis de ambiente do projeto"
    echo "   3. Adicione/atualize as variáveis:"
    echo "      KESTRA_SERVER_BASICAUTH_USERNAME=leonardo@darwinai.com.br"
    echo "      KESTRA_SERVER_BASICAUTH_PASSWORD=@Atjlc151523"
    echo "   4. Reinicie o container kestra"
    echo "   5. Teste novamente"
    echo ""
    echo "🌐 Ou use a Setup Page:"
    echo "   Acesse: $KESTRA_URL/ui/"
    echo "   Configure as credenciais via interface web"
fi
