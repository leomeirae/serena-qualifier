# WhatsApp MCP Server - HTTP Wrapper para WhatsApp Business API

Este repositório contém um servidor HTTP wrapper para a WhatsApp Business API, implementado seguindo o Model Context Protocol (MCP). O servidor permite que agentes de IA como Cursor, Claude, Windsurf e outros enviem mensagens via WhatsApp através de uma interface REST simples.

## 🌐 **URL do Servidor**

**Servidor Ativo:** http://bw48gc80kokwwckg0wskc40c.157.180.32.249.sslip.io/

## 🎯 **O que é o WhatsApp MCP Server?**

O WhatsApp MCP Server é um servidor HTTP que atua como wrapper para a WhatsApp Business API, permitindo:

- **Envio de Mensagens**: Texto, templates, imagens, documentos
- **Gestão de Templates**: Mensagens estruturadas e aprovadas
- **Confirmação de Leitura**: Tracking de entrega de mensagens
- **Integração com IA**: Via protocolo MCP através de HTTP requests
- **Deploy no Coolify**: Containerização completa com Docker

## 🚀 **Funcionalidades Disponíveis**

### 📱 **Ferramentas de Mensagens (Tools)**

#### 1. **sendTextMessage**
Envia mensagens de texto simples via WhatsApp.

**Parâmetros:**
- `to` (string, obrigatório): Número de telefone no formato internacional (ex: "5511999999999")
- `message` (string, obrigatório): Conteúdo da mensagem de texto

**Exemplo de uso:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "sendTextMessage",
    "arguments": {
      "to": "5511999999999",
      "message": "Olá! Esta é uma mensagem de teste do MCP Server."
    }
  }
}
```

#### 2. **sendTemplateMessage**
Envia mensagens usando templates aprovados pelo WhatsApp.

**Parâmetros:**
- `to` (string, obrigatório): Número de telefone no formato internacional
- `templateName` (string, obrigatório): Nome do template aprovado
- `language` (string, obrigatório): Código do idioma (ex: "pt_BR", "en_US")
- `components` (array, opcional): Componentes do template (parâmetros dinâmicos)

**Exemplo de uso:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "sendTemplateMessage",
    "arguments": {
      "to": "5511999999999",
      "templateName": "welcome_profile_site",
      "language": "pt_BR",
      "components": [
        {
          "type": "body",
          "parameters": [
            {
              "type": "text",
              "text": "João Silva"
            }
          ]
        }
      ]
    }
  }
}
```

#### 3. **sendImageMessage**
Envia imagens com legenda via WhatsApp.

**Parâmetros:**
- `to` (string, obrigatório): Número de telefone no formato internacional
- `imageUrl` (string, obrigatório): URL pública da imagem
- `caption` (string, opcional): Legenda da imagem

**Exemplo de uso:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "sendImageMessage",
    "arguments": {
      "to": "5511999999999",
      "imageUrl": "https://example.com/image.jpg",
      "caption": "Confira nossa nova imagem!"
    }
  }
}
```

#### 4. **markMessageAsRead**
Marca uma mensagem como lida no WhatsApp.

**Parâmetros:**
- `messageId` (string, obrigatório): ID da mensagem a ser marcada como lida

**Exemplo de uso:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "markMessageAsRead",
    "arguments": {
      "messageId": "wamid.ABC123..."
    }
  }
}
```

## 🔧 **Endpoints HTTP Disponíveis**

### **Base URL:** http://bw48gc80kokwwckg0wskc40c.157.180.32.249.sslip.io/

#### 1. **GET /** - Informações Gerais
Retorna informações sobre o servidor e endpoints disponíveis.

```bash
curl http://bw48gc80kokwwckg0wskc40c.157.180.32.249.sslip.io/
```

**Resposta:**
```json
{
  "message": "WhatsApp MCP HTTP Server is running!",
  "endpoints": {
    "health": "/health",
    "mcp": "/mcp (POST)",
    "status": "/status",
    "test": "/test"
  },
  "timestamp": "2025-07-30T20:11:16.687Z"
}
```

#### 2. **GET /health** - Health Check
Verifica se o servidor está funcionando corretamente.

