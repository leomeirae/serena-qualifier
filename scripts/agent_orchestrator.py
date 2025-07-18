import os
import argparse
import json
from dotenv import load_dotenv

# --- Importações Essenciais do LangChain ---
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# --- Importar Ferramentas Específicas do Agente ---
from scripts.agent_tools.knowledge_base_tool import consultar_faq_serena
from scripts.agent_tools.serena_tools import (
    buscar_planos_de_energia_por_localizacao,
    analisar_conta_de_energia_de_imagem,
)
from scripts.agent_tools.supabase_agent_tools import salvar_ou_atualizar_lead_silvia, consultar_dados_lead

# Carregar variáveis de ambiente (ex: OPENAI_API_KEY)
load_dotenv()

# --- PASSO 1: Montagem do Agente "Sílvia" ---

# 1.1 - Lista de ferramentas que o agente poderá usar.
tools = [
    consultar_dados_lead,
    consultar_faq_serena,
    buscar_planos_de_energia_por_localizacao,
    analisar_conta_de_energia_de_imagem,
    salvar_ou_atualizar_lead_silvia
]

# 1.2 - O "cérebro" do agente: o modelo de linguagem.
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 1.3 - O prompt do agente, definindo a persona e as entradas.
# O conteúdo do FAQ_INTERNO_TRAINING.md é inserido aqui.
system_prompt = """
# Persona

Você é a Sílvia, uma especialista em energia da Serena. Sua comunicação é clara, amigável e proativa.

# Regras de Raciocínio

1.  **PRIMEIRA INTERAÇÃO**: Se o histórico da conversa (chat_history) estiver vazio, apresente-se brevemente.
2.  **CONSULTAR LEAD**: No início de CADA NOVA CONVERSA (quando o histórico estiver vazio ou contiver apenas a primeira mensagem), use a ferramenta `consultar_dados_lead` para identificar o usuário. Não use esta ferramenta novamente a menos que o usuário peça para atualizar seus dados.
3.  **BUSCAR PLANOS**: Use a ferramenta `buscar_planos_de_energia_por_localizacao` APENAS UMA VEZ por conversa, depois de ter confirmado a cidade e o estado do usuário. Não a utilize novamente, a menos que o usuário pergunte sobre planos para uma NOVA localização.
4.  **USO DO FAQ**: Para perguntas gerais sobre a Serena, energia solar ou o processo (ex: 'o que é?', 'como funciona?', 'é seguro?'), use a ferramenta `consultar_faq_serena`.
5.  **EFICIÊNCIA**: Não execute ferramentas cujas informações você já possui no histórico da conversa. Responda diretamente com base no que já foi discutido. Evite saudações repetitivas se a conversa já estiver em andamento.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# 1.4 - Cria o agente, unindo o LLM, o prompt e as ferramentas.
agent = create_openai_tools_agent(llm, tools, prompt)

# 1.5 - Cria o executor do agente.
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=10
)


# --- PASSO 2: Adicionar Memória de Conversa (com Persistência no Redis) ---

# 2.1 - Obtenha a URL do Redis das variáveis de ambiente.
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# 2.2 - Função que agora usa o Redis para buscar ou criar o histórico.
def get_session_history(session_id: str) -> RedisChatMessageHistory:
    """
    Recupera o histórico da conversa do Redis. Cada sessão (número de telefone)
    terá sua própria chave no Redis.
    """
    return RedisChatMessageHistory(session_id, url=REDIS_URL)

# 2.3 - Envolve o executor do agente com o gerenciador de histórico.
# Esta é a cadeia final, pronta para ser usada.
agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# --- PASSO 3: Função Principal de Execução ---

def handle_agent_invocation(phone_number: str, user_message: str, image_url: str | None = None):
    """
    Recebe a mensagem do usuário, prepara a entrada e invoca o agente com memória.
    """
    if image_url:
        input_data = f"Número de telefone do usuário: {phone_number}. O usuário enviou esta imagem para análise: {image_url}. Mensagem adicional: {user_message}"
    else:
        input_data = f"Número de telefone do usuário: {phone_number}. Mensagem: {user_message}"

    # A configuração da sessão é passada via 'configurable'.
    config = {"configurable": {"session_id": phone_number}}

    response = agent_with_chat_history.invoke(
        {"input": input_data},
        config=config
    )
    
    output = response.get("output")
    if output is None:
        output = "Não consegui processar sua solicitação."
    
    return {"response": output}

# --- PASSO 4: Ponto de Entrada para o Script (para testes) ---

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Orquestrador do Agente Sílvia.')
    parser.add_argument('--phone_number', type=str, required=True, help='Número de telefone do usuário (ID da sessão).')
    parser.add_argument('--message', type=str, required=True, help='Mensagem do usuário.')
    parser.add_argument('--image_url', type=str, help='URL da imagem (opcional).')
    
    args = parser.parse_args()

    # Executa a lógica do agente
    result = handle_agent_invocation(args.phone_number, args.message, args.image_url)
    
    # Imprime o resultado final em formato JSON para ser consumido pelo Kestra
    print(json.dumps(result)) 