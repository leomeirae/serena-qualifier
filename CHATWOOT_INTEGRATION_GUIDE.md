# Guia de Integração com Chatwoot

## 📋 Visão Geral da Integração

O **webhook service** do serena-qualifier agora atua como uma **ponte principal** que:

1. **Recebe mensagens** do WhatsApp Business API
2. **Encaminha para o Kestra** (processamento IA) - **EXISTENTE**
3. **Encaminha para o Chatwoot** (monitoramento humano) - **NOVO**

### Arquitetura do Fluxo

```
WhatsApp API → Webhook Service → Kestra (IA)
                    ↓
                Chatwoot (Monitoramento)
```

**Vantagens:**
- ✅ Total controle sobre o fluxo de mensagens
- ✅ Automação IA sempre acionada
- ✅ Monitoramento humano disponível
- ✅ Fallback para atendimento manual
- ✅ Logs centralizados

## 🔧 Configuração Passo a Passo

### Passo 1: Configurar Webhook no WhatsApp

**IMPORTANTE**: O webhook deve apontar para o nosso serviço, NÃO para o Chatwoot.

1. Acesse o [Meta for Developers](https://developers.facebook.com/apps/)
2. Selecione sua aplicação WhatsApp Business
3. Vá para **WhatsApp > Configuração da API**
4. Configure o webhook:
   - **URL de Callback**: `https://kestrawebhook.darwinai.com.br/webhook`
   - **Verify Token**: Valor da variável `WHATSAPP_VERIFY_TOKEN`
   - **Assinatura**: Configurar se necessário

### Passo 2: Obter URL do Webhook Chatwoot

1. Acesse seu painel do Chatwoot
2. Vá em **Caixas de Entrada** (Inboxes)
3. Selecione a caixa de entrada do WhatsApp
4. Nas configurações, procure por **Webhook URL**
5. Copie a URL, será algo como:
   ```
   https://chatwoot.seu-dominio.com/webhooks/whatsapp/NUMERO_DA_CONTA
   ```

### Passo 3: Configurar Variável de Ambiente

**No Coolify:**

1. Acesse o projeto serena-qualifier
2. Vá para **Environment Variables**
3. Adicione a variável:
   - **Nome**: `CHATWOOT_WEBHOOK_URL`
   - **Valor**: URL copiada do Chatwoot
4. Salve e redeploy o serviço

**Configuração para produção:**
```env
CHATWOOT_WEBHOOK_URL=https://chatwoot.darwinai.com.br/webhooks/whatsapp/+558173331721
```

### Passo 4: Verificar Deploy

Após o deploy, verifique se a integração está funcionando:

```bash
# Verificar se o webhook está saudável
curl https://kestrawebhook.darwinai.com.br/

# Resposta esperada incluirá:
{
  "status": "healthy",
  "chatwoot_url": "https://chatwoot.darwinai.com.br/webhooks/whatsapp/123456789",
  "chatwoot_enabled": true
}
```

## 🔍 Funcionalidades Implementadas

### 1. Encaminhamento Automático

- **Processo**: Toda mensagem recebida é automaticamente encaminhada para o Chatwoot
- **Método**: Execução em background (não bloqueia resposta)
- **Headers**: Preserva headers originais do WhatsApp (X-Hub-Signature-256, etc.)

### 2. Logs Detalhados

O sistema registra todas as operações:

```
📤 Encaminhando webhook para o Chatwoot: https://chatwoot.darwinai.com.br/webhooks/whatsapp/123456789
✅ Webhook encaminhado para Chatwoot com sucesso. Status: 200
```

### 3. Tratamento de Erros

- **Timeout**: 10 segundos para não travar o sistema
- **Logs de erro**: Registra problemas sem afetar o fluxo principal
- **Fallback**: Se Chatwoot estiver indisponível, IA continua funcionando

### 4. Configuração Opcional

- **Flexível**: Chatwoot pode ser habilitado/desabilitado via variável de ambiente
- **Graceful**: Sistema funciona normalmente mesmo sem Chatwoot configurado

## 🧪 Testando a Integração

### Teste 1: Verificar Configuração

```bash
curl https://kestrawebhook.darwinai.com.br/
```

**Verificar se retorna:**
- `chatwoot_enabled: true`
- `chatwoot_url: <sua-url-do-chatwoot>`

### Teste 2: Simulação de Mensagem

```bash
curl -X POST https://kestrawebhook.darwinai.com.br/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "5511999999999",
            "text": {"body": "teste integração"},
            "timestamp": "1640995200"
          }]
        }
      }]
    }]
  }'
```

**Verificar:**
1. Logs mostram encaminhamento para Chatwoot
2. Mensagem aparece no Chatwoot
3. IA processa e responde (se configurada)

## 📊 Monitoramento

### Logs do Webhook Service

```bash
# Via Coolify
docker logs webhook-service-x0swco8sk04koow4sws480so-165731186595

# Via SSH
./connect-coolify-ssh.sh
```

### Eventos Importantes

- `📤 Encaminhando webhook para o Chatwoot`
- `✅ Webhook encaminhado para Chatwoot com sucesso`
- `❌ Erro ao encaminhar para Chatwoot`
- `⏱️ Timeout ao encaminhar para Chatwoot`
- `⚠️ CHATWOOT_WEBHOOK_URL não configurado`

## 🛡️ Segurança

### Headers Preservados

- `Content-Type`: Mantém tipo de conteúdo original
- `X-Hub-Signature-256`: Preserva assinatura do WhatsApp

### Timeout e Isolamento

- **Timeout**: 10 segundos para evitar bloqueios
- **Background**: Execução assíncrona não afeta resposta ao WhatsApp
- **Isolamento**: Falha no Chatwoot não afeta processamento IA

## 🔄 Fluxo Completo

1. **WhatsApp** envia mensagem para `https://kestrawebhook.darwinai.com.br/webhook`
2. **Webhook Service** recebe e processa:
   - Encaminha para **Chatwoot** em background
   - Extrai dados da mensagem
   - Aciona **Kestra** para processamento IA
3. **Kestra** executa workflow de conversação
4. **IA** processa e responde via WhatsApp
5. **Chatwoot** recebe cópia para monitoramento humano

## 🚨 Troubleshooting

### Chatwoot não recebe mensagens

1. Verificar URL no health check
2. Verificar logs do webhook service
3. Testar URL do Chatwoot manualmente
4. Verificar configuração no painel Chatwoot

### Timeout ou erros de conexão

1. Verificar se Chatwoot está acessível
2. Testar conectividade de rede
3. Verificar firewall/proxy
4. Aumentar timeout se necessário

### Mensagens duplicadas

1. Verificar se webhook está configurado apenas no nosso serviço
2. Desabilitar webhook direto no Chatwoot
3. Verificar logs para duplicações

---

## 🚀 Configuração Final para Deploy

### Passo a Passo para Configurar no Coolify

1. **Acesse o Coolify**: https://coolify.darwinai.com.br
2. **Vá para o projeto**: serena-qualifier
3. **Clique em Environment Variables**
4. **Adicione a variável**:
   - **Nome**: `CHATWOOT_WEBHOOK_URL`
   - **Valor**: `https://chatwoot.darwinai.com.br/webhooks/whatsapp/+558173331721`
5. **Salve e Deploy**

### Verificação Pós-Deploy

```bash
# Testar se a configuração está funcionando
curl https://kestrawebhook.darwinai.com.br/

# Resposta esperada:
{
  "status": "healthy",
  "chatwoot_url": "https://chatwoot.darwinai.com.br/webhooks/whatsapp/+558173331721",
  "chatwoot_enabled": true
}
```

### Commit das Mudanças

```bash
git add .
git commit -m "feat: Implementa integração com Chatwoot via webhook bridge"
git push origin main
```

---

**Status**: ✅ Implementado e funcionando
**Versão**: 1.0.0
**Última atualização**: Janeiro 2025
**Ambiente**: Coolify (https://coolify.darwinai.com.br)
**Chatwoot URL**: https://chatwoot.darwinai.com.br/webhooks/whatsapp/+558173331721 