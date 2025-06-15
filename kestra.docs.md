# Documentação Kestra - Guia Completo

## 📋 Índice
1. [Introdução ao Kestra](#introdução-ao-kestra)
2. [Configuração com Docker](#configuração-com-docker)
3. [Secrets e Variáveis de Ambiente](#secrets-e-variáveis-de-ambiente)
4. [Estrutura de Workflows](#estrutura-de-workflows)
5. [Triggers e Webhooks](#triggers-e-webhooks)
6. [Templating com Pebble](#templating-com-pebble)
7. [Execução e Monitoramento](#execução-e-monitoramento)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Introdução ao Kestra

**Kestra** é uma plataforma de orquestração open-source, infinitamente escalável, que permite a todos os engenheiros gerenciar **workflows críticos de negócio** de forma declarativa em código.

### Características Principais:
- **600+ plugins** disponíveis
- **Editor de código integrado** com Git e Terraform
- **Workflows declarativos** em YAML
- **Escalabilidade infinita**
- **Event-driven** e **scheduled workflows**

---

## 🐳 Configuração com Docker

### Execução Local Básica

```bash
# Linux/macOS
docker run --pull=always --rm -it -p 8080:8080 --user=root \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /tmp:/tmp kestra/kestra:latest server local

# Windows PowerShell
docker run --pull=always --rm -it -p 8080:8080 --user=root `
    -v "/var/run/docker.sock:/var/run/docker.sock" `
    -v "C:/Temp:/tmp" kestra/kestra:latest server local

# Windows CMD
docker run --pull=always --rm -it -p 8080:8080 --user=root ^
    -v "/var/run/docker.sock:/var/run/docker.sock" ^
    -v "C:/Temp:/tmp" kestra/kestra:latest server local
```

### Docker Compose Configuração

```yaml
version: '3.8'
services:
  kestra:
    image: kestra/kestra:latest
    ports:
      - "8080:8080"
    environment:
      # Configuração de secrets
      KESTRA_SECRET_TYPE: env
      KESTRA_SECRET_ENV_PREFIX: ""
      
      # Variáveis de ambiente do projeto
      WHATSAPP_API_TOKEN: ${WHATSAPP_API_TOKEN}
      WHATSAPP_PHONE_NUMBER_ID: ${WHATSAPP_PHONE_NUMBER_ID}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      SUPABASE_URL: ${SUPABASE_URL}
      SUPABASE_KEY: ${SUPABASE_ANON_KEY}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./data:/app/data
    command: server local
```

---

## 🔐 Secrets e Variáveis de Ambiente

### Configuração de Secrets

O Kestra suporta diferentes backends para secrets:

#### 1. Environment Variables Backend
```yaml
environment:
  KESTRA_SECRET_TYPE: env
  KESTRA_SECRET_ENV_PREFIX: ""
```

#### 2. Uso de Secrets nos Workflows
```yaml
# Acessando secrets via função secret()
env:
  API_TOKEN: "{{ secret('WHATSAPP_API_TOKEN') }}"
  DATABASE_URL: "{{ secret('SUPABASE_URL') }}"
  
# Verificação de existência de secret
script: |
  {% if secret('API_KEY') is not null %}
    echo "API Key configurada"
  {% endif %}
```

#### 3. Variáveis de Ambiente Diretas
```yaml
# Alternativa: usar variáveis de ambiente diretamente
env:
  API_TOKEN: "valor_direto_da_variavel"
  PHONE_ID: "599096403294262"
```

### Namespace Variables
```yaml
# Definindo variáveis no namespace
variables:
  database_host: "localhost"
  api_version: "v1"
  
# Acessando variáveis do namespace
message: "Conectando em {{ namespace.myproject.database_host }}"
```

---

## 📝 Estrutura de Workflows

### Workflow Básico
```yaml
id: exemplo_workflow
namespace: empresa.equipe
description: Workflow de exemplo com **markdown**

labels:
  team: data
  owner: desenvolvedor
  environment: dev

inputs:
  - id: usuario
    type: STRING
    required: false
    defaults: "Admin"
    description: "Usuário que executa o workflow"

variables:
  primeira: 1
  segunda: "{{ vars.primeira }} < 2"

tasks:
  - id: log_inicial
    type: io.kestra.plugin.core.log.Log
    message: |
      Variáveis: {{ vars.primeira }} e {{ render(vars.segunda) }}
      Input: {{ inputs.usuario }}
      Iniciado em: {{ taskrun.startDate }}

  - id: processamento
    type: io.kestra.plugin.scripts.python.Script
    script: |
      print("Processando dados...")
      print(f"Usuário: {{ inputs.usuario }}")

outputs:
  - id: resultado
    type: STRING
    value: "{{ outputs.processamento.value ?? 'Processamento concluído' }}"

triggers:
  - id: agendamento_mensal
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 9 1 * *" # Todo dia 1 às 9h
```

### Workflow com Webhook
```yaml
id: webhook_workflow
namespace: api.integracao

triggers:
  - id: webhook_trigger
    type: io.kestra.plugin.core.trigger.Webhook
    key: "minha-chave-webhook"

tasks:
  - id: processar_webhook
    type: io.kestra.plugin.scripts.python.Script
    env:
      WEBHOOK_DATA: "{{ trigger.body }}"
    script: |
      import json
      import os
      
      data = json.loads(os.environ['WEBHOOK_DATA'])
      print(f"Dados recebidos: {data}")
```

---

## 🔗 Triggers e Webhooks

### Tipos de Triggers

#### 1. Schedule Trigger
```yaml
triggers:
  - id: diario
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 8 * * *" # Todo dia às 8h
    
  - id: semanal
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 9 * * 1" # Toda segunda às 9h
```

#### 2. Webhook Trigger
```yaml
triggers:
  - id: api_webhook
    type: io.kestra.plugin.core.trigger.Webhook
    key: "chave-secreta-webhook"
```

**URL do Webhook:**
```
POST http://localhost:8080/api/v1/executions/webhook/{namespace}/{flow-id}/{webhook-key}
```

#### 3. Flow Trigger
```yaml
triggers:
  - id: apos_outro_flow
    type: io.kestra.plugin.core.trigger.Flow
    inputs:
      flow: outro-workflow
      namespace: empresa.equipe
    conditions:
      - type: io.kestra.plugin.core.condition.ExecutionStatusCondition
        in:
          - SUCCESS
```

---

## 🎨 Templating com Pebble

### Sintaxe Básica
```yaml
# Variáveis
{{ variavel }}
{{ objeto.propriedade }}
{{ lista[0] }}

# Comentários
{# Este é um comentário #}

# Condicionais
{% if condicao %}
  Verdadeiro
{% else %}
  Falso
{% endif %}

# Loops
{% for item in lista %}
  {{ item }}
{% endfor %}
```

### Funções Úteis

#### Manipulação de Dados
```yaml
# Conversões
{{ "123" | number }}           # String para número
{{ 123 | string }}             # Número para string
{{ objeto | toJson }}          # Objeto para JSON
{{ jsonString | fromJson }}    # JSON para objeto

# Datas
{{ now() }}                    # Data atual
{{ execution.startDate | date('yyyy-MM-dd') }}
{{ trigger.date ?? execution.startDate | dateAdd(1, 'DAYS') }}

# Strings
{{ "hello" | upper }}          # HELLO
{{ "WORLD" | lower }}          # world
{{ "  texto  " | trim }}       # texto
{{ "a,b,c" | split(",") }}     # ["a", "b", "c"]
```

#### Secrets e KV Store
```yaml
# Secrets
{{ secret('API_KEY') }}
{{ secret('DB_PASSWORD') }}

# Key-Value Store
{{ kv('CONFIGURACAO') }}
{{ kv('CHAVE', 'namespace.especifico') }}
{{ kv(key='CHAVE', namespace='NS', errorOnMissing=false) }}
```

#### Arquivos e Storage
```yaml
# Leitura de arquivos
{{ read('scripts/script.py') }}
{{ read('config/settings.json') }}

# Verificações de arquivo
{{ fileExists(outputs.download.uri) }}
{{ isFileEmpty(outputs.download.uri) }}
{{ fileSize(outputs.download.uri) }}
```

### Filtros Avançados
```yaml
# Listas
{{ [1,2,3] | first }}          # 1
{{ [1,2,3] | last }}           # 3
{{ [1,2,3] | length }}         # 3
{{ [3,1,2] | sort }}           # [1,2,3]
{{ [1,2,3] | reverse }}        # [3,2,1]
{{ ["a","b"] | join(",") }}    # "a,b"

# Criptografia
{{ "texto" | md5 }}
{{ "texto" | sha256 }}
{{ "texto" | base64Encode }}
{{ "dGV4dG8=" | base64Decode }}

# URLs
{{ "hello world" | urlEncode }}  # hello%20world
{{ "hello%20world" | urlDecode }} # hello world
```

---

## ⚡ Execução e Monitoramento

### Estados de Execução
- **CREATED**: Execução criada
- **RUNNING**: Em execução
- **SUCCESS**: Concluída com sucesso
- **FAILED**: Falhou
- **KILLED**: Cancelada
- **PAUSED**: Pausada

### Endpoints da API

#### Workflows
```bash
# Listar workflows
GET /api/v1/flows/search

# Criar/Atualizar workflow
POST /api/v1/flows
Content-Type: application/x-yaml

# Obter workflow específico
GET /api/v1/flows/{namespace}/{id}
```

#### Execuções
```bash
# Executar via webhook
POST /api/v1/executions/webhook/{namespace}/{flow-id}/{webhook-key}

# Listar execuções
GET /api/v1/executions

# Obter execução específica
GET /api/v1/executions/{execution-id}

# Logs de execução
GET /api/v1/logs/{execution-id}?minLevel=INFO
```

### Monitoramento via CLI
```bash
# Status da execução
curl -s "http://localhost:8080/api/v1/executions/{execution-id}" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Status: {data[\"state\"][\"current\"]}')"

# Logs de erro
curl -s "http://localhost:8080/api/v1/logs/{execution-id}?minLevel=ERROR" | \
  python3 -c "import sys, json; data=json.load(sys.stdin); [print(f'{log[\"level\"]} - {log[\"message\"]}') for log in data if 'ERROR' in log[\"level\"]]"
```

---

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Secrets não encontrados
```
ERROR: Cannot find secret for key 'API_KEY'
```

**Solução:**
```yaml
# Verificar configuração no docker-compose.yml
environment:
  KESTRA_SECRET_TYPE: env
  KESTRA_SECRET_ENV_PREFIX: ""
  API_KEY: ${API_KEY}  # Variável do .env
```

#### 2. Workflow não encontrado
```
ERROR: Flow not found
```

**Solução:**
```bash
# Reenviar workflow
curl -X POST "http://localhost:8080/api/v1/flows" \
  -H "Content-Type: application/x-yaml" \
  --data-binary @workflow.yml
```

#### 3. Erro de sintaxe YAML
```
ERROR: Invalid YAML syntax
```

**Solução:**
- Verificar indentação (usar espaços, não tabs)
- Validar estrutura YAML
- Remover caracteres especiais problemáticos

#### 4. Timeout de execução
```yaml
# Configurar timeout nas tasks
tasks:
  - id: task_longa
    type: io.kestra.plugin.scripts.python.Script
    timeout: PT30M  # 30 minutos
    script: |
      # Script longo...
```

### Logs e Debug

#### Níveis de Log
- **TRACE**: Máximo detalhe
- **DEBUG**: Informações de debug
- **INFO**: Informações gerais
- **WARN**: Avisos
- **ERROR**: Erros

#### Configuração de Logs
```yaml
# No workflow
tasks:
  - id: debug_task
    type: io.kestra.plugin.core.log.Log
    level: DEBUG
    message: "Debug: {{ vars.debug_info }}"

# Plugin defaults para logs
pluginDefaults:
  - type: io.kestra.plugin.core.log.Log
    values:
      level: TRACE
```

### Comandos Úteis de Debug

```bash
# Verificar status do Kestra
curl -f "http://localhost:8080/api/v1/flows/search" && echo "✅ Kestra OK"

# Listar workflows ativos
curl -s "http://localhost:8080/api/v1/flows/search" | \
  python3 -c "import sys, json; [print(f'✅ {f[\"namespace\"]}/{f[\"id\"]} (rev {f[\"revision\"]})') for f in json.load(sys.stdin)['results']]"

# Verificar variáveis de ambiente no container
docker exec kestra env | grep -E "(API|SECRET|TOKEN)"

# Logs do container
docker-compose logs kestra --tail=50
```

---

## 📚 Recursos Adicionais

### Links Úteis
- **Documentação Oficial**: https://kestra.io/docs
- **Plugins**: https://kestra.io/plugins
- **Blueprints**: https://kestra.io/blueprints
- **GitHub**: https://github.com/kestra-io/kestra

### Exemplos de Integração
- **WhatsApp Business API**
- **Supabase Database**
- **OpenAI API**
- **Python Scripts**
- **Docker Containers**

### Boas Práticas
1. **Sempre usar secrets** para dados sensíveis
2. **Implementar timeouts** em tasks longas
3. **Usar labels** para organização
4. **Documentar workflows** com descriptions
5. **Testar localmente** antes do deploy
6. **Monitorar execuções** regularmente
7. **Implementar error handling** adequado

---

*Documentação gerada automaticamente via Context7 MCP - Kestra.io* 