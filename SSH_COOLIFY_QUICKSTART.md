# 🚀 Guia Rápido - Correção Redis via SSH

## ⚡ Execução Rápida

Para corrigir o problema do Redis **Memory Overcommit** no seu Coolify:

```bash
# 1. Execute o script de conexão SSH (substitua pelo IP do seu servidor)
./connect-coolify-ssh.sh SEU_IP_DO_SERVIDOR

# 2. No menu, escolha a opção 1 para corrigir o Redis
```

## 📋 O que será corrigido

O script corrigirá automaticamente:

### ✅ **Problema Principal - Memory Overcommit**
```
WARNING Memory overcommit must be enabled!
```

**Solução aplicada:**
- Adiciona `vm.overcommit_memory = 1` ao `/etc/sysctl.conf`
- Aplica configuração temporária: `sysctl vm.overcommit_memory=1`
- Torna configuração permanente (mantém após reboot)

### ✅ **Otimizações Adicionais**
- **Transparent Huge Pages (THP)**: Desabilitado para melhor performance
- **TCP Backlog**: Configurado para `net.core.somaxconn=65535`
- **Restart automático**: Reinicia containers Redis após correção

## 🔧 Opções do Menu

| Opção | Descrição |
|-------|-----------|
| **1** | 🔴 **Corrigir problema do Redis** - Executa correção completa |
| **2** | 📊 **Diagnóstico completo** - Executa análise detalhada |
| **3** | 💻 **Shell interativo** - Acesso direto ao servidor |
| **4** | 🔍 **Testar conexão SSH** - Verifica conectividade |
| **5** | 🚪 **Sair** - Encerra o script |

## 🎯 Execução Manual (Alternativa)

Se preferir executar manualmente:

```bash
# 1. Conectar ao servidor
ssh -i ~/.ssh/coolify_key root@SEU_IP

# 2. Aplicar correção diretamente
sudo sysctl vm.overcommit_memory=1
echo "vm.overcommit_memory = 1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# 3. Reiniciar containers Redis
docker restart $(docker ps -q --filter "name=redis")
```

## 🔍 Verificação Pós-Correção

Após executar a correção, verifique:

```bash
# 1. Verificar configuração aplicada
sysctl -n vm.overcommit_memory
# Deve retornar: 1

# 2. Verificar logs do Redis (não deve mais mostrar WARNING)
docker logs $(docker ps -q --filter "name=redis") 2>&1 | grep -i warning

# 3. Testar Redis
docker exec $(docker ps -q --filter "name=redis") redis-cli ping
# Deve retornar: PONG
```

## 🚨 Troubleshooting

### Erro: "Permission denied"
```bash
# Verificar permissões da chave SSH
ls -la ~/.ssh/coolify_key
# Deve mostrar: -rw------- (600)

# Corrigir se necessário
chmod 600 ~/.ssh/coolify_key
```

### Erro: "Connection refused"
- Verifique se o IP do servidor está correto
- Confirme que o SSH está rodando na porta 22
- Verifique firewall do servidor

### Erro: "sudo: command not found"
```bash
# Se estiver como root, execute sem sudo
sysctl vm.overcommit_memory=1
```

## ✅ Resultado Esperado

Após a correção bem-sucedida:

```
✓ Memory overcommit habilitado
✓ Configuração salva permanentemente  
✓ Containers Redis reiniciados
✓ Redis respondendo: PONG
```

## 🔄 Restart Completo (Se Necessário)

Se ainda houver problemas:

```bash
# Via SSH no servidor
cd /path/to/project
docker-compose down
docker-compose up -d
```

---

**⚠️ Importante:** A correção será mantida após reboot do servidor. Os logs do Redis não devem mais mostrar o WARNING de memory overcommit. 