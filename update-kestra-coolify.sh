#!/bin/bash

# Script para atualização do Kestra no Coolify
# Versão: v0.23.6

echo "🚀 Iniciando atualização do Kestra para v0.23.6..."

# Função para verificar se o comando foi executado com sucesso
check_success() {
    if [ $? -eq 0 ]; then
        echo "✅ $1"
    else
        echo "❌ Erro em: $1"
        exit 1
    fi
}

# 1. Verificar se estamos na pasta correta
if [ ! -f "docker-compose-coolify.yml" ]; then
    echo "❌ Arquivo docker-compose-coolify.yml não encontrado!"
    echo "Execute este script na pasta do projeto."
    exit 1
fi

# 2. Criar backup dos dados atuais
echo "📦 Criando backup dos dados atuais..."
BACKUP_DIR="backup-kestra-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Copiar arquivo de configuração atual
cp docker-compose-coolify.yml "$BACKUP_DIR/docker-compose-coolify.yml.backup"
check_success "Backup do docker-compose criado"

# 3. Verificar se a nova versão está disponível
echo "🔍 Verificando disponibilidade da imagem v0.23.6..."
docker pull kestra/kestra:v0.23.6-full
check_success "Download da nova imagem do Kestra"

# 4. Parar os serviços gradualmente
echo "⏸️ Parando serviços dependentes..."
echo "IMPORTANTE: Execute os seguintes comandos no Coolify:"
echo ""
echo "1. No painel do Coolify, vá para o seu projeto"
echo "2. Pare os serviços na seguinte ordem:"
echo "   - api-principal (primeiro)"
echo "   - webhook-service (segundo)"
echo "   - kestra (terceiro)"
echo "   - postgres e redis (por último)"
echo ""
echo "3. Após parar todos os serviços, execute:"
echo "   git pull origin main"
echo "   (ou faça o redeploy no Coolify)"
echo ""

# 5. Verificar configurações
echo "🔧 Verificando configurações atualizadas..."
echo "Alterações feitas:"
echo "- Imagem atualizada: kestra/kestra:v0.23.6-full"
echo "- JAVA_OPTS otimizado para melhor performance"
echo "- Configurações mantidas compatíveis"
echo ""

# 6. Instruções para restart
echo "🔄 Instruções para restart no Coolify:"
echo "1. Inicie os serviços na seguinte ordem:"
echo "   - postgres (primeiro)"
echo "   - redis (segundo)"
echo "   - kestra (terceiro - aguarde ficar healthy)"
echo "   - webhook-service (quarto)"
echo "   - api-principal (por último)"
echo ""
echo "2. Verificar logs de cada serviço para garantir que iniciaram corretamente"
echo "3. Testar a interface do Kestra em: https://kestra.darwinai.com.br"
echo ""

# 7. Testes de validação
echo "✅ Testes de validação após update:"
echo "1. Acesse https://kestra.darwinai.com.br"
echo "2. Verifique se os 3 workflows estão funcionando:"
echo "   - 2_ai_conversation_flow.yml"
echo "   - 3_ai_conversation_flow_simplified.yml"
echo "   - 4_ai_conversation_flow_advanced.yml"
echo "3. Teste uma execução de webhook"
echo "4. Verifique os logs para erros"
echo ""

# 8. Rollback se necessário
echo "🔄 Plano de rollback (se necessário):"
echo "1. Restaurar: cp $BACKUP_DIR/docker-compose-coolify.yml.backup docker-compose-coolify.yml"
echo "2. Fazer redeploy no Coolify"
echo "3. Reiniciar serviços na ordem correta"
echo ""

echo "🎉 Atualização preparada! Agora execute as etapas no Coolify."
echo "📁 Backup salvo em: $BACKUP_DIR" 