

**Análise dos Logs:**

1.  **Sucesso Inicial:**
    *   `Iniciando qualificação do lead: Carminha`
    *   `Telefone: +5581991781985`
    *   `Email: lelecomeiralins@gmail.com`
    *   `Execution ID: 3H8yE8f82u0u5Tx4q3RVbU`
    *   `Enviando mensagem de boas-vindas WhatsApp...`
    *   `Enviando para: +5581991781985 (Nome: Carminha)`
    *   A resposta do serviço de WhatsApp foi: `{"success":true,"message":"Welcome message sent successfully to +5581991781985", ...}`. **Isso indica que a API do seu serviço de WhatsApp respondeu com sucesso.**

2.  **❌ Problema 1: Falha na Lógica de Verificação do Envio do WhatsApp (`send-welcome-whatsapp`)**
    *   Log: `❌ Falha na resposta da API ou template incorreto`
    *   Log: `Detalhes do erro: {"success":true, ...}`
    *   **Causa Provável:** Sua task `send-welcome-whatsapp` tem uma lógica de verificação no script shell:
        ```shell
        if echo "$RESPONSE" | grep -q '"success".*true' && echo "$RESPONSE" | grep -q '"template_name".*"hello_world"'; then
          # ... sucesso
        else
          # ... falha
        fi
        ```
        A API retornou `success:true`, mas **provavelmente não retornou `"template_name":"hello_world"`**. O seu serviço de envio de WhatsApp pode não retornar o `template_name` ou o nome do template usado é diferente de "hello_world". Por isso, o script considerou uma falha, mesmo que a mensagem possa ter sido enviada.

3.  **Progresso das Tarefas Simuladas:**
    *   `Intenção classificada: informou_cidade` (Simulado)
    *   `Consultando planos para a cidade: Recife` (Simulado)
    *   `2 planos encontrados para Recife` (Simulado)
    *   `Processamento OCR simulado concluído.` (Simulado) - **Esta é a task `process-invoice-ocr`.**

4.  **❌ Problema 2: Erro Crítico na Passagem de Output da Task de OCR (`validate-and-send-proceed-template`)**
    *   Log: `ERROR Unable to find 'ocr_result' used in the expression '{{ outputs['process-invoice-ocr'].ocr_result | json }}' at line 1`
    *   **Causa Provável:** A task `validate-and-send-proceed-template` está tentando acessar `outputs['process-invoice-ocr'].ocr_result`. O erro indica que a chave `ocr_result` não foi encontrada nos outputs da task `process-invoice-ocr`.
        *   Olhando a task `process-invoice-ocr`:
            ```python
            # ...
            ocr_data = { ... }
            print(f'::{json.dumps({"outputs": {"ocr_result": ocr_data}})}::') # Esta linha DEVERIA criar o output
            print("📄 Processamento OCR simulado concluído.")
            ```
        *   A sintaxe para criar o output está correta. As possíveis razões para falha são:
            1.  A linha `print(f'::{json.dumps({"outputs": {"ocr_result": ocr_data}})}::')` não está sendo executada ou seu stdout não está sendo capturado corretamente pelo Kestra para definir o output.
            2.  Há algum problema com o `taskRunner` ou a imagem Docker que impede a correta propagação do output.
            3.  A task `process-invoice-ocr` pode estar falhando silenciosamente *antes* de definir o output, mas o log "Processamento OCR simulado concluído" sugere que ela chegou perto do fim.

5.  **Error Handler Ativado:**
    *   Devido ao erro acima, o workflow foi para o `error-handler`.
    *   `ERRO NO WORKFLOW DE QUALIFICAÇÃO na tarefa: unknown_task` - O error handler não conseguiu identificar a task exata que falhou com base na estrutura de `execution.taskruns`. Isso pode ser melhorado.

**Planejamento para Ajustes e Funcionalidade:**

Proponho um plano focado em resolver os erros atuais e, em seguida, evoluir para a implementação completa conforme o "PROJECT_GUIDE.md".

**FASE A: Estabilização e Correção dos Erros Atuais**

