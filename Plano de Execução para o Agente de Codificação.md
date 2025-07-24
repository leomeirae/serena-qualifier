-----

### **Plano de Execução para o Agente de Codificação**

**Objetivo:** Implementar o "Plano de Refatoração Definitivo: Agente SDR 'Sílvia' v2.0". Vamos centralizar a lógica de interpretação de mensagens, simplificar o workflow Kestra, refatorar o orquestrador do agente e limpar o código obsoleto.

#### **Fase 1: Centralizar a Inteligência no `webhook_service.py`**

**Justificativa:** A causa raiz do problema atual é que o webhook não extrai o texto real dos botões do WhatsApp. Esta fase corrige isso, garantindo que uma mensagem limpa e com contexto seja enviada para o resto do sistema.

  * **Arquivo Alvo:** `scripts/webhook_service.py`
  * **Função Alvo:** `extract_whatsapp_message`
  * **Ação:** Substitua **completamente** a função `extract_whatsapp_message` existente pelo código abaixo. Este novo código é capaz de interpretar corretamente o clique em botões (`button` e `interactive`) e extrair o texto real deles.

<!-- end list -->

```python
# Código para substituir a função em scripts/webhook_service.py

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

**Justificativa:** Como o webhook agora envia os dados já processados, a tarefa intermediária de extração de mensagem no Kestra se torna desnecessária. Removê-la vai simplificar e acelerar o workflow.

  * **Arquivo Alvo:** `kestra/workflows/3_ai_conversation_optimized.yml`

  * **Ação:** Modifique a tarefa `ai_agent_processing` para receber os dados diretamente do gatilho (`trigger`).

      * Altere o valor da variável de ambiente `USER_MESSAGE` para: `{{ trigger.body.message }}`
      * Altere o valor da variável de ambiente `PHONE_NUMBER` para: `{{ trigger.body.phone }}`

<!-- end list -->

```yaml
# Bloco a ser modificado em kestra/workflows/3_ai_conversation_optimized.yml

# FASE 3: PROCESSAMENTO IA
- id: ai_agent_processing
  type: io.kestra.plugin.scripts.python.Script
  description: "Processamento principal do agente IA com entrada direta do webhook"
  taskRunner:
    type: io.kestra.plugin.scripts.runner.docker.Docker
    image: kestra-agent:latest
    networkMode: coolify
  env:
    OPENAI_API_KEY: "{{ secret('OPENAI_API_KEY') }}"
    DB_CONNECTION_STRING: "{{ secret('DB_CONNECTION_STRING') }}"
    SERENA_API_TOKEN: "{{ secret('SERENA_API_TOKEN') }}"
    SERENA_API_BASE_URL: "https://partnership-service-staging.api.srna.co"
    # ALTERAÇÃO CRÍTICA: Obter dados diretamente do gatilho do webhook
    USER_MESSAGE: "{{ trigger.body.message }}"
    PHONE_NUMBER: "{{ trigger.body.phone }}"
    REDIS_URL: "{{ vars.redis_url }}"
    PYTHONPATH: "/app"
  inputFiles:
    # ... (inputFiles permanecem os mesmos) ...
  script: |
    # ... (o script python interno permanece o mesmo) ...
```

#### **Fase 3: Refatorar o Orquestrador da IA**

**Justificativa:** O agente de IA agora receberá um texto claro e direto (ex: "Sim, confirmar cidade\!"). A lógica para tratar mensagens genéricas pode ser removida, simplificando o código.

  * **Arquivo Alvo:** `scripts/agent_orchestrator.py`
  * **Função Alvo:** `handle_agent_invocation`
  * **Ação:** Substitua **completamente** a função `handle_agent_invocation` pela versão mais simples e direta abaixo.

<!-- end list -->

```python
# Código para substituir a função em scripts/agent_orchestrator.py

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

Ao completar estas três fases, o sistema estará alinhado com o plano de refatoração, e a agente "Sílvia" deverá começar a responder de forma inteligente e contextual, exatamente como você projetou.