#!/bin/bash

# Teste Detalhado de Autenticação do Kestra v0.24.0
# Data: $(date)

echo "🔍 Teste Detalhado de Autenticação do Kestra v0.24.0"
echo "===================================================="
echo ""

KESTRA_URL="https://kestra.darwinai.com.br"
USERNAME="leonardo@darwinai.com.br"
PASSWORD="@Atjlc151523"

echo "📋 Configurações de Teste:"
echo "   URL: $KESTRA_URL"
echo "   Username: $USERNAME"
echo "   Password: $PASSWORD"
echo ""

# Teste 1: Verificar se há WWW-Authenticate header
echo "1. Verificando headers de autenticação..."
echo ""

RESPONSE=$(curl -s -I "$KESTRA_URL/ui/" 2>/dev/null)
WWW_AUTH=$(echo "$RESPONSE" | grep -i "www-authenticate" | head -1)

if [ -n "$WWW_AUTH" ]; then
    echo "   ✅ WWW-Authenticate header encontrado:"
    echo "   $WWW_AUTH"
else
    echo "   ⚠️  WWW-Authenticate header não encontrado"
    echo "   Isso pode indicar que a autenticação não está configurada"
fi

echo ""

# Teste 2: Verificar diferentes codificações de senha
echo "2. Testando diferentes codificações de senha..."
echo ""

# Senha original
echo "   Teste 1: Senha original (@Atjlc151523)..."
STATUS1=$(curl -s -o /dev/null -w "%{http_code}" -u "$USERNAME:$PASSWORD" "$KESTRA_URL/ui/" 2>/dev/null)
echo "   Status: $STATUS1"

# Senha sem @
echo "   Teste 2: Senha sem @ (Atjlc151523)..."
STATUS2=$(curl -s -o /dev/null -w "%{http_code}" -u "$USERNAME:Atjlc151523" "$KESTRA_URL/ui/" 2>/dev/null)
echo "   Status: $STATUS2"

# Senha URL encoded
echo "   Teste 3: Senha URL encoded (%40Atjlc151523)..."
STATUS3=$(curl -s -o /dev/null -w "%{http_code}" -u "$USERNAME:%40Atjlc151523" "$KESTRA_URL/ui/" 2>/dev/null)
echo "   Status: $STATUS3"

echo ""

# Teste 3: Verificar se o problema é específico do /ui/
echo "3. Testando diferentes endpoints..."
echo ""

echo "   Teste 1: Endpoint /ui/..."
STATUS_UI=$(curl -s -o /dev/null -w "%{http_code}" -u "$USERNAME:$PASSWORD" "$KESTRA_URL/ui/" 2>/dev/null)
echo "   Status: $STATUS_UI"

echo "   Teste 2: Endpoint raiz /..."
STATUS_ROOT=$(curl -s -o /dev/null -w "%{http_code}" -u "$USERNAME:$PASSWORD" "$KESTRA_URL/" 2>/dev/null)
echo "   Status: $STATUS_ROOT"

echo "   Teste 3: Endpoint /api/v1/..."
STATUS_API=$(curl -s -o /dev/null -w "%{http_code}" -u "$USERNAME:$PASSWORD" "$KESTRA_URL/api/v1/" 2>/dev/null)
echo "   Status: $STATUS_API"

echo ""

# Teste 4: Verificar se há Setup Page
echo "4. Verificando Setup Page..."
echo ""

SETUP_RESPONSE=$(curl -s "$KESTRA_URL/ui/" 2>/dev/null)
SETUP_DETECTED=$(echo "$SETUP_RESPONSE" | grep -i "setup\|config\|admin\|welcome" | head -3)

if [ -n "$SETUP_DETECTED" ]; then
    echo "   ✅ Setup Page detectada:"
    echo "$SETUP_DETECTED"
else
    echo "   ⚠️  Setup Page não detectada"
fi

echo ""

# Teste 5: Verificar se há problema com caracteres especiais
echo "5. Testando com diferentes usernames..."
echo ""

echo "   Teste 1: Username original (leonardo@darwinai.com.br)..."
STATUS_U1=$(curl -s -o /dev/null -w "%{http_code}" -u "$USERNAME:$PASSWORD" "$KESTRA_URL/ui/" 2>/dev/null)
echo "   Status: $STATUS_U1"

echo "   Teste 2: Username simplificado (leonardo)..."
STATUS_U2=$(curl -s -o /dev/null -w "%{http_code}" -u "leonardo:$PASSWORD" "$KESTRA_URL/ui/" 2>/dev/null)
echo "   Status: $STATUS_U2"

echo "   Teste 3: Username sem domínio (leonardo@darwinai)..."
STATUS_U3=$(curl -s -o /dev/null -w "%{http_code}" -u "leonardo@darwinai:$PASSWORD" "$KESTRA_URL/ui/" 2>/dev/null)
echo "   Status: $STATUS_U3"

echo ""
echo "===================================================="
echo "📋 Resumo dos Testes:"
echo ""

if [ "$STATUS1" = "200" ]; then
    echo "✅ CREDENCIAIS ORIGINAIS FUNCIONANDO!"
    echo "   Use: $USERNAME / $PASSWORD"
elif [ "$STATUS2" = "200" ]; then
    echo "✅ CREDENCIAIS SEM @ FUNCIONANDO!"
    echo "   Use: $USERNAME / Atjlc151523"
elif [ "$STATUS3" = "200" ]; then
    echo "✅ CREDENCIAIS URL ENCODED FUNCIONANDO!"
    echo "   Use: $USERNAME / %40Atjlc151523"
else
    echo "❌ NENHUMA COMBINAÇÃO FUNCIONOU"
    echo ""
    echo "🔧 Possíveis causas:"
    echo "   1. Variáveis de ambiente não aplicadas no Coolify"
    echo "   2. Container não reiniciado após mudanças"
    echo "   3. Configuração de autenticação incorreta"
    echo "   4. Problema com proxy reverso (Traefik)"
    echo ""
    echo "🛠️  Ações necessárias:"
    echo "   1. Verificar variáveis no Coolify"
    echo "   2. Reiniciar container kestra"
    echo "   3. Verificar logs do container"
    echo "   4. Usar Setup Page se disponível"
fi

echo ""
echo "🌐 Para testar no navegador:"
echo "   URL: $KESTRA_URL"
echo "   Modo incógnito recomendado"
echo "   Limpar cache se necessário"
