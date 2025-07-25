from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory

# Função incremental para gerenciar memória conversacional
# Criada JUL/2025 conforme AI_UPGRADE_GUIDE.md

def get_memory(phone: str):
    """
    Retorna objeto de memória conversacional para o lead usando Redis.
    Parâmetros:
        phone (str): Telefone do lead (usado como session_id).
    Retorna:
        ConversationBufferMemory: Objeto de memória da conversa.
    """
    redis_url = "redis://localhost:6379"
    memory = ConversationBufferMemory(
        chat_memory=RedisChatMessageHistory(session_id=phone, url=redis_url),
        return_messages=True
    )
    return memory

# Função incremental para salvar contexto da conversa

def save_context(memory, user_input: str, ai_response: str) -> None:
    """
    Salva o contexto da interação na memória conversacional.
    Parâmetros:
        memory: Objeto de memória conversacional.
        user_input (str): Mensagem do usuário.
        ai_response (str): Resposta da IA.
    """
    memory.save_context({"input": user_input}, {"output": ai_response})

# Comentado e implementado incrementalmente JUL/2025 