1.  **Corrigir a Lógica de Verificação do Envio de WhatsApp (Task: `send-welcome-whatsapp`)**
    *   **Ação:** Modifique o script shell. Se o seu serviço `/whatsapp/send_welcome` não retorna `template_name` de forma confiável ou se o nome do template não é fixo como "hello_world", ajuste a condição.
    *   **Sugestão:**
        ```shell
        # ... (curl command) ...
        if [ $CURL_EXIT_CODE -ne 0 ]; then
          echo "❌ Curl falhou com código de saída: $CURL_EXIT_CODE"
          echo '::{"outputs":{"whatsapp_sent":false,"template_confirmed":"none","error_details":"curl_failed_exit_'$CURL_EXIT_CODE'"}}::'
          # Considere se deve ser exit 0 ou exit 1 aqui. Se for um erro crítico, exit 1.
        elif echo "$RESPONSE" | grep -q '"success".*true'; then # Simplifique a checagem
          echo "✅ Mensagem enviada com sucesso (confirmado pela API)"
          # Você pode tentar extrair o template_name se ele existir, mas não o torne um critério de falha rígido se não for essencial.
          TEMPLATE_USED=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('template_name', 'N/A'))" 2>/dev/null || echo "N/A")
          echo "📱 Template (se informado pela API): $TEMPLATE_USED"
          echo '::{"outputs":{"whatsapp_sent":true,"template_confirmed":"'${TEMPLATE_USED:-none}'"}}::'
        else
          echo "❌ Falha na resposta da API"
          echo '::{"outputs":{"whatsapp_sent":false,"template_confirmed":"none","error_details":"api_response_failure_or_unexpected_format"}}::'
          echo "Detalhes do erro: $RESPONSE"
        fi
        ```
    *   **Verifique:** Qual o nome real do template de boas-vindas que você configurou na Meta? É "hello_world" mesmo? O endpoint `/whatsapp/send_welcome` no seu `whatsapp_sender.py` está configurado para usar e retornar este template?

2.  **Corrigir a Propagação do Output da OCR (Task: `process-invoice-ocr` e `validate-and-send-proceed-template`)**
    *   **Ação 1 (na task `process-invoice-ocr`):** Garanta que o output seja enviado e "flushed".
        *   **Sugestão no script Python:**
            ```python
            import os
            import json
            import sys # Adicionar

            ocr_data = {
                "valor_total": "550.00",
                "mes_referencia": "Maio/2025",
                "consumo_kwh": "400",
                "qualification_score": 85,
                "is_qualified": True
            }
            # Certifique-se que esta é a última (ou única relevante para Kestra) linha de output formatado
            print(f'::{json.dumps({"outputs": {"ocr_result": ocr_data}})}::')
            sys.stdout.flush() # Forçar o flush do stdout
            print("📄 Processamento OCR simulado concluído.") # Mantenha outros logs se precisar
            ```
    *   **Ação 2 (na task `validate-and-send-proceed-template`):** Ajuste como o JSON é recebido.
        *   Quando `ocr_result` é definido como `ocr_data` (um dicionário Python) e passado via `json.dumps`, o Kestra armazena `ocr_result` como um objeto/mapa Kestra.
        *   **No `env` da task `validate-and-send-proceed-template`:**
            ```yaml
            env:
              # ...
              # OCR_RESULT_JSON: "{{ outputs['process-invoice-ocr'].ocr_result | json }}" # O filtro |json aqui pode ser o problema se ocr_result já é um objeto
              OCR_RESULT_STRING: "{{ outputs['process-invoice-ocr'].ocr_result }}"
            ```
        *   **No script Python da task `validate-and-send-proceed-template`:**
            ```python
            import os, json

            ocr_result_str = os.getenv("OCR_RESULT_STRING", "{}")
            print("DEBUG OCR_RESULT_STRING:", ocr_result_str) # Adicione este log para depuração

            try:
                # Se o Kestra passou o objeto como uma string JSON:
                ocr_data_dict = json.loads(ocr_result_str)
            except json.JSONDecodeError:
                print(f"ERRO: Não foi possível decodificar OCR_RESULT_STRING: {ocr_result_str}")
                # Lide com o erro, talvez definindo ocr_data_dict para um valor padrão ou saindo
                ocr_data_dict = {"qualification_score": 0} # Exemplo de fallback

            if ocr_data_dict.get("qualification_score", 0) >= 75:
                print("📱 Lead qualificado! Enviando template 'prosseguir_com_solicitacao'…")
                print('::{"outputs":{"prosseguir_sent":true,"template_confirmed":"prosseguir_com_solicitacao"}}::')
            else:
                print("⚠️ Lead não qualificado; não envio template.")
                print('::{"outputs":{"prosseguir_sent":false,"template_confirmed":"none"}}::')
            ```
    *   **Teste:** Execute o workflow após essas alterações. Verifique os logs da task `validate-and-send-proceed-template`, especialmente o "DEBUG OCR_RESULT_STRING:".

3.  **Melhorar Identificação da Task Falha no Error Handler (Task: `qualification-error-handler`)**
    *   **Ação:** Ajuste o script do error handler para inspecionar `taskRunList` (se for a nomenclatura correta no seu `{{ execution | json }}`) ou a estrutura equivalente que lista as tasks e seus status.
    *   **Nota:** Isso é menos crítico para fazer o workflow funcionar, mas bom para a depuração.

