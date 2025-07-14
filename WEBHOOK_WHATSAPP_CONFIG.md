# Configuração do Webhook WhatsApp - Produção

## 📋 Informações Essenciais

### URL do Webhook (Produção)
```
https://kestrawebhook.darwinai.com.br/webhook
```

### Configuração no Meta for Developers

1. **Acesse o painel**: https://developers.facebook.com/apps/
2. **Selecione sua aplicação WhatsApp Business**
3. **Vá para WhatsApp > Configuration**
4. **Configure o Webhook**:
   - **Callback URL**: `https://kestrawebhook.darwinai.com.br/webhook`
   - **Verify Token**: Use o valor da variável de ambiente `WHATSAPP_VERIFY_TOKEN`

### Verificação do Webhook

O endpoint `/webhook` suporta dois métodos:

#### GET (Verificação)
- **Usado pelo WhatsApp** para verificar se o webhook é válido
- **Parâmetros esperados**:
  - `hub.mode=subscribe`
  - `hub.verify_token=<seu_token>`
  - `hub.challenge=<challenge_do_whatsapp>`

#### POST (Recebimento de Mensagens)
- **Usado pelo WhatsApp** para enviar mensagens dos usuários
- **Formato**: JSON com estrutura padrão da API WhatsApp v23.0

## 🔧 Configuração de Ambiente

### Variáveis Obrigatórias
```env
WHATSAPP_VERIFY_TOKEN=serena_webhook_verify_token
KESTRA_API_URL=http://kestra:8081
```

### Configuração no Coolify
- A variável `WHATSAPP_VERIFY_TOKEN` deve estar definida no docker-compose-coolify.yml
- O serviço webhook-service está exposto publicamente em `kestrawebhook.darwinai.com.br`

## 🧪 Testes de Validação

### 1. Verificação de Health Check
```bash
curl https://kestrawebhook.darwinai.com.br/
```
**Resposta esperada**: `{"status": "healthy"}`

### 2. Simulação de Verificação WhatsApp
```bash
curl "https://kestrawebhook.darwinai.com.br/webhook?hub.mode=subscribe&hub.verify_token=serena_webhook_verify_token&hub.challenge=test_challenge"
```
**Resposta esperada**: `test_challenge`

### 3. Teste de Mensagem (JSON)
```bash
curl -X POST https://kestrawebhook.darwinai.com.br/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "5511999999999",
            "text": {"body": "teste"},
            "timestamp": "1640995200"
          }]
        }
      }]
    }]
  }'
```

## 📝 Logs e Monitoramento

### Verificação de Logs
```bash
# Via Coolify
docker logs webhook-service-x0swco8sk04koow4sws480so-165731186595

# Ou via SSH
./connect-coolify-ssh.sh
```

### Eventos Importantes nos Logs
- `🔐 Verificação webhook: mode=subscribe`
- `✅ Webhook verificado com sucesso!`
- `📨 Mensagem recebida do WhatsApp`
- `🚀 Workflow acionado com sucesso`

## 🔄 Integração com Kestra

Após receber uma mensagem, o webhook:
1. **Extrai** dados da mensagem WhatsApp
2. **Valida** formato e conteúdo
3. **Aciona** o workflow `2_ai_conversation_flow` no Kestra
4. **Retorna** confirmação ao WhatsApp

### URL do Workflow Kestra (Interna)
```
http://kestra:8081/api/v1/executions/webhook/serena.production/2_ai_conversation_flow/converse_production_lead
```

## 🛡️ Segurança

- **HTTPS obrigatório** para webhook em produção
- **Token de verificação** configurado via variável de ambiente
- **Validação de payload** para evitar mensagens inválidas
- **CORS configurado** para permitir comunicação entre domínios

## 📞 Contato e Suporte

Para problemas na configuração do webhook:
1. Verifique os logs do serviço webhook-service
2. Confirme se o token está correto
3. Teste manualmente os endpoints de verificação
4. Verifique se o Kestra está respondendo internamente

---

**Status**: ✅ Configurado e funcionando em produção
**Última atualização**: Janeiro 2025
**Ambiente**: Coolify (https://coolify.darwinai.com.br) 