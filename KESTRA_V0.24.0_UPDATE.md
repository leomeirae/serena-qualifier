# Atualização do Kestra para v0.24.0

## 📋 Resumo da Atualização

**Versão Anterior:** v0.23.7  
**Nova Versão:** v0.24.0  
**Data da Atualização:** $(date)  
**Status:** ✅ Pronto para deploy

## 🔄 Mudanças Implementadas

### 1. **Atualização da Imagem Docker**
- ✅ Atualizada de `kestra/kestra:v0.23.7` para `kestra/kestra:v0.24.0`

### 2. **Configuração de Autenticação Básica**
- ✅ Removida a variável `KESTRA_SERVER_BASICAUTH_ENABLED` (não é mais necessária)
- ✅ Mantidas as credenciais obrigatórias:
  - Username: `leonardo@darwinai.com.br`
  - Password: `@Atjlc151523`

### 3. **Verificações de Compatibilidade**
- ✅ Nenhuma referência ao plugin `langchain4j` encontrada
- ✅ Nenhum workflow com upload de arquivos FILE encontrado
- ✅ Configurações de CORS mantidas
- ✅ Configurações de proxy reverso mantidas

## 🚀 Como Executar a Atualização

### Opção 1: Script Automático (Recomendado)
```bash
./update-kestra-v0.24.0.sh
```

### Opção 2: Manual
```bash
# 1. Backup (opcional mas recomendado)
docker run --rm -v kestra_data:/data -v $(pwd)/backup:/backup alpine tar czf /backup/kestra_data_backup.tar.gz -C /data .

# 2. Parar serviços
docker-compose -f docker-compose-coolify.yml down

# 3. Pull nova imagem
docker pull kestra/kestra:v0.24.0

# 4. Iniciar serviços
docker-compose -f docker-compose-coolify.yml up -d

# 5. Verificar status
docker-compose -f docker-compose-coolify.yml ps
```

## 🔍 Verificações Pós-Atualização

### 1. **Status dos Serviços**
```bash
docker-compose -f docker-compose-coolify.yml ps
```

### 2. **Logs do Kestra**
```bash
docker-compose -f docker-compose-coolify.yml logs --tail=50 kestra
```

### 3. **Acesso à Interface Web**
- URL: https://kestra.darwinai.com.br
- Login: leonardo@darwinai.com.br
- Senha: @Atjlc151523

### 4. **Verificação de Workflows**
- Acesse a interface web
- Verifique se todos os workflows estão funcionando
- Teste a execução de workflows simples

## 🆕 Novos Recursos da v0.24.0

### 1. **AI Agent**
- Novo recurso de agente de IA integrado
- Melhorias na automação de workflows

### 2. **Melhorias de Segurança**
- Autenticação básica obrigatória
- Melhorias na validação de entrada

### 3. **Performance**
- Otimizações gerais de performance
- Melhor gerenciamento de recursos

### 4. **Interface do Usuário**
- Novos recursos de debug de expressões
- Melhorias na visualização de dependências
- Suporte a playground para testes

## 🔧 Troubleshooting

### Problema: Erro de Autenticação
**Solução:** Verificar se as credenciais estão corretas no docker-compose

### Problema: Workflows não carregam
**Solução:** Verificar logs do Kestra e reiniciar o serviço

### Problema: Erro de conexão com banco
**Solução:** Verificar se o PostgreSQL está rodando e acessível

## 📞 Suporte

Em caso de problemas:
1. Verificar logs: `docker-compose -f docker-compose-coolify.yml logs kestra`
2. Restaurar backup se necessário
3. Contatar equipe de desenvolvimento

## 📝 Notas Importantes

- A autenticação básica agora é **obrigatória** para todas as instalações OSS
- Backup automático é criado antes da atualização
- Todos os dados existentes são preservados
- A atualização é compatível com a configuração atual do Coolify
