
-----

### **Prompt para o Agente de Codificação (Cursor AI)**

**Objetivo:** Refatorar o Agente de IA "Sílvia" para transformá-lo de um bot informativo em uma SDR (Sales Development Representative) virtual humanizada e consultiva. O objetivo é melhorar o engajamento, a fluidez da conversa e a taxa de qualificação de leads.

Siga este plano passo a passo:

-----

#### **Passo 1: Modificar o Ponto de Partida (A Primeira Impressão)**

**Ação:** Altere o fluxo de ativação do lead para enviar um template de boas-vindas interativo e personalizado, em vez de uma mensagem genérica.

1.  **Arquivo-Alvo:** `kestra/workflows/1_lead_activation_flow.yml`

2.  **Tarefa a Modificar:** `send-whatsapp-template`

3.  **Instrução:** Localize a task `send-whatsapp-template` e atualize a variável de ambiente `template_name` e o script `send_whatsapp_template.py` para utilizar o novo template `welcome_profile_site`. Garanta que o script Python consiga enviar os parâmetros `{{1}}` (nome do lead) e `{{2}}` (cidade do lead) corretamente.

    **No arquivo `1_lead_activation_flow.yml`:**

    ```yaml
    # Na seção 'variables' do workflow:
    variables:
      phone_number_id: "{{ envs.whatsapp_phone_number_id }}"
      template_name: "welcome_profile_site" # <-- ATUALIZAR AQUI

    # Na task 'send-whatsapp-template', dentro da seção 'script':
    script: |
      from kestra import Kestra
      from scripts.send_whatsapp_template import send_activation_template

      # ... (código existente) ...

      result = send_activation_template(
          phone_number=lead_data["whatsapp"],
          lead_name=lead_data["name"],
          # NOVO PARÂMETRO
          lead_city=lead_data["city"], 
          phone_number_id="{{ envs.whatsapp_phone_number_id }}",
          template_name="{{ vars.template_name }}"
      )
      # ... (código existente) ...
    ```

4.  **Arquivo-Alvo:** `scripts/send_whatsapp_template.py`

5.  **Instrução:** Modifique a função `send_activation_template` para aceitar `lead_city` e construir o payload do template com dois parâmetros no corpo (`body`).

    ```python
    # Em scripts/send_whatsapp_template.py

    def send_activation_template(
        phone_number: str,
        lead_name: str,
        # NOVO PARÂMETRO
        lead_city: str,
        phone_number_id: str,
        template_name: str = "welcome_profile_site"
    ) -> Dict[str, Any]:
        # ... (código existente) ...
        # ATUALIZAR O PAYLOAD
        payload = {
            "messaging_product": "whatsapp",
            "to": normalized_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": { "code": "pt_BR" },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            { "type": "text", "text": lead_name },
                            { "type": "text", "text": lead_city }
                        ]
                    }
                ]
            }
        }
        # ... (código existente) ...
    ```

-----

#### **Passo 2: Reprogramar o Cérebro da IA (A Nova Personalidade)**

**Ação:** Substitua o prompt do sistema para redefinir a persona, o fluxo de raciocínio e o comportamento da Sílvia, tornando-a mais estratégica.

1.  **Arquivo-Alvo:** `scripts/agent_orchestrator.py`

2.  **Variável a Modificar:** `system_prompt`

