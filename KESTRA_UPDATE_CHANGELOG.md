# Changelog - Atualização Kestra v0.23.6

## 📅 Data: $(date +%Y-%m-%d)

## 🚀 Principais Mudanças

### ✅ Versão Atualizada
- **Antes**: `kestra/kestra:latest-full` (versão indefinida)
- **Depois**: `kestra/kestra:v0.23.6-full` (versão específica estável)
- **Lançamento**: 15 de julho de 2024

### 🔧 Otimizações de Performance

#### Java Virtual Machine (JVM)
- **MaxRAMPercentage**: `75.0%` → `80.0%` (melhor uso de memória)
- **Garbage Collector**: Adicionado `G1GC` para melhor performance
- **String Deduplication**: Habilitado para reduzir uso de memória

```yaml
# Antes
JAVA_OPTS: "-server -XX:MaxRAMPercentage=75.0 -Xms512m -Xmx2g"

# Depois  
JAVA_OPTS: "-server -XX:MaxRAMPercentage=80.0 -Xms512m -Xmx2g -XX:+UseG1GC -XX:+UseStringDeduplication"
```

## 🔄 Processo de Migração

### 1. Backup Automático
- ✅ Configurações salvas em `backup-kestra-[timestamp]/`
- ✅ Estratégia de rollback preparada

### 2. Ordem de Restart (Coolify)
1. **Parar serviços**: api-principal → webhook-service → kestra → postgres/redis
2. **Aplicar mudanças**: git pull / redeploy
3. **Iniciar serviços**: postgres → redis → kestra → webhook-service → api-principal

### 3. Validação Pós-Update
- [ ] Interface web: https://kestra.darwinai.com.br
- [ ] Workflow 1: `2_ai_conversation_flow.yml`
- [ ] Workflow 2: `3_ai_conversation_flow_simplified.yml`
- [ ] Workflow 3: `4_ai_conversation_flow_advanced.yml`
- [ ] Teste de webhook
- [ ] Verificação de logs

## 🛠️ Compatibilidade

### ✅ Mantidas
- Configurações de proxy reverso (Traefik)
- Configurações de CORS
- Volumes e persistent storage
- Configurações de banco (PostgreSQL)
- Configurações de cache (Redis)

### ⚠️ Verificar
- Plugins personalizados (se houver)
- Configurações avançadas de workflow
- Integrações customizadas

## 📋 Changelog Oficial v0.23.6

Segundo o [repositório oficial do Kestra](https://github.com/kestra-io/kestra/releases/tag/v0.23.6):

### 🐛 Bug Fixes
- **core**: trim expressions in select & multiselect to be able to use '|' instead of '>-' (#10017)

### 👥 Contributors
- YannC.
- brian-mulier-p  
- brian.mulier

## 🔄 Plano de Rollback

```bash
# Se algo der errado:
cp backup-kestra-[timestamp]/docker-compose-coolify.yml.backup docker-compose-coolify.yml
# Redeploy no Coolify
# Reiniciar serviços na ordem correta
```

## 📞 Suporte

- **Documentação**: https://kestra.io/docs/
- **GitHub**: https://github.com/kestra-io/kestra
- **Versão**: v0.23.6 (15 jul 2024)

---

**Status da migração**: ⏳ Preparada para execução
**Ambiente**: Coolify + Docker Compose
**Downtime estimado**: 2-5 minutos 