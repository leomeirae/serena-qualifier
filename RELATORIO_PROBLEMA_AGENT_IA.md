````markdown
# Roteiro para Correção do Fluxo WhatsApp + Kestra + Agente IA

## Objetivo
Corrigir o fluxo para garantir que apenas **mensagens de texto reais dos usuários** sejam processadas pelo agente de IA, evitando que eventos de status (como "read", "delivered" ou "button") disparem o pipeline e causem respostas erradas.

---

## 1. Diagnóstico Resumido

- O webhook está recebendo **vários tipos de eventos do WhatsApp**, não apenas mensagens de texto.
- O agente de IA está recebendo eventos como `"Mensagem do tipo button recebida"` em vez do texto real enviado pelo usuário.
- O pipeline processa eventos irrelevantes e responde de forma inadequada.

---

## 2. **Tarefas para o Agente de Codificação**

### 2.1. **Analisar e Identificar a Origem do Problema**

- [ ] Localizar o ponto no código (ex: `webhook_service.py`) onde os webhooks recebidos do WhatsApp são tratados.
- [ ] Verificar como os eventos são classificados e encaminhados ao Kestra.

---

### 2.2. **Filtrar Apenas Mensagens de Texto**

- [ ] Implementar um filtro para que apenas eventos contendo mensagens de texto (`type: "text"`) sejam considerados válidos para processamento pelo Kestra.
- [ ] Ignorar eventos de tipo "status", "button", "image", etc.

#### Exemplo (pseudo-código):

```python
if "messages" in payload and payload["messages"]:
    for msg in payload["messages"]:
        if msg.get("type") == "text" and "body" in msg["text"]:
            # Encaminhar para Kestra
        else:
            # Ignorar ou apenas logar o evento
else:
    # Ignorar eventos sem mensagem relevante
````

---

### 2.3. **Ajustar o Payload Enviado ao Kestra**

* [ ] Certificar que o JSON enviado ao trigger do Kestra contenha:

  * O texto da mensagem real do usuário
  * O número do telefone
  * Qualquer dado adicional relevante

---

### 2.4. **Aprimorar Logs e Observabilidade**

* [ ] Adicionar logs detalhados mostrando:

  * Todos os eventos recebidos
  * Quais eventos foram processados
  * Quais eventos foram ignorados

---

### 2.5. **Testar Comportamento**

* [ ] Realizar testes enviando:

  * Mensagem de texto (deve ser processada normalmente)
  * Evento de botão/status (deve ser ignorado)
* [ ] Validar nos logs e no workflow que só mensagens de texto chegam ao Kestra.

---

### 2.6. **Documentar Solução**

* [ ] Comentar no código e/ou criar um README curto explicando a lógica do filtro e o motivo da implementação.

---

## 3. **Checklist para o Pull Request**

* [ ] O agente de IA só é acionado para mensagens de texto reais.
* [ ] Logs claros para auditoria e debug.
* [ ] Documentação breve no código.

---

## 4. **Dicas de Código e Fontes**

* [Meta WhatsApp Webhooks Payloads](https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples/)
* [Exemplo oficial de webhook de texto](https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples/#when-a-user-sends-a-text-message)

---

## 5. **Resumo**

> O foco é garantir que **apenas mensagens relevantes do usuário sejam processadas pelo agente de IA**, eliminando o ruído dos eventos do WhatsApp e tornando o atendimento mais inteligente e eficiente.

```
Se quiser, posso gerar o template de código Python adaptado para sua stack atual!
```
