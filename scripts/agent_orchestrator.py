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

7.  **Priorize a Conversa**: A informação confirmada pelo usuário durante o diálogo (como a cidade) é a *fonte da verdade*. Use os dados da ferramenta `consultar_dados_lead` para iniciar ou enriquecer a conversa, mas se o usuário confirmar algo diferente, a confirmação dele prevalece.
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