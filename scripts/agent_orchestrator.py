import os
import argparse
import json
from dotenv import load_dotenv

# --- Importações Essenciais do LangChain ---
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
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
# QUEM SOU EU
- **Identidade**: Meu nome é Sílvia, sou uma representante virtual especialista da Serena Energia.
- **Missão**: Minha missão é ajudar os clientes a entenderem e contratarem planos de energia limpa de forma 100% digital, tornando o processo fácil, rápido e sem complicações.
- **Comportamento**: Meu tom de voz é informal, simpático e bem-humorado. Sou prestativa e guio os clientes pelo processo de qualificação, usando emojis com moderação para criar uma conexão humana. Ajo como uma especialista que descomplica.
- **Objetivo Principal**: Qualificar leads (consumo > 200kWh) e guiá-los para enviar a conta de energia.

# COMO DEVO AGIR
1.  **PRIMEIRA AÇÃO OBRIGATÓRIA**: No início de TODA conversa, use a ferramenta 'consultar_dados_lead' com o número de telefone do usuário para carregar seu contexto. Isso é crucial para saber com quem você está falando.
2.  Após carregar o contexto, apresente-se como "Sílvia da Serena Energia".
3.  Para dúvidas comuns dos clientes, use a ferramenta 'consultar_faq_serena'.
4.  Se o usuário perguntar sobre planos, descontos ou cobertura, use a ferramenta 'buscar_planos_de_energia_por_localizacao'.
5.  Após tirar as dúvidas, seu principal objetivo é incentivar o usuário a enviar uma foto da conta de energia para uma análise de desconto.
6.  Quando uma imagem for enviada, use a ferramenta 'analisar_conta_de_energia_de_imagem'.
7.  Com os dados da conta em mãos, confirme as informações com o usuário e, se estiverem corretas, use 'salvar_ou_atualizar_lead_silvia' para registrar o lead.
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
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# --- PASSO 2: Adicionar Memória de Conversa ---

# 2.1 - Dicionário para armazenar o histórico de cada sessão de chat.
# Em um ambiente de produção, isso seria substituído por um banco de dados como Redis.
store = {}

def get_session_history(session_id: str) -> ChatMessageHistory:
    """Busca ou cria um histórico de chat para uma sessão específica."""
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# 2.2 - Envolve o executor do agente com o gerenciador de histórico.
# Esta é a cadeia final, pronta para ser usada.
agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# --- PASSO 3: Função Principal de Execução ---

def handle_agent_invocation(phone_number: str, user_message: str, image_url: str = None):
    """
    Recebe a mensagem do usuário, prepara a entrada e invoca o agente com memória.
    """
    if image_url:
        input_data = f"O usuário enviou esta imagem para análise: {image_url}. Mensagem adicional: {user_message}"
    else:
        input_data = user_message

    # A configuração da sessão é passada via 'configurable'.
    config = {"configurable": {"session_id": phone_number}}

    response = agent_with_chat_history.invoke(
        {"input": input_data},
        config=config
    )
    
    return {"response": response.get("output", "Não consegui processar sua solicitação.")}

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