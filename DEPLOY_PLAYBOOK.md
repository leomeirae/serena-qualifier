# 🚀 Playbook de Deploy - Serena SDR

## 📋 Visão Geral

Este documento contém o passo a passo completo para fazer o deploy da integração Serena SDR no ambiente Coolify.

## 🎯 Objetivos do Deploy

- ✅ Integrar o agente SDR (Sílvia) ao sistema existente
- ✅ Configurar MCP servers (Supabase, Serena, WhatsApp)
- ✅ Ativar workflow de conversação SDR
- ✅ Validar funcionamento end-to-end
- ✅ Configurar monitoramento e alertas

## 📦 Pré-requisitos

### 🔧 Ambiente Local
- [ ] Git configurado e acesso ao repositório
- [ ] Docker instalado (para testes locais)
- [ ] Python 3.11+ instalado
- [ ] Acesso ao dashboard do Coolify

### 🔑 Credenciais Necessárias
- [ ] OpenAI API Key
- [ ] Serena API Token
- [ ] WhatsApp Business API Token
- [ ] Supabase URL e Key
- [ ] Acesso ao repositório Git

## 🚀 Fase 1: Preparação do Código

### 1.1 Verificação Local
```bash
# Clonar repositório (se necessário)
git clone <repo-url>
cd serena-qualifier

# Verificar se todas as alterações estão presentes
ls -la scripts/sdr/
ls -la config/mcp/
ls -la kestra/workflows/2_sdr_conversation_flow.yml
ls -la tests/e2e/

# Executar testes locais
pytest tests/e2e/ -v
python scripts/verify_mcp_servers.py
```

### 1.2 Commit e Push
```bash
# Adicionar todas as alterações
git add .

# Commit com mensagem descritiva
git commit -m "feat: Integração completa Serena SDR

- Adicionado agente SDR (Sílvia) com IA conversacional
- Configurados MCP servers (Supabase, Serena, WhatsApp)
- Implementado workflow 2_sdr_conversation_flow.yml
- Adicionados testes end-to-end completos
- Configurado healthchecks e monitoramento
- Portas MCP: Supabase(3000), Serena(3002), WhatsApp(3003)"

# Push para o repositório
git push origin main
```

## 🌐 Fase 2: Deploy no Coolify

### 2.1 Acesso ao Dashboard
1. Acessar o dashboard do Coolify
2. Navegar até o projeto "serena-qualifier"
3. Verificar se o branch `main` foi atualizado
4. Aguardar build automático ou forçar rebuild

### 2.2 Configuração de Variáveis de Ambiente

No painel do Coolify, verificar e configurar as seguintes variáveis:

#### 🔑 APIs Principais
```bash
OPENAI_API_KEY=sk-proj-L7BHQG27o_Yo3kw...
SERENA_API_TOKEN=eyJhbGciOiJIUzI1NiIsInR5...
SERENA_API_BASE_URL=https://api.serena.com.br
WHATSAPP_API_TOKEN=RUFBUFIwRkc1c3E4Qk85...
WHATSAPP_PHONE_NUMBER_ID=123456789
WHATSAPP_BUSINESS_ACCOUNT_ID=123456789
```

#### 🗄️ Supabase
```bash
SECRET_SUPABASE_URL=https://xxx.supabase.co
SECRET_SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5...
SECRET_DB_CONNECTION_STRING=postgresql://...
```

#### 🔐 Outras Configurações
```bash
WHATSAPP_VERIFY_TOKEN=serena_verify_token
WHATSAPP_APP_SECRET=your_app_secret
CHATWOOT_WEBHOOK_URL=https://chatwoot.example.com
```

### 2.3 Rebuild & Redeploy
1. Clicar em "Rebuild & Redeploy" no Coolify
2. Aguardar a conclusão do build (5-10 minutos)
3. Monitorar logs durante o processo
4. Verificar se todos os serviços iniciaram

## 🔍 Fase 3: Validação Pós-Deploy

### 3.1 Verificação de Serviços
```bash
# Verificar status de todos os serviços
docker-compose ps

# Verificar logs dos MCP servers
docker-compose logs supabase-mcp-server
docker-compose logs serena-mcp-server
docker-compose logs whatsapp-mcp-server

# Verificar logs do kestra-agent
docker-compose logs kestra-agent
```

