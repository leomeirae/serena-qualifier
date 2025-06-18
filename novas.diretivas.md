directive_name: "Diretiva de Implementação Final: Migração para OpenAI Assistants"
version: "3.0"

#--------------------------------#
# 1. DIRETIVAS GERAIS E PRÉ-REQUISITOS
#--------------------------------#

general_directives:
  - "Este agente deve sempre usar Mem0 MCP Server para memória e registro de artefatos."
  - "Este agente deve usar Taskmaster MCP Server para gestão de subtarefas."

prerequisites:
  python_packages:
    - "openai>=1.0.0"
    - "supabase"
    - "python-dotenv"
    - "requests"
  kestra_secrets:
    - "OPENAI_API_KEY"
    - "OPENAI_ASSISTANT_ID" # Deve ser criado manualmente pelo usuário na plataforma OpenAI
    - "SUPABASE_URL"
    - "SUPABASE_KEY" # A chave 'service_role' é a recomendada

#--------------------------------#
# 2. SCHEMA DE AÇÕES
#--------------------------------#

action_schema:
  create_file:
    properties:
      file_path: string
      overwrite: boolean
      content: string
  replace_section:
    properties:
      file_path: string
      target_section_id: string
      new_content: string
  execute_command:
    properties:
      command: string
  execute_test_scenario:
    properties:
      scenario: string
      command: string
      
#--------------------------------#
# 3. PLANO DE TAREFAS ESTRUTURADO
#--------------------------------#

