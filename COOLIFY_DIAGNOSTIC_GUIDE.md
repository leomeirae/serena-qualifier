# Guia de Diagnóstico Coolify - Serena Qualifier

## Informações do Setup Atual

**Domínios configurados:**
- **Kestra**: `kestra.darwinai.com.br` (porta 8081)
- **Webhook**: `kestrawebhook.darwinai.com.br` (porta 8001)
- **API Principal**: `api.darwinai.com.br` (porta 3001)

**Arquitetura:**
- PostgreSQL (banco Kestra)
- Redis (cache/queue)
- Kestra (orquestração)
- Webhook Service (integração WhatsApp)
- API Principal (endpoints principais)

## Comandos de Diagnóstico via SSH

### 1. Verificar Status dos Containers
```bash
# Conectar via SSH
ssh -i ~/.ssh/id_ed25519 user@your-coolify-server

# Verificar containers rodando
docker ps -a

# Verificar logs do Docker Compose
docker-compose logs -f --tail=50

# Verificar logs de um serviço específico
docker-compose logs -f kestra
docker-compose logs -f webhook-service
docker-compose logs -f api-principal
```

### 2. Verificar Saúde dos Serviços
```bash
# Testar conectividade interna
docker exec -it $(docker ps -q -f name=kestra) curl -f http://localhost:8081/

# Testar webhook service
docker exec -it $(docker ps -q -f name=webhook) curl -f http://localhost:8001/

# Testar API principal
docker exec -it $(docker ps -q -f name=api) curl -f http://localhost:3001/
```

### 3. Verificar Conectividade Externa
```bash
# Testar domínios externos
curl -I https://kestra.darwinai.com.br/
curl -I https://kestrawebhook.darwinai.com.br/
curl -I https://api.darwinai.com.br/
```

### 4. Verificar Banco de Dados
```bash
# Conectar ao PostgreSQL
docker exec -it $(docker ps -q -f name=postgres) psql -U kestra -d kestra

# Dentro do psql:
\dt  # listar tabelas
SELECT * FROM flows LIMIT 5;  # verificar workflows
\q   # sair
```

### 5. Verificar Variáveis de Ambiente
```bash
# Verificar variáveis do Kestra
docker exec -it $(docker ps -q -f name=kestra) env | grep -E "(KESTRA|POSTGRES|JAVA)"

# Verificar variáveis do webhook
docker exec -it $(docker ps -q -f name=webhook) env | grep -E "(WHATSAPP|KESTRA|PYTHON)"
```

### 6. Verificar Workflows Kestra
```bash
# Fazer upload dos workflows (se necessário)
cd /path/to/serena-qualifier

# Upload workflow 1
curl -X POST \
  -H "Content-Type: application/x-yaml" \
  --data-binary @kestra/workflows/1_lead_activation_flow.yml \
  http://kestra.darwinai.com.br/api/v1/serena.production/flows

# Upload workflow 2  
curl -X POST \
  -H "Content-Type: application/x-yaml" \
  --data-binary @kestra/workflows/2_ai_conversation_flow.yml \
  http://kestra.darwinai.com.br/api/v1/serena.production/flows
```

### 7. Testar Integração WhatsApp-Chatwoot
```bash
# Testar webhook do Chatwoot
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": {"content": "teste", "conversation": {"contact_inbox": {"source_id": "5511999999999"}}}}' \
  https://kestrawebhook.darwinai.com.br/chatwoot/webhook
```

## Principais Problemas Conhecidos

### 1. **Integração WhatsApp-Chatwoot não funciona**
**Problema**: WhatsApp configurado para webhook do Chatwoot (darwinai.com.br) mas webhook local (localhost:8000) nunca recebe mensagens.

**Solução**: Configurar webhook do Chatwoot para:
```
https://kestrawebhook.darwinai.com.br/chatwoot/webhook
```

### 2. **Workflows Kestra não executam**
**Verificar**:
- Workflows foram uploadados corretamente
- Sintaxe YAML está correta
- Banco PostgreSQL está funcionando
- Variáveis de ambiente estão configuradas

### 3. **Containers reiniciam constantemente**
**Verificar**:
- Logs dos containers com `docker-compose logs -f`
- Healthchecks estão passando
- Recursos de memória/CPU suficientes

## Comandos de Recuperação

### Restart Completo
```bash
# Parar todos os serviços
docker-compose down

# Remover volumes (CUIDADO: perde dados)
docker-compose down -v

# Rebuild e restart
docker-compose up -d --build

# Verificar logs
docker-compose logs -f
```

### Rebuild de Imagem Específica
```bash
# Rebuild apenas webhook service
docker-compose up -d --build webhook-service

# Rebuild apenas API principal
docker-compose up -d --build api-principal
```

## Checklist de Verificação

- [ ] Todos os containers estão rodando (`docker ps`)
- [ ] Healthchecks passando
- [ ] Domínios externos respondendo
- [ ] Banco PostgreSQL acessível
- [ ] Workflows Kestra carregados
- [ ] Variáveis de ambiente configuradas
- [ ] Webhook Chatwoot configurado corretamente
- [ ] Logs sem erros críticos

## Próximos Passos

1. **Execute os comandos de diagnóstico** na ordem apresentada
2. **Identifique o problema específico** baseado nos resultados
3. **Aplique as soluções** correspondentes
4. **Teste a integração completa** WhatsApp → Chatwoot → Webhook → Kestra

---

**Importante**: Mantenha este guia atualizado conforme descobrir novos problemas ou soluções. 