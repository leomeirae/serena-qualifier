# **MASTER GUIDE FINAL: Sistema Serena Lead Qualifier**

Versão: Final 1.0  
Status: Este documento é a fonte canônica e definitiva de informação para o projeto, substituindo todas as versões e documentos anteriores.

### **Navegação Rápida (Quick Links)**

1. [Estrutura de Pastas do Projeto](#bookmark=id.4yzm4496vgq2)  
2. [Visão Geral e Arquitetura](#bookmark=id.mj57gfy6mags)  
3. [Fluxo 1: Ativação do Lead](#bookmark=id.68yr141nmzac)  
4. [Fluxo 2: Conversa com IA](#bookmark=id.rr694zqo0tth)  
5. [Guia do Agente de IA](#bookmark=id.jcqno9si2yzp)  
6. [Modelo de Dados](#bookmark=id.rcnd36j43q7n)  
7. [Políticas e Métricas](#bookmark=id.7lzmj3j5k44i)  
8. [Guia de Conversação](#bookmark=id.jrntdwb51345)  
9. [Variáveis de Ambiente](#bookmark=id.y38khhkejksa)  
10. [Operações e Produção](#bookmark=id.5mgb9yxnnub8)

## **1\. Estrutura de Pastas do Projeto**

A seguir, a estrutura de diretórios principal para rápida localização dos artefatos. O caminho raiz é /Users/user/Desktop/serena-qualifier.

/  
├── kestra/                    \# Orquestração  
│   └── workflows/             \# Definições dos fluxos Kestra  
├── knowledge\_base/            \# Documentos para o RAG da IA  
├── scripts/                   \# Módulos e serviços Python  
│   ├── serena\_agent/          \# Lógica do Agente LangChain  
│   │   ├── tools/             \# Ferramentas do Agente  
│   │   └── prompts/           \# Templates de prompt  
│   ├── ocr\_processor.py       \# Lógica de OCR  
│   ├── serena\_api.py          \# Cliente da API Serena  
│   └── whatsapp\_sender.py     \# Serviço de webhook e envio de msg  
├── serena-landing-page/       \# Código-fonte da página de captura (Next.js)  
├── tests/                     \# Testes automatizados (pytest)  
├── utils/                     \# Módulos utilitários  
│   └── conversation\_manager.py \# Gestão de estado com Supabase  
├── docker-compose-minimal.yml \# Arquivo Docker para ambiente local  
└── .env.example               \# Exemplo de variáveis de ambiente

## **2\. Visão Geral e Arquitetura Consolidada**

### **Objetivo do Sistema**

Implementar um sistema automatizado para a captura, interação, qualificação e persistência de leads para a Serena Energia, utilizando Kestra para orquestração de alto nível e um agente de IA especializado (baseado em LangChain) para toda a lógica de conversação.

### **Arquitetura de Dois Workflows**

O sistema opera com uma arquitetura de **dois workflows Kestra distintos e desacoplados** para garantir robustez e clareza.

1. **Fluxo de Ativação**: Responsável unicamente pela captura do lead e pelo envio da primeira mensagem de ativação.  
2. **Fluxo de Conversação**: Responsável por toda a interação subsequente, delegando a "inteligência" para o SerenaAIAgent.

### **Diagrama da Arquitetura**

**Versão Lógica (Mermaid):**

sequenceDiagram  
    participant User as Usuário  
    participant LP as Landing Page (Next.js)  
    participant Kestra1 as Kestra (Fluxo Ativação)  
    participant WhatsApp as WhatsApp API  
    participant WebhookSvc as Serviço Webhook (Python)  
    participant Kestra2 as Kestra (Fluxo Conversa)  
    participant AIAgent as SerenaAIAgent (LangChain)  
    participant Supabase  
    participant SerenaAPI as API Serena

    User-\>\>LP: Preenche Formulário  
    LP-\>\>Kestra1: POST /capture (Webhook)  
    Kestra1-\>\>Supabase: Salva Lead Inicial  
    Kestra1-\>\>WhatsApp: Envia Template de Ativação  
    activate WhatsApp  
        WhatsApp--\>\>User: Mostra Mensagem com Botão  
    deactivate WhatsApp  
    User-\>\>WhatsApp: Clica em "Ativar Perfil\!"  
    WhatsApp-\>\>WebhookSvc: POST /webhook (Mensagem do Lead)  
    WebhookSvc-\>\>Kestra2: POST /continue (Webhook)  
    Kestra2-\>\>AIAgent: Executa Agente com a mensagem  
    activate AIAgent  
        AIAgent-\>\>Supabase: Pede histórico da conversa  
        Supabase--\>\>AIAgent: Retorna histórico  
        AIAgent-\>\>SerenaAPI: Verifica cobertura/planos  
        SerenaAPI--\>\>AIAgent: Retorna dados  
        AIAgent-\>\>AIAgent: Gera resposta  
        AIAgent--\>\>Kestra2: Retorna texto da resposta  
    deactivate AIAgent  
    Kestra2-\>\>WhatsApp: Envia resposta da IA  
    WhatsApp--\>\>User: Exibe resposta

Versão Gráfica:  
\[Imagem da Arquitetura\]  
(Nota: Inserir aqui um PNG ou SVG do diagrama para stakeholders não técnicos).

## **3\. Fluxo 1: lead-activation.yml (Ativação do Lead)**

* **Arquivo**: /Users/user/Desktop/serena-qualifier/kestra/workflows/lead-activation.yml.

### **Gatilho (Trigger)**

* **Tipo**: io.kestra.core.tasks.flows.Webhook  
* **URI**: /capture  
* **Origem**: API route em serena-landing-page/app/api/form-submit/route.ts.

**Request Body (JSON):**

{  
  "name": "João da Silva",  
  "email": "joao.silva@example.com",  
  "phone": "+5511987654321",  
  "city": "São Paulo"  
}

**Response (Success):**

* **Status Code**: 202 Accepted  
* **Body**: {"message": "Lead capture accepted", "executionId": "xyz..."}

**Response (Error):**

* **Status Code**: 400 Bad Request (ex: campo faltando) \-\> {"error": "Field 'phone' is required"}  
* **Status Code**: 422 Unprocessable Entity (ex: email inválido) \-\> {"error": "Invalid email format"}  
* **Status Code**: 500 Internal Server Error \-\> {"error": "Kestra trigger failed"}

### **Tarefas (Tasks)**

1. **save-initial-lead (Python)**: Salva os dados do lead no Supabase.  
2. **send-activation-template (Bash)**: Envia o template "Ativar Perfil\!" via curl para o serviço whatsapp\_sender.py.

## **4\. Fluxo de Qualificação do Lead (v3) {#fluxo-qualificacao-v3}

Este fluxo unificado descreve a jornada completa do lead, desde a captura até a qualificação final, orquestrado por Kestra e utilizando o modelo `gpt-4o-mini` para interação e análise de imagens.

### Arquitetura Simplificada

- **Orquestração**: Kestra
- **Comunicação**: WhatsApp API
- **Inteligência Artificial**: OpenAI `gpt-4o-mini` (para conversação e análise de imagem/vision)
- **Persistência**: Supabase (os dados do lead são salvos **apenas ao final** da interação completa).

### Etapas do Fluxo

1.  **Captura (Formulário)**: Um formulário na página de captura coleta `Nome`, `E-mail`, `WhatsApp` e `Valor da Conta`.
2.  **Ativação (Kestra)**: Um workflow Kestra (`lead-activation-v3.yml`) é acionado, recebendo os dados do formulário. Ele envia um template de WhatsApp aprovado para o número do lead.
3.  **Interesse do Lead**: O lead clica no botão do template, enviando a mensagem "Ativar Perfil" (ou similar).
4.  **Início da Conversa com IA**: Um segundo workflow Kestra (`ai-conversation-v3.yml`) é acionado pela mensagem do lead. A IA (usando `gpt-4o-mini`) agradece e solicita a **cidade e estado** do lead.
5.  **Consulta e Análise de Conta**:
    - Com a localização, a IA consulta a API da Serena para obter as promoções.
    - Em seguida, a IA solicita uma **imagem da conta de energia**.
    - A IA utiliza sua capacidade de "vision" (`gpt-4o-mini`) para analisar a imagem, extrair e validar o valor da conta.
6.  **Apresentação e Finalização**:
    - A IA apresenta as promoções de forma enumerada.
    - Após o lead escolher ou tirar dúvidas, a IA informa que um responsável entrará em contato, agradece e se despede.
7.  **Persistência Final**: Ao final de toda a interação, um script é executado para salvar **todos os dados consolidados** do lead (dados do formulário, localização, thread da conversa, promoção de interesse, status de qualificação) em uma única tabela no Supabase.

## **5\. Guia de Comportamento do Agente de IA (OpenAI Assistant)**

O OpenAI Assistant é o cérebro do sistema, gerenciado pelos novos componentes:

* **scripts/assistant_manager.py**: Gerencia criação e configuração do Assistant
* **scripts/thread_manager.py**: Gerencia threads de conversação por usuário
* **scripts/assistant_function_handler.py**: Bridge para ferramentas customizadas

### **Ferramentas Disponíveis (tools)**

* **conversation\_tool**: Interage com o Supabase.  
* **serena\_api\_tool**: Consulta a API da Serena.  
* **ocr\_tool**: Extrai dados de contas de energia com processamento inteligente.
  - **6 Ações**: process_image, extract_fields, validate_invoice, identify_distributor, validate_structured, get_supported_distributors
  - **20+ Distribuidoras**: CEMIG, ENEL, LIGHT, CPFL, ELEKTRO, COELBA, CELPE, COSERN, COELCE, CELG, CEB, COPEL, RGE, CEEE, CELESC, ENERGISA, AMPLA, BANDEIRANTE, PIRATININGA, AES SUL
  - **Validação Robusta**: 8 critérios com score de confiança 0-100%
  - **Qualificação Automática**: Mínimo R$ 200/mês para aprovação
* **rag\_tool**: Responde dúvidas gerais sobre energia solar usando knowledge base.

### **Tratamento de Exceções e Casos Especiais**

* **Dúvidas Gerais (RAG)**: Responder perguntas com base em knowledge\_base/faq\_serena.txt.  
* **Timeout (Lembrete)**: ✅ **IMPLEMENTADO** - ai-conversation.yml v6.0.0 com WaitForWebhook timeout PT2H (2 horas).
  - **Task**: `wait-for-response` com `onTimeout: send-reminder-message`
  - **Webhook Key**: Dinâmica baseada em `conversation_id`
  - **Mensagem**: Template personalizado com emojis e call-to-action
  - **Analytics**: Tracking completo de timeout vs resposta antes do timeout
  - **Cancelamento**: Automático quando lead responde antes das 2 horas
* **Processamento Inteligente de Contas**: ✅ **IMPLEMENTADO** - OCR avançado com detecção automática de contexto.
  - **Detecção Automática**: Identifica quando imagem é conta de energia vs. conversa geral
  - **Extração Estruturada**: Nome, distribuidora, valor, consumo, endereço, vencimento
  - **Validação Robusta**: 8 critérios de validação com feedback detalhado
  - **Qualificação Inteligente**: Leads com consumo mínimo R$ 200/mês são qualificados
  - **Respostas Personalizadas**: Diferentes para leads qualificados vs. não qualificados
  - **Suporte a 20+ Distribuidoras**: Cobertura nacional completa
* **Fatura de Terceiros**: Se o ocr\_tool detectar nome divergente, invalidar o lead.

## **5.1. Guia Específico: Processamento OCR de Contas de Energia**

### **Fluxo de Processamento OCR**

O sistema implementa processamento inteligente de contas de energia através do SerenaAIAgent integrado ao core\_agent.py.

### **Detecção Automática de Contexto**

O agente detecta automaticamente quando uma mensagem contém uma conta de energia:

**Indicadores Positivos (Detecta como Conta):**
* Palavras-chave: "conta", "fatura", "luz", "energia", "CEMIG", "ENEL", "LIGHT", etc.
* Presença de media\_id (imagem anexada)
* Contexto de qualificação ativo

**Indicadores Negativos (Exclui da Detecção):**
* Conversas gerais: "energia solar", "sobre energia", "quanto custa"
* Dúvidas educacionais sobre o processo
* Mensagens sem contexto de fatura

### **Ações OCR Disponíveis**

1. **process\_image**: Processamento completo da conta com extração e validação
2. **extract\_fields**: Extração de campos específicos (nome, valor, consumo, etc.)
3. **validate\_invoice**: Validação de dados já extraídos
4. **identify\_distributor**: Identificação da distribuidora de energia
5. **validate\_structured**: Validação estruturada completa com score
6. **get\_supported\_distributors**: Lista das 20+ distribuidoras suportadas

### **Critérios de Validação**

O sistema aplica 8 critérios rigorosos de validação:

1. **Nome do Cliente**: Mínimo 10 caracteres, formato válido
2. **Valor da Conta**: Formato monetário brasileiro (R$ X,XX)
3. **Consumo kWh**: Range válido 0-10000 kWh
4. **Distribuidora**: Uma das 20+ distribuidoras conhecidas
5. **Endereço**: Estrutura mínima de endereço brasileiro
6. **Data de Vencimento**: Formato DD/MM/AAAA válido
7. **CPF/CNPJ**: Formato brasileiro válido (quando presente)
8. **Número de Instalação**: Formato numérico válido

### **Qualificação Automática**

**Critério Principal**: Valor da conta ≥ R$ 200,00/mês

**Respostas Diferenciadas:**
* **Lead Qualificado**: Confirma dados extraídos + próximos passos + contato consultor
* **Lead Não Qualificado**: Explica critérios + oferece alternativas + mantém relacionamento

### **Exemplo de Fluxo Completo**

```
1. ENTRADA: "aqui está minha conta de luz" + media_id
2. DETECÇÃO: Contexto de conta de energia identificado
3. PROCESSAMENTO: OCR extrai dados estruturados
4. VALIDAÇÃO: Aplica 8 critérios de validação
5. QUALIFICAÇÃO: Verifica valor ≥ R$ 200/mês
6. RESPOSTA: Gera resposta personalizada com dados extraídos
```

**Exemplo de Resposta Qualificada:**
```
✅ Perfeito! Analisei sua conta da CEMIG.

📊 Dados extraídos:
• Cliente: MARIA SILVA
• Valor atual: R$ 387,45
• Consumo: 450 kWh
• Endereço: Belo Horizonte/MG

🎯 Ótima notícia! Com esse perfil de consumo você pode economizar significativamente com energia solar. Vou conectar você com um de nossos consultores especializados para calcular sua economia personalizada.

Um consultor entrará em contato em até 24 horas! 📞
```

## **6\. Modelo de Dados (Supabase)**

* **leads\_iniciados**: Dados brutos do formulário.  
* **active\_conversations**: Estado e histórico das conversas.  
* **leads\_validated**: Leads qualificados.  
* **leads\_invalidated**: Leads não qualificados.

## **7\. Políticas e Métricas de Sucesso**

### **Políticas de Resiliência**

* **Chamadas de API (Externas)**: 3 tentativas com backoff exponencial (1s, 2s, 4s). Timeout de conexão de 15s.  
* **Processamento de Tarefas (OCR, IA)**: Timeout da tarefa de 90s. Falhas devem acionar um error-handler no workflow.

### **Métricas de Sucesso (SLAs)**

* **Latência do Fluxo 1**: \< 5s (do formulário ao envio da mensagem).  
* **Latência de Resposta da IA (P95)**: \< 3s (da recepção à resposta).  
* **Disponibilidade dos Serviços**: \> 99.9%.  
* **Taxa de Sucesso do OCR**: \> 90% na extração do nome do titular.

## **8\. Guia de Conversação (Golden Path)**

Este script exemplifica o fluxo ideal para guiar desenvolvimento e testes.

* **LEAD**: Ativar Perfil\!  
* **AGENTE**: Olá, João\! Sou a assistente virtual da Serena Energia. 😊 Recebemos seu cadastro, obrigado pelo interesse\! Para começar, pode me confirmar em qual cidade e estado você mora, por favor?  
* **LEAD**: Claro, moro em Recife, Pernambuco.  
* **AGENTE**: Excelente\! Tenho ótimas notícias: atendemos a região de Recife\! 🎉 Temos alguns planos e promoções especiais disponíveis. Gostaria de conhecê-los?  
* ... (continua conforme o fluxo ideal) ...  
* **AGENTE**: Tudo certo, João\! Fatura validada com sucesso. ✅ Seu perfil foi aprovado e um de nossos consultores entrará em contato. A Serena Energia agradece\!

## **9\. Dicionário de Variáveis de Ambiente**

### **Configuração da API WhatsApp Business (v23.0)**

**IMPORTANTE**: O sistema utiliza a versão 23.0 da API oficial do WhatsApp Business da Meta. A URL base é `https://graph.facebook.com/v23.0/`.

| Variável | Escopo | Descrição | Formato Exemplo |
| :---- | :---- | :---- | :---- |
| **WHATSAPP\_API\_TOKEN** | whatsapp\_sender | Token de Acesso Permanente da API do WhatsApp v23.0. | EAAD... |
| **WHATSAPP\_PHONE\_NUMBER\_ID** | whatsapp\_sender | ID do número de telefone registrado na API v23.0. | 599096403294262 |
| **WHATSAPP\_BUSINESS\_ID** | whatsapp\_sender | ID da conta WhatsApp Business (opcional). | 1097835408776820 |
| **WHATSAPP\_WELCOME\_TEMPLATE\_NAME** | whatsapp\_sender | Nome do template aprovado para mensagens de boas-vindas. | prosseguir\_com\_solicitacao |
| **SUPABASE\_URL** | conversation\_tool | URL do projeto no Supabase. | https://\[id\].supabase.co |
| **SUPABASE\_KEY** | conversation\_tool | Chave de API (public anon key) do Supabase. | eyJhbGci... |
| **OPENAI\_API\_KEY** | assistant\_manager | Chave de API da OpenAI para o modelo de linguagem. | sk-proj-... |
| **OPENAI\_ASSISTANT\_ID** | assistant\_manager | ID do Assistant OpenAI (criado manualmente). | asst-... |
| **KESTRA\_API\_URL** | serena-landing-page | URL da instância Kestra para acionar webhooks. | http://localhost:8080 |

### **Especificações Técnicas da API WhatsApp v23.0**

- **Endpoint Base**: `https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages`
- **Autenticação**: Bearer Token no header `Authorization`
- **Content-Type**: `application/json`
- **Template Messages**: Requer templates pré-aprovados pela Meta
- **Rate Limits**: 1000 mensagens/segundo (padrão)
- **Webhook Verification**: Obrigatório para recebimento de mensagens

## **10\. Operações e Produção**

### **Guia de Execução Local**

* **Ambiente**: docker-compose \-f docker-compose-minimal.yml up \-d.  
* **Dependências**: pip install \-r requirements.txt.  
* **Variáveis de Ambiente**: Preencher .env a partir do .env.example.

### **Testes Automatizados**

A suíte de testes está na pasta /tests.

* **Testes de Contrato**: Validam os payloads dos webhooks.  
* **Testes de Integração**: Testam a comunicação entre o agente e suas tools.  
* **Exemplo de Teste E2E (Pytest)**:  
  \# /Users/user/Desktop/serena-qualifier/tests/test\_e2e\_lead\_qualification\_flow.py  
  def test\_full\_successful\_qualification(mock\_requests, mock\_supabase):  
      """Testa o fluxo completo de qualificação de um lead com sucesso."""  
      \# 1\. Simular chamada ao webhook /capture  
      payload \= {"name": "Test Lead", "phone": "+123456789"}  
      response \= simulate\_kestra\_trigger('/capture', payload)  
      assert response.status\_code \== 202

      \# 2\. Simular resposta do lead e chamada ao /continue  
      lead\_message \= {"phone\_number": "+123456789", "message\_text": "Ativar Perfil\!"}  
      response \= simulate\_kestra\_trigger('/continue', lead\_message)  
      assert response.status\_code \== 202

      \# 3\. Verificar se a ferramenta da API Serena foi chamada  
      mock\_requests.get.assert\_any\_call("https://partnership.api.srna.co/...")

      \# 4\. Assertar que o lead foi movido para a tabela 'leads\_validated'  
      mock\_supabase.table("leads\_validated").insert.assert\_called\_once()

### **Guia de Deploy e Validação**

* **Deploy**: docker-compose \-f docker-compose-minimal.yml up \-d \--build  
* **Validação (Health Check)**: Após o deploy, verificar curl http://localhost:8000/health. Cada serviço deve expor este endpoint.  
* **Rollback de Código**: docker-compose \-f docker-compose-minimal.yml down && git checkout \<commit\_anterior\> && docker-compose \-f docker-compose-minimal.yml up \-d \--build  
* **Rollback de Banco de Dados**: Restaurar a partir do último backup válido do Supabase. Procedimentos de migração devem usar ferramentas como [Flyway](https://flywaydb.org/) ou [Alembic](https://alembic.sqlalchemy.org/en/latest/) e ter scripts de undo correspondentes.

### **Padrões de Segurança**

* **Gerenciamento de Secrets**: Em produção, usar um gerenciador de secrets como [HashiCorp Vault](https://www.vaultproject.io/) ou [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/).  
* **Criptografia em Trânsito**: Todas as comunicações externas devem obrigatoriamente usar TLS 1.2+.  
* **Hardening de Containers**: As imagens Docker devem passar por scans de vulnerabilidade (e.g., [Trivy](https://github.com/aquasecurity/trivy)) e rodar com usuários não-root.  
* **Políticas Web**: A Landing Page (Next.js) e o serviço de webhook (FastAPI) devem ter políticas de CORS (Cross-Origin Resource Sharing) e CSP (Content Security Policy) estritas para mitigar ataques de cross-site scripting.