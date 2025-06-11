
Documento 1: PROJECT_GUIDE.md
Este documento serve como o guia completo do projeto, detalhando a arquitetura,
as fases de implementação, os requisitos e os princípios de engenharia. É a
referência principal para o desenvolvimento do sistema.

PROJECT_GUIDE.md
0. Visão Geral do Sistema: Serena Lead Qualifier
Objetivo: Implementar um sistema automatizado para qualificação de leads para
a Serena Energia. O sistema deve:

Capturar dados de leads provenientes de formulários web.
Iniciar e conduzir interações com leads via WhatsApp, utilizando Inteligência
Artificial (IA).
Coletar informações adicionais relevantes durante a conversa.
Validar contas de energia enviadas pelos leads através de Reconhecimento
Óptico de Caracteres (OCR) avançado.
Consultar planos de energia disponíveis na API da Serena com base na
localização do lead.
Persistir dados de leads qualificados e não qualificados em um banco de dados
(Supabase).
Arquitetura Central:
O Kestra será a plataforma central de orquestração. Ele
coordenará todas as etapas do fluxo de qualificação de leads, desde a recepção
inicial de eventos até a persistência final de dados. O Kestra receberá eventos (e.g.,
envio de formulário, novas mensagens WhatsApp), invocará módulos Python para
tarefas específicas (e.g., interações com APIs externas, IA, OCR) e gerenciará o
fluxo complexo da conversa.

Benefícios da Arquitetura:

Centralização: Gerenciamento e visibilidade unificados do fluxo de automação
no Kestra.
Resiliência: Utilização dos recursos nativos do Kestra para retentativas
(retries), tratamento de erros e escalabilidade.
Observabilidade: Monitoramento do status de cada lead em tempo real e
facilidade na depuração.
Reutilização: Desenvolvimento de módulos Python independentes e
reutilizáveis.
1. Configuração Preliminar: Requisitos e Credenciais
Antes de iniciar a implementação do código, as seguintes configurações e
credenciais devem ser obtidas e preparadas.

Antes de iniciar a implementação do código, as seguintes configurações e
credenciais devem ser obtidas e preparadas.