**FASE B: Alinhamento com o PROJECT_GUIDE.md - Rumo à Interatividade e Módulos Reais**

Após estabilizar o workflow atual (mesmo que simulado), o próximo passo é substituir as simulações e introduzir a interatividade.

1.  **Implementar `utils.conversation_manager` e `scripts.supabase_client`:**
    *   Crie os módulos Python conforme o guia (Fase 5 Parte 1 e Fase 9).
    *   Garanta que a imagem Docker `serena/kestra-python-runner:latest` tenha as dependências (`supabase-py`, `python-dotenv`).
    *   Adicione as variáveis de ambiente do Supabase ao Kestra (secrets) e ao seu ambiente de desenvolvimento.

2.  **Implementar `scripts.whatsapp_sender.py` (Real):**
    *   Certifique-se que o endpoint FastAPI `POST /whatsapp/send_welcome` está funcional e usa as variáveis de ambiente corretas (`WHATSAPP_API_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_WELCOME_TEMPLATE_NAME`).
    *   A task `send-welcome-whatsapp` no Kestra já faz a chamada `curl`, o que está correto.

3.  **Introduzir `WaitForWebhook` e `scripts.whatsapp_webhook_receiver.py`:**
    *   Após `send-welcome-whatsapp`, adicione uma task `io.kestra.core.tasks.flows.WaitForWebhook` (conforme Fase 10, Task 3 do guia).
        *   Ela pausará o workflow esperando um callback.
        *   Configure um `timeout`.
    *   Desenvolva `scripts.whatsapp_webhook_receiver.py` como um serviço FastAPI:
        *   Endpoint `POST /webhook/whatsapp` para a Meta (Facebook).
        *   Endpoint `GET /webhook/whatsapp` para verificação da Meta.
        *   Lógica para obter o `kestra_execution_id` (via `conversation_manager`) e fazer o callback para o Kestra (resumir o `WaitForWebhook`).
    *   **Ajuste na Task `initialize-qualification` (ou criar uma nova task inicial):**
        *   Salvar o estado inicial da conversa usando `utils.conversation_manager.save_conversation_state(phone, execution.id, 'initial')`.

4.  **Implementar `scripts.ai_agent.py` (Real):**
    *   Crie as funções `classify_intent`, `generate_rag_response`, `extract_city_from_message`.
    *   Adicione a API Key do LLM (OpenAI, Anthropic, Google) aos secrets do Kestra.
    *   Modifique a task `classify-lead-intent` no Kestra para chamar `scripts.ai_agent.classify_intent` (em vez de simular). O script Python da task Kestra importará e usará o `ai_agent`.

5.  **Implementar `Switch` e Fluxos Condicionais:**
    *   Adicione a task `io.kestra.core.tasks.flows.Switch` após a classificação da intenção.
    *   Desenvolva as branches (`informou_cidade`, `fez_pergunta_geral`, etc.) conforme o guia.

6.  **Implementar `scripts.serena_api.py` (Real):**
    *   Crie a função `get_plans_by_city`.
    *   Adicione `SERENA_API_KEY` aos secrets.
    *   Ajuste a task `get-available-plans` para chamar esta função.

7.  **Implementar `scripts.ocr_processor.py` (Real) e Upload de Fatura:**
    *   Crie as funções `preprocess_image`, `extract_invoice_amount`, `validate_invoice`.
    *   Adicione um endpoint `POST /upload_invoice` (provavelmente no `whatsapp_webhook_receiver.py` ou um novo `file_receiver.py`) que:
        *   Recebe o arquivo e o telefone.
        *   Chama o `ocr_processor`.
        *   Faz callback para um `WaitForWebhook` no Kestra (que espera o upload da fatura).
    *   Modifique a task `process-invoice-ocr` para realmente usar o arquivo processado (o caminho do arquivo ou seus dados seriam passados no callback do `WaitForWebhook`).

8.  **Finalizar Lógica de Persistência e Encerramento:**
    *   Implementar as tasks `save-lead-and-finalize` e `handle-inactive-lead` chamando os módulos reais (`supabase_client`, `whatsapp_sender`, `conversation_manager`).

**Próximos Passos Imediatos (Sugestão):**

1.  Aplique as correções da **FASE A** (verificação do WhatsApp e output do OCR).
2.  Teste o workflow. Verifique se ele roda do início ao fim (mesmo com simulações) sem o erro `Unable to find 'ocr_result'`.
3.  Compartilhe os resultados.

