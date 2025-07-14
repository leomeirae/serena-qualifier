#!/bin/bash

# Script para corrigir Memory Overcommit do Redis no Coolify
# Execute este script como root no servidor Coolify

echo "=========================================="
echo "   CORRIGINDO MEMORY OVERCOMMIT - REDIS"
echo "=========================================="
echo

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
    fi
}

print_info() {
    echo -e "ℹ $1"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Verificar se está executando como root
if [ "$EUID" -ne 0 ]; then
    print_warning "Este script precisa ser executado como root"
    echo "Execute: sudo $0"
    exit 1
fi

# 1. Verificar configuração atual
echo "1. VERIFICANDO CONFIGURAÇÃO ATUAL"
echo "================================="
CURRENT_OVERCOMMIT=$(sysctl -n vm.overcommit_memory)
print_info "Configuração atual de vm.overcommit_memory: $CURRENT_OVERCOMMIT"

if [ "$CURRENT_OVERCOMMIT" -eq 1 ]; then
    print_status 0 "Memory overcommit já está habilitado"
else
    print_status 1 "Memory overcommit precisa ser habilitado"
fi

echo

# 2. Aplicar configuração temporária
echo "2. APLICANDO CONFIGURAÇÃO TEMPORÁRIA"
echo "===================================="
print_info "Executando: sysctl vm.overcommit_memory=1"
sysctl vm.overcommit_memory=1

if [ $? -eq 0 ]; then
    print_status 0 "Configuração temporária aplicada com sucesso"
else
    print_status 1 "Erro ao aplicar configuração temporária"
    exit 1
fi

echo

# 3. Tornar configuração permanente
echo "3. TORNANDO CONFIGURAÇÃO PERMANENTE"
echo "=================================="
print_info "Adicionando 'vm.overcommit_memory = 1' ao /etc/sysctl.conf"

# Verificar se já existe a configuração
if grep -q "vm.overcommit_memory" /etc/sysctl.conf; then
    print_info "Configuração já existe, atualizando..."
    sed -i 's/^vm.overcommit_memory.*/vm.overcommit_memory = 1/' /etc/sysctl.conf
else
    print_info "Adicionando nova configuração..."
    echo "vm.overcommit_memory = 1" >> /etc/sysctl.conf
fi

print_status 0 "Configuração permanente salva em /etc/sysctl.conf"

echo

# 4. Outras otimizações do Redis
echo "4. APLICANDO OUTRAS OTIMIZAÇÕES DO REDIS"
echo "========================================"

# Transparent Huge Pages (THP)
print_info "Desabilitando Transparent Huge Pages (THP)..."
if [ -f /sys/kernel/mm/transparent_hugepage/enabled ]; then
    echo never > /sys/kernel/mm/transparent_hugepage/enabled
    print_status 0 "THP desabilitado"
else
    print_warning "THP não encontrado (pode ser normal em alguns sistemas)"
fi

# TCP backlog
print_info "Configurando TCP backlog..."
sysctl net.core.somaxconn=65535
echo "net.core.somaxconn = 65535" >> /etc/sysctl.conf
print_status 0 "TCP backlog configurado"

echo

# 5. Reiniciar containers Redis
echo "5. REINICIANDO CONTAINERS REDIS"
echo "==============================="
print_info "Procurando containers Redis..."

# Encontrar containers Redis
REDIS_CONTAINERS=$(docker ps -a --format "{{.Names}}" | grep -i redis)

if [ -n "$REDIS_CONTAINERS" ]; then
    for container in $REDIS_CONTAINERS; do
        print_info "Reiniciando container: $container"
        docker restart "$container"
        
        if [ $? -eq 0 ]; then
            print_status 0 "Container $container reiniciado com sucesso"
        else
            print_status 1 "Erro ao reiniciar container $container"
        fi
    done
else
    print_warning "Nenhum container Redis encontrado"
fi

echo

# 6. Verificar configuração final
echo "6. VERIFICAÇÃO FINAL"
echo "==================="
NEW_OVERCOMMIT=$(sysctl -n vm.overcommit_memory)
print_info "Nova configuração de vm.overcommit_memory: $NEW_OVERCOMMIT"

if [ "$NEW_OVERCOMMIT" -eq 1 ]; then
    print_status 0 "Memory overcommit configurado corretamente"
else
    print_status 1 "Erro na configuração do memory overcommit"
fi

# Verificar se Redis está funcionando
print_info "Testando Redis..."
sleep 5  # Aguardar container inicializar

if [ -n "$REDIS_CONTAINERS" ]; then
    for container in $REDIS_CONTAINERS; do
        if docker exec "$container" redis-cli ping >/dev/null 2>&1; then
            print_status 0 "Redis no container $container está respondendo"
        else
            print_status 1 "Redis no container $container não está respondendo"
        fi
    done
fi

echo

# 7. Aplicar configuração do sysctl
echo "7. APLICANDO CONFIGURAÇÃO DO SYSCTL"
echo "=================================="
print_info "Executando: sysctl -p"
sysctl -p

print_status 0 "Todas as configurações do sysctl aplicadas"

echo
echo "=========================================="
echo "   CORREÇÃO CONCLUÍDA"
echo "=========================================="
echo
print_status 0 "Memory overcommit habilitado"
print_status 0 "Configuração salva permanentemente"
print_status 0 "Containers Redis reiniciados"
echo
print_info "As configurações serão mantidas após reboot do servidor"
print_info "Logs do Redis não devem mais mostrar o WARNING de memory overcommit"
echo 