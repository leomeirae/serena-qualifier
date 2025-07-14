#!/bin/bash

# Script de Diagnóstico Coolify - Serena Qualifier
# Execute este script no servidor Coolify via SSH

echo "=========================================="
echo "   DIAGNÓSTICO COOLIFY - SERENA QUALIFIER"
echo "=========================================="
echo

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para printar com cores
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "ℹ $1"
}

# 1. Verificar Docker e Docker Compose
echo "1. VERIFICANDO DOCKER ENVIRONMENT"
echo "=================================="
docker --version
docker-compose --version
echo

# 2. Verificar containers rodando
echo "2. STATUS DOS CONTAINERS"
echo "========================"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo

# 3. Verificar saúde dos serviços
echo "3. HEALTHCHECK DOS SERVIÇOS"
echo "=========================="

# Kestra
print_info "Testando Kestra (porta 8081)..."
if docker exec -it $(docker ps -q -f name=kestra) curl -f http://localhost:8081/ >/dev/null 2>&1; then
    print_status 0 "Kestra responde localmente"
else
    print_status 1 "Kestra não responde localmente"
fi

# Webhook Service
print_info "Testando Webhook Service (porta 8001)..."
if docker exec -it $(docker ps -q -f name=webhook) curl -f http://localhost:8001/ >/dev/null 2>&1; then
    print_status 0 "Webhook Service responde localmente"
else
    print_status 1 "Webhook Service não responde localmente"
fi

# API Principal
print_info "Testando API Principal (porta 3001)..."
if docker exec -it $(docker ps -q -f name=api) curl -f http://localhost:3001/ >/dev/null 2>&1; then
    print_status 0 "API Principal responde localmente"
else
    print_status 1 "API Principal não responde localmente"
fi

echo

# 4. Verificar conectividade externa
echo "4. CONECTIVIDADE EXTERNA"
echo "========================"

# Kestra
print_info "Testando kestra.darwinai.com.br..."
if curl -I https://kestra.darwinai.com.br/ >/dev/null 2>&1; then
    print_status 0 "kestra.darwinai.com.br acessível"
else
    print_status 1 "kestra.darwinai.com.br não acessível"
fi

# Webhook
print_info "Testando kestrawebhook.darwinai.com.br..."
if curl -I https://kestrawebhook.darwinai.com.br/ >/dev/null 2>&1; then
    print_status 0 "kestrawebhook.darwinai.com.br acessível"
else
    print_status 1 "kestrawebhook.darwinai.com.br não acessível"
fi

# API
print_info "Testando api.darwinai.com.br..."
if curl -I https://api.darwinai.com.br/ >/dev/null 2>&1; then
    print_status 0 "api.darwinai.com.br acessível"
else
    print_status 1 "api.darwinai.com.br não acessível"
fi

echo

# 5. Verificar banco de dados
echo "5. VERIFICANDO BANCO DE DADOS"
echo "============================="
print_info "Testando conexão PostgreSQL..."
if docker exec -it $(docker ps -q -f name=postgres) pg_isready -U kestra -d kestra >/dev/null 2>&1; then
    print_status 0 "PostgreSQL respondendo"
    
    # Verificar tabelas Kestra
    print_info "Verificando tabelas Kestra..."
    TABLE_COUNT=$(docker exec -it $(docker ps -q -f name=postgres) psql -U kestra -d kestra -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d '[:space:]')
    if [ "$TABLE_COUNT" -gt 0 ]; then
        print_status 0 "Banco possui $TABLE_COUNT tabelas"
    else
        print_status 1 "Banco não possui tabelas"
    fi
    
    # Verificar workflows
    print_info "Verificando workflows carregados..."
    FLOW_COUNT=$(docker exec -it $(docker ps -q -f name=postgres) psql -U kestra -d kestra -t -c "SELECT COUNT(*) FROM flows;" 2>/dev/null | tr -d '[:space:]')
    if [ "$FLOW_COUNT" -gt 0 ]; then
        print_status 0 "Encontrados $FLOW_COUNT workflows"
    else
        print_status 1 "Nenhum workflow encontrado"
    fi
    
else
    print_status 1 "PostgreSQL não está respondendo"
fi

echo

# 6. Verificar Redis
echo "6. VERIFICANDO REDIS"
echo "==================="
print_info "Testando Redis..."
if docker exec -it $(docker ps -q -f name=redis) redis-cli ping >/dev/null 2>&1; then
    print_status 0 "Redis respondendo"
else
    print_status 1 "Redis não está respondendo"
fi

echo

# 7. Verificar logs recentes (últimas 20 linhas)
echo "7. LOGS RECENTES (últimas 20 linhas)"
echo "===================================="

echo "--- KESTRA ---"
docker-compose logs --tail=20 kestra

echo
echo "--- WEBHOOK SERVICE ---"
docker-compose logs --tail=20 webhook-service

echo
echo "--- API PRINCIPAL ---"
docker-compose logs --tail=20 api-principal

echo

# 8. Verificar variáveis de ambiente críticas
echo "8. VARIÁVEIS DE AMBIENTE CRÍTICAS"
echo "================================="

print_info "Verificando variáveis do Kestra..."
docker exec -it $(docker ps -q -f name=kestra) env | grep -E "(KESTRA|POSTGRES)" | head -10

echo
print_info "Verificando variáveis do Webhook..."
docker exec -it $(docker ps -q -f name=webhook) env | grep -E "(WHATSAPP|KESTRA)" | head -10

echo

# 9. Verificar uso de recursos
echo "9. USO DE RECURSOS"
echo "=================="
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

echo
echo "=========================================="
echo "   DIAGNÓSTICO CONCLUÍDO"
echo "=========================================="
echo
echo "Para mais detalhes, execute:"
echo "  docker-compose logs -f [nome_do_serviço]"
echo
echo "Para restart completo:"
echo "  docker-compose down && docker-compose up -d"
echo 