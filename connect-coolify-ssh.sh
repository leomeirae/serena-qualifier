#!/bin/bash

# Script para conectar ao Coolify via SSH e executar correções
# Configuração da chave SSH e comandos necessários

echo "=========================================="
echo "   CONEXÃO COOLIFY SSH - SERENA QUALIFIER"
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

# Configurações SSH
SSH_KEY_CONTENT="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILyl+tS5u8N3Pj/140gqjaJZGh++wtEk+Y/9/cbzzBMI"
SSH_KEY_FILE="$HOME/.ssh/coolify_key"
SSH_USER="root"  # Ajuste conforme necessário
SSH_HOST=""  # Será preenchido pelo usuário

# Função para configurar chave SSH
setup_ssh_key() {
    print_info "Configurando chave SSH..."
    
    # Criar diretório SSH se não existir
    mkdir -p "$HOME/.ssh"
    
    # Salvar chave SSH
    echo "$SSH_KEY_CONTENT" > "$SSH_KEY_FILE"
    chmod 600 "$SSH_KEY_FILE"
    
    print_status 0 "Chave SSH configurada em $SSH_KEY_FILE"
}

# Função para testar conexão SSH
test_ssh_connection() {
    print_info "Testando conexão SSH para $SSH_USER@$SSH_HOST..."
    
    ssh -i "$SSH_KEY_FILE" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$SSH_USER@$SSH_HOST" "echo 'Conexão SSH funcionando'" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        print_status 0 "Conexão SSH estabelecida com sucesso"
        return 0
    else
        print_status 1 "Erro ao conectar via SSH"
        return 1
    fi
}

# Função para enviar e executar script de correção
execute_redis_fix() {
    print_info "Enviando script de correção para o servidor..."
    
    # Enviar script para o servidor
    scp -i "$SSH_KEY_FILE" -o StrictHostKeyChecking=no "fix-redis-memory-overcommit.sh" "$SSH_USER@$SSH_HOST:/tmp/"
    
    if [ $? -eq 0 ]; then
        print_status 0 "Script enviado com sucesso"
    else
        print_status 1 "Erro ao enviar script"
        return 1
    fi
    
    # Executar script no servidor
    print_info "Executando correção do Redis no servidor..."
    ssh -i "$SSH_KEY_FILE" -o StrictHostKeyChecking=no "$SSH_USER@$SSH_HOST" "chmod +x /tmp/fix-redis-memory-overcommit.sh && sudo /tmp/fix-redis-memory-overcommit.sh"
    
    if [ $? -eq 0 ]; then
        print_status 0 "Correção do Redis executada com sucesso"
    else
        print_status 1 "Erro ao executar correção do Redis"
        return 1
    fi
}

# Função para diagnóstico completo
execute_diagnostic() {
    print_info "Enviando script de diagnóstico para o servidor..."
    
    # Enviar script de diagnóstico
    scp -i "$SSH_KEY_FILE" -o StrictHostKeyChecking=no "coolify-diagnostic.sh" "$SSH_USER@$SSH_HOST:/tmp/"
    
    if [ $? -eq 0 ]; then
        print_status 0 "Script de diagnóstico enviado com sucesso"
    else
        print_status 1 "Erro ao enviar script de diagnóstico"
        return 1
    fi
    
    # Executar diagnóstico no servidor
    print_info "Executando diagnóstico completo no servidor..."
    ssh -i "$SSH_KEY_FILE" -o StrictHostKeyChecking=no "$SSH_USER@$SSH_HOST" "chmod +x /tmp/coolify-diagnostic.sh && cd /path/to/project && /tmp/coolify-diagnostic.sh"
}

# Função para shell interativo
interactive_shell() {
    print_info "Conectando ao shell interativo..."
    print_warning "Digite 'exit' para sair do shell remoto"
    
    ssh -i "$SSH_KEY_FILE" -o StrictHostKeyChecking=no "$SSH_USER@$SSH_HOST"
}

# Menu principal
show_menu() {
    echo
    echo "=========================================="
    echo "   OPÇÕES DISPONÍVEIS"
    echo "=========================================="
    echo "1. Corrigir problema do Redis (Memory Overcommit)"
    echo "2. Executar diagnóstico completo"
    echo "3. Conectar ao shell interativo"
    echo "4. Testar conexão SSH"
    echo "5. Sair"
    echo "=========================================="
    echo
}

# Verificar se host foi fornecido
if [ -z "$1" ]; then
    echo "Uso: $0 <IP_DO_SERVIDOR>"
    echo "Exemplo: $0 192.168.1.100"
    exit 1
fi

SSH_HOST="$1"

# Configurar chave SSH
setup_ssh_key

# Menu interativo
while true; do
    show_menu
    read -p "Escolha uma opção [1-5]: " choice
    
    case $choice in
        1)
            echo
            print_info "=== CORREÇÃO DO REDIS ==="
            if test_ssh_connection; then
                execute_redis_fix
            fi
            ;;
        2)
            echo
            print_info "=== DIAGNÓSTICO COMPLETO ==="
            if test_ssh_connection; then
                execute_diagnostic
            fi
            ;;
        3)
            echo
            print_info "=== SHELL INTERATIVO ==="
            if test_ssh_connection; then
                interactive_shell
            fi
            ;;
        4)
            echo
            print_info "=== TESTE DE CONEXÃO ==="
            test_ssh_connection
            ;;
        5)
            echo
            print_info "Saindo..."
            break
            ;;
        *)
            print_warning "Opção inválida. Tente novamente."
            ;;
    esac
    
    echo
    read -p "Pressione Enter para continuar..."
done

echo "Conexão encerrada." 