```bash
curl http://bw48gc80kokwwckg0wskc40c.157.180.32.249.sslip.io/health
```

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-30T20:11:16.687Z",
  "port": 45679,
  "env": {
    "hasToken": true,
    "hasPhoneNumberId": true,
    "hasBusinessAccountId": true
  }
}
```

#### 3. **GET /status** - Status Detalhado
Retorna informações detalhadas sobre o servidor e configurações.

```bash
curl http://bw48gc80kokwwckg0wskc40c.157.180.32.249.sslip.io/status
```

#### 4. **POST /mcp** - Endpoint Principal MCP
Endpoint principal para interação com o protocolo MCP.

### **Métodos MCP Suportados:**

#### **tools/list** - Listar Ferramentas Disponíveis
```bash
curl -X POST http://bw48gc80kokwwckg0wskc40c.157.180.32.249.sslip.io/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

**Resposta:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "sendTextMessage",
        "description": "Send a text message via WhatsApp",
        "inputSchema": {
          "type": "object",
          "properties": {
            "to": { "type": "string", "description": "Phone number to send message to" },
            "message": { "type": "string", "description": "Text message content" }
          },
          "required": ["to", "message"]
        }
      },
      {
        "name": "sendTemplateMessage",
        "description": "Send a template message via WhatsApp",
        "inputSchema": {
          "type": "object",
          "properties": {
            "to": { "type": "string", "description": "Phone number to send message to" },
            "templateName": { "type": "string", "description": "Template name" },
            "language": { "type": "string", "description": "Template language code" },
            "components": { "type": "array", "description": "Template components" }
          },
          "required": ["to", "templateName", "language"]
        }
      },
      {
        "name": "sendImageMessage",
        "description": "Send an image message via WhatsApp",
        "inputSchema": {
          "type": "object",
          "properties": {
            "to": { "type": "string", "description": "Phone number to send message to" },
            "imageUrl": { "type": "string", "description": "URL of the image" },
            "caption": { "type": "string", "description": "Image caption" }
          },
          "required": ["to", "imageUrl"]
        }
      },
      {
        "name": "markMessageAsRead",
        "description": "Mark a message as read",
        "inputSchema": {
          "type": "object",
          "properties": {
            "messageId": { "type": "string", "description": "Message ID to mark as read" }
          },
          "required": ["messageId"]
        }
      }
    ]
  }
}
```

#### **tools/call** - Executar Ferramenta
```bash
curl -X POST http://bw48gc80kokwwckg0wskc40c.157.180.32.249.sslip.io/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "sendTextMessage",
      "arguments": {
        "to": "5511999999999",
        "message": "Teste do MCP Server"
      }
    }
  }'
```

## 🤖 **Como Usar com Agentes de IA**

### **1. Configuração Inicial**
Para usar este MCP Server com um agente de IA, configure a URL base:
```
Base URL: http://bw48gc80kokwwckg0wskc40c.157.180.32.249.sslip.io/
```

### **2. Fluxo de Uso**
1. **Listar ferramentas disponíveis** usando `tools/list`
2. **Executar ferramentas** usando `tools/call` com os parâmetros apropriados
3. **Verificar status** usando `/health` ou `/status`

### **3. Exemplo de Integração com Kestra/Serena SDR**
```yaml
- id: send_whatsapp_response
  type: io.kestra.plugin.http.Request
  uri: http://bw48gc80kokwwckg0wskc40c.157.180.32.249.sslip.io/mcp
  method: POST
  headers:
    Content-Type: application/json
  body: |
    {
      "jsonrpc": "2.0",
      "id": 1,
      "method": "tools/call",
      "params": {
        "name": "sendTextMessage",
        "arguments": {
          "to": "{{ inputs.phone_number }}",
          "message": "{{ outputs.ai_response }}"
        }
      }
    }
