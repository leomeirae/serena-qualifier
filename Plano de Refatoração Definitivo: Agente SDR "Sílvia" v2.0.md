Este documento servirá como a **fonte definitiva** para a evolução do seu sistema. Ele explica o **porquê** (os objetivos), o **o quê** (a arquitetura) e o **como** (o passo a passo detalhado) da refatoração. Você pode entregar este guia diretamente à sua IA de codificação para execução.

Vamos começar.



-----

## **Plano de Refatoração Definitivo: Agente SDR "Sílvia" v2.0**

### **1. Introdução e Objetivos (O que iremos fazer)**

**Visão Geral:**
O objetivo desta refatoração é evoluir a arquitetura do projeto "serena-qualifier" de um modelo reativo para uma estrutura **simplificada, mais robusta e de maior performance**. Vamos eliminar redundâncias, centralizar responsabilidades e preparar o sistema para futuras expansões de forma limpa e organizada.

**Objetivos Principais:**

  * **Simplificar a Arquitetura:** Reduzir o número de "peças móveis" no fluxo de conversação, tornando o sistema mais fácil de entender e depurar.
  * **Centralizar a Lógica de Mensagens:** Criar uma única fonte da verdade para a interpretação de mensagens recebidas do WhatsApp.
  * **Melhorar a Performance:** Diminuir a latência do workflow Kestra removendo etapas de processamento desnecessárias.
  * **Aumentar a Robustez:** Tornar o sistema menos suscetível a erros de interpretação de mensagens e mais fácil de manter.

-----

### **2. Arquitetura Proposta: Foco na Simplificação**

Atualmente, o sistema utiliza um fluxo com uma etapa intermediária (`extract_message_content.py`) para "traduzir" mensagens de botão que o `webhook_service.py` não interpreta completamente.

**A nova arquitetura elimina essa redundância:**

1.  O `webhook_service.py` será aprimorado para se tornar a **única autoridade** na interpretação de mensagens do WhatsApp. Ele irá extrair o conteúdo real de qualquer interação (texto, clique de botão, etc.) e enviar uma mensagem limpa e direta para o Kestra.
2.  O workflow do Kestra (`3_ai_conversation_optimized.yml`) será simplificado, removendo a tarefa intermediária de extração. Ele receberá a mensagem limpa do webhook e a passará diretamente para o orquestrador do agente.
3.  O `agent_orchestrator.py` receberá sempre uma mensagem clara e não precisará mais de lógicas complexas para adivinhar a intenção do usuário.

**Fluxo de Dados Refatorado:**
`Mensagem do WhatsApp` → `Webhook Service (Intérprete Central)` → `Kestra (Orquestrador Simples)` → `Agent Orchestrator (Lógica de IA)`

-----

### **3. Plano de Implementação Detalhado (Como iremos fazer)**

Esta seção contém as instruções precisas para a IA de codificação.

#### **Fase 1: Centralizar a Inteligência no `webhook_service.py`**

**Justificativa:** Corrigir o problema na fonte. O webhook deve ser inteligente o suficiente para entender todos os tipos de mensagem do WhatsApp e enviar um payload limpo para o Kestra.

  * **Arquivo Alvo:** `webhook_service.py`

  * **Função Alvo:** `extract_whatsapp_message`

  * **Instruções:** Substitua completamente a função `extract_whatsapp_message` pelo código abaixo. Esta nova versão lida de forma robusta com textos, imagens e, mais importante, os diferentes tipos de botões (`interactive` e `button`), extraindo sempre o conteúdo significativo.

    ```python
    # Código final para a função em webhook_service.py

    def extract_whatsapp_message(webhook_data: Dict[str, Any]) -> Optional[WhatsAppMessage]:
        """
        Extrai dados da mensagem do payload do WhatsApp de forma robusta.
        """
        try:
            entry = webhook_data.get('entry', [])
            if not entry or not entry[0].get('changes'):
                return None
                
            value = entry[0]['changes'][0].get('value', {})
            messages = value.get('messages', [])
            
            if not messages:
                logger.info("📭 Webhook recebido sem mensagens (provavelmente um status de entrega)")
                return None
                
            message = messages[0]
            phone_number = message.get('from', '')
            message_type = message.get('type', '')
            timestamp = message.get('timestamp', str(int(datetime.now().timestamp())))
            
            message_text = ""
            media_id = None
            
            if message_type == 'text':
                message_text = message.get('text', {}).get('body', '')
            elif message_type == 'image':
                media_id = message.get('image', {}).get('id', '')
                message_text = message.get('image', {}).get('caption', 'Imagem enviada')
            elif message_type == 'interactive':
                reply = message.get('interactive', {}).get('button_reply', {})
                message_text = reply.get('title', 'Botão Interativo Clicado')
                logger.info(f"🔘 Botão Interativo pressionado, título extraído: '{message_text}'")
            elif message_type == 'button':
                reply = message.get('button', {})
                message_text = reply.get('text', 'Botão de Template Clicado')
                logger.info(f"🔘 Botão de Template pressionado, texto extraído: '{message_text}'")
            else:
                message_text = f"Mensagem do tipo '{message_type}' não suportado recebida"

            logger.info(f"📱 Mensagem final extraída para {phone_number}: '{message_text[:100]}'")
            
            return WhatsAppMessage(
                phone=phone_number,
                message=message_text,
                media_id=media_id,
                timestamp=timestamp
            )
            
        except Exception as e:
            logger.error(f"❌ Erro crítico ao extrair mensagem do webhook: {str(e)}")
            return None
    ```

