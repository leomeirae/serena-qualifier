# ✅ Checklist de Go-Live - Serena SDR

## 🎯 Objetivo

Este checklist garante que a integração Serena SDR esteja completamente funcional antes do lançamento em produção.

## 📋 Checklist de Configuração

### 🔧 Infraestrutura Docker
- [ ] **docker-compose-coolify.yml** atualizado com MCP servers
- [ ] **Portas MCP** configuradas corretamente:
  - [ ] Supabase MCP: 3000
  - [ ] Serena MCP: 3002
  - [ ] WhatsApp MCP: 3003
- [ ] **Rede coolify** configurada para todos os serviços
- [ ] **Healthchecks** funcionando para todos os MCPs
- [ ] **depends_on** configurado com `service_healthy`
- [ ] **Volumes** montados corretamente:
  - [ ] `./scripts:/app/scripts`
  - [ ] `./serena-sdr/scripts:/app/scripts/sdr`
  - [ ] `./config/mcp/*:/app`

### 🔑 Variáveis de Ambiente
- [ ] **OpenAI API Key** configurada
- [ ] **Serena API Token** configurado
- [ ] **Serena API Base URL** configurado
- [ ] **WhatsApp API Token** configurado
- [ ] **WhatsApp Phone Number ID** configurado
- [ ] **WhatsApp Business Account ID** configurado
- [ ] **Supabase URL** configurado
- [ ] **Supabase Key** configurado
- [ ] **WhatsApp Verify Token** configurado
- [ ] **URLs dos MCPs** configuradas no kestra-agent