```

## 📋 **Pré-requisitos**

1. **WhatsApp Business API**: Credenciais da API oficial
2. **Templates Aprovados**: Para uso com `sendTemplateMessage`
3. **URLs Públicas**: Para imagens em `sendImageMessage`

## 🔐 **Configuração de Segurança**

### **Variáveis de Ambiente Obrigatórias:**
- `WHATSAPP_API_TOKEN`: Token de acesso da API
- `WHATSAPP_PHONE_NUMBER_ID`: ID do número de telefone
- `WHATSAPP_BUSINESS_ACCOUNT_ID`: ID da conta de negócio

### **Variáveis Opcionais:**
- `WHATSAPP_API_VERSION`: Versão da API (padrão: v23.0)
- `PORT`: Porta do servidor (padrão: 45679)
- `NODE_ENV`: Ambiente de execução (padrão: production)

## ⚠️ **Limitações e Considerações**

1. **Rate Limiting**: Respeite os limites da API WhatsApp
2. **Templates**: Use apenas templates aprovados pelo WhatsApp
3. **Números de Telefone**: Use formato internacional (ex: "5511999999999")
4. **Imagens**: URLs devem ser públicas e acessíveis
5. **Logs**: Todas as operações são logadas para auditoria

## 🐳 **Deploy no Coolify**

### **Configuração no Coolify:**
1. **Crie um novo recurso** do tipo "Deploy from Git Repository"
2. **Conecte o repositório** GitHub
3. **Configure as variáveis de ambiente** necessárias
4. **Faça o deploy** e aguarde a inicialização

### **Verificação do Deploy:**
```bash
# Health check
curl http://bw48gc80kokwwckg0wskc40c.157.180.32.249.sslip.io/health

# Teste de ferramentas
curl -X POST http://bw48gc80kokwwckg0wskc40c.157.180.32.249.sslip.io/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

## 📚 **Exemplos de Uso**

### **Envio de Mensagem de Boas-vindas:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "sendTextMessage",
    "arguments": {
      "to": "5581997498268",
      "message": "👋 Olá! Bem-vindo ao WhatsApp MCP Server!\n\n✅ Servidor funcionando perfeitamente\n✅ Integração com WhatsApp Business API ativa\n✅ Pronto para uso com agentes de IA"
    }
  }
}
```

### **Envio de Template com Parâmetros:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "sendTemplateMessage",
    "arguments": {
      "to": "5581997498268",
      "templateName": "welcome_profile_site",
      "language": "pt_BR",
      "components": [
        {
          "type": "body",
          "parameters": [
            {
              "type": "text",
              "text": "João Silva"
            }
          ]
        }
      ]
    }
  }
}
```

**⚠️ Nota:** Templates requerem número exato de parâmetros conforme aprovado pelo WhatsApp. Erro comum: `(#132000) Number of parameters does not match`.

### **Envio de Imagem com Legenda:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "sendImageMessage",
    "arguments": {
      "to": "5581997498268",
      "imageUrl": "https://picsum.photos/400/300",
      "caption": "🖼️ Teste do WhatsApp MCP Server - Imagem enviada com sucesso!"
    }
  }
}
```

## 🔍 **Troubleshooting**

### **Erros Comuns:**
1. **"WHATSAPP_API_TOKEN not set"**: Configure a variável de ambiente
2. **"Invalid phone number"**: Use formato internacional (ex: "5581997498268")
3. **"Template not found"**: Verifique se o template está aprovado
4. **"Rate limit exceeded"**: Aguarde antes de enviar mais mensagens
5. **"(#132000) Number of parameters does not match"**: Ajuste os parâmetros do template conforme aprovado

### **Logs de Debug:**
O servidor loga todas as operações com timestamp e detalhes:
```
2025-07-30T20:11:16.687Z - POST /mcp - User-Agent: curl/8.7.1
Sending message to URL: https://graph.facebook.com/v23.0/599096403294262/messages
```

## 📄 **Licença**

MIT

## ✅ **Resultados dos Testes**

### **Testes Realizados com Sucesso:**
- ✅ **Mensagem de Texto Simples** - Funcionando perfeitamente
- ✅ **Imagem com Legenda** - Funcionando perfeitamente  
- ✅ **Mensagem de Boas-vindas** - Funcionando perfeitamente
- ✅ **Status do Sistema** - Funcionando perfeitamente

### **Exemplo de Resposta de Sucesso:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Message sent successfully to 5581997498268. Message ID: wamid.HBgMNTU4MTk3NDk4MjY4FQIAERgSRUVDRDEyMDFGQzNERjMxNkQ5AA=="
      }
    ]
  }
}
```

### **Status Atual do Servidor:**
- 🟢 **Servidor:** ONLINE e funcionando
- 🟢 **WhatsApp API:** Conectado e operacional
- 🟢 **MCP Protocol:** Ativo e respondendo
- 🟢 **Envio de Mensagens:** 100% funcional
- 🟢 **Envio de Imagens:** 100% funcional
- ⚠️ **Templates:** Requer ajuste de parâmetros

---

**Servidor Ativo:** http://bw48gc80kokwwckg0wskc40c.157.180.32.249.sslip.io/
**Documentação:** Este README
**Suporte:** Verifique os logs do servidor para debugging