#### **Fase 2: Simplificar Drasticamente o Workflow Kestra**

**Justificativa:** Com o webhook enviando dados limpos, a tarefa `extract_message_content` torna-se obsoleta e pode ser removida, acelerando o fluxo.

  * **Arquivo Alvo:** `kestra/workflows/3_ai_conversation_optimized.yml`

  * **Instruções:**

    1.  **Remova completamente a tarefa `extract_message_content`** do arquivo YAML.
    2.  **Modifique a tarefa `ai_agent_processing`** para consumir os dados diretamente do `trigger`. Atualize as variáveis de ambiente `USER_MESSAGE` e `PHONE_NUMBER` conforme abaixo.

    <!-- end list -->

    ```yaml
    # Em kestra/workflows/3_ai_conversation_optimized.yml

    # ... (outras tarefas)

    # A TAREFA 'extract_message_content' DEVE SER REMOVIDA

    # FASE 3: PROCESSAMENTO IA (MODIFICADA)
    - id: ai_agent_processing
      type: io.kestra.plugin.scripts.python.Script
      description: "Processamento principal do agente IA com entrada direta do webhook"
      # ... (taskRunner e outras configs permanecem)
      env:
        OPENAI_API_KEY: "{{ secret('OPENAI_API_KEY') }}"
        DB_CONNECTION_STRING: "{{ secret('DB_CONNECTION_STRING') }}"
        SERENA_API_TOKEN: "{{ secret('SERENA_API_TOKEN') }}"
        SERENA_API_BASE_URL: "https://partnership-service-staging.api.srna.co"
        # ALTERAÇÃO: Obter dados diretamente do gatilho do webhook
        USER_MESSAGE: "{{ trigger.body.message }}"
        PHONE_NUMBER: "{{ trigger.body.phone }}"
        REDIS_URL: "{{ vars.redis_url }}"
      # ... (inputFiles permanecem os mesmos)
      script: |
        # O script Python dentro desta tarefa permanece o mesmo,
        # pois ele já lê as variáveis de ambiente.
        import os
        import logging
        from kestra import Kestra
        # ... (resto do script)
    ```

#### **Fase 3: Refatorar o Orquestrador para o Novo Contrato de Dados**

**Justificativa:** O orquestrador agora receberá mensagens diretas como "Sim, confirmar cidade\!" em vez de "O usuário clicou no botão...". A lógica interna pode ser simplificada.

  * **Arquivo Alvo:** `scripts/agent_orchestrator.py`

  * **Função Alvo:** `handle_agent_invocation`

  * **Instruções:** Substitua a função `handle_agent_invocation` pela versão simplificada abaixo.

    ```python
    # Código final para a função em scripts/agent_orchestrator.py

    def handle_agent_invocation(phone_number: str, user_message: str, image_url: str | None = None):
        """
        Recebe a mensagem limpa do usuário, prepara a entrada e invoca o agente com memória.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Lógica de entrada simplificada
        if image_url:
            input_data = f"O usuário {phone_number} enviou esta imagem para análise: {image_url}. Mensagem adicional: {user_message}"
        else:
            # A mensagem já é o conteúdo real, seja texto ou o título de um botão.
            input_data = user_message

        config = {"configurable": {"session_id": phone_number}}

        try:
            logger.info(f"🤖 Invocando agente para {phone_number} com input: '{input_data[:100]}...'")
            response = agent_with_chat_history.invoke(
                {"input": input_data},
                config=config
            )
            
            output = response.get("output", "Não consegui processar sua solicitação.")
            return {"response": output}
        except Exception as e:
            logger.error(f"❌ Erro ao invocar agente para {phone_number}: {str(e)}")
            return {"response": f"Desculpe, tive um problema técnico. Por favor, tente novamente. Erro: {str(e)}"}
    ```

#### **Fase 4: Limpeza do Projeto**

**Justificativa:** Remover código que não é mais utilizado para manter o projeto limpo.

  * **Ação:** Delete o seguinte arquivo do seu projeto:
      * `scripts/extract_message_content.py`

-----

### **4. Resultados Esperados**

Após a conclusão desta refatoração, o sistema apresentará as seguintes melhorias:

  * **Manutenibilidade:** A lógica de interpretação de mensagens estará em um único lugar (`webhook_service.py`), facilitando futuras alterações na API do WhatsApp.
  * **Performance Aprimorada:** A remoção de uma tarefa inteira (`extract_message_content`) do workflow Kestra reduzirá a latência total em cada interação do usuário.
  * **Código Mais Limpo:** A eliminação de código de "tradução" e workarounds torna o fluxo de dados direto e a base de código mais enxuta.
  * **Maior Confiabilidade:** A centralização da lógica diminui as chances de inconsistências e bugs entre os diferentes componentes do sistema.

Este plano, quando executado, estabelecerá uma base sólida e eficiente para o seu projeto, permitindo que futuras melhorias, como o aprimoramento da persona da SDR "Sílvia", sejam construídas sobre uma fundação de alta qualidade.