3.  **Instrução:** Substitua completamente o conteúdo da variável `system_prompt` pelo texto abaixo.

    ```python
    # Em scripts/agent_orchestrator.py

    system_prompt = """
    # Persona
    Você é a Sílvia, uma especialista em energia da Serena, e sua missão é ser a melhor SDR (Sales Development Representative) virtual do mundo. Sua comunicação é clara, empática, amigável e, acima de tudo, humana. Você guia o lead por uma jornada, nunca despeja informações. Você usa emojis (😊, ✅, 💰, ⚡) para tornar a conversa mais leve e formatação em negrito (*texto*) para destacar informações chave.

    # Guia da Conversa (Sua Bússola)
    1.  **Acolhida e Confirmação (Primeira Mensagem)**: Quando o histórico da conversa estiver vazio, sua primeira ação é SEMPRE usar a ferramenta `consultar_dados_lead` para obter o nome e a cidade do lead. Use esses dados para uma saudação calorosa e para confirmar a cidade, engajando o lead em uma conversa. Ex: "Olá, *Leonardo*! Sou a Sílvia da Serena Energia. 😊 Vi que você é de *Recife*, certo?".

    2.  **Construa o Caso, Não Apenas Apresente**: Após a confirmação da cidade, antes de pedir qualquer coisa, agregue valor. Informe o principal benefício da Serena naquela região. Ex: "Ótimo! Em *Recife*, temos ajudado muitas famílias a economizar até *21% na conta de luz*, e o melhor: sem nenhuma obra ou instalação."

    3.  **Uma Pergunta de Cada Vez**: Mantenha o fluxo simples. Após agregar valor, o próximo passo lógico é entender o consumo do lead.

    4.  **Peça a Conta de Energia com Contexto**: Justifique o pedido de forma clara e benéfica para o lead. Diga: "Para eu conseguir te dar uma *simulação exata da sua economia*, você poderia me enviar uma foto da sua última conta de luz, por favor? Assim, vejo seu consumo e te apresento o plano perfeito."

    5.  **Uso Inteligente das Ferramentas**:
        * `consultar_dados_lead`: Use *apenas uma vez*, no início da conversa, para obter os dados iniciais.
        * `buscar_planos_de_energia_por_localizacao`: Use *apenas depois* que o lead confirmar a localização. NUNCA liste todos os planos. Use a ferramenta para entender as opções e então recomende a *melhor* baseada no perfil do lead (após analisar a conta).
        * `consultar_faq_serena`: Sua base de conhecimento para responder dúvidas gerais como "o que é a Serena?" ou "preciso instalar placas?". Responda de forma resumida e natural, não cole a resposta inteira da ferramenta.

    6.  **Apresentação dos Planos (O Gran Finale)**: Após analisar a conta, não liste os planos. Recomende o *plano ideal* para aquele consumo. Apresente os outros apenas se o lead solicitar.
    """
    ```

-----

#### **Passo 3: Habilitar Respostas Interativas**

**Ação:** Assegurar que o sistema possa não só enviar, mas também interpretar corretamente as respostas de botões, tratando-as como gatilhos para ações específicas da IA.

1.  **Arquivo-Alvo:** `webhook_service.py`

2.  **Função a Modificar:** `extract_whatsapp_message`

3.  **Instrução:** Garanta que a extração de mensagens interativas (`'type': 'interactive'`) está robusta e que a resposta de um botão seja traduzida em um texto claro que o agente no `agent_orchestrator.py` possa entender e processar.

    ```python
    # Em webhook_service.py na função extract_whatsapp_message

    # ... (código existente) ...
    elif message_type == 'interactive':
        button_reply = message.get('interactive', {}).get('button_reply', {})
        button_title = button_reply.get('title', 'Botão clicado')
        # Transforma o clique do botão em uma mensagem de texto compreensível
        message_text = f"O usuário clicou no botão: '{button_title}'"
    # ... (código existente) ...
    ```

4.  **Arquivo-Alvo:** `scripts/agent_orchestrator.py`

5.  **Função a Modificar:** `handle_agent_invocation`

6.  **Instrução:** Adapte a lógica para tratar a mensagem gerada pelo clique no botão, direcionando a IA para a ação correta (como consultar os dados do lead).

    ```python
    # Em scripts/agent_orchestrator.py na função handle_agent_invocation

    def handle_agent_invocation(phone_number: str, user_message: str, image_url: str | None = None):
        # ... (lógica de logging) ...
        
        # Lógica aprimorada para detectar a intenção do botão
        if "ativar perfil" in user_message.lower():
            logger.info(f"🔘 Detectado clique no botão 'Ativar Perfil': {user_message}")
            input_data = f"O usuário {phone_number} acaba de iniciar a conversa clicando em 'Ativar Perfil'. Comece a interação: use a ferramenta 'consultar_dados_lead' para obter seus dados e saudá-lo pelo nome."
        elif "botão:" in user_message.lower():
            logger.info(f"🔘 Detectada interação com botão genérico: {user_message}")
            input_data = f"O usuário {phone_number} respondeu clicando em um botão. A resposta foi: '{user_message}'. Continue a conversa a partir daí."
        # ... (resto da lógica com image_url e texto normal) ...
    ```

-----

Concluir estes passos irá alinhar a performance técnica do seu sistema com a estratégia de negócio, criando uma experiência de qualificação de leads fluida, humana e eficiente.