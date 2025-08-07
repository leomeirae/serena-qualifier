#!/bin/bash

# Script de Atualização do Kestra para v0.24.0
# Data: $(date)
# Autor: Sistema de Atualização Automática

set -e

echo "🚀 Iniciando atualização do Kestra para v0.24.0..."
echo "=================================================="

# 1. Backup dos dados atuais
echo "📦 Criando backup dos dados atuais..."
BACKUP_DIR="backup-kestra-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup do volume de dados do Kestra
echo "   - Backup do volume kestra_data..."
docker run --rm -v kestra_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/kestra_data_backup.tar.gz -C /data .

# Backup do volume do PostgreSQL
echo "   - Backup do volume postgres_data..."
docker run --rm -v postgres_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/postgres_data_backup.tar.gz -C /data .

echo "✅ Backup concluído em: $BACKUP_DIR"

# 2. Parar os serviços atuais
echo "🛑 Parando serviços atuais..."
docker-compose -f docker-compose-coolify.yml down

# 3. Pull da nova imagem
echo "⬇️  Baixando nova imagem do Kestra v0.24.0..."
docker pull kestra/kestra:v0.24.0

# 4. Iniciar os serviços com a nova versão
echo "🚀 Iniciando serviços com Kestra v0.24.0..."
docker-compose -f docker-compose-coolify.yml up -d

# 5. Aguardar inicialização
echo "⏳ Aguardando inicialização dos serviços..."
sleep 30

# 6. Verificar status dos serviços
echo "🔍 Verificando status dos serviços..."
docker-compose -f docker-compose-coolify.yml ps

# 7. Verificar logs do Kestra
echo "📋 Verificando logs do Kestra..."
docker-compose -f docker-compose-coolify.yml logs --tail=50 kestra

echo ""
echo "✅ Atualização concluída!"
echo "🌐 Acesse: https://kestra.darwinai.com.br"
echo "👤 Login: leonardo@darwinai.com.br"
echo ""
echo "📝 Notas importantes da v0.24.0:"
echo "   - Autenticação básica agora é obrigatória"
echo "   - Melhorias na segurança e performance"
echo "   - Novos recursos de AI agent"
echo ""
echo "🔧 Se houver problemas, restaure o backup:"
echo "   docker-compose -f docker-compose-coolify.yml down"
echo "   docker run --rm -v kestra_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar xzf /backup/kestra_data_backup.tar.gz -C /data"
echo "   docker-compose -f docker-compose-coolify.yml up -d"
