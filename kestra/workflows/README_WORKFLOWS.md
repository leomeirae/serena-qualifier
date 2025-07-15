# Workflows de Conversação com IA - Guia de Uso

## 📋 **Visão Geral**

Este projeto possui **3 workflows** diferentes para conversação com IA via WhatsApp:

| **Workflow** | **Tecnologia** | **Uso Recomendado** | **Webhook Key** |
|-------------|----------------|---------------------|-----------------|
| `2_ai_conversation_flow.yml` | Python customizado | **Produção atual** | `converse_production_lead` |
| `3_ai_conversation_flow_simplified.yml` | Plugin ChatCompletion | **Migração/Testes** | `converse_production_lead_v2` |
| `4_ai_conversation_flow_advanced.yml` | Plugin Responses | **Funcionalidades avançadas** | `converse_production_lead_advanced` |

## 🔄 **Estratégia de Migração**

### **Fase 1: Manter Atual (Produção)**
- **Workflow**: `2_ai_conversation_flow.yml`
- **Status**: ✅ Funcionando em produção
- **URL**: `https://kestra.darwinai.com.br/api/v1/executions/webhook/serena.production/converse_production_lead`

### **Fase 2: Testar Simplificado (Paralelo)**
- **Workflow**: `3_ai_conversation_flow_simplified.yml`
- **Status**: 🧪 Pronto para testes
- **URL**: `https://kestra.darwinai.com.br/api/v1/executions/webhook/serena.production/converse_production_lead_v2`

### **Fase 3: Evoluir para Avançado (Futuro)**
- **Workflow**: `4_ai_conversation_flow_advanced.yml`
- **Status**: 🚀 Funcionalidades avançadas
- **URL**: `https://kestra.darwinai.com.br/api/v1/executions/webhook/serena.production/converse_production_lead_advanced`

## 🛠️ **Configuração para Testes**

### **Opção 1: Teste com Landing Page**
Altere a URL no código da landing page temporariamente:

```html
<!-- Antes (Produção) -->
<form action="https://kestra.darwinai.com.br/api/v1/executions/webhook/serena.production/converse_production_lead" method="POST">

<!-- Depois (Teste) -->
<form action="https://kestra.darwinai.com.br/api/v1/executions/webhook/serena.production/converse_production_lead_v2" method="POST">
```

### **Opção 2: Teste com Webhook Service**
Modifique o `webhook_service.py`:

```python
# Antes (Produção)
KESTRA_WEBHOOK_URL = f"{KESTRA_BASE_URL}/api/v1/executions/webhook/serena.production/converse_production_lead"

# Depois (Teste)
KESTRA_WEBHOOK_URL = f"{KESTRA_BASE_URL}/api/v1/executions/webhook/serena.production/converse_production_lead_v2"
```

### **Opção 3: Teste Manual via cURL**
```bash
curl -X POST \
  https://kestra.darwinai.com.br/api/v1/executions/webhook/serena.production/converse_production_lead_v2 \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "5511999999999",
    "message": "Ativar perfil"
  }'
```

## 📊 **Comparação de Funcionalidades**

| **Funcionalidade** | **Atual** | **Simplificado** | **Avançado** |
|-------------------|-----------|------------------|--------------|
| **Resposta da IA** | ✅ GPT-4o-mini | ✅ GPT-4o-mini | ✅ GPT-4o-mini |
| **Envio WhatsApp** | ✅ API v23.0 | ✅ API v23.0 | ✅ API v23.0 |
| **Salvar no banco** | ✅ Supabase | ✅ Supabase | ❌ Não implementado |
| **Análise estruturada** | ❌ Não | ❌ Não | ✅ JSON Schema |
| **Classificação de leads** | ❌ Não | ❌ Não | ✅ Hot/Warm/Cold |
| **Estratégia de resposta** | ❌ Não | ❌ Não | ✅ Automática |
| **Complexidade** | 🟡 Média | 🟢 Baixa | 🔴 Alta |
| **Manutenção** | 🟡 Média | 🟢 Fácil | 🔴 Complexa |
| **Performance** | 🟡 Média | 🟢 Rápida | 🟡 Média |

## 🎯 **Recomendações**

### **Para Produção Atual**
- **Mantenha**: `2_ai_conversation_flow.yml`
- **Motivo**: Estável e funcionando
- **Ação**: Nenhuma mudança necessária

### **Para Testes e Migração**
- **Use**: `3_ai_conversation_flow_simplified.yml`
- **Motivo**: Mais simples e maintível
- **Ação**: Teste com alguns leads antes da migração

### **Para Futuro (Recursos Avançados)**
- **Evolua para**: `4_ai_conversation_flow_advanced.yml`
- **Motivo**: Análise inteligente e classificação automática
- **Ação**: Implemente após validar o simplificado

## 🔧 **Variáveis de Ambiente Necessárias**

Todos os workflows precisam das seguintes variáveis configuradas no Coolify:

```env
# OpenAI
OPENAI_API_KEY=sk-proj-...

# WhatsApp
WHATSAPP_API_TOKEN=EAAPR0FG5sq8...
WHATSAPP_PHONE_NUMBER_ID=599096403294262

# Serena API
SERENA_API_TOKEN=eyJhbGciOiJIUzI1NiIs...
SERENA_API_BASE_URL=https://partnership-service-staging.api.srna.co

# Banco de dados
SECRET_DB_CONNECTION_STRING=postgresql://...
```

## 📈 **Monitoramento**

### **Logs de Sucesso**
- ✅ Mensagem enviada
- 📱 WhatsApp Message ID
- 🤖 Resposta da IA
- 📊 Tokens utilizados

### **Logs de Erro**
- ❌ Falha na API OpenAI
- ❌ Falha no envio WhatsApp
- ❌ Falha na persistência

### **Métricas Importantes**
- Taxa de sucesso de envio
- Tempo de resposta da IA
- Consumo de tokens
- Erros por tipo

## 🚀 **Próximos Passos**

1. **Testar o workflow simplificado** com alguns leads
2. **Comparar performance** com o atual
3. **Migrar gradualmente** se os resultados forem positivos
4. **Evoluir para o avançado** quando precisar de classificação automática

## 🆘 **Troubleshooting**

### **Erro: Variáveis não encontradas**
```bash
❌ Variáveis WHATSAPP_API_TOKEN ou WHATSAPP_PHONE_NUMBER_ID não configuradas
```
**Solução**: Verificar se as variáveis estão configuradas no Coolify

### **Erro: API OpenAI**
```bash
❌ Error code: 401 - Incorrect API key
```
**Solução**: Verificar se `OPENAI_API_KEY` está atualizada

### **Erro: WhatsApp API**
```bash
❌ Erro ao enviar mensagem WhatsApp
```
**Solução**: Verificar se `WHATSAPP_API_TOKEN` está válida e não expirou

### **Workflow não aciona**
**Solução**: Verificar se a URL do webhook está correta e se o workflow está ativado no Kestra 