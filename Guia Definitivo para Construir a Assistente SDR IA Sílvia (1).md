\# 🚀 GUIA DEFINITIVO: Serena SDR AI Sílvia 2.0 \- Especificações Completas para IA de Codificação

\#\# 🎯 MISSÃO EXECUTIVA

\*\*Objetivo\*\*: Construir um AI SDR humanizado e inteligente que automatiza pré-vendas de energia solar via WhatsApp, superando concorrentes com personalização contextual, resposta \<500ms e conversão 3-5x superior.

\*\*Meta de Performance\*\*:

\- Response Rate: 25-35% (vs. 5-10% atual)

\- Lead-to-Meeting: 45-60% (vs. 20% atual)

\- Response Time: \<500ms (vs. 8-12s atual)

\- ROI: 400-500% (vs. 150% atual)

\# 📋 ESPECIFICAÇÕES TÉCNICAS COMPLETAS

\#\# 🏗️ ARQUITETURA DO SISTEMA

\#\#\# \*\*Stack Tecnológico Obrigatório\*\*

\`\`\`yaml

core\_framework: "Kestra (plugin-native workflows)"

ai\_engine: "OpenAI GPT-4o (ChatCompletion plugin)"

database: "Supabase PostgreSQL (JDBC plugin)"

messaging: "WhatsApp Business API (MCP via HTTP)"

ocr\_engine: "OpenAI Vision API"

cache: "Redis (para respostas rápidas)"

monitoring: "Slack \+ Kestra logs"

deployment: "Docker \+ Coolify"

\`\`\`

\#\#\# \*\*Estrutura Modular de Workflows\*\*

\`\`\`

workflows/

├── 1\_lead\_reception\_warmup.yml      \# Recepção \+ quebra-gelo personalizada

├── 2\_plan\_presentation.yml          \# Apresentação de planos \+ aquecimento

├── 3\_document\_collection.yml        \# Coleta educativa de fatura

├── 4\_processing\_qualification.yml   \# OCR \+ qualificação \+ oferta

├── 5\_followup\_nurturing.yml         \# Follow-up inteligente \+ recuperação

└── 6\_monitoring\_alerts.yml          \# Alertas \+ métricas \+ falhas

\`\`\`

\#\# 🧠 SISTEMA DE PERSONALIZAÇÃO INTELIGENTE

\#\#\# \*\*1. Gestão de Prompts Versionados\*\*

\`\`\`yaml

\# Arquivo: prompts/serena\_prompts.yml

prompts:

  silvia\_persona:

    base\_personality: |

      Você é Sílvia, consultora de energia solar da Serena.

      Personalidade: amigável, consultiva, expertise técnica.

      Tom: brasileiro informal mas profissional.

      Emojis: 1-2 por mensagem, contextual.

      

  greeting\_templates:

    v2.0\_casual:

      high\_value: |

        Oi {name}\! 😊 Sou a Sílvia da Serena Energia.

        

        Vi que você mora em {city} e sua conta de luz está em R$ {bill\_amount}.

        Baseado no perfil da sua região, você pode economizar até R$ {yearly\_savings} 

        por ano com energia solar\! 

        

        Quer que eu mostre as opções disponíveis para {city}? ⚡

        

    v2.0\_premium:

      enterprise: |

        Olá {name}\! 🌟 Sou Sílvia, especialista em energia solar da Serena.

        

        Analisando o perfil da {company} em {city}, identifiquei uma oportunidade

        significativa: com sua conta de R$ {bill\_amount}/mês, o investimento em

        energia solar pode gerar economia de R$ {yearly\_savings}/ano.

        

        Posso apresentar nossos planos corporativos personalizados? ☀️

  plan\_presentation:

    v2.1\_interactive: |

      Perfeito, {name}\! Com base no seu perfil em {city}, temos 3 opções ideais:

      

      🌟 \*\*Plano Essencial\*\* \- R$ {plan\_basic\_price}

      └ Economia: {basic\_savings}% | ROI: {basic\_roi} meses

      

      ⚡ \*\*Plano Plus\*\* \- R$ {plan\_plus\_price} \*(MAIS POPULAR\!)\*

      └ Economia: {plus\_savings}% | ROI: {plus\_roi} meses

      

      🏆 \*\*Plano Premium\*\* \- R$ {plan\_premium\_price}

      └ Economia: {premium\_savings}% | ROI: {premium\_roi} meses

      

      Qual opção desperta mais seu interesse? 🤔

  document\_request:

    v1.5\_educational: |

      Excelente escolha, {name}\! 🎉

      

      Para liberar as condições especiais do {selected\_plan} e calcular seu

      desconto personalizado, preciso analisar sua fatura atual.

      

      Pode enviar uma foto da sua conta de luz? 📸

      

      \*É super rápido \- em 30 segundos tenho sua proposta pronta\!\* ⚡

  qualification\_result:

    qualified\_high: |

      Fantástico, {name}\! 🚀

      

      Analisando sua fatura:

      • Consumo: {consumption} kWh/mês

      • Valor atual: R$ {current\_bill}

      • Economia projetada: R$ {monthly\_savings}/mês

      

      Com o {recommended\_plan}, você investiria R$ {investment\_amount}

      e recuperaria em {payback\_months} meses\!

      

      Nosso especialista {specialist\_name} vai entrar em contato hoje

      para finalizar sua proposta. Perfeito? 👍

error\_handling:

  generic\_fallback: |

    Oi\! 😊 Tive um pequeno problema técnico aqui.

    Pode repetir sua mensagem? Prometo que agora vai funcionar perfeitamente\!

    

  ocr\_failed: |

    Hmm, não consegui ler sua fatura direito 🤔

    Pode enviar uma foto mais nítida? Tente com boa iluminação e foco na conta.

    

  no\_response\_2h: |

    Oi {name}\! 👋 

    

    Vi que você se interessou pelos nossos planos de energia solar.

    Ainda tem alguma dúvida? Estou aqui para ajudar\! 😊

\`\`\`

\#\#\# \*\*2. Sistema de Memória Contextual\*\*

\`\`\`yaml

\# Implementação no workflow

\- id: build\_conversation\_context

  type: io.kestra.plugin.scripts.python.Script

  script: |

    from kestra import Kestra

    import json

    import redis

    

    lead\_id \= "{{ trigger.body.phone }}"

    

    \# Cache Redis para contexto de sessão

    r \= redis.Redis(host='redis', port=6379, db=0)

    

    \# Memória de sessão (últimas 5 interações)

    session\_key \= f"session:{lead\_id}"

    session\_history \= r.lrange(session\_key, 0, 4\)

    

    \# Perfil persistente do lead (Supabase)

    lead\_profile \= get\_lead\_profile(lead\_id)

    

    \# Análise comportamental

    behavioral\_data \= analyze\_engagement\_patterns(lead\_id)

    

    context \= {

        "session\_history": \[json.loads(msg) for msg in session\_history\],

        "lead\_profile": lead\_profile,

        "communication\_preferences": {

            "preferred\_style": lead\_profile.get("communication\_style", "casual"),

            "best\_response\_time": behavioral\_data.get("optimal\_time"),

            "engagement\_level": behavioral\_data.get("engagement\_score"),

            "previous\_objections": lead\_profile.get("objections", \[\]),

            "interaction\_count": len(session\_history)

        },

        "business\_context": {

            "last\_interaction": session\_history\[0\] if session\_history else None,

            "current\_stage": determine\_conversation\_stage(lead\_id),

            "interest\_level": behavioral\_data.get("interest\_score", "medium")

        }

    }

    

    Kestra.outputs({"conversation\_context": json.dumps(context)})

\`\`\`

\#\# ⚡ SISTEMA DE RESPOSTA RÁPIDA EM CAMADAS

\#\#\# \*\*Arquitetura de Performance\*\*

\`\`\`yaml

\# Layer 1: Cache de Respostas (\< 50ms)

\- id: quick\_response\_cache

  type: io.kestra.plugin.scripts.python.Script

  script: |

    import redis

    import hashlib

    

    message \= "{{ trigger.body.message }}".lower()

    lead\_context \= "{{ outputs.get\_lead\_basic\_data.vars.context\_hash }}"

    

    \# Cache key baseado em mensagem \+ contexto

    cache\_key \= hashlib.md5(f"{message}:{lead\_context}".encode()).hexdigest()

    

    r \= redis.Redis()

    cached\_response \= r.get(f"quick\_response:{cache\_key}")

    

    if cached\_response:

        Kestra.outputs({

            "response": cached\_response.decode(),

            "response\_type": "cached",

            "latency\_ms": 45

        })

    else:

        Kestra.outputs({"use\_intent\_classification": True})

\# Layer 2: Classificação de Intenção (\< 100ms)

\- id: intent\_classification

  type: io.kestra.plugin.huggingface.TextClassification

  model: "microsoft/DialoGPT-medium"

  inputs: "{{ trigger.body.message }}"

  runIf: "{{ outputs.quick\_response\_cache.vars.use\_intent\_classification \== true }}"

\# Layer 3: Template Response (\< 200ms)

\- id: template\_response

  type: io.kestra.plugin.scripts.python.Script

  runIf: "{{ outputs.intent\_classification.classification in \['greeting', 'yes', 'no', 'pricing'\] }}"

  script: |

    intent \= "{{ outputs.intent\_classification.classification }}"

    lead\_data \= {{ outputs.get\_lead\_basic\_data.vars | toJson }}

    

    templates \= {

        "greeting": f"Oi {lead\_data\['name'\]}\! 😊 Sou a Sílvia da Serena\!",

        "yes": f"Perfeito, {lead\_data\['name'\]}\! Vamos prosseguir... ⚡",

        "pricing": f"Vou calcular sua economia personalizada, {lead\_data\['name'\]}\! 💰"

    }

    

    response \= templates.get(intent, "")

    if response:

        \# Cache para próximas vezes

        cache\_response(response, intent, lead\_data)

        

        Kestra.outputs({

            "response": response,

            "response\_type": "template",

            "latency\_ms": 180

        })

\# Layer 4: Full AI Response (\< 2s)

\- id: full\_ai\_response

  type: io.kestra.plugin.openai.ChatCompletion

  runIf: "{{ outputs.template\_response.vars.response \== null }}"

  apiKey: "{{ secret('OPENAI\_API\_KEY') }}"

  model: "gpt-4o"

  messages:

    \- role: "system"

      content: |

        {{ file('prompts/serena\_prompts.yml').prompts.silvia\_persona.base\_personality }}

        

        Contexto da conversa:

        {{ outputs.build\_conversation\_context.vars.conversation\_context }}

        

        Use o template apropriado para a situação atual.

        

    \- role: "user" 

      content: "{{ trigger.body.message }}"

  maxTokens: 150

  temperature: 0.7

\`\`\`

\#\# 📊 WORKFLOWS COMPLETOS ESPECIFICADOS

\#\#\# \*\*Workflow 1: Lead Reception & Warmup\*\*

\`\`\`yaml

id: lead\_reception\_warmup

namespace: serena.production

description: "Recepção personalizada com quebra-gelo inteligente"

triggers:

  \- id: whatsapp\_webhook

    type: io.kestra.plugin.core.trigger.Webhook

    key: "silvia\_reception"

variables:

  SUPABASE\_MCP\_URL: "{{ secret('SUPABASE\_MCP\_URL') }}"

  WHATSAPP\_MCP\_URL: "{{ secret('WHATSAPP\_MCP\_URL') }}"

  SERENA\_MCP\_URL: "{{ secret('SERENA\_MCP\_URL') }}"

tasks:

  \- id: extract\_webhook\_data

    type: io.kestra.plugin.scripts.python.Script

    script: |

      from kestra import Kestra

      import json

      

      webhook\_data \= {{ trigger.body | toJson }}

      

      phone \= webhook\_data.get("phone", "")

      message \= webhook\_data.get("message", "")

      message\_type \= webhook\_data.get("type", "text")

      

      Kestra.outputs({

          "phone": phone,

          "message": message,

          "message\_type": message\_type,

          "timestamp": "{{ execution.startDate }}"

      })

  \- id: get\_lead\_profile

    type: io.kestra.plugin.jdbc.postgres.Query

    url: "{{ secret('SUPABASE\_CONNECTION\_STRING') }}"

    sql: |

      SELECT 

        l.name, l.city, l.state, l.invoice\_amount, l.client\_type,

        l.additional\_data, l.initial\_template\_sent,

        ls.qualification\_score, ls.interaction\_count,

        ls.last\_interaction\_date, ls.preferred\_style

      FROM leads l

      LEFT JOIN lead\_status ls ON l.phone\_number \= ls.lead\_id

      WHERE l.phone\_number \= ?

    parameters:

      \- "{{ outputs.extract\_webhook\_data.vars.phone }}"

    fetchOne: true

  \- id: calculate\_economics

    type: io.kestra.plugin.scripts.python.Script

    script: |

      from kestra import Kestra

      import json

      

      lead \= {{ outputs.get\_lead\_profile.row | toJson }}

      

      if lead and lead.get("invoice\_amount"):

          invoice\_amount \= float(lead\["invoice\_amount"\])

          

          \# Cálculos baseados em dados reais da Serena

          monthly\_savings \= invoice\_amount \* 0.18  \# 18% economia média

          yearly\_savings \= monthly\_savings \* 12

          

          \# Estimativa de investimento baseado na região

          region\_multiplier \= {

              "PE": 1.0, "CE": 0.95, "BA": 1.05, "RN": 0.98

          }.get(lead.get("state", "PE"), 1.0)

          

          investment\_estimate \= invoice\_amount \* 45 \* region\_multiplier

          payback\_months \= investment\_estimate / monthly\_savings if monthly\_savings \> 0 else 60

          

          Kestra.outputs({

              "monthly\_savings": round(monthly\_savings, 2),

              "yearly\_savings": round(yearly\_savings, 2),

              "investment\_estimate": round(investment\_estimate, 2),

              "payback\_months": round(payback\_months, 1),

              "economics\_calculated": True

          })

      else:

          Kestra.outputs({

              "economics\_calculated": False,

              "error": "No invoice amount found"

          })

  \- id: build\_conversation\_context

    type: io.kestra.plugin.scripts.python.Script

    script: |

      from kestra import Kestra

      import json

      

      lead \= {{ outputs.get\_lead\_profile.row | toJson }}

      economics \= {{ outputs.calculate\_economics.vars | toJson }}

      

      \# Determinar estágio da conversa

      if not lead:

          stage \= "new\_lead"

      elif lead.get("initial\_template\_sent"):

          stage \= "returning"

      else:

          stage \= "first\_contact"

      

      \# Determinar tom baseado no valor da conta

      if economics.get("yearly\_savings", 0\) \> 3000:

          tone \= "premium"

      else:

          tone \= "casual"

      

      context \= {

          "stage": stage,

          "tone": tone,

          "lead\_data": lead,

          "economics": economics,

          "personalization\_vars": {

              "name": lead.get("name", "amigo"),

              "city": lead.get("city", "sua cidade"),

              "bill\_amount": lead.get("invoice\_amount", 0),

              "yearly\_savings": economics.get("yearly\_savings", 0),

              "monthly\_savings": economics.get("monthly\_savings", 0\)

          }

      }

      

      Kestra.outputs({"conversation\_context": json.dumps(context)})

  \- id: generate\_personalized\_greeting

    type: io.kestra.plugin.openai.ChatCompletion

    apiKey: "{{ secret('OPENAI\_API\_KEY') }}"

    model: "gpt-4o"

    messages:

      \- role: "system"

        content: |

          {{ file('prompts/serena\_prompts.yml').prompts.silvia\_persona.base\_personality }}

          

          Contexto: {{ outputs.build\_conversation\_context.vars.conversation\_context }}

          

          Use o template de greeting apropriado baseado no tone e stage.

          Personalize com as variáveis disponíveis.

          

      \- role: "user"

        content: |

          Gere uma saudação personalizada para este lead.

          Inclua: nome, cidade, valor da conta, economia potencial.

          

    maxTokens: 200

    temperature: 0.7

  \- id: send\_whatsapp\_message

    type: io.kestra.plugin.core.http.Request

    uri: "{{ vars.WHATSAPP\_MCP\_URL }}/mcp"

    method: POST

    headers:

      Content-Type: "application/json"

    body: |

      {

        "jsonrpc": "2.0",

        "id": "{{ execution.id }}",

        "method": "tools/call",

        "params": {

          "name": "sendTextMessage",

          "arguments": {

            "to": "{{ outputs.extract\_webhook\_data.vars.phone }}",

            "message": "{{ outputs.generate\_personalized\_greeting.choices\[0\].message.content }}"

          }

        }

      }

    retries:

      maxAttempts: 3

      backoff:

        type: EXPONENTIAL

        delay: PT1S

  \- id: update\_lead\_interaction

    type: io.kestra.plugin.jdbc.postgres.Query

    url: "{{ secret('SUPABASE\_CONNECTION\_STRING') }}"

    sql: |

      INSERT INTO lead\_interactions (

        lead\_id, message\_sent, message\_received, interaction\_type, 

        response\_time\_ms, created\_at

      ) VALUES (?, ?, ?, ?, ?, NOW())

      ON CONFLICT (lead\_id, created\_at) DO NOTHING

    parameters:

      \- "{{ outputs.extract\_webhook\_data.vars.phone }}"

      \- "{{ outputs.generate\_personalized\_greeting.choices\[0\].message.content }}"

      \- "{{ outputs.extract\_webhook\_data.vars.message }}"

      \- "greeting"

      \- "{{ execution.duration.toMillis() }}"

  \- id: schedule\_followup

    type: io.kestra.plugin.core.trigger.Schedule

    inputs:

      flowId: "followup\_nurturing"

      inputs:

        lead\_id: "{{ outputs.extract\_webhook\_data.vars.phone }}"

        trigger\_type: "no\_response\_2h"

    cron: "{{ cronExpression(now().plusHours(2)) }}"

errors:

  \- id: error\_notification

    type: io.kestra.plugin.notifications.slack.SlackExecution

    url: "{{ secret('SLACK\_WEBHOOK\_URL') }}"

    channel: "\#serena-sdr-alerts"

    customMessage: |

      🚨 Erro no Workflow de Recepção

      Lead: {{ outputs.extract\_webhook\_data.vars.phone }}

      Erro: {{ task.errorMessage }}

      

  \- id: send\_fallback\_message

    type: io.kestra.plugin.core.http.Request

    uri: "{{ vars.WHATSAPP\_MCP\_URL }}/mcp"

    method: POST

    body: |

      {

        "jsonrpc": "2.0",

        "method": "tools/call",

        "params": {

          "name": "sendTextMessage",

          "arguments": {

            "to": "{{ outputs.extract\_webhook\_data.vars.phone }}",

            "message": "{{ file('prompts/serena\_prompts.yml').error\_handling.generic\_fallback }}"

          }

        }

      }

\`\`\`

\#\#\# \*\*Workflow 2: Plan Presentation\*\*

\`\`\`yaml

id: plan\_presentation

namespace: serena.production

description: "Apresentação inteligente de planos baseada no perfil"

triggers:

  \- id: plan\_interest\_webhook

    type: io.kestra.plugin.core.trigger.Webhook

    key: "silvia\_plan\_presentation"

tasks:

  \- id: get\_available\_plans

    type: io.kestra.plugin.core.http.Request

    uri: "{{ vars.SERENA\_MCP\_URL }}/mcp"

    method: POST

    body: |

      {

        "jsonrpc": "2.0",

        "id": "{{ execution.id }}",

        "method": "tools/call",

        "params": {

          "name": "obter\_planos\_gd",

          "arguments": {

            "cidade": "{{ trigger.body.city }}",

            "estado": "{{ trigger.body.state }}"

          }

        }

      }

  \- id: personalize\_plan\_presentation

    type: io.kestra.plugin.openai.ChatCompletion

    apiKey: "{{ secret('OPENAI\_API\_KEY') }}"

    model: "gpt-4o"

    messages:

      \- role: "system"

        content: |

          {{ file('prompts/serena\_prompts.yml').prompts.plan\_presentation.v2.1\_interactive }}

          

          Planos disponíveis: {{ outputs.get\_available\_plans.body }}

          Lead profile: {{ trigger.body.lead\_data }}

          

      \- role: "user"

        content: "Apresente os 3 melhores planos para este perfil específico"

    temperature: 0.6

  \- id: send\_plan\_presentation

    type: io.kestra.plugin.core.http.Request

    uri: "{{ vars.WHATSAPP\_MCP\_URL }}/mcp"

    method: POST

    body: |

      {

        "jsonrpc": "2.0",

        "method": "tools/call",

        "params": {

          "name": "sendTextMessage",

          "arguments": {

            "to": "{{ trigger.body.phone }}",

            "message": "{{ outputs.personalize\_plan\_presentation.choices\[0\].message.content }}"

          }

        }

      }

  \- id: wait\_for\_plan\_selection

    type: io.kestra.plugin.core.conds.Wait

    duration: PT10M

    

  \- id: trigger\_document\_collection

    type: io.kestra.plugin.core.trigger.Flow

    runIf: "{{ outputs.wait\_for\_plan\_selection.completed }}"

    flowId: "document\_collection"

    inputs:

      lead\_id: "{{ trigger.body.phone }}"

      selected\_plan: "{{ trigger.body.selected\_plan }}"

\`\`\`

\#\#\# \*\*Workflow 3: Document Collection (Educativo)\*\*

\`\`\`yaml

id: document\_collection

namespace: serena.production

description: "Coleta educativa e persuasiva de documentos"

triggers:

  \- id: document\_request\_trigger

    type: io.kestra.plugin.core.trigger.Webhook

    key: "silvia\_document\_collection"

tasks:

  \- id: generate\_educational\_request

    type: io.kestra.plugin.openai.ChatCompletion

    apiKey: "{{ secret('OPENAI\_API\_KEY') }}"

    model: "gpt-4o"

    messages:

      \- role: "system"

        content: |

          {{ file('prompts/serena\_prompts.yml').prompts.document\_request.v1.5\_educational }}

          

          Lead escolheu: {{ trigger.body.selected\_plan }}

          

      \- role: "user"

        content: "Crie uma mensagem educativa pedindo a fatura, explicando o benefício"

    temperature: 0.5

  \- id: send\_document\_request

    type: io.kestra.plugin.core.http.Request

    uri: "{{ vars.WHATSAPP\_MCP\_URL }}/mcp"

    method: POST

    body: |

      {

        "jsonrpc": "2.0",

        "method": "tools/call",

        "params": {

          "name": "sendTextMessage",

          "arguments": {

            "to": "{{ trigger.body.lead\_id }}",

            "message": "{{ outputs.generate\_educational\_request.choices\[0\].message.content }}"

          }

        }

      }

  \- id: wait\_for\_document

    type: io.kestra.plugin.core.conds.Wait

    duration: PT1H

    

  \- id: gentle\_reminder

    type: io.kestra.plugin.openai.ChatCompletion

    runIf: "{{ outputs.wait\_for\_document.timedOut }}"

    apiKey: "{{ secret('OPENAI\_API\_KEY') }}"

    model: "gpt-4o"

    messages:

      \- role: "system"

        content: "Gere um lembrete gentil sobre enviar a fatura"

      \- role: "user"

        content: "Lembre educadamente sobre a fatura para continuar"

  \- id: send\_gentle\_reminder

    type: io.kestra.plugin.core.http.Request

    runIf: "{{ outputs.wait\_for\_document.timedOut }}"

    uri: "{{ vars.WHATSAPP\_MCP\_URL }}/mcp"

    method: POST

    body: |

      {

        "jsonrpc": "2.0",

        "method": "tools/call",

        "params": {

          "name": "sendTextMessage",

          "arguments": {

            "to": "{{ trigger.body.lead\_id }}",

            "message": "{{ outputs.gentle\_reminder.choices\[0\].message.content }}"

          }

        }

      }

\`\`\`

\#\#\# \*\*Workflow 4: Processing & Qualification\*\*

\`\`\`yaml

id: processing\_qualification

namespace: serena.production

description: "OCR inteligente \+ qualificação \+ proposta personalizada"

triggers:

  \- id: document\_received\_trigger

    type: io.kestra.plugin.core.trigger.Webhook

    key: "silvia\_document\_processing"

tasks:

  \- id: download\_whatsapp\_image

    type: io.kestra.plugin.core.http.Download

    uri: "{{ trigger.body.image\_url }}"

    headers:

      Authorization: "Bearer {{ secret('WHATSAPP\_API\_TOKEN') }}"

  \- id: process\_invoice\_ocr

    type: io.kestra.plugin.openai.ImageToText

    apiKey: "{{ secret('OPENAI\_API\_KEY') }}"

    model: "gpt-4o"

    image: "{{ outputs.download\_whatsapp\_image.uri }}"

    prompt: |

      Analise esta fatura de energia elétrica e extraia:

      1\. Nome do cliente

      2\. Valor total da conta

      3\. Consumo em kWh

      4\. Distribuidora

      5\. Endereço de instalação

      6\. Tipo de cliente (residencial/comercial)

      

      Retorne em formato JSON estruturado.

  \- id: validate\_extraction

    type: io.kestra.plugin.scripts.python.Script

    script: |

      from kestra import Kestra

      import json

      import re

      

      ocr\_result \= {{ outputs.process\_invoice\_ocr.text | toJson }}

      

      try:

          \# Parse JSON do OCR

          invoice\_data \= json.loads(ocr\_result)

          

          \# Validações

          valor\_conta \= float(re.sub(r'\[^\\d,.\]', '', str(invoice\_data.get('valor\_total', '0'))))

          consumo\_kwh \= float(re.sub(r'\[^\\d,.\]', '', str(invoice\_data.get('consumo', '0'))))

          

          is\_valid \= valor\_conta \> 50 and consumo\_kwh \> 0

          

          Kestra.outputs({

              "invoice\_data": invoice\_data,

              "valor\_conta": valor\_conta,

              "consumo\_kwh": consumo\_kwh,

              "is\_valid": is\_valid,

              "extraction\_success": True

          })

          

      except Exception as e:

          Kestra.outputs({

              "extraction\_success": False,

              "error": str(e)

          })

  \- id: qualify\_lead

    type: io.kestra.plugin.core.http.Request

    uri: "{{ vars.SERENA\_MCP\_URL }}/mcp"

    method: POST

    body: |

      {

        "jsonrpc": "2.0",

        "method": "tools/call",

        "params": {

          "name": "validar\_qualificacao\_lead",

          "arguments": {

            "cidade": "{{ trigger.body.city }}",

            "estado": "{{ trigger.body.state }}",

            "tipo\_pessoa": "natural",

            "valor\_conta": {{ outputs.validate\_extraction.vars.valor\_conta }}

          }

        }

      }

  \- id: generate\_qualification\_result

    type: io.kestra.plugin.openai.ChatCompletion

    apiKey: "{{ secret('OPENAI\_API\_KEY') }}"

    model: "gpt-4o"

    messages:

      \- role: "system"

        content: |

          {{ file('prompts/serena\_prompts.yml').prompts.qualification\_result.qualified\_high }}

          

          Dados da fatura: {{ outputs.validate\_extraction.vars.invoice\_data }}

          Qualificação: {{ outputs.qualify\_lead.body }}

          

      \- role: "user"

        content: "Gere resultado da qualificação personalizada"

    temperature: 0.4

  \- id: send\_qualification\_result

    type: io.kestra.plugin.core.http.Request

    uri: "{{ vars.WHATSAPP\_MCP\_URL }}/mcp"

    method: POST

    body: |

      {

        "jsonrpc": "2.0",

        "method": "tools/call",

        "params": {

          "name": "sendTextMessage",

          "arguments": {

            "to": "{{ trigger.body.lead\_id }}",

            "message": "{{ outputs.generate\_qualification\_result.choices\[0\].message.content }}"

          }

        }

      }

  \- id: update\_lead\_qualification

    type: io.kestra.plugin.jdbc.postgres.Query

    url: "{{ secret('SUPABASE\_CONNECTION\_STRING') }}"

    sql: |

      INSERT INTO lead\_status (

        lead\_id, status, qualification\_score, bill\_amount, 

        consumption\_kwh, qualification\_date, notes

      ) VALUES (?, ?, ?, ?, ?, NOW(), ?)

      ON CONFLICT (lead\_id) DO UPDATE SET

        qualification\_score \= EXCLUDED.qualification\_score,

        bill\_amount \= EXCLUDED.bill\_amount,

        consumption\_kwh \= EXCLUDED.consumption\_kwh,

        qualification\_date \= NOW(),

        notes \= EXCLUDED.notes

    parameters:

      \- "{{ trigger.body.lead\_id }}"

      \- "qualified"

      \- 1

      \- "{{ outputs.validate\_extraction.vars.valor\_conta }}"

      \- "{{ outputs.validate\_extraction.vars.consumo\_kwh }}"

      \- "{{ outputs.validate\_extraction.vars.invoice\_data }}"

  \- id: create\_serena\_lead

    type: io.kestra.plugin.core.http.Request

    runIf: "{{ outputs.qualify\_lead.body.qualified \== true }}"

    uri: "{{ vars.SERENA\_MCP\_URL }}/mcp"

    method: POST

    body: |

      {

        "jsonrpc": "2.0",

        "method": "tools/call",

        "params": {

          "name": "cadastrar\_lead",

          "arguments": {

            "dados\_lead": {

              "fullName": "{{ outputs.validate\_extraction.vars.invoice\_data.nome\_cliente }}",

              "personType": "natural",

              "phone": "{{ trigger.body.lead\_id }}",

              "city": "{{ trigger.body.city }}",

              "state": "{{ trigger.body.state }}",

              "monthlyBill": {{ outputs.validate\_extraction.vars.valor\_conta }},

              "consumption": {{ outputs.validate\_extraction.vars.consumo\_kwh }},

              "leadSource": "WhatsApp\_Silvia\_AI"

            }

          }

        }

      }

\`\`\`

\#\#\# \*\*Workflow 5: Follow-up Inteligente\*\*

\`\`\`yaml

id: followup\_nurturing

namespace: serena.production

description: "Sistema de follow-up contextual e recuperação de leads"

triggers:

  \- id: scheduled\_followup

    type: io.kestra.plugin.core.trigger.Schedule

    cron: "0 9,14,18 \* \* \*"  \# 3x por dia

    

  \- id: manual\_followup\_trigger

    type: io.kestra.plugin.core.trigger.Webhook

    key: "silvia\_followup"

tasks:

  \- id: get\_leads\_needing\_followup

    type: io.kestra.plugin.jdbc.postgres.Query

    url: "{{ secret('SUPABASE\_CONNECTION\_STRING') }}"

    sql: |

      SELECT DISTINCT

        l.phone\_number as lead\_id,

        l.name, l.city, l.state,

        ls.last\_interaction\_date,

        ls.interaction\_count,

        ls.lead\_stage,

        EXTRACT(HOURS FROM (NOW() \- ls.last\_interaction\_date)) as hours\_since\_last

      FROM leads l

      JOIN lead\_status ls ON l.phone\_number \= ls.lead\_id

      WHERE ls.status \= 'active'

        AND ls.last\_interaction\_date \< NOW() \- INTERVAL '2 hours'

        AND ls.followup\_count \< 3

        AND EXTRACT(HOURS FROM NOW()) BETWEEN 9 AND 18

      ORDER BY ls.qualification\_score DESC, ls.last\_interaction\_date ASC

      LIMIT 50

    fetchType: FETCH

  \- id: process\_followup\_leads

    type: io.kestra.plugin.core.flowable.EachSequential

    value: "{{ outputs.get\_leads\_needing\_followup.rows }}"

    tasks:

      \- id: analyze\_lead\_context

        type: io.kestra.plugin.scripts.python.Script

        script: |

          from kestra import Kestra

          import json

          

          lead \= {{ taskrun.value | toJson }}

          hours\_since \= lead.get("hours\_since\_last", 0\)

          interaction\_count \= lead.get("interaction\_count", 0\)

          stage \= lead.get("lead\_stage", "initial")

          

          \# Determinar tipo de follow-up

          if hours\_since \< 4 and stage \== "document\_requested":

              followup\_type \= "document\_reminder"

          elif hours\_since \< 24 and interaction\_count \< 3:

              followup\_type \= "gentle\_nudge"

          elif hours\_since \> 24 and stage in \["qualified", "interested"\]:

              followup\_type \= "value\_reinforcement"

          else:

              followup\_type \= "last\_chance"

          

          Kestra.outputs({

              "lead\_data": lead,

              "followup\_type": followup\_type,

              "personalization\_context": {

                  "urgency\_level": "high" if followup\_type \== "last\_chance" else "medium",

                  "content\_focus": "benefits" if followup\_type \== "value\_reinforcement" else "action"

              }

          })

      \- id: generate\_contextual\_followup

        type: io.kestra.plugin.openai.ChatCompletion

        apiKey: "{{ secret('OPENAI\_API\_KEY') }}"

        model: "gpt-4o"

        messages:

          \- role: "system"

            content: |

              Você é Sílvia da Serena Energia. Gere uma mensagem de follow-up contextual.

              

              Contexto: {{ outputs.analyze\_lead\_context.vars | toJson }}

              

              Regras:

              \- Seja natural, não robótica

              \- Referencie conversas anteriores

              \- Ofereça valor, não pressione

              \- Use emojis apropriados

              \- Mantenha tom brasileiro amigável

              

          \- role: "user"

            content: |

              Tipo de follow-up: {{ outputs.analyze\_lead\_context.vars.followup\_type }}

              Lead: {{ outputs.analyze\_lead\_context.vars.lead\_data.name }}

              Última interação: {{ outputs.analyze\_lead\_context.vars.lead\_data.hours\_since\_last }} horas atrás

              

        temperature: 0.7

        maxTokens: 150

      \- id: send\_followup\_message

        type: io.kestra.plugin.core.http.Request

        uri: "{{ vars.WHATSAPP\_MCP\_URL }}/mcp"

        method: POST

        body: |

          {

            "jsonrpc": "2.0",

            "method": "tools/call",

            "params": {

              "name": "sendTextMessage",

              "arguments": {

                "to": "{{ outputs.analyze\_lead\_context.vars.lead\_data.lead\_id }}",

                "message": "{{ outputs.generate\_contextual\_followup.choices\[0\].message.content }}"

              }

            }

          }

        retries:

          maxAttempts: 2

      \- id: update\_followup\_record

        type: io.kestra.plugin.jdbc.postgres.Query

        url: "{{ secret('SUPABASE\_CONNECTION\_STRING') }}"

        sql: |

          UPDATE lead\_status 

          SET followup\_count \= followup\_count \+ 1,

              last\_followup\_date \= NOW(),

              last\_followup\_type \= ?

          WHERE lead\_id \= ?

        parameters:

          \- "{{ outputs.analyze\_lead\_context.vars.followup\_type }}"

          \- "{{ outputs.analyze\_lead\_context.vars.lead\_data.lead\_id }}"

  \- id: daily\_followup\_report

    type: io.kestra.plugin.notifications.slack.SlackExecution

    url: "{{ secret('SLACK\_WEBHOOK\_URL') }}"

    channel: "\#serena-sdr-reports"

    customMessage: |

      📊 Relatório de Follow-up Sílvia

      

      ✅ Mensagens enviadas: {{ outputs.process\_followup\_leads.numberOfExecutedTasks }}

      ⏰ Período: {{ execution.startDate | date('dd/MM/yyyy HH:mm') }}

      

      Próximo follow-up em 4 horas.

\`\`\`

\#\#\# \*\*Workflow 6: Monitoring & Alerts\*\*

\`\`\`yaml

id: monitoring\_alerts

namespace: serena.production

description: "Monitoramento em tempo real \+ alertas inteligentes"

triggers:

  \- id: health\_check\_schedule

    type: io.kestra.plugin.core.trigger.Schedule

    cron: "\*/5 \* \* \* \*"  \# A cada 5 minutos

tasks:

  \- id: check\_mcp\_servers\_health

    type: io.kestra.plugin.core.flowable.Parallel

    tasks:

      \- id: check\_whatsapp\_mcp

        type: io.kestra.plugin.core.http.Request

        uri: "{{ vars.WHATSAPP\_MCP\_URL }}/health"

        timeout: PT5S

        

      \- id: check\_supabase\_mcp

        type: io.kestra.plugin.core.http.Request

        uri: "{{ vars.SUPABASE\_MCP\_URL }}/health"

        timeout: PT5S

        

      \- id: check\_serena\_mcp

        type: io.kestra.plugin.core.http.Request

        uri: "{{ vars.SERENA\_MCP\_URL }}/health"

        timeout: PT5S

  \- id: check\_system\_metrics

    type: io.kestra.plugin.jdbc.postgres.Query

    url: "{{ secret('SUPABASE\_CONNECTION\_STRING') }}"

    sql: |

      WITH metrics AS (

        SELECT 

          COUNT(\*) FILTER (WHERE created\_at \> NOW() \- INTERVAL '1 hour') as leads\_1h,

          COUNT(\*) FILTER (WHERE created\_at \> NOW() \- INTERVAL '24 hours') as leads\_24h,

          AVG(response\_time\_ms) FILTER (WHERE created\_at \> NOW() \- INTERVAL '1 hour') as avg\_response\_time,

          COUNT(\*) FILTER (WHERE status \= 'error' AND created\_at \> NOW() \- INTERVAL '1 hour') as errors\_1h

        FROM lead\_interactions

      )

      SELECT \* FROM metrics

    fetchOne: true

  \- id: evaluate\_system\_health

    type: io.kestra.plugin.scripts.python.Script

    script: |

      from kestra import Kestra

      

      metrics \= {{ outputs.check\_system\_metrics.row | toJson }}

      mcp\_health \= {

          "whatsapp": {{ outputs.check\_whatsapp\_mcp.code \== 200 }},

          "supabase": {{ outputs.check\_supabase\_mcp.code \== 200 }},

          "serena": {{ outputs.check\_serena\_mcp.code \== 200 }}

      }

      

      \# Critérios de saúde

      issues \= \[\]

      

      \# Verificar MCPs

      for service, healthy in mcp\_health.items():

          if not healthy:

              issues.append(f"MCP {service} indisponível")

      

      \# Verificar métricas

      avg\_response \= metrics.get("avg\_response\_time", 0\)

      if avg\_response \> 2000:  \# \> 2 segundos

          issues.append(f"Tempo de resposta alto: {avg\_response}ms")

      

      errors\_1h \= metrics.get("errors\_1h", 0\)

      if errors\_1h \> 10:

          issues.append(f"Muitos erros na última hora: {errors\_1h}")

      

      leads\_1h \= metrics.get("leads\_1h", 0\)

      if leads\_1h \== 0:

          issues.append("Nenhum lead processado na última hora")

      

      health\_status \= "healthy" if not issues else "degraded" if len(issues) \<= 2 else "critical"

      

      Kestra.outputs({

          "health\_status": health\_status,

          "issues": issues,

          "metrics": metrics,

          "mcp\_status": mcp\_health

      })

  \- id: send\_critical\_alert

    type: io.kestra.plugin.notifications.slack.SlackExecution

    runIf: "{{ outputs.evaluate\_system\_health.vars.health\_status \== 'critical' }}"

    url: "{{ secret('SLACK\_WEBHOOK\_URL') }}"

    channel: "\#serena-sdr-alerts"

    customMessage: |

      🚨 ALERTA CRÍTICO \- Sílvia SDR

      

      Status: {{ outputs.evaluate\_system\_health.vars.health\_status }}

      

      Problemas identificados:

      {% for issue in outputs.evaluate\_system\_health.vars.issues %}

      • {{ issue }}

      {% endfor %}

      

      MCPs Status:

      • WhatsApp: {{ outputs.evaluate\_system\_health.vars.mcp\_status.whatsapp ? "✅" : "❌" }}

      • Supabase: {{ outputs.evaluate\_system\_health.vars.mcp\_status.supabase ? "✅" : "❌" }}

      • Serena: {{ outputs.evaluate\_system\_health.vars.mcp\_status.serena ? "✅" : "❌" }}

      

      Verifique o sistema imediatamente\!

  \- id: daily\_performance\_report

    type: io.kestra.plugin.core.conds.RunIf

    condition: "{{ execution.startDate.hour \== 18 }}"  \# 18h todos os dias

    tasks:

      \- id: generate\_daily\_metrics

        type: io.kestra.plugin.jdbc.postgres.Query

        url: "{{ secret('SUPABASE\_CONNECTION\_STRING') }}"

        sql: |

          WITH daily\_stats AS (

            SELECT 

              COUNT(DISTINCT lead\_id) as unique\_leads,

              COUNT(\*) as total\_interactions,

              AVG(response\_time\_ms) as avg\_response\_time,

              COUNT(\*) FILTER (WHERE interaction\_type \= 'qualification') as qualifications,

              COUNT(\*) FILTER (WHERE interaction\_type \= 'contract\_created') as contracts

            FROM lead\_interactions 

            WHERE DATE(created\_at) \= CURRENT\_DATE

          )

          SELECT 

            \*,

            ROUND((qualifications::float / NULLIF(unique\_leads, 0)) \* 100, 2\) as qualification\_rate,

            ROUND((contracts::float / NULLIF(qualifications, 0)) \* 100, 2\) as conversion\_rate

          FROM daily\_stats

        fetchOne: true

      \- id: send\_daily\_report

        type: io.kestra.plugin.notifications.slack.SlackExecution

        url: "{{ secret('SLACK\_WEBHOOK\_URL') }}"

        channel: "\#serena-sdr-reports"

        customMessage: |

          📊 Relatório Diário \- Sílvia SDR

          Data: {{ execution.startDate | date('dd/MM/yyyy') }}

          

          📈 \*\*Performance\*\*

          • Leads únicos: {{ outputs.generate\_daily\_metrics.row.unique\_leads }}

          • Total interações: {{ outputs.generate\_daily\_metrics.row.total\_interactions }}

          • Tempo médio resposta: {{ outputs.generate\_daily\_metrics.row.avg\_response\_time }}ms

          

          🎯 \*\*Conversão\*\*

          • Qualificações: {{ outputs.generate\_daily\_metrics.row.qualifications }}

          • Taxa qualificação: {{ outputs.generate\_daily\_metrics.row.qualification\_rate }}%

          • Contratos: {{ outputs.generate\_daily\_metrics.row.contracts }}

          • Taxa conversão: {{ outputs.generate\_daily\_metrics.row.conversion\_rate }}%

          

          {% if outputs.generate\_daily\_metrics.row.avg\_response\_time \> 1000 %}

          ⚠️ Atenção: Tempo de resposta acima do ideal

          {% endif %}

\`\`\`

\#\# 🗂️ ESTRUTURA DE DADOS COMPLETA

\#\#\# \*\*Schemas Supabase\*\*

\`\`\`sql

\-- Tabela principal de leads

CREATE TABLE leads (

    id SERIAL PRIMARY KEY,

    phone\_number VARCHAR(20) UNIQUE NOT NULL,

    name VARCHAR(100) NOT NULL,

    email VARCHAR(100),

    city VARCHAR(50),

    state VARCHAR(2),

    invoice\_amount DECIMAL(10,2),

    client\_type VARCHAR(20) DEFAULT 'residential',

    lead\_source VARCHAR(50) DEFAULT 'whatsapp\_silvia',

    additional\_data JSONB DEFAULT '{}',

    initial\_template\_sent BOOLEAN DEFAULT FALSE,

    created\_at TIMESTAMP DEFAULT NOW(),

    updated\_at TIMESTAMP DEFAULT NOW()

);

\-- Status e histórico detalhado

CREATE TABLE lead\_status (

    lead\_id VARCHAR(20) PRIMARY KEY,

    status VARCHAR(20) NOT NULL DEFAULT 'new',

    lead\_stage VARCHAR(30) DEFAULT 'initial\_contact',

    qualification\_score INTEGER DEFAULT 0,

    bill\_amount DECIMAL(10,2),

    consumption\_kwh DECIMAL(10,2),

    interaction\_count INTEGER DEFAULT 0,

    followup\_count INTEGER DEFAULT 0,

    last\_interaction\_date TIMESTAMP DEFAULT NOW(),

    last\_followup\_date TIMESTAMP,

    last\_followup\_type VARCHAR(30),

    qualification\_date TIMESTAMP,

    contract\_created\_date TIMESTAMP,

    preferred\_style VARCHAR(20) DEFAULT 'casual',

    notes TEXT,

    created\_at TIMESTAMP DEFAULT NOW(),

    updated\_at TIMESTAMP DEFAULT NOW()

);

\-- Interações detalhadas para análise

CREATE TABLE lead\_interactions (

    id SERIAL PRIMARY KEY,

    lead\_id VARCHAR(20) NOT NULL,

    interaction\_type VARCHAR(30) NOT NULL,

    message\_sent TEXT,

    message\_received TEXT,

    response\_time\_ms INTEGER,

    ai\_model\_used VARCHAR(20) DEFAULT 'gpt-4o',

    prompt\_version VARCHAR(10),

    success BOOLEAN DEFAULT TRUE,

    error\_message TEXT,

    metadata JSONB DEFAULT '{}',

    created\_at TIMESTAMP DEFAULT NOW()

);

\-- Logs técnicos para debugging

CREATE TABLE sdr\_logs (

    id SERIAL PRIMARY KEY,

    execution\_id VARCHAR(50),

    workflow\_id VARCHAR(50),

    task\_id VARCHAR(50),

    lead\_id VARCHAR(20),

    log\_level VARCHAR(10) DEFAULT 'INFO',

    message TEXT,

    duration\_ms INTEGER,

    success BOOLEAN DEFAULT TRUE,

    error\_details JSONB,

    created\_at TIMESTAMP DEFAULT NOW()

);

\-- Cache de respostas para performance

CREATE TABLE response\_cache (

    id SERIAL PRIMARY KEY,

    cache\_key VARCHAR(64) UNIQUE,

    intent\_type VARCHAR(30),

    response\_text TEXT,

    hit\_count INTEGER DEFAULT 0,

    last\_used TIMESTAMP DEFAULT NOW(),

    expires\_at TIMESTAMP,

    created\_at TIMESTAMP DEFAULT NOW()

);

\-- Índices para performance

CREATE INDEX idx\_leads\_phone ON leads(phone\_number);

CREATE INDEX idx\_lead\_status\_stage ON lead\_status(lead\_stage, last\_interaction\_date);

CREATE INDEX idx\_interactions\_lead\_created ON lead\_interactions(lead\_id, created\_at DESC);

CREATE INDEX idx\_logs\_execution ON sdr\_logs(execution\_id, created\_at DESC);

CREATE INDEX idx\_cache\_key ON response\_cache(cache\_key, expires\_at);

\-- Views para métricas

CREATE VIEW daily\_metrics AS

SELECT 

    DATE(created\_at) as date,

    COUNT(DISTINCT lead\_id) as unique\_leads,

    COUNT(\*) as total\_interactions,

    AVG(response\_time\_ms) as avg\_response\_time,

    COUNT(\*) FILTER (WHERE interaction\_type \= 'qualification') as qualifications,

    COUNT(\*) FILTER (WHERE interaction\_type \= 'contract\_created') as contracts,

    COUNT(\*) FILTER (WHERE success \= false) as errors

FROM lead\_interactions 

GROUP BY DATE(created\_at)

ORDER BY date DESC;

\`\`\`

\#\# 🚀 CONFIGURAÇÃO E DEPLOYMENT

\#\#\# \*\*1. Variáveis de Ambiente\*\*

\`\`\`yaml

\# .env

\# OpenAI

OPENAI\_API\_KEY=sk-your-openai-api-key

OPENAI\_MODEL=gpt-4o

OPENAI\_MAX\_TOKENS=200

OPENAI\_TEMPERATURE=0.7

\# MCP Servers

WHATSAPP\_MCP\_URL=http://bw48gc80kokwwckg0wskc40c.157.180.32.249.sslip.io

SUPABASE\_MCP\_URL=http://hwg4ks4ooooc04wsosookoog.157.180.32.249.sslip.io

SERENA\_MCP\_URL=http://mwc8k8wk0wg8o8s4k0w8scc4.157.180.32.249.sslip.io

\# Supabase Database

SUPABASE\_CONNECTION\_STRING=postgresql://postgres:password@your-project.supabase.co:5432/postgres

SUPABASE\_URL=https://your-project.supabase.co

SUPABASE\_ANON\_KEY=your-supabase-anon-key

SUPABASE\_SERVICE\_ROLE\_KEY=your-supabase-service-role-key

\# WhatsApp Business API

WHATSAPP\_API\_TOKEN=your-whatsapp-api-token

WHATSAPP\_PHONE\_NUMBER\_ID=599096403294262

WHATSAPP\_BUSINESS\_ACCOUNT\_ID=your-business-account-id

\# Serena API

SERENA\_API\_TOKEN=your-serena-api-token

PARTNERSHIP\_API\_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

\# Monitoring

SLACK\_WEBHOOK\_URL=https://hooks.slack.com/your-webhook-url

REDIS\_URL=redis://redis:6379/0

\# Kestra

KESTRA\_URL=https://kestra.darwinai.com.br

KESTRA\_NAMESPACE=serena.production

\`\`\`

\#\#\# \*\*2. Docker Compose Setup\*\*

\`\`\`yaml

\# docker-compose.yml

version: '3.8'

services:

  redis:

    image: redis:7-alpine

    container\_name: serena-redis

    ports:

      \- "6379:6379"

    volumes:

      \- redis\_/data

    networks:

      \- serena-network

  kestra-postgres:

    image: postgres:15

    environment:

      POSTGRES\_DB: kestra

      POSTGRES\_USER: kestra

      POSTGRES\_PASSWORD: kestra\_password

    volumes:

      \- postgres\_/var/lib/postgresql/data

    networks:

      \- serena-network

  kestra:

    image: kestra/kestra:latest

    environment:

      KESTRA\_CONFIGURATION: |

        kestra:

          server:

            base-url: "http://localhost:8080"

          repository:

            type: postgres

          datasources:

            postgres:

              url: jdbc:postgresql://kestra-postgres:5432/kestra

              username: kestra

              password: kestra\_password

    ports:

      \- "8080:8080"

    depends\_on:

      \- kestra-postgres

      \- redis

    volumes:

      \- ./workflows:/app/workflows

      \- ./prompts:/app/prompts

      \- ./scripts:/app/scripts

    networks:

      \- serena-network

volumes:

  postgres\_

  redis\_

networks:

  serena-network:

    driver: bridge

\`\`\`

\#\#\# \*\*3. Scripts de Deploy\*\*

\`\`\`bash

\#\!/bin/bash

\# deploy.sh

echo "🚀 Iniciando deploy do Serena SDR Sílvia 2.0..."

\# Build e start dos containers

docker-compose up \-d \--build

\# Aguardar Kestra inicializar

echo "⏳ Aguardando Kestra inicializar..."

sleep 30

\# Upload dos workflows

echo "📂 Fazendo upload dos workflows..."

for workflow in workflows/\*.yml; do

    curl \-X POST \\

        \-H "Content-Type: application/yaml" \\

        \-d @"$workflow" \\

        "http://localhost:8080/api/v1/flows"

done

\# Criar tabelas no Supabase

echo "🗄️ Criando estrutura do banco..."

psql $SUPABASE\_CONNECTION\_STRING \-f scripts/create\_tables.sql

\# Configurar webhooks

echo "🔗 Configurando webhooks..."

./scripts/setup\_webhooks.sh

\# Verificar saúde do sistema

echo "🏥 Verificando saúde do sistema..."

curl \-f http://localhost:8080/api/v1/stats || exit 1

curl \-f $WHATSAPP\_MCP\_URL/health || exit 1

curl \-f $SUPABASE\_MCP\_URL/health || exit 1

curl \-f $SERENA\_MCP\_URL/health || exit 1

echo "✅ Deploy concluído com sucesso\!"

echo "🌟 Sílvia 2.0 está online e pronta para atender\!"

\`\`\`

\#\# 📊 MÉTRICAS E KPIs

\#\#\# \*\*Dashboard de Métricas\*\*

\`\`\`yaml

\# Métricas principais para monitorar

kpis:

  performance:

    \- response\_time\_avg: "\< 500ms"

    \- response\_time\_p95: "\< 2s"

    \- availability: "\> 99.5%"

    \- error\_rate: "\< 1%"


  business:

    \- leads\_per\_day: "target: 50+"

    \- qualification\_rate: "target: 35%+"

    \- lead\_to\_meeting: "target: 45%+"

    \- conversion\_rate: "target: 15%+"


  ai\_quality:

    \- response\_relevance: "target: 95%+"

    \- personality\_consistency: "target: 90%+"

    \- context\_retention: "target: 85%+"

    \- user\_satisfaction: "target: 4.5/5"

\`\`\`

\#\# ✅ CHECKLIST DE IMPLEMENTAÇÃO

\#\#\# \*\*Fase 1: Fundação (Semana 1)\*\*

\- \[ \] Setup do ambiente Docker \+ Kestra

\- \[ \] Configuração dos MCPs e APIs

\- \[ \] Criação das tabelas Supabase

\- \[ \] Workflow básico de recepção

\- \[ \] Sistema de prompts versionados

\- \[ \] Testes básicos de conectividade

\#\#\# \*\*Fase 2: Core Features (Semana 2-3)\*\*

\- \[ \] Sistema de personalização contextual

\- \[ \] Cache de respostas rápidas

\- \[ \] OCR inteligente com OpenAI Vision

\- \[ \] Qualificação automática via Serena API

\- \[ \] Sistema de follow-up inteligente

\- \[ \] Monitoring básico \+ alertas Slack

\#\#\# \*\*Fase 3: Otimização (Semana 4)\*\*

\- \[ \] Sistema de memória contextual

\- \[ \] Conversation flows dinâmicos

\- \[ \] A/B testing de prompts

\- \[ \] Métricas avançadas

\- \[ \] Dashboard de performance

\- \[ \] Testes de carga

\#\#\# \*\*Fase 4: Scale & Polish (Semana 5-6)\*\*

\- \[ \] Multi-channel expansion

\- \[ \] Advanced personalization

\- \[ \] Predictive analytics

\- \[ \] Error recovery avançado

\- \[ \] Documentation completa

\- \[ \] Training da equipe

\#\# 🎯 RESULTADO ESPERADO

Com esta implementação, a \*\*Sílvia 2.0\*\* será:

✅ \*\*Humanizada\*\*: Conversas naturais com personalização contextual  

✅ \*\*Rápida\*\*: \<500ms para 80% das respostas  

✅ \*\*Inteligente\*\*: Memória contextual \+ qualificação automática  

✅ \*\*Escalável\*\*: Arquitetura modular que suporta crescimento  

✅ \*\*Monitorável\*\*: Métricas em tempo real \+ alertas proativos  

✅ \*\*Resiliente\*\*: Error handling \+ fallbacks inteligentes


\*\*Meta de ROI\*\*: 400-500% vs. 150% atual  

\*\*Performance Target\*\*: 3-5x melhoria em conversões  

\*\*Satisfação do Lead\*\*: 4.5/5 stars


\# 🔥 CONCLUSÃO

Este guia definitivo fornece \*\*tudo\*\* que uma IA de codificação precisa para implementar o \*\*Serena SDR Sílvia 2.0\*\* com excelência:

1\. \*\*Especificações técnicas completas\*\* com código real

2\. \*\*Workflows modulares\*\* totalmente especificados

3\. \*\*Sistema de personalização avançado\*\* baseado em dados reais

4\. \*\*Arquitetura de performance\*\* com resposta \<500ms

5\. \*\*Monitoramento e alertas\*\* profissionais

6\. \*\*Deploy e configuração\*\* step-by-step

A Sílvia 2.0 será uma \*\*revolução\*\* no mercado de AI SDRs brasileiro, combinando o melhor da tecnologia com a personalidade humana brasileira. 

\*\*Próximo passo\*\*: Execute este guia e transforme o Serena SDR no líder absoluto do mercado\! 🚀⚡🇧🇷

Fontes

