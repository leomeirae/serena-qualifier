# AI\_UPGRADE\_GUIDE.md

## Guia Completo de Evolução Incremental do Serena Qualifier

Este documento orienta claramente o agente de codificação (Cursor AI, ChatGPT) a realizar melhorias técnicas sem reescrever ou sobrescrever o código existente, garantindo segurança, integridade e continuidade operacional.

---

## 1. Diretrizes Fundamentais

- **Nunca sobrescreva funções existentes.**
- **Faça alterações incrementais e crie funções auxiliares.**
- **Adicione comentários detalhados em português (PT-BR).**
- **Teste exaustivamente cada alteração em ambiente de staging antes de produção.**
- **Registre todas as alterações no changelog ao final deste documento.**

---

## 2. Problemas e Soluções Propostas

### 2.1 OCR Automático (Extração Dados Conta Energia)

#### Instalar Dependências:

```bash
pip install openai supabase
```

#### Criar função incremental:

Crie arquivo novo: `scripts/energy_bill_processor.py`

```python
import openai
from supabase import create_client

# Função incremental para OCR com OpenAI Vision API
def process_energy_bill_image(image_path, lead_phone):
    openai.api_key = "SUA_OPENAI_API_KEY"
    supabase_url = "SUA_SUPABASE_URL"
    supabase_key = "SUA_SUPABASE_KEY"
    supabase = create_client(supabase_url, supabase_key)

    with open(image_path, "rb") as img:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": img.read()}]
        )
        extracted_data = response['choices'][0]['message']['content']

    # Salvar dados no Supabase
    supabase.table("energy_bills").insert({
        "phone": lead_phone,
        "image_path": image_path,
        "extracted_data": extracted_data
    }).execute()

    # Comente claramente a implementação
    # Função criada incrementalmente JUL/2025
```

---

### 2.2 Follow-up Automático (Lembrete 2h)

#### Criar função incremental:

Novo arquivo: `scripts/followup.py`

```python
import threading, time
from datetime import datetime, timedelta
from scripts.whatsapp_sender import send_whatsapp_message

# Função incremental para agendar follow-up
def schedule_followup(phone, delay_seconds=7200):
    def reminder():
        time.sleep(delay_seconds)
        if not check_bill_received(phone):
            send_whatsapp_message(phone, "Oi! Ainda não recebi sua conta de luz. Pode me enviar agora? 😊")
    threading.Thread(target=reminder).start()

# Checagem incremental, não substitui lógica original
def check_bill_received(phone):
    # consultar Supabase se a conta já foi enviada
    return False  # Implemente corretamente!

# Função incremental JUL/2025
```

---

### 2.3 Memória Conversacional (Langchain Memory)

#### Dependências:

```bash
pip install langchain redis
```

#### Novo módulo incremental:

`scripts/conversational_memory.py`

```python
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory

# Função incremental para gerenciar memória
def get_memory(phone):
    redis_url = "redis://localhost:6379"
    memory = ConversationBufferMemory(
        chat_memory=RedisChatMessageHistory(session_id=phone, url=redis_url),
        return_messages=True
    )
    return memory

# Função para salvar contexto incrementalmente
def save_context(memory, user_input, ai_response):
    memory.save_context({"input": user_input}, {"output": ai_response})

# Comentado e implementado incrementalmente JUL/2025
```

---

### 2.4 Logging e Feedback

#### Estrutura de logging incremental:

`scripts/interaction_logger.py`

```python
import logging

logging.basicConfig(
    filename="interaction.log",
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

def log_interaction(phone, interaction_type, message):
    logging.info(f"{phone} | {interaction_type} | {message}")

# Função incremental de JUL/2025
```

#### Feedback ao final do fluxo:

```python
from scripts.whatsapp_sender import send_whatsapp_message
from scripts.supabase_agent_tools import salvar_feedback

# Função incremental para solicitar feedback
def request_feedback(phone):
    mensagem = "Fui útil pra você? Quer falar com nosso consultor? 😊"
    send_whatsapp_message(phone, mensagem)

# Incremental, sem substituir JUL/2025
```

---

## 3. Templates para Mensagens

- **Inicial:**

> "Oi, {nome}! Vi que você está em {cidade}. Pode me enviar sua conta de luz agora?"

- **Follow-up:**

> "Oi! Ainda não recebi sua conta de luz. Pode me enviar agora? 😊"

- **Feedback:**

> "Fui útil pra você? Quer falar com nosso consultor? 😊"

---

## 4. Critérios Técnicos e Testes

- Todas funções devem ser testadas em ambiente staging.
- Nenhuma funcionalidade antiga pode ser impactada.
- Logging claro e disponível.
- Persistência da memória em Redis verificada.
- OCR com extração correta validado.

---

## 5. Changelog

- `[JUL/2025] Implementado OCR via OpenAI Vision.`
- `[JUL/2025] Agendado follow-up automático após 2 horas.`
- `[JUL/2025] Adicionado Langchain Memory com Redis.`
- `[JUL/2025] Logging estruturado de interações.`
- `[JUL/2025] Coleta estruturada de feedback do lead.`

---

## 6. Orientações Finais para IA

- Seja incremental.
- Não reescreva códigos existentes.
- Documente e comente claramente cada passo.
- Mantenha sempre compatibilidade com o que já funciona.

---