### 📦 Scripts SDR
- [ ] **ai_sdr_agent.py** presente em `/app/scripts/sdr/`
- [ ] **classify_media.py** presente em `/app/scripts/sdr/`
- [ ] **follow_up_agent.py** presente em `/app/scripts/sdr/`
- [ ] **agent_tools/** presente em `/app/scripts/sdr/`
- [ ] **utils/** presente em `/app/scripts/sdr/`
- [ ] **verify_mcp_servers.py** presente em `/app/scripts/`
- [ ] **monitor_mcp_servers.py** presente em `/app/scripts/`

### 🔄 Workflows Kestra
- [ ] **2_sdr_conversation_flow.yml** presente em `kestra/workflows/`
- [ ] **Workflow ativo** no Kestra UI
- [ ] **Trigger webhook** configurado: `converse_sdr_silvia`
- [ ] **Variáveis do workflow** configuradas:
  - [ ] `supabase_mcp_url: "http://supabase-mcp-server:3000"`
  - [ ] `serena_mcp_url: "http://serena-mcp-server:3002"`
  - [ ] `whatsapp_mcp_url: "http://whatsapp-mcp-server:3003"`

## 🧪 Checklist de Testes

### 🔍 Testes de Infraestrutura
- [ ] **Docker Compose** inicia sem erros
- [ ] **Todos os serviços** estão rodando
- [ ] **Healthchecks** dos MCPs passando
- [ ] **Conectividade** entre serviços funcionando
- [ ] **Logs** sem erros críticos

### 🧪 Testes End-to-End
- [ ] **Teste de mensagem de texto** passando
- [ ] **Teste de imagem de fatura** passando
- [ ] **Teste de follow-up** passando
- [ ] **Teste de fallback** passando
- [ ] **Teste de métricas** passando

### 📱 Testes Manuais
- [ ] **Envio de mensagem** via WhatsApp
- [ ] **Recebimento de resposta** da IA
- [ ] **Envio de imagem** de fatura
- [ ] **Processamento OCR** funcionando
- [ ] **Qualificação automática** funcionando
- [ ] **Follow-up automático** após 2h

### 🔧 Testes de MCP Servers
- [ ] **Supabase MCP** respondendo corretamente
- [ ] **Serena MCP** respondendo corretamente
- [ ] **WhatsApp MCP** respondendo corretamente
- [ ] **JSON-RPC calls** funcionando
- [ ] **Error handling** funcionando

## 📊 Checklist de Monitoramento

### 🔍 Scripts de Verificação
- [ ] **verify_mcp_servers.py** executando sem erros
- [ ] **monitor_mcp_servers.py** configurado
- [ ] **Logs** sendo coletados corretamente
- [ ] **Métricas** sendo registradas

### 📈 Alertas e Notificações
- [ ] **Email notifications** configuradas (opcional)
- [ ] **Slack notifications** configuradas (opcional)
- [ ] **Healthcheck alerts** funcionando
- [ ] **Error notifications** funcionando

### 📋 Logs e Debugging
- [ ] **Logs do Kestra** acessíveis
- [ ] **Logs dos MCPs** acessíveis
- [ ] **Logs do webhook-service** acessíveis
- [ ] **Logs do kestra-agent** acessíveis

## 🚀 Checklist de Deploy

### 📦 Preparação do Código
- [ ] **Código commitado** no repositório
- [ ] **Branch main** atualizado
- [ ] **Build automático** no Coolify
- [ ] **Deploy concluído** sem erros

### 🔄 Pós-Deploy
- [ ] **Serviços iniciados** corretamente
- [ ] **Healthchecks** passando
- [ ] **Workflows ativos** no Kestra
- [ ] **Webhook funcionando** corretamente

### ✅ Validação Final
- [ ] **Teste manual** de mensagem de texto
- [ ] **Teste manual** de imagem de fatura
- [ ] **Verificação** de logs e métricas
- [ ] **Confirmação** de funcionamento

## 🚨 Checklist de Rollback

### 🔄 Plano de Rollback
- [ ] **Backup** do estado anterior
- [ ] **Procedimento** de rollback documentado
- [ ] **Comunicação** de rollback preparada
- [ ] **Teste** de rollback realizado

### 📋 Procedimento de Rollback
1. **Parar** todos os serviços
2. **Reverter** para versão anterior
3. **Reiniciar** serviços
4. **Validar** funcionamento
5. **Comunicar** mudança

## 📞 Checklist de Comunicação

### 👥 Equipe
- [ ] **Desenvolvimento** notificado sobre go-live
- [ ] **Operações** notificado sobre monitoramento
- [ ] **Suporte** notificado sobre nova funcionalidade
- [ ] **Stakeholders** notificados sobre lançamento

### 📢 Usuários
- [ ] **Documentação** atualizada
- [ ] **FAQ** atualizado
- [ ] **Suporte** preparado
- [ ] **Feedback** coletado

## 🎉 Checklist de Sucesso

### 📈 Métricas de Sucesso
- [ ] **Tempo de resposta** < 15 segundos
- [ ] **Taxa de sucesso** > 95%
- [ ] **Uptime** > 99.9%
- [ ] **Satisfação do usuário** > 4.5/5

### 🔍 Monitoramento Contínuo
- [ ] **Alertas** configurados
- [ ] **Dashboards** atualizados
- [ ] **Relatórios** automatizados
- [ ] **Revisões** agendadas

## 📝 Notas de Implementação

### ✅ Concluído
- [x] Integração Serena SDR
- [x] Configuração MCP servers
- [x] Workflow de conversação
- [x] Testes end-to-end
- [x] Scripts de verificação
- [x] Monitoramento automático
- [x] Documentação completa

### 🔄 Em Andamento
- [ ] Deploy no Coolify
- [ ] Validação pós-deploy
- [ ] Testes manuais
- [ ] Configuração de alertas

### ⏳ Pendente
- [ ] Go-live final
- [ ] Monitoramento contínuo
- [ ] Otimizações baseadas em feedback
- [ ] Expansão de funcionalidades

---

**Responsável:** Equipe de Desenvolvimento  
**Data de Criação:** 2025-01-17  
**Última Atualização:** 2025-01-17  
**Versão:** 1.0.0 