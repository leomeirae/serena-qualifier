# Plano de Refatoração Completo para o Agente SDR “Sílvia”

Este plano descreve, passo a passo, todas as ações necessárias para transformar o repositório serena-qualifier em um agente de IA conversacional robusto, capaz de atender leads via WhatsApp de forma automatizada. As instruções a seguir combinam limpeza de código, atualização da base de dados, criação de serviços, orquestração assíncrona e boas práticas de segurança e observabilidade.

## 1\. Revisão de premissas e estado atual

Antes de iniciar qualquer refatoração, é essencial entender o que já existe:

1. O **workflow de ativação de lead** (1\_template\_activation\_flow.yml) funciona corretamente e envia o template de boas-vindas após o cadastro.

2. Os **fluxos 2 e 3** (2\_lead\_reception\_warmup.yml e 3\_lead\_conversation\_processing.yml) são simplificados; eles apenas repassam o webhook e enviam uma saudação fixa[\[1\]](https://raw.githubusercontent.com/leomeirae/serena-qualifier/main/kestra/workflows/3_lead_conversation_processing.yml#:~:text=,from%20kestra%20import%20Kestra). Por isso, a conversa não evolui após o clique no botão do template.

3. O script ai\_sdr\_agent.py já implementa as funções necessárias (buscar lead, processar imagem, validar qualificação e apresentar planos) via OpenAI Function Calling[\[2\]](https://github.com/leomeirae/serena-qualifier/blob/main/scripts/ai_sdr_agent.py#L414-L453). Essa lógica ainda não está conectada ao fluxo principal.

## 2\. Preparação e limpeza

### 2.1 Remover workflows obsoletos

No diretório kestra/workflows, exclua os arquivos que não refletem a lógica desejada:

* 2\_lead\_reception\_warmup.yml (apenas encaminha o webhook)

* 3\_lead\_conversation\_processing.yml (envia saudação fixa)

Isso evitará execuções erradas e conflitos.

### 2.2 Atualizar o esquema do banco

Adicione um campo de estado de conversa na tabela leads para que a IA saiba em que etapa cada lead está. Use a interface do Supabase ou um script de migração:

ALTER TABLE leads  
ADD COLUMN IF NOT EXISTS conversation\_state TEXT NOT NULL DEFAULT 'INITIAL';

Esse campo será usado para armazenar valores como INITIAL, AWAITING\_BILL, QUALIFIED, PLANS\_SENT e FOLLOW\_UP.

Caso ainda não existam, crie também tabelas para **histórico de mensagens** e **follow‑ups**. Por exemplo:

CREATE TABLE IF NOT EXISTS lead\_messages (  
  id SERIAL PRIMARY KEY,  
  phone\_number VARCHAR NOT NULL,  
  message\_direction TEXT NOT NULL, \-- 'user' ou 'bot'  
  message\_content TEXT NOT NULL,  
  timestamp TIMESTAMP DEFAULT NOW()  
);

CREATE TABLE IF NOT EXISTS follow\_up\_queue (  
  id SERIAL PRIMARY KEY,  
  phone\_number VARCHAR NOT NULL,  
  scheduled\_at TIMESTAMP NOT NULL,  
  status TEXT DEFAULT 'PENDING'  
);

Essas tabelas darão ao agente contexto e permitirão programar lembretes.

## 3\. Criação do microserviço FastAPI

Substitua a lógica de conversação em YAML por um serviço HTTP dedicado, que processará mensagens de WhatsApp em tempo real e chamará o agente de IA.

### 3.1 Estrutura

Crie um arquivo main.py na raiz do projeto com o seguinte conteúdo resumido:

import os  
from fastapi import FastAPI, Request, HTTPException  
from dotenv import load\_dotenv  
from scripts.ai\_sdr\_agent import SerenaSDRAgent  
from scripts.agent\_tools.supabase\_tools import SupabaseTools  
from scripts.agent\_tools.whatsapp\_tools import WhatsAppTools

load\_dotenv()

app \= FastAPI()  
sdr\_agent \= SerenaSDRAgent()  
supabase\_tools \= SupabaseTools()  
whatsapp\_tools \= WhatsAppTools()

@app.post("/webhook/whatsapp")  
async def handle\_whatsapp\_webhook(request: Request):  
    """  
    Endpoint que recebe mensagens do WhatsApp, extrai dados e aciona o agente.  
    """  
    try:  
        payload \= await request.json()  
        \# Extrair telefone e texto da mensagem (incluindo interativo)  
        change \= payload\['entry'\]\[0\]\['changes'\]\[0\]  
        if 'messages' not in change\['value'\]:  
            return {"status": "ok", "reason": "Not a user message"}

        message\_data \= change\['value'\]\['messages'\]\[0\]  
        phone\_number \= message\_data\['from'\]

        \# Tratar texto e botões  
        if 'text' in message\_data:  
            user\_message \= message\_data\['text'\]\['body'\]  
        elif 'interactive' in message\_data and 'button\_reply' in message\_data\['interactive'\]:  
            user\_message \= message\_data\['interactive'\]\['button\_reply'\]\['title'\]  
        else:  
            user\_message \= ''

        \# Registrar mensagem do usuário  
        supabase\_tools.record\_message(phone\_number, 'user', user\_message)

        \# Recuperar dados do lead e estado da conversa  
        lead\_data \= supabase\_tools.get\_lead\_by\_phone(phone\_number)  
        conversation\_state \= lead\_data.get('conversation\_state', 'INITIAL') if lead\_data else 'INITIAL'

        \# Executar agente  
        agent\_response \= sdr\_agent.run\_agent(  
            lead\_id=phone\_number,  
            user\_message=user\_message,  
            message\_type='text'  
        )

        \# Enviar resposta ao WhatsApp  
        if agent\_response.get('success'):  
            response\_text \= agent\_response.get('response')  
            whatsapp\_tools.send\_text\_message(phone\_number, response\_text)  
            supabase\_tools.record\_message(phone\_number, 'bot', response\_text)  
        else:  
            whatsapp\_tools.send\_text\_message(phone\_number, 'Desculpe, ocorreu um problema. Tente novamente mais tarde.')

        return {"status": "success"}

    except Exception as e:  
        raise HTTPException(status\_code=500, detail=str(e))

@app.get("/health")  
def health():  
    return {"status": "ok"}

### 3.2 Novos métodos de utilidades

Para dar suporte a essa API, adicione os seguintes métodos a scripts/agent\_tools/supabase\_tools.py:

* record\_message(phone\_number: str, direction: str, content: str): insere a mensagem na tabela lead\_messages.

* update\_lead\_conversation\_state(phone\_number: str, state: str): atualiza o campo conversation\_state na tabela leads. Essa função será chamada pelo agente (via OpenAI Function Calling) para avançar a conversa.

* get\_lead\_conversation\_history(phone\_number: str): retorna as últimas N mensagens do lead para construir o contexto.

Também exponha essas funções como ferramentas no SerenaSDRAgent (modificando \_define\_functions e \_call\_function) para permitir que a IA controle o estado e consulte histórico[\[2\]](https://github.com/leomeirae/serena-qualifier/blob/main/scripts/ai_sdr_agent.py#L414-L453).

### 3.3 Dockerização

Crie um Dockerfile para o microserviço:

FROM python:3.11-slim  
WORKDIR /app  
COPY . .  
RUN pip install \--no-cache-dir \-r requirements.txt  
CMD \["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"\]

Atualize docker-compose.yml (ou crie um novo) para executar o microserviço ao lado dos MCP servers e do Kestra. Por exemplo:

services:  
  sdr-agent:  
    build: .  
    environment:  
      \- OPENAI\_API\_KEY=${OPENAI\_API\_KEY}  
      \- WHATSAPP\_MCP\_URL=${WHATSAPP\_MCP\_URL}  
      \- SUPABASE\_MCP\_URL=${SUPABASE\_MCP\_URL}  
      \- SERENA\_MCP\_URL=${SERENA\_MCP\_URL}  
    ports:  
      \- "8000:8000"  
    depends\_on:  
      \- supabase-mcp  
      \- serena-mcp  
      \- whatsapp-mcp

Certifique-se de expor a porta 8000 em seu servidor para apontar o webhook do WhatsApp para /webhook/whatsapp.

## 4\. Refatoração do agente de IA (ai\_sdr\_agent.py)

O agente existente já possui funções para buscar dados do lead, processar fatura, validar qualificação, obter planos e enviar mensagens[\[2\]](https://github.com/leomeirae/serena-qualifier/blob/main/scripts/ai_sdr_agent.py#L414-L453). As refatorações principais são:

1. **Buscar contexto e estado**: antes de iniciar o loop de function calling, o método run\_agent deve buscar o lead no Supabase e obter o campo conversation\_state e o histórico de mensagens. O histórico pode ser resumido e incluído em messages para dar à IA contexto adicional.

2. **Atualizar estado**: inclua a função update\_lead\_conversation\_state na lista de funções disponíveis para o OpenAI Function Calling. Isso permitirá que a IA altere o estado do lead quando apropriado (ex.: de INITIAL para AWAITING\_BILL após solicitar a conta).

3. **Registrar mensagens**: após gerar uma resposta, o agente deve registrar a mensagem do usuário e a resposta da IA via record\_message.

4. **Controle de loops**: mantenha a limitação de interações (ex.: max\_iterations \= 10) para evitar loops infinitos[\[3\]](https://github.com/leomeirae/serena-qualifier/blob/main/scripts/ai_sdr_agent.py#L456-L505).

## 5\. Atualização das ferramentas de integração

### 5.1 WhatsAppTools

O módulo whatsapp\_tools.py já encapsula a chamada ao MCP para enviar mensagens e templates[\[4\]](https://github.com/leomeirae/serena-qualifier/blob/main/scripts/agent_tools/whatsapp_tools.py#L79-L112). Certifique-se de que:

1. As variáveis de ambiente WHATSAPP\_MCP\_URL e WHATSAPP\_PHONE\_NUMBER\_ID estejam configuradas.

2. O método sendTextMessage esteja registrado no MCP e que o microserviço o utilize corretamente.

3. Adicione métodos específicos, se necessário, para **marcar mensagens como lidas**, **enviar imagens** ou **listar mensagens** (para follow‑up). Esses métodos já existem no módulo e podem ser expostos ao agente quando necessário[\[5\]](https://github.com/leomeirae/serena-qualifier/blob/main/scripts/agent_tools/whatsapp_tools.py#L161-L201).

### 5.2 SupabaseTools

Além das novas funções mencionadas, revise as consultas SQL para evitar **SQL injection**. Utilize sempre prepared statements com parâmetros no objeto arguments (vide exemplo na README[\[6\]](https://github.com/leomeirae/serena-qualifier/blob/main/README.md#L541-L670)). Altere as strings de consulta estática no código para usar placeholders $1, $2, etc., e passe os valores via lista params.

## 6\. Recriar workflows no Kestra

O Kestra continuará sendo usado para rotinas assíncronas, como follow‑ups, relatórios e manutenção. Crie um workflow chamado automatic\_follow\_up.yml com as seguintes características:

id: automatic\_follow\_up  
namespace: serena.production  
description: "Dispara lembretes para leads que não responderam."

triggers:  
  \- id: hourly\_schedule  
    type: io.kestra.plugin.core.trigger.Schedule  
    cron: "0 \* \* \* \*"

tasks:  
  \- id: run\_follow\_up\_agent  
    type: io.kestra.plugin.scripts.python.Script  
    description: "Busca leads pendentes e envia follow‑ups"  
    taskRunner:  
      type: io.kestra.plugin.scripts.runner.docker.Docker  
      image: python:3.11-slim  
    beforeCommands:  
      \- pip install supabase-py requests openai  
    env:  
      SUPABASE\_URL: "{{ secret('SUPABASE\_URL') }}"  
      SUPABASE\_KEY: "{{ secret('SUPABASE\_SERVICE\_ROLE\_KEY') }}"  
      WHATSAPP\_MCP\_URL: "{{ secret('WHATSAPP\_MCP\_URL') }}"  
    script: |  
      import os  
      from datetime import datetime, timedelta  
      from scripts.agent\_tools.supabase\_tools import SupabaseTools  
      from scripts.agent\_tools.whatsapp\_tools import WhatsAppTools

      supabase \= SupabaseTools()  
      whatsapp \= WhatsAppTools()

      \# Buscar leads na tabela follow\_up\_queue com status PENDING e horário \<= agora  
      pending \= supabase.fetch\_pending\_followups(datetime.now())  
      for row in pending:  
          phone \= row\['phone\_number'\]  
          \# Gere uma mensagem personalizada ou reutilize FollowUpAgent  
          message \= "Olá\! Você ainda está interessado em conhecer nossos planos de energia solar? Responda SIM para continuar."  
          whatsapp.send\_text\_message(phone, message)  
          supabase.mark\_followup\_sent(row\['id'\])

Esse workflow roda todo início de hora para verificar leads sem resposta e enviar lembretes. Ajuste a lógica conforme sua necessidade (ex.: variação do texto, múltiplos lembretes).

## 7\. Testes e observabilidade

### 7.1 Testes automatizados

Implemente testes unitários e de integração para cada componente:

* **Microserviço**: use pytest para simular requisições ao endpoint /webhook/whatsapp e verificar se o agente responde conforme esperado. Injeções de payloads diferentes (texto, botão, imagem) garantirão cobertura.

* **Agente**: teste os métodos de SerenaSDRAgent de forma isolada, verificando se o loop de function calling encerra e se as funções são chamadas corretamente.

* **Supabase**: crie fixtures com bases de dados temporárias para testar as novas funções record\_message, update\_lead\_conversation\_state e fetch\_pending\_followups.

### 7.2 Logging e métricas

Além das tabelas lead\_status e sdr\_logs descritas na README[\[7\]](https://github.com/leomeirae/serena-qualifier/blob/main/README.md#L940-L1000), configure:

1. **Log estruturado** no microserviço (ex.: via uvicorn \+ structlog) incluindo IDs de leads, estado da conversa e mensagens enviadas.

2. **Dashboards** em ferramentas como Supabase ou Grafana, monitorando métricas de desempenho (tempo médio de resposta, taxa de qualificação, taxa de conversão).

3. **Alertas** para falhas no webhook (HTTP 500\) ou acúmulo de mensagens pendentes no follow\_up\_queue.

## 8\. Segurança e boas práticas

1. **Validação de Webhook**: configure o token de verificação do WhatsApp e valide a assinatura do payload para garantir que as requisições são legítimas.

2. **Proteção de API Keys**: armazene todas as chaves e URLs sensíveis em variáveis de ambiente e use o mecanismo de secret do Kestra para injetá-las nos workflows e no microserviço.

3. **Tratamento de erros gracioso**: quando o agente ou o MCP falhar, envie uma mensagem genérica ao usuário e registre o erro; nunca exponha detalhes técnicos aos leads.

4. **Rate limiting**: implemente limites de taxa no microserviço para evitar abusos ou loops de mensagens.

5. **SQL seguro**: use parâmetros em vez de concatenar strings nas consultas MCP. O exemplo do workflow de conversa na README mostra como utilizar params[\[6\]](https://github.com/leomeirae/serena-qualifier/blob/main/README.md#L541-L670).

## 9\. Deploy final e configuração

1. **Compile a imagem Docker** do microserviço e atualize o docker-compose.yml para incluir todos os serviços (Supabase MCP, Serena MCP, WhatsApp MCP, Kestra, microserviço).

2. **Execute docker-compose up \-d** para iniciar os contêineres. Verifique logs com docker-compose logs \-f.

3. **Ajuste o webhook do WhatsApp** na Meta Developers configurando a URL para o seu domínio/porta: https://seu-servidor.com/webhook/whatsapp.

4. **Rode as migrações SQL** para atualizar as tabelas e criar as novas (lead\_messages, follow\_up\_queue).

5. **Teste ponta a ponta** simulando a jornada de um lead: cadastro, clique no botão, envio da conta, apresentação de planos, follow‑up.

Com estas etapas, o agente Sílvia passa a atuar de forma humana, pedindo a fatura, processando via OCR, validando se o lead é qualificado e apresentando planos de forma dinâmica. A combinação de microserviço para conversas em tempo real e Kestra para tarefas agendadas garante robustez e escalabilidade. Ajustes finos no prompt do agente e nos textos de follow‑up permitirão otimizar a experiência do usuário.

---

[\[1\]](https://raw.githubusercontent.com/leomeirae/serena-qualifier/main/kestra/workflows/3_lead_conversation_processing.yml#:~:text=,from%20kestra%20import%20Kestra) raw.githubusercontent.com

[https://raw.githubusercontent.com/leomeirae/serena-qualifier/main/kestra/workflows/3\_lead\_conversation\_processing.yml](https://raw.githubusercontent.com/leomeirae/serena-qualifier/main/kestra/workflows/3_lead_conversation_processing.yml)

[\[2\]](https://github.com/leomeirae/serena-qualifier/blob/main/scripts/ai_sdr_agent.py#L414-L453) [\[3\]](https://github.com/leomeirae/serena-qualifier/blob/main/scripts/ai_sdr_agent.py#L456-L505) ai\_sdr\_agent.py

[https://github.com/leomeirae/serena-qualifier/blob/main/scripts/ai\_sdr\_agent.py](https://github.com/leomeirae/serena-qualifier/blob/main/scripts/ai_sdr_agent.py)

[\[4\]](https://github.com/leomeirae/serena-qualifier/blob/main/scripts/agent_tools/whatsapp_tools.py#L79-L112) [\[5\]](https://github.com/leomeirae/serena-qualifier/blob/main/scripts/agent_tools/whatsapp_tools.py#L161-L201) whatsapp\_tools.py

[https://github.com/leomeirae/serena-qualifier/blob/main/scripts/agent\_tools/whatsapp\_tools.py](https://github.com/leomeirae/serena-qualifier/blob/main/scripts/agent_tools/whatsapp_tools.py)

[\[6\]](https://github.com/leomeirae/serena-qualifier/blob/main/README.md#L541-L670) [\[7\]](https://github.com/leomeirae/serena-qualifier/blob/main/README.md#L940-L1000) README.md

[https://github.com/leomeirae/serena-qualifier/blob/main/README.md](https://github.com/leomeirae/serena-qualifier/blob/main/README.md)