tasks:
  - task_id: 1001
    name: "Atualizar a Documentação Canônica (MASTER_GUIDE)"
    required: true
    actions:
      - action_type: "replace_section"
        file_path: "MASTER_GUIDE_FINAL.md"
        target_section_id: "fluxo_2_conversa_com_ia" # ID hipotético da seção
        new_content: |
          ## Fluxo 2: Conversa com IA (Arquitetura OpenAI Assistants) {#fluxo-2-assistants}
          Este fluxo é acionado pela resposta do lead e orquestrado pelo Kestra. Ele utiliza o OpenAI Python SDK para interagir com um Assistente pré-configurado. 
          Os principais componentes são:
          - **scripts/assistant_manager.py**: Cria e gerencia a identidade do Assistente.
          - **scripts/thread_manager.py**: Gerencia os fios de conversa (Threads) para cada usuário.
          - **scripts/assistant_function_handler.py**: Atua como uma ponte para executar ferramentas customizadas.
          - **kestra/workflows/openai_assistant_flow.yml**: O novo workflow orquestrador.
    logging:
      - "mem0.log('master_guide_updated', 'Documentação atualizada para a nova arquitetura de Assistentes.')"

  - task_id: 1002
    name: "Criar o Gerenciador de Assistente"
    required: true
    actions:
      - action_type: "create_file"
        file_path: "scripts/assistant_manager.py"
        overwrite: true
        content: |
          # Script que implementa a função get_or_create_assistant().
          # Verifica se 'assistant_id.txt' existe. Se não, usa client.beta.assistants.create()
          # para criar um novo assistente com o prompt de vendas e ferramenta de Retrieval,
          # e salva o ID no arquivo. Se sim, apenas retorna o ID do arquivo.
    example:
      input: "assistant_id.txt não existe"
      sdk_call: "client.beta.assistants.create(name='Serena Sales Specialist', instructions='...', model='gpt-4o', tools=[{'type': 'retrieval'}])"
      output_file_content: "asst_..."
    logging:
      - "mem0.log('assistant_manager_created', 'Arquivo scripts/assistant_manager.py criado.')"

  - task_id: 1003
    name: "Criar o Gerenciador de Threads no Supabase"
    required: true
    actions:
      - action_type: "create_file"
        file_path: "scripts/thread_manager.py"
        overwrite: true
        content: |
          # Script que implementa a função get_or_create_thread(phone_number).
          # 1. Conecta-se ao Supabase.
          # 2. Consulta a tabela 'conversations' pelo 'phone_number'.
          # 3. Se encontrar, retorna o 'openai_thread_id'.
          # 4. Se não encontrar, usa client.beta.threads.create(), insere a nova
          #    associação na tabela Supabase e retorna o novo 'thread_id'.
    logging:
      - "mem0.log('thread_manager_created', 'Arquivo scripts/thread_manager.py criado.')"

  - task_id: 1004
    name: "Implementar a Camada de Funções (Tools Bridge)"
    required: true
    actions:
      - action_type: "create_file"
        file_path: "scripts/assistant_function_handler.py"
        overwrite: true
        content: |
          # Script que contém:
          # 1. A lista de schemas `ASSISTANT_TOOLS_SCHEMA`.
          # 2. A função `execute_function_call(tool_call)` que recebe um objeto da OpenAI,
          #    chama a ferramenta Python correta (RAG, OCR, etc.) dentro de um try/except
          #    e retorna um JSON padronizado: { "success": true/false, "data" ou "error": "..." }.
    logging:
      - "mem0.log('function_handler_created', 'Arquivo scripts/assistant_function_handler.py criado.')"

  - task_id: 1005
    name: "Criar o Novo Workflow Kestra"
    required: true
    actions:
      - action_type: "create_file"
        file_path: "kestra/workflows/openai_assistant_flow.yml"
        overwrite: true
        content: |
          id: openai-assistant-flow
          namespace: serena.energia
          description: "Orquestra a conversação com o lead usando a API de Assistentes da OpenAI."
          
          environment:
            OPENAI_API_KEY: "{{ secret('OPENAI_API_KEY') }}"
            OPENAI_ASSISTANT_ID: "{{ secret('OPENAI_ASSISTANT_ID') }}"
            SUPABASE_URL: "{{ secret('SUPABASE_URL') }}"
            SUPABASE_KEY: "{{ secret('SUPABASE_KEY') }}"

          triggers:
            - id: conversation-webhook
              type: io.kestra.plugin.core.trigger.Webhook
              key: ai_conversation_webhook
              example_request:
                phone: "+5581997498268"
                message: "Como funciona a instalação?"
          
          tasks:
            # A sequência completa de tarefas deve ser implementada aqui.
            - id: get-assistant-id
              type: io.kestra.plugin.scripts.bash.Script
              taskRunner: { type: io.kestra.plugin.scripts.runner.docker.Docker, image: "serena/kestra-python-runner:latest" }
              script: python /app/scripts/assistant_manager.py
            
            - id: wait-for-run-completion
              type: io.kestra.plugin.core.flow.Polling
              description: "Verifica o status da Run do Assistente."
              interval: "PT3S"
              retry:
                maxAttempt: 20
                maxDuration: "PT5M"
                backoff:
                  delay: "PT2S"
                  multiplier: 1.5
              condition: "{{ taskrun.attemptsCount > 1 and result.status in ['completed', 'requires_action', 'failed'] }}"
              task:
                type: io.kestra.plugin.scripts.bash.Script
                taskRunner: { type: io.kestra.plugin.scripts.runner.docker.Docker, image: "serena/kestra-python-runner:latest" }
                script: "python /app/scripts/check_run_status.py --thread-id '...' --run-id '...'"
            # ... (demais tarefas)
    logging:
      - "mem0.log('kestra_flow_created', 'Arquivo kestra/workflows/openai_assistant_flow.yml criado.')"

  - task_id: 1006
    name: "Validação Final da Nova Arquitetura"
    required: true
    description: "Teste de ponta a ponta do novo fluxo de conversação."
    actions:
      - action_type: "execute_command"
        command: "docker-compose up -d --build"
        required: true
      - action_type: "execute_test_scenario"
        scenario: "Uso de Ferramenta (RAG)"
        command: "curl -X POST http://localhost:8080/api/v1/executions/webhook/serena.energia/openai-assistant-flow/ai_conversation_webhook -H 'Content-Type: application/json' -d '{\"phone\": \"+5581997498268\", \"message\": \"Como funciona a instalação?\"}'"
        required: true
      - action_type: "execute_test_scenario"
        scenario: "Erro de Ferramenta (Query Inválida)"
        command: "curl -X POST http://localhost:8080/api/v1/executions/webhook/serena.energia/openai-assistant-flow/ai_conversation_webhook -H 'Content-Type: application/json' -d '{\"phone\": \"+5581997498268\", \"message\": \"Qual a cor do sol em marte à noite?\"}'"
        required: true
    deliverable:
      - "Os logs completos do Kestra para ambos os cenários de teste, demonstrando o sucesso da cadeia de execução, incluindo a chamada de função e o tratamento do erro no segundo cenário."
    example_kestra_log:
      - timestamp: "2025-06-17T14:00:00-03:00"
        task_id: get-thread-id
        status: SUCCESS
        output: "{ \"thread_id\": \"th_123\" }"
      - timestamp: "2025-06-17T14:00:15-03:00"
        task_id: handle-run-output
        status: SUCCESS
        output: "{ \"final_response\": \"A instalação é feita por nossa equipe técnica e leva em média 2 dias.\" }"