### 3.2 Teste de Healthchecks
```bash
# Testar healthchecks dos MCPs
curl http://localhost:3000/health  # Supabase MCP
curl http://localhost:3002/health  # Serena MCP
curl http://localhost:3003/health  # WhatsApp MCP

# Executar script de verificação completo
python scripts/verify_mcp_servers.py
```

### 3.3 Verificação do Kestra
1. Acessar Kestra UI: https://kestra.darwinai.com.br
2. Verificar se o workflow "2_sdr_conversation_flow" está ativo
3. Verificar logs de execução recentes
4. Testar trigger manual do workflow

### 3.4 Teste End-to-End
```bash
# Executar testes automatizados
pytest tests/e2e/test_text_message_flow.py -v
pytest tests/e2e/test_energy_bill_ocr_flow.py -v
pytest tests/e2e/test_follow_up_flow.py -v
pytest tests/e2e/test_fallback_and_metrics.py -v
```

## 📊 Fase 4: Monitoramento

### 4.1 Configuração de Alertas
```bash
# Verificar se os healthchecks estão funcionando
docker-compose exec kestra-agent curl http://supabase-mcp-server:3000/health
docker-compose exec kestra-agent curl http://serena-mcp-server:3002/health
docker-compose exec kestra-agent curl http://whatsapp-mcp-server:3003/health
```

### 4.2 Logs e Métricas
- Monitorar logs do Kestra para execuções do workflow SDR
- Verificar métricas de performance (tempo de resposta, taxa de sucesso)
- Monitorar uso de recursos dos MCP servers

### 4.3 Teste Manual
1. Enviar mensagem de teste para o WhatsApp
2. Verificar se a resposta é recebida corretamente
3. Testar envio de imagem de fatura
4. Verificar follow-up automático após 2 horas

## 🚨 Troubleshooting

### Problema: MCP Server não inicia
```bash
# Verificar logs específicos
docker-compose logs supabase-mcp-server --tail=50

# Verificar variáveis de ambiente
docker-compose exec supabase-mcp-server env | grep SUPABASE

# Reiniciar serviço específico
docker-compose restart supabase-mcp-server
```

### Problema: Workflow não executa
1. Verificar se o webhook está configurado corretamente
2. Verificar logs do webhook-service
3. Testar trigger manual no Kestra UI
4. Verificar se as variáveis de ambiente estão corretas

### Problema: Erro de conectividade
```bash
# Verificar rede Docker
docker network ls
docker network inspect coolify

# Testar conectividade entre containers
docker-compose exec kestra-agent ping supabase-mcp-server
docker-compose exec kestra-agent ping serena-mcp-server
docker-compose exec kestra-agent ping whatsapp-mcp-server
```

## ✅ Checklist de Go-Live

### 🔧 Configuração
- [ ] Código commitado e pushado para main
- [ ] Build no Coolify concluído com sucesso
- [ ] Todas as variáveis de ambiente configuradas
- [ ] MCP servers iniciados e saudáveis
- [ ] Workflow SDR ativo no Kestra

### 🧪 Testes
- [ ] Healthchecks dos MCPs funcionando
- [ ] Testes end-to-end passando
- [ ] Teste manual de mensagem de texto
- [ ] Teste manual de imagem de fatura
- [ ] Verificação de logs e métricas

### 📊 Monitoramento
- [ ] Alertas configurados
- [ ] Logs sendo coletados
- [ ] Métricas de performance sendo monitoradas
- [ ] Plano de rollback definido

## 🎉 Conclusão

Após completar todas as etapas deste playbook, o sistema Serena SDR estará completamente integrado e operacional no ambiente Coolify.

### 📞 Suporte
Em caso de problemas durante o deploy:
1. Verificar logs detalhados
2. Consultar este playbook
3. Executar scripts de verificação
4. Contatar equipe de desenvolvimento

---

**Versão:** 1.0.0  
**Data:** 2025-01-17  
**Autor:** Serena-Coder AI Agent 