1.1. Contas e Credenciais Essenciais
Meta / WhatsApp Business API:
Plataforma: Meta Business Suite.
Credenciais necessárias:
Número de telefone verificado para o WhatsApp Business API.
WHATSAPP_API_TOKEN: Token de Acesso Permanente para
autenticação da API.
WHATSAPP_PHONE_NUMBER_ID: ID do número de telefone no
WhatsApp Business API.
WHATSAPP_WELCOME_TEMPLATE_NAME: Nome exato de um
template de mensagem inicial aprovado (e.g., "Bem-vindo! Olá {{1}}, tudo bem?
Poderíamos conversar sobre como economizar na sua conta de energia?").
Webhook de Entrada: A configuração do webhook do WhatsApp no Meta
Business Manager para o endpoint do Kestra que receberá as mensagens será
realizada na Fase 5.
Serena Energia API:
Obtenção: Contato com a equipe da Serena Energia para acesso à API de
consulta de planos.
Credenciais necessárias:
SERENA_API_KEY: Chave de API para autenticação.
Supabase:
Plataforma: supabase.com.
Credenciais necessárias:
Novo projeto Supabase.
SUPABASE_URL e SUPABASE_KEY: Credenciais do projeto
(disponíveis em Project Settings > API).
Configuração das Tabelas (Criar no projeto Supabase):
active_conversations: Gerencia o estado da conversa com cada
lead.
phone_number (TEXT, Primary Key, Unique)
kestra_execution_id (TEXT, Index)
last_step (TEXT, e.g., 'initial', 'asked_for_city', 'asked_for_invoice')
conversation_history (JSONB, armazena o histórico de mensagens
para a IA)
updated_at (TIMESTAMP WITH TIME ZONE, Default NOW())
leads_validated: Armazena leads qualificados.
id (UUID, Primary Key, Default gen_random_uuid())
name (TEXT)
email (TEXT)
phone (TEXT)
city (TEXT)
invoice_amount (NUMERIC)
created_at (TIMESTAMP WITH TIME ZONE, Default NOW())
leads_invalidated: Armazena leads não qualificados.
id (UUID, Primary Key, Default gen_random_uuid())
name (TEXT)
email (TEXT)
phone (TEXT)
city (TEXT)
reason (TEXT, e.g., "Valor insuficiente", "Não enviou fatura", "Lead
inativo")
created_at (TIMESTAMP WITH TIME ZONE, Default NOW())
Modelos de Linguagem (LLMs - OpenAI / Anthropic / Google):
Plataformas: openai.com, [anthropic.com](https://
http://www.anthropic.com/)) ou cloud.google.com.
Credenciais necessárias:
OPENAI_API_KEY (ou ANTHROPIC_API_KEY ou
GOOGLE_API_KEY): Chave de API para acesso ao modelo escolhido.
Kestra:
Requisito: Docker deve estar instalado e em execução no ambiente de
desenvolvimento.
1.2. Estrutura Inicial do Projeto
Instrução para Geração de Código: Este é o primeiro prompt para a ferramenta
de codificação.

Prompt para a Ferramenta de Codificação (Fase 1 - Estrutura Inicial do Projeto):

# PROMPT PARA GERAÇÃO DE CÓDIGO - FASE 1: ESTRUTURA INICIAL DO
PROJETO

Crie a estrutura inicial de um projeto chamado “serena-qualifier", contendo:

- pasta `scripts/` para os módulos Python (WhatsApp Sender, WhatsApp Webhook
Receiver, OCR Processor, AI Agent, Supabase Client).
- pasta `kestra/workflows/` para os arquivos YAML dos workflows do Kestra.
- pasta `utils/` para funções auxiliares e módulos comuns (e.g., gerenciador de
conversa, validações genéricas).
- arquivo `requirements.txt` com as dependências básicas: `fastapi`, `uvicorn`,
`requests`, `supabase-py`, `openai` (ou `anthropic`, `google-generativeai`),
`pydantic`, `pytesseract`, `pdf2image`, `opencv-python`, `python-dotenv`, `httpx`.
- arquivo `.env.example` listando as variáveis de ambiente necessárias
(WHATSAPP_API_TOKEN, WHATSAPP_PHONE_NUMBER_ID,
WHATSAPP_WELCOME_TEMPLATE_NAME, SERENA_API_KEY,
SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY ou ANTHROPIC_API_KEY
ou GOOGLE_API_KEY, WHATSAPP_VERIFY_TOKEN).
- arquivo `README.md` com instruções concisas de setup e execução local,
incluindo uma referência a este `PROJECT_GUIDE.md` para detalhes completos.
2. Fases de Implementação
Cada fase descreve um componente ou integração específica do sistema. As
instruções são detalhadas para a ferramenta de codificação.

Fase 2: Formulário na Página de Captura
Objetivo: Configurar o envio de dados do formulário da página de captura
(saasia.com.br) diretamente para um webhook do Kestra.
Ação Manual Necessária: Após a geração do workflow Kestra e do exemplo
de JavaScript, o JavaScript da página de captura (saasia.com.br) deve ser
atualizado para enviar os dados para o endereço de webhook do Kestra.
Prompt para a Ferramenta de Codificação:

# PROMPT PARA GERAÇÃO DE CÓDIGO - FASE 2: FORMULÁRIO NA PÁGINA
DE CAPTURA

# PARTE 1: Kestra Workflow para Recepção Inicial
# Contexto: Crie (ou modifique se já existir) o arquivo `kestra/workflows/
lead_initial_workflow.yml`.
# Objetivo: Configurar o Kestra para atuar como o endpoint de webhook inicial do
formulário.
# A lógica deve ser:
# 1. Definir o `id` do workflow como `lead-capture-workflow`.
# 2. Definir o `namespace` como `serena`.
# 3. Adicionar um `trigger` do tipo `io.kestra.plugin.core.trigger.Webhook`.
# - O ID do trigger deve ser `form-webhook`.
# - O endpoint do webhook deve ser `/capture`.
# - Os `inputs` do workflow devem ser mapeados diretamente do corpo do
webhook (payload JSON):
# - `name` (string)
# - `email` (string)
# - `phone` (string)
# - `city` (string)
# 4. A primeira `task` do workflow deve ser para salvar o estado inicial da conversa
no Supabase.
# - ID da task: `save-initial-conversation-state`.
# - Tipo: `io.kestra.core.tasks.scripts.Python`.
# - Scripts: Chamar `utils.conversation_manager.save_conversation_state`,
passando `inputs.phone`, `{{execution.id}}` (ID da execução do Kestra) e `'initial'`.
Certifique-se de importar `utils.conversation_manager`.
# - **Observação:** O módulo `utils.conversation_manager` será criado na Fase 5.
O código deve ser gerado considerando a futura existência deste módulo.
# 5. A segunda `task` do workflow deve ser para enviar a mensagem de boas-
vindas.
# - ID da task: `send-welcome-message`.
# - Tipo: `io.kestra.core.tasks.scripts.Bash`.


# - Comando: Chame o endpoint local do FastAPI que será criado na próxima fase
(`scripts/whatsapp_sender.py`). Use `curl -X POST [http://localhost:8000/whatsapp/](http://localhost:8000/whatsapp/)
send_welcome -H "Content-Type: application/json" -d '{"phone": "{{inputs.phone}}",
"name": "{{inputs.name}}"}'`.

# PARTE 2: JavaScript para o Front-end
# Contexto: Adicione ao `README.md` uma seção de "Configuração do Formulário
Frontend".
# Objetivo: Explicar como o JavaScript do formulário deve ser ajustado para enviar
os dados diretamente ao webhook do Kestra.
# Lógica:
# 1. Fornecer o código JavaScript completo para a função `submitForm(event)`.
# 2. O `fetch` deve ser para `http://<URL_DO_SEU_KESTRA>:8080/api/v1/
executions/webhook/serena/lead-capture-workflow/capture`.
# 3. Os dados a serem enviados (name, email, phone, city) devem ser extraídos dos
campos do formulário.
# 4. A função deve prevenir o comportamento padrão do submit do formulário
(`event.preventDefault()`).
# 5. Incluir um exemplo de como exibir uma mensagem de agradecimento ao
usuário após o envio.
Fase 3: Envio de Mensagem Inicial no WhatsApp
Objetivo: Criar um módulo Python para enviar a primeira mensagem template
via WhatsApp Business API, a ser invocado pelo Kestra.
Ação Manual Necessária: O template de boas-vindas deve estar aprovado no
Meta Business Manager com o nome exato especificado em
WHATSAPP_WELCOME_TEMPLATE_NAME.
Prompt para a Ferramenta de Codificação:

# PROMPT PARA GERAÇÃO DE CÓDIGO - FASE 3: ENVIO DE MENSAGEM
INICIAL NO WHATSAPP

# Contexto: Crie um arquivo `scripts/whatsapp_sender.py`.
# Objetivo: Um módulo Python para enviar mensagens template do WhatsApp e
expor um endpoint FastAPI para o Kestra chamar.
# A lógica deve ser:
# 1. Importar `os` para variáveis de ambiente, `requests` para chamadas HTTP, e
`dotenv.load_dotenv()` para carregar o .env.
# 2. Definir uma função assíncrona `send_whatsapp_template_message(phone: str,
template_name: str, components: list) -> bool`:
# - Carregar variáveis de ambiente usando `os.getenv()`.
# - Fazer uma chamada POST para `https://graph.facebook.com/v19.0/
{WHATSAPP_PHONE_NUMBER_ID}/messages`.
# - Usar `WHATSAPP_API_TOKEN` para autenticação (Bearer Token).
# - O payload JSON deve incluir: `messaging_product`, `recipient_type`, `to` (o
número de telefone), `type` ('template'), e a estrutura do template (`name` e
`components`).


# - O payload JSON deve incluir: `messaging_product`, `recipient_type`, `to` (o
número de telefone), `type` ('template'), e a estrutura do template (`name` e
`components`).
# - Capturar erros de requisição (status HTTP diferente de 200) e logar no
console.
# - Retornar `True` se sucesso, `False` se falha.
# 3. Criar um endpoint FastAPI neste mesmo arquivo:
# - Rota: `POST /whatsapp/send_welcome`.
# - Receber `phone` e `name` no corpo da requisição.
# - Chamar `send_whatsapp_template_message`, usando
`os.getenv("WHATSAPP_WELCOME_TEMPLATE_NAME")` e os `components`
para o nome do lead.
# - Retornar um JSON de sucesso ou erro.
Fase 5: Recepção de Mensagens WhatsApp e IA
Objetivo: Capturar as respostas do lead no WhatsApp, gerenciar o estado da
conversa e repassar ao fluxo do Kestra para processamento de IA.
Ação Manual Necessária: Após a geração do código, configurar o webhook
do WhatsApp no Meta Business Manager para apontar para o endpoint http:// <SEU_DOMINIO_OU_IP>:8000/webhook/whatsapp. Utilizar o
WHATSAPP_VERIFY_TOKEN configurado no .env para a verificação.
Prompt para a Ferramenta de Codificação:

# PROMPT PARA GERAÇÃO DE CÓDIGO - FASE 5: RECEPÇÃO DE
MENSAGENS WHATSAPP E IA

# PARTE 1: Módulo de Gerenciamento de Conversa (State Management)
# Contexto: Crie um arquivo `utils/conversation_manager.py`.
# Objetivo: Gerenciar o estado de cada conversa no Supabase.
# A lógica deve ser:
# 1. Importar `os`, `supabase.create_client`, `dotenv.load_dotenv()`.
# 2. Inicializar o cliente Supabase usando `SUPABASE_URL` e `SUPABASE_KEY`
das variáveis de ambiente.
# 3. Criar uma função assíncrona `get_conversation_state(phone_number: str) ->
Optional[dict]`:
# - Busca na tabela `active_conversations` o registro para o `phone_number`.
# - Retorna o dicionário com `kestra_execution_id`, `last_step` e
`conversation_history` (JSONB) ou `None` se não encontrar.
# 4. Criar uma função assíncrona `save_conversation_state(phone_number: str,
execution_id: str, step: str, new_message: dict = None) -> None`:
# - Insere ou atualiza (UPSERT) um registro na tabela `active_conversations`.
# - Atualiza `kestra_execution_id` e `last_step`.
# - Se `new_message` (dicionário com `role` e `content`) for fornecido, anexa-o ao
`conversation_history` existente (ou inicia um novo, se `conversation_history` for
nulo).
# 5. Criar uma função assíncrona `delete_conversation_state(phone_number: str) ->
None`:
# - Remove o registro da tabela `active_conversations` quando a conversa for
finalizada.


# - Remove o registro da tabela `active_conversations` quando a conversa for
finalizada.

# PARTE 2: Webhook de Recepção de Mensagens WhatsApp
# Contexto: Crie um arquivo `scripts/whatsapp_webhook_receiver.py`.
# Objetivo: Receber as mensagens do WhatsApp, identificar o lead, e continuar o
workflow Kestra apropriado.
# A lógica deve ser:
# 1. Importar `FastAPI`, `Request`, `JSONResponse`, `os`, `dotenv.load_dotenv()`,
`httpx`.
# 2. Importar o módulo `utils.conversation_manager`.
# 3. Criar um FastAPI app.
# 4. Criar um endpoint `GET /webhook/whatsapp` para a verificação do webhook da
Meta:
# - Receber `hub.mode`, `hub.challenge`, `hub.verify_token` como query
parameters.
# - Validar `hub.mode` ser "subscribe" e `hub.verify_token` contra
`os.getenv("WHATSAPP_VERIFY_TOKEN")`.
# - Retornar `hub.challenge`.
# 5. Criar um endpoint `POST /webhook/whatsapp` para receber as mensagens
reais:
# - Receber o `Request` object.
# - Extrair `phone` (de `payload["entry"][0]["changes"][0]["value"]["messages"][0]
["from"]`) e `text` (de `payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]
["body"]`).
# - Chamar `utils.conversation_manager.get_conversation_state(phone_number)`.
# - Se encontrar um estado ativo (`conversation_state`):
# - Chamar `utils.conversation_manager.save_conversation_state` para
adicionar a nova mensagem ao histórico (`new_message={"role": "user", "content":
text}`).
# - Usar `httpx.AsyncClient` para chamar a API de execução do Kestra para
*resumir* o workflow:
# - URL: `http://localhost:8080/api/v1/flows/{namespace}/{flow_id}/executions/
{execution_id}/callbacks`
# - Substituir `{namespace}`, `{flow_id}` e `{execution_id}` pelos valores
corretos (e.g., `serena`, `full-lead-qualification`, e
`conversation_state["kestra_execution_id"]`).
# - Fazer um POST com JSON contendo `{"text": text_da_mensagem}`.
# - Incluir o `Kestra` API key se necessário (deve ser configurada como
secret no Kestra).
# - Se não encontrar um estado ativo: logar um aviso ou iniciar um novo workflow
(por agora, apenas logar).
# 6. Retornar um `JSONResponse` com status 200 OK para a Meta rapidamente.
Fase 6: Função de IA / RAG para Respostas
Objetivo: Implementar a lógica de IA para classificação de intenção do
usuário, geração de respostas contextuais e direção do fluxo da conversa,
mantendo o histórico.
Ação Manual Necessária: A API Key do LLM escolhido (OpenAI/Claude/
Gemini) deve estar configurada nas variáveis de ambiente.
Ação Manual Necessária: A API Key do LLM escolhido (OpenAI/Claude/
Gemini) deve estar configurada nas variáveis de ambiente.
Prompt para a Ferramenta de Codificação:

# PROMPT PARA GERAÇÃO DE CÓDIGO - FASE 6: FUNÇÃO DE IA / RAG PARA
RESPOSTAS

# Contexto: Crie um arquivo `scripts/ai_agent.py`.
# Objetivo: Criar funções de IA para classificação de intenção, geração de respostas
com RAG, e extração de informações.
# A lógica deve ser:
# 1. Importar a biblioteca do LLM escolhido (e.g., `openai` ou `anthropic` ou
`google.generativeai`), `os`, `dotenv.load_dotenv()`, `typing.List`, `typing.Optional`.
# 2. Inicializar o cliente do LLM usando a API Key da variável de ambiente
(`os.getenv("OPENAI_API_KEY")` ou similar).
# 3. Função assíncrona `classify_intent(message: str, conversation_history:
List[dict]) -> str`:
# - Montar um prompt para o LLM que inclua a `message` atual do usuário e o
`conversation_history` (como mensagens de sistema/usuário/assistente).
# - Instruir o LLM a classificar a intenção em uma das seguintes strings (e apenas
essas):
# - `'informou_cidade'`
# - `'fez_pergunta_geral'`
# - `'pediu_para_parar'`
# - `'agradeceu'`
# - `'solicitou_fatura'` (se o lead indica que vai enviar a fatura ou já enviou)
# - `'incompreensivel'`
# - Retornar a string da intenção detectada.
# 4. Função assíncrona `generate_rag_response(question: str, conversation_history:
List[dict], context_docs: List[str]) -> str`:
# - Montar um prompt para o LLM que inclua a `question` atual, o
`conversation_history`, e os `context_docs` (se não vazios).
# - Os `context_docs` devem ser inseridos de forma clara para o LLM usar como
base de conhecimento.
# - Retornar a resposta gerada pelo LLM.
# 5. Função `extract_city_from_message(message: str) -> Optional[str]`:
# - Utilizar uma abordagem baseada em LLM (invocando o LLM para extrair a
cidade) ou regex simples para tentar extrair o nome de uma cidade da mensagem.
# - Retornar a cidade como string ou `None`.
# 6. **Comentar no código** como `context_docs` seria alimentado (e.g., lendo de
PDFs ou FAQ da Serena).
Fase 7: Consulta de Planos na API da Serena
Objetivo: Obter planos de energia da Serena com base na cidade do lead,
com resiliência e cache.
Ação Manual Necessária: A API Key da Serena deve estar configurada nas
variáveis de ambiente.
Prompt para a Ferramenta de Codificação:

# PROMPT PARA GERAÇÃO DE CÓDIGO - FASE 7: CONSULTA DE PLANOS NA
API DA SERENA

# Contexto: Crie um arquivo `scripts/serena_api.py`.
# Objetivo: Módulo para buscar planos da Serena com tratamento de erros,
retentativas e cache.
# A lógica deve ser:
# 1. Importar `requests`, `os`, `dotenv.load_dotenv()`, `functools`, `time`,
`typing.List`.
# 2. Definir uma função assíncrona `get_plans_by_city(city: str) -> List[dict]`:
# - Decorar a função com `@functools.lru_cache(maxsize=128, ttl=3600)` para
cachear resultados por 1 hora.
# - Carregar `SERENA_API_KEY` das variáveis de ambiente.
# - Implementar um loop de retentativas (e.g., 3 tentativas, atraso de 1s, 2s, 4s)
com `time.sleep`.
# - Dentro do loop, usar `requests.get` para chamar a API GET `https://
partnership.api.srna.co/distribuited-generation/plans?city={city}`.
# - Usar `SERENA_API_KEY` para autenticação (Bearer Token no cabeçalho
`Authorization`).
# - **Tratamento de Erros:** Capturar `requests.exceptions.RequestException` e
verificar códigos de status HTTP não 200.
# - Se todas as retentativas falharem, levantar uma exceção (`Exception`).
# - Retornar a lista de planos (lista de dicionários) ou uma lista vazia se nenhum
for encontrado.
# 3. Documentar no código como configurar a variável de ambiente
`SERENA_API_KEY` e qual header usar.
Fase 8: Solicitar e Processar Conta de Energia (OCR Robusto)
Objetivo: Implementar a solicitação da conta, o download do anexo e a
extração confiável do valor via OCR avançado, incluindo pré-processamento de
imagem e fallback.
Ação Manual Necessária: Nenhuma específica além de ter um ambiente
Python com os pacotes de OCR.
Prompt para a Ferramenta de Codificação:

# PROMPT PARA GERAÇÃO DE CÓDIGO - FASE 8: SOLICITAR E PROCESSAR
CONTA DE ENERGIA (OCR)

# PARTE 1: Processador de OCR Robusto
# Contexto: Crie um arquivo `scripts/ocr_processor.py`.
# Objetivo: Extrair valores de contas de energia com pré-processamento e fallback
de OCR.


# A lógica deve ser:
# 1. Importar `cv2` (OpenCV), `numpy`, `pytesseract`, `pdf2image`, `os`, `re`,
`tempfile`, `typing.Optional`.
# 2. Função `preprocess_image(file_path: str) -> np.array`:
# - Se o arquivo for PDF, converter a primeira página para imagem (PNG) usando
`pdf2image.convert_from_path` e salvar temporariamente.
# - Carregar a imagem com `cv2.imread`.
# - Converter para tons de cinza (`cv2.cvtColor`).
# - Aplicar filtros para remover ruído e melhorar o contraste/nitidez (e.g.,
`cv2.threshold`, `cv2.adaptiveThreshold`, `cv2.erode`, `cv2.dilate`).
# - Corrigir possível rotação da imagem (e.g., usando `cv2.findContours` e
`cv2.minAreaRect`).
# - Retornar a imagem pré-processada como um array NumPy.
# 3. Função `extract_invoice_amount(file_path: str) -> float`:
# - Chamar `preprocess_image` com `file_path`.
# - **Múltiplas Tentativas de OCR (Fallback):**
# - Tentar usar `pytesseract.image_to_string` na imagem pré-processada.
# - Se `pytesseract` falhar ou não encontrar valor (usar `try-except` e verificar se
o resultado é vazio/inválido), tentar usar uma API de OCR externa (e.g., Google
Vision API via `google-cloud-vision` se configurado, usando
`os.getenv("GOOGLE_API_KEY")`).
# - Procurar padrões como "R$ XXX,XX", "XXX,XX", "TOTAL A PAGAR", "VALOR
TOTAL" no texto extraído usando `re.findall`.
# - Se encontrar múltiplos valores numéricos, retornar o maior valor.
# - Se não encontrar valor com nenhum OCR, lançar `ValueError("Não foi
possível extrair valor da fatura.")`.
# 4. Função `validate_invoice(amount: float) -> bool`:
# - Retorna `True` se `amount >= 200.0`, senão `False`.
# 5. Comentar no código os pacotes necessários em `requirements.txt`
(`pytesseract`, `pdf2image`, `opencv-python`, `google-cloud-vision` - se usado).

# PARTE 2: Endpoint para Upload da Fatura
# Contexto: Adicione ao arquivo `scripts/whatsapp_webhook_receiver.py` (ou crie
um novo `scripts/file_receiver.py` se a separação for mais limpa).
# Objetivo: Receber o upload da fatura do lead, processá-la e retomar o workflow
Kestra.
# A lógica deve ser:
# 1. Importar `FastAPI`, `UploadFile`, `File`, `Form`, `shutil`, `os`, `httpx`, `tempfile`.
# 2. Importar `scripts.ocr_processor` e `utils.conversation_manager`.
# 3. Criar uma rota `POST /upload_invoice`:
# - Receberá `file: UploadFile = File(...)` e `phone: str = Form(...)`.
# - Salvar o arquivo recebido em uma pasta temporária (e.g., `/tmp/`) com um
nome único (e.g., `<phone>_<timestamp>_invoice.<extensao>`).
# - Chamar `scripts.ocr_processor.extract_invoice_amount(file_path)` e
`scripts.ocr_processor.validate_invoice(amount)`.
# - **Após processamento, retomar o Kestra Workflow:**
# - Chamar `utils.conversation_manager.get_conversation_state(phone)` para
obter o `kestra_execution_id`.
# - Usar `httpx.AsyncClient` para chamar a API de execução do Kestra para
*resumir* o workflow:


# - URL: `http://localhost:8080/api/v1/flows/{namespace}/{flow_id}/executions/
{execution_id}/callbacks`
# - Fazer um POST com JSON contendo `{"amount": amount, "valid": valid}`.
# - Retornar JSON: `{"phone": phone, "amount": <float>, "valid": <bool>}`.
# - Limpar o arquivo temporário após o processamento.
Fase 9: Persistência no Supabase
Objetivo: Gravar os dados dos leads (qualificados ou não) nas tabelas
corretas do Supabase.
Ação Manual Necessária: As tabelas active_conversations, leads_validated
e leads_invalidated devem ter sido criadas no Supabase conforme o item 1.1.3.
Prompt para a Ferramenta de Codificação:

# PROMPT PARA GERAÇÃO DE CÓDIGO - FASE 9: PERSISTÊNCIA NO
SUPABASE

# Contexto: Crie um arquivo `scripts/supabase_client.py`.
# Objetivo: Funções para persistir dados de leads no Supabase.
# A lógica deve ser:
# 1. Importar `os`, `supabase.create_client`, `dotenv.load_dotenv()`.
# 2. Inicializar o cliente Supabase usando `SUPABASE_URL` e `SUPABASE_KEY`
das variáveis de ambiente.
# 3. Função assíncrona `save_validated_lead(lead_data: dict) -> dict`:
# - Insere o `lead_data` (com `id`, `name`, `email`, `phone`, `city`,
`invoice_amount`, `created_at`) na tabela `leads_validated`.
# - Retorna o registro inserido.
# 4. Função assíncrona `save_invalid_lead(lead_data: dict, reason: str) -> dict`:
# - Insere o `lead_data` (com `id`, `name`, `email`, `phone`, `city`, `created_at`
mais o `reason`) na tabela `leads_invalidated`.
# - Retorna o registro inserido.
Fase 10: Composição do Workflow Kestra Completo
Objetivo: Integrar todos os componentes desenvolvidos em um único workflow
Kestra, que orquestrará todo o processo de qualificação de leads, incluindo lógica
de ramificação e espera.
Ação Manual Necessária: Este será o principal arquivo a ser inspecionado no
Kestra UI. Prestar atenção aos IDs das tarefas e às condições when.
Prompt para a Ferramenta de Codificação:

# PROMPT PARA GERAÇÃO DE CÓDIGO - FASE 10: COMPOSIÇÃO DO
WORKFLOW KESTRA COMPLETO


# Contexto: Crie (ou modifique extensivamente) o arquivo `kestra/workflows/
full_lead_qualification.yml`.
# Objetivo: Orquestrar todo o processo de qualificação de leads, desde o webhook
inicial até a persistência no Supabase, incorporando IA, OCR e gerenciamento de
estado.
# A lógica deve ser:
# 1. ID do Workflow: `full-lead-qualification`. Namespace: `serena`.
# 2. Inputs: `name`, `email`, `phone`, `city` (todos string).
# 3. **Trigger (Recepção do Formulário):**
# - Um trigger `Webhook` com `id: form-webhook` e `uri: /capture`.
# - Os inputs do workflow devem ser mapeados diretamente do corpo do
webhook.
# 4. **Tasks (Sequência Lógica):**
# - **Task 1: `save-initial-conversation-state`:** (Python)
# - Type: `io.kestra.core.tasks.scripts.Python`
# - Scripts: Importa `utils.conversation_manager`. Chama
`utils.conversation_manager.save_conversation_state` com `inputs.phone`,
`{{execution.id}}` e `'initial'`.
# - **Task 2: `send-welcome-message`:** (Bash)
# - Type: `io.kestra.core.tasks.scripts.Bash`
# - Commands: `curl -X POST [http://localhost:8001/whatsapp/send_welcome](http://localhost:8001/whatsapp/send_welcome) -H
"Content-Type: application/json" -d '{"phone": "{{inputs.phone}}", "name":
"{{inputs.name}}"}'` (Assumindo whatsapp_sender está na porta 8001).
# - **Task 3: `wait-for-lead-response`:**
(io.kestra.core.tasks.flows.WaitForWebhook)
# - Type: `io.kestra.core.tasks.flows.WaitForWebhook`
# - Aguarda o callback do `scripts/whatsapp_webhook_receiver.py`.
# - Define um `timeout: PT1H` (1 hora).
# - Se o timeout ocorrer, o workflow deve continuar para a tarefa `handle-
inactive-lead`.
# - **Task 4: `process-lead-message-with-ia`:** (Python)
# - Type: `io.kestra.core.tasks.scripts.Python`
# - Scripts: Importa `scripts.ai_agent` e `utils.conversation_manager`.
# - Pega a mensagem do lead (`message = "{{outputs.wait-for-lead-
response.body.text}}"`).
# - Pega o histórico da conversa do Supabase (`conversation_state = await
utils.conversation_manager.get_conversation_state(inputs.phone)`).
# - Chama `intent = await scripts.ai_agent.classify_intent(message,
conversation_state['conversation_history'])`.
# - Salva a intenção e o novo histórico da conversa no Supabase (`await
utils.conversation_manager.save_conversation_state(inputs.phone, execution.id,
'processed_by_ia', new_message={"role": "assistant", "content": intent})`).
# - Printa a `intent` para o Kestra capturar como output.
# - **Task 5: Ramificação por Intenção (`switch`):**
# - Type: `io.kestra.core.tasks.flows.Switch`
# - Value: `{{outputs.process-lead-message-with-ia.stdout}}` (a intenção
retornada pela IA).
# - **Case 1: `informou_cidade`:**
# - **Task 5.1.1: `extract-and-validate-city`:** (Python) Chama
`scripts.ai_agent.extract_city_from_message` com a mensagem do lead. Outputa a
cidade.


# - **Task 5.1.1: `extract-and-validate-city`:** (Python) Chama
`scripts.ai_agent.extract_city_from_message` com a mensagem do lead. Outputa a
cidade.
# - **Task 5.1.2: `get-serena-plans`:** (Python) Chama
`scripts.serena_api.get_plans_by_city` com a cidade extraída.
# - **Task 5.1.3: `send-plans-to-lead`:** (Bash) Envia mensagem WhatsApp
formatando os planos recebidos.
# - **Task 5.1.4: `update-state-asked-for-invoice`:** (Python) Chama
`utils.conversation_manager.save_conversation_state` com `inputs.phone`,
`{{execution.id}}` e `'asked_for_invoice'`.
# - **Task 5.1.5: `wait-for-invoice-upload`:**
(io.kestra.core.tasks.flows.WaitForWebhook) Aguarda o callback do endpoint `/
upload_invoice`. Define um `timeout: PT1H`. Se timeout, vai para `handle-inactive-
lead`.
# - **Case 2: `fez_pergunta_geral`:**
# - **Task 5.2.1: `answer-with-rag`:** (Python) Chama
`scripts.ai_agent.generate_rag_response`, passando a pergunta, histórico e docs de
contexto (o Cursor AI deve simular ou deixar um placeholder para docs).
# - **Task 5.2.2: `send-rag-response`:** (Bash) Envia a resposta da IA via
WhatsApp.
# - **Task 5.2.3: `update-state-waiting-for-next-question`:** (Python) Atualiza
estado da conversa.
# - **Task 5.2.4: `loop-to-wait-for-lead-response`:**
(io.kestra.core.tasks.flows.GoTo) Volta para `wait-for-lead-response`.
# - **Case 3: `pediu_para_parar` ou `agradeceu`:**
# - **Task 5.3.1: `end-conversation`:** (Python) Envia mensagem de
agradecimento e **deleta o estado da conversa no Supabase**
(`utils.conversation_manager.delete_conversation_state`).
# - **Case 4: `incompreensivel`:**
# - **Task 5.4.1: `ask-for-clarification`:** (Bash) Envia mensagem pedindo
para o lead ser mais claro.
# - **Task 5.4.2: `loop-to-wait-for-lead-response`:**
(io.kestra.core.tasks.flows.GoTo) Volta para `wait-for-lead-response`.
# - **Task 6: `process-uploaded-invoice`:** (Python)
# - Type: `io.kestra.core.tasks.scripts.Python`
# - When: `{{outputs.wait-for-invoice-upload.uri}} is not null` (garante que só
roda se a fatura foi enviada).
# - Scripts: Importa `scripts.ocr_processor`. Pega o `file_path` e `phone` do
output de `wait-for-invoice-upload`. Chama `amount =
scripts.ocr_processor.extract_invoice_amount(file_path)` e `valid =
scripts.ocr_processor.validate_invoice(amount)`. Printa `amount` e `valid` para o
Kestra.
# - **Task 7: `save-lead-and-finalize`:** (Python)
# - Type: `io.kestra.core.tasks.scripts.Python`
# - When: `{{outputs.process-uploaded-invoice.valid}} is not null`
# - Scripts: Importa `scripts.supabase_client` e `scripts.whatsapp_sender`.
# - Pega `valid` e `amount` do output de `process-uploaded-invoice`.
# - Pega `name`, `email`, `phone`, `city` dos inputs do workflow.
# - Cria `lead_data` com todos os campos necessários, incluindo
`invoice_amount` e `created_at`.
# - Se `valid=True`: Chama
`scripts.supabase_client.save_validated_lead(lead_data)` e envia mensagem de
"Parabéns, lead validado!".


# - Se `valid=True`: Chama
`scripts.supabase_client.save_validated_lead(lead_data)` e envia mensagem de
"Parabéns, lead validado!".
# - Se `valid=False`: Chama
`scripts.supabase_client.save_invalid_lead(lead_data, reason="Valor abaixo de
R$200 ou não enviado")` e envia mensagem de "Obrigado, mas não podemos
prosseguir.".
# - **Finalizar Conversa:** Chama
`utils.conversation_manager.delete_conversation_state(inputs.phone)`.
# - **Task 8: `handle-inactive-lead`:** (Python)
# - Type: `io.kestra.core.tasks.scripts.Python`
# - When: `{{outputs.wait-for-lead-response.timeout}}` OR `{{outputs.wait-for-
invoice-upload.timeout}}`
# - Scripts: Importa `scripts.supabase_client` e `scripts.whatsapp_sender`. Pega
`name`, `email`, `phone`, `city` dos inputs do workflow. Cria `lead_data`. Chama
`scripts.supabase_client.save_invalid_lead(lead_data, reason="Lead inativo")` e
envia uma mensagem final.
# - **Finalizar Conversa:** Chama
`utils.conversation_manager.delete_conversation_state(inputs.phone)`.
3. Princípios de Engenharia e Melhorias Transversais
Estas são diretrizes gerais a serem aplicadas a todos os módulos Python e
workflows Kestra durante a implementação.

Tratamento de Erros e Resiliência:
Retentativas (Retries): Implementar retentativas automáticas com backoff
exponencial para todas as chamadas de API externas (WhatsApp, Serena, LLM).
Utilizar recursos nativos do Kestra para retries ou implementar lógica em Python
(try-except com time.sleep).
Circuit Breaker: Considerar a implementação de um "circuit breaker" para
APIs externas que falham consistentemente, evitando sobrecarga e falhas
repetidas.
Fluxos Alternativos/Fallback: Definir fluxos de fallback para falhas críticas
(e.g., se o OCR não conseguir extrair o valor, a IA deve solicitar a informação
manualmente ao lead).
Logging Detalhado: Todos os módulos e tarefas devem gerar logs
informativos sobre o sucesso, falha, dados importantes e IDs de execução. Utilizar o
módulo logging em Python.
Observabilidade:
Métricas e Logs Kestra: Aproveitar as capacidades de logging e métricas do
Kestra. Garantir que os logs dos scripts Python sejam visíveis no painel do Kestra.
Status de Execução: O Kestra exibirá o status de cada execução.
Assegurar que os outputs e erros das tarefas sejam claros para facilitar a
depuração.
Experiência do Usuário (UX) na Conversa:
Reconhecimento de Contexto: A IA deve utilizar o histórico da conversa
para entender mensagens, mesmo que fornecidas fora da ordem esperada.
Reconhecimento de Contexto: A IA deve utilizar o histórico da conversa
para entender mensagens, mesmo que fornecidas fora da ordem esperada.
Personalização: Incorporar o nome do lead e referências a mensagens
anteriores para tornar a conversa mais natural.
Timeouts Amigáveis: Implementar mensagens de "retomada" educadas se
o lead não responder por um período, antes de finalizar a conversa.
Tipos de Mensagem: O webhook de WhatsApp deve ser robusto para lidar
com diferentes tipos de mensagens (foco inicial em texto).
Performance e Escalabilidade:
Processamento Assíncrono: Otimizar módulos Python que realizam
operações demoradas (OCR, chamadas de API lentas) para não bloquear o fluxo
principal.
Cache: Implementar caching simples para chamadas de API que não
mudam frequentemente (e.g., planos da Serena).
Rate Limiting: Implementar limitações de taxa para chamadas de API
externas para evitar bloqueio por parte dos serviços.
4. Guia de Execução e Testes
Este guia resume os passos para configurar e testar o sistema localmente. Para
instruções detalhadas, consulte o README.md.

4.1. Setup Local
Variáveis de Ambiente: Criar .env com base em .env.example.
Instalar Dependências: pip install -r requirements.txt
Iniciar Serviços Python (FastAPI):
uvicorn scripts.whatsapp_webhook_receiver:app --reload --port 8000
uvicorn scripts.whatsapp_sender:app --reload --port 8001
Iniciar Kestra (Docker): docker run -d -p 8080:8080 -e "JAVA_OPTS=- Xms512m -Xmx1024m" kestra/kestra:latest
Acessar Painel Kestra: http://localhost:8080/ui
Configurar Secrets no Kestra: Adicionar chaves e tokens como secrets no
Kestra UI.
Importar Workflow: Importar kestra/workflows/full_lead_qualification.yml no
Kestra UI.
4.2. Testes Incrementais
Testar cada componente à medida que é implementado.

Formulário e Kestra Webhook (Fase 2): Preencher formulário e verificar
execução no Kestra.
Mensagem Inicial (Fase 3): Verificar WhatsApp e logs do
whatsapp_sender.py.
Interação IA/WhatsApp (Fase 5 e 6): Responder no WhatsApp, observar logs
do whatsapp_webhook_receiver.py e o Kestra workflow.
Consulta de Planos (Fase 7): Responder com cidade e verificar tarefa get- serena-plans no Kestra.
Consulta de Planos (Fase 7): Responder com cidade e verificar tarefa get- serena-plans no Kestra.
OCR e Validação (Fase 8): Enviar fatura e observar logs do
ocr_processor.py e tarefa process-uploaded-invoice no Kestra.
Persistência Supabase (Fase 9): Verificar dados nas tabelas do Supabase.
4.3. Ajustes Comuns
Logs: Acompanhar logs do Kestra e serviços Python para depuração.
Variáveis de Ambiente/Secrets: Confirmar a correção das chaves e URLs.
when Clauses: Verificar condições de ramificação no Kestra se o fluxo não
seguir o esperado.
Documento 2: README.md
Este é o documento conciso, focado em como levantar e testar o sistema
localmente. Ele estará na raiz do seu projeto e é o primeiro arquivo que qualquer
pessoa (ou script de CI) leria para entender como rodar o projeto rapidamente.

README.md
Serena Lead Qualifier - Sistema de Qualificação de Leads Automatizado
Este projeto implementa um sistema automatizado para qualificação de leads para a
Serena Energia. Ele interage com leads via WhatsApp usando IA, valida contas de
energia com OCR, consulta planos de energia e persiste os dados em um banco de
dados.

A orquestração central é realizada pelo Kestra, que coordena os
módulos de Python (FastAPI, OCR, IA, Supabase) para gerenciar todo o fluxo de
qualificação.

Estrutura do Projeto
serena-qualifier/
├── PROJECT_GUIDE.md # Guia completo do projeto, fases de
implementação, prompts para codificação.
├── README.md # Este arquivo: instruções concisas para execução e
testes rápidos.
├── .env.example # Modelo das variáveis de ambiente.
├── requirements.txt # Dependências Python.
├── scripts/ # Módulos Python (WhatsApp, OCR, AI, Supabase).


├── utils/ # Módulos auxiliares (gerenciador de conversa).
└── kestra/
└── workflows/ # Arquivos YAML dos workflows Kestra.
Como Rodar o Projeto Localmente
Siga estes passos para configurar e iniciar o sistema em sua máquina local.

1. Pré-requisitos
Docker: Essencial para rodar o Kestra.
Python 3.9+: Com pip instalado.
2. Configuração Inicial
Clonar o Repositório:
git clone https://github.com/seu-usuario/serena-qualifier.git
cd serena-qualifier
Variáveis de Ambiente:
Crie um arquivo .env na raiz do projeto (serena-qualifier/.env).
Copie o conteúdo de .env.example para .env.
Preencha todas as variáveis com as credenciais reais do seu ambiente
(Meta/WhatsApp API, Serena API, Supabase, LLMs).
Exemplo de .env (preencha com seus valores!):
WHATSAPP_API_TOKEN="YOUR_WHATSAPP_API_TOKEN"

WHATSAPP_PHONE_NUMBER_ID="YOUR_WHATSAPP_PHONE_NUMBER_ID"

WHATSAPP_WELCOME_TEMPLATE_NAME="your_approved_template_name"
SERENA_API_KEY="YOUR_SERENA_API_KEY"
SUPABASE_URL="https://your_project.supabase.co"
SUPABASE_KEY="YOUR_SUPABASE_API_KEY"
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
WHATSAPP_VERIFY_TOKEN="YOUR_WEBHOOK_VERIFY_TOKEN"
# ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY" # Se usar Claude
# GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY" # Se usar Gemini
Instalar Dependências Python:
pip install -r requirements.txt
3. Iniciar os Serviços
Abra três terminais separados e execute um comando em cada um:

Terminal 1: Iniciar WhatsApp Webhook Receiver (FastAPI)
uvicorn scripts.whatsapp_webhook_receiver:app --reload --port 8000
Serviço responsável por receber mensagens do WhatsApp e uploads de
faturas.
Terminal 2: Iniciar WhatsApp Sender (FastAPI)
uvicorn scripts.whatsapp_sender:app --reload --port 8001
Serviço responsável por enviar mensagens para o WhatsApp.
Terminal 3: Iniciar Kestra (Docker)
docker run -d -p 8080:8080 \
-e "JAVA_OPTS=-Xms512m -Xmx1024m" \
kestra/kestra:latest
Kestra é o orquestrador principal do fluxo.
4. Configurar Kestra UI
Acesse o painel do Kestra em seu navegador: http://localhost:8080/ui
Configurar Secrets:
No painel do Kestra, navegue até a seção "Secrets".
Adicione os seguintes secrets, utilizando os mesmos nomes e valores definidos
no seu arquivo .env:
whatsapp_api_token
whatsapp_phone_number_id
whatsapp_welcome_template_name
serena_api_key
supabase_url
supabase_key
openai_api_key (ou o key do LLM escolhido)
Importar Workflow:
No painel do Kestra, vá para a seção "Flows".
Clique em "Import" e selecione o arquivo kestra/workflows/ full_lead_qualification.yml.
5. Configurar Webhook do WhatsApp (Meta Business Manager)
Acesse o Meta Business Manager e navegue
até as configurações do seu aplicativo WhatsApp Business.
Na seção "Webhooks", configure o webhook de mensagens para apontar para:
URL de Callback: http://<SEU_IP_PUBLICO_OU_DOMINIO>:8000/ webhook/whatsapp
Verify Token: Utilize o mesmo valor definido em
WHATSAPP_VERIFY_TOKEN no seu .env.
Verify Token: Utilize o mesmo valor definido em
WHATSAPP_VERIFY_TOKEN no seu .env.
Assine o campo messages.
Como Testar o Sistema
Com todos os serviços configurados e em execução, o sistema pode ser testado
passo a passo:

Iniciar um Lead (Via Formulário Web):
Simule o preenchimento e envio do formulário na sua página de captura
(saasia.com.br). O JavaScript configurado enviará os dados diretamente para o
webhook do Kestra.
Verificação: No painel do Kestra (http://localhost:8080/ui), uma nova
execução do workflow full-lead-qualification deverá iniciar.
Interação via WhatsApp:
A mensagem de boas-vindas será enviada para o número de WhatsApp do
lead simulado.
Responda à mensagem (e.g., "Moro em São Paulo").
Observação: A execução do workflow no Kestra deverá continuar,
processando a mensagem via IA e seguindo o fluxo correspondente.
Envio de Fatura:
Quando o sistema solicitar a fatura, envie uma imagem ou PDF da conta de
energia para o número do WhatsApp.
Observação: O Kestra processará o arquivo via OCR e validará o valor.
Verificação de Persistência:
Acesse o painel do Supabase.
Verifique as tabelas active_conversations, leads_validated e
leads_invalidated para confirmar que os dados estão sendo gravados e o estado
da conversa é gerenciado corretamente.
Recursos Adicionais
Guia Completo do Projeto: Para detalhes aprofundados sobre a arquitetura,
prompts de codificação e a lógica de cada componente, consulte o arquivo
PROJECT_GUIDE.md na raiz deste repositório.
Kestra Documentation: https://kestra.io/docs
FastAPI Documentation: [https://fastapi.tiangolo.com/](https://
fastapi.tiangolo.com/)
Supabase Documentation: [https://supabase.com/docs](https://supabase.com/
docs)