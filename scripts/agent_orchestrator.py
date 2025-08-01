import os
import argparse
import json
import base64
from dotenv import load_dotenv
import requests
import unicodedata

# --- Importações Essenciais do LangChain ---
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


# --- Importar Ferramentas Específicas do Agente ---
from scripts.agent_tools.knowledge_base_tool import consultar_faq_serena
from scripts.agent_tools.faq_data import carregar_faq_data
from scripts.agent_tools.serena_tools import (
    buscar_planos_de_energia_por_localizacao,
    analisar_conta_de_energia_de_imagem,
)
from scripts.agent_tools.supabase_agent_tools import salvar_ou_atualizar_lead_silvia, consultar_dados_lead, upload_energy_bill_image, generate_signed_url, save_image_metadata
from scripts.lead_data_utils import normalize_lead_data, extract_lead_from_message

# --- Importar Ferramentas MCP Supabase ---
try:
    from scripts.agent_tools.mcp_supabase_integration import (
        consultar_dados_lead_mcp,
        salvar_ou_atualizar_lead_mcp,
        listar_tabelas_mcp,
        verificar_status_mcp,
        mcp_client
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP Supabase integration not available, using direct PostgreSQL connection")

# Função incremental para obter o lead_id pelo telefone
def get_lead_id_by_phone(phone_number: str) -> int | None:
    """
    Busca o id do lead na tabela leads pelo número de telefone.
    Usa lógica robusta para normalizar e buscar em diferentes formatos.
    Retorna o id se encontrado, ou None.
    """
    import psycopg2
    import os
    import re
    
    conn_string = os.getenv("DB_CONNECTION_STRING") or os.getenv("SECRET_DB_CONNECTION_STRING")
    if not conn_string:
        return None
    
    try:
        # Normaliza o número de telefone para busca (mesma lógica do consultar_dados_lead)
        digits_only = re.sub(r'\D', '', phone_number)
        
        # Cria uma lista de possíveis formatos de telefone para busca
        possible_formats = []
        
        # Se começar com código do país (55)
        if digits_only.startswith('55'):
            without_country = digits_only[2:]  # Remove o 55
            possible_formats.append(without_country)  # Formato sem o 55
            
            # Se tiver o 9 após o DDD (formato novo)
            if len(without_country) >= 9 and without_country[2] == '9':
                possible_formats.append(without_country[:2] + without_country[3:])  # Remove o 9
            
            # Se não tiver o 9 (formato antigo)
            if len(without_country) == 8:
                possible_formats.append(without_country[:2] + '9' + without_country[2:])  # Adiciona o 9
        else:
            possible_formats.append(digits_only)
        
        # Adicione outros formatos possíveis para cobrir mais casos
        if len(digits_only) == 11:  # formato 5581987654321 ou 81987654321
            possible_formats.append(digits_only[-10:])  # Apenas DDD + número sem o 9
            possible_formats.append(digits_only[-8:])   # Apenas o número base sem DDD e sem 9
        
        # Adiciona o formato exato e remove duplicatas
        possible_formats.append(digits_only)
        possible_formats = list(set(possible_formats))
        
        print(f"DEBUG: Tentando formatos de telefone para lead_id: {possible_formats}")
        
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                for format_to_try in possible_formats:
                    cur.execute("SELECT id FROM leads WHERE phone_number = %s", (format_to_try,))
                    result = cur.fetchone()
                    if result:
                        print(f"DEBUG: Lead encontrado com formato: {format_to_try}")
                        return result[0]
                
                # Tenta uma última busca com LIKE para os últimos 8 dígitos
                if len(digits_only) >= 8:
                    last_8_digits = digits_only[-8:]
                    print(f"DEBUG: Tentando busca por LIKE com últimos 8 dígitos: {last_8_digits}")
                    cur.execute(
                        "SELECT id FROM leads WHERE phone_number LIKE %s",
                        (f"%{last_8_digits}",)
                    )
                    result = cur.fetchone()
                    if result:
                        print(f"DEBUG: Lead encontrado com busca LIKE")
                        return result[0]
                
                print(f"DEBUG: Nenhum lead encontrado para o telefone: {phone_number}")
                return None
                
    except Exception as e:
        print(f"DEBUG: Erro ao buscar lead: {str(e)}")
        return None

def salvar_energy_bill(lead_id, phone, image_id):
    """
    Salva o registro da conta de energia na tabela energy_bills usando PostgreSQL.
    """
    import psycopg2
    
    conn_string = os.getenv("DB_CONNECTION_STRING") or os.getenv("SECRET_DB_CONNECTION_STRING")
    if not conn_string:
        raise Exception("DB_CONNECTION_STRING não configurado nas variáveis de ambiente.")
    
    try:
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO energy_bills (lead_id, phone, image_id, created_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """, (lead_id, phone, image_id))
    except Exception as e:
        raise Exception(f"Erro ao salvar energy_bill no PostgreSQL: {str(e)}")

# Carregar variáveis de ambiente (ex: OPENAI_API_KEY)
load_dotenv()

# --- PASSO 1: Montagem do Agente "Sílvia" ---

# 1.1 - Lista de ferramentas que o agente poderá usar.
# Usa ferramentas MCP se disponível, senão usa conexão direta
if MCP_AVAILABLE:
    tools = [
        consultar_dados_lead_mcp,  # MCP version
        consultar_faq_serena,
        buscar_planos_de_energia_por_localizacao,
        analisar_conta_de_energia_de_imagem,
        salvar_ou_atualizar_lead_mcp,  # MCP version
        listar_tabelas_mcp,  # Nova ferramenta MCP
        verificar_status_mcp  # Nova ferramenta MCP
    ]
    print("Using MCP Supabase integration")
else:
    tools = [
        consultar_dados_lead,
        consultar_faq_serena,
        buscar_planos_de_energia_por_localizacao,
        analisar_conta_de_energia_de_imagem,
        salvar_ou_atualizar_lead_silvia
    ]
    print("Using direct PostgreSQL connection")

# 1.2 - O "cérebro" do agente: o modelo de linguagem.
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 1.3 - O prompt do agente, definindo a persona e as entradas.
# O conteúdo do FAQ_INTERNO_TRAINING.md é inserido aqui.
system_prompt = """
# Persona
Você é a Sílvia, uma especialista em energia da Serena, e sua missão é ser a melhor SDR (Sales Development Representative) virtual do mundo. Sua comunicação é clara, empática, amigável e, acima de tudo, humana. Você guia o lead por uma jornada, nunca despeja informações. Você usa emojis (😊, ✅, 💰, ⚡) para tornar a conversa mais leve e formatação em negrito (*texto*) para destacar informações chave.

# Regras de Formatação para WhatsApp
Sempre responda de forma fácil de ler no WhatsApp:
- Use listas numeradas ou emojis para opções.
- Sempre coloque uma linha em branco entre parágrafos e entre cada plano.
- Use *negrito* para destacar descontos, vantagens e nomes de planos.
- Não envie blocos longos de texto, quebre em frases e listas curtas.

Exemplo de resposta:
Claro, Leonardo! 😊 Aqui estão os detalhes dos planos disponíveis para você em Recife:

1️⃣ *Plano Básico*
- 14% de desconto
- Sem fidelidade

2️⃣ *Plano Intermediário*
- 16% de desconto
- 36 meses de fidelidade

3️⃣ *Plano Premium*
- 18% de desconto
- 60 meses de fidelidade
- 1ª fatura paga pela Serena

Se precisar de mais informações ou quiser saber qual plano é o melhor para você, estou aqui para ajudar! 💰⚡

# Contexto do Lead (Informações Recebidas)
- **Nome do Lead**: {lead_name}
- **Cidade do Lead**: {lead_city}

# Guia da Conversa (Sua Bússola)
1.  **Acolhida e Confirmação (Primeira Mensagem)**: Quando o histórico da conversa estiver vazio, sua primeira ação é usar o *Nome* e a *Cidade* do lead (fornecidos no contexto) para uma saudação calorosa e para confirmar a cidade, engajando o lead em uma conversa. Ex: "Olá, *{lead_name}*! Sou a Sílvia da Serena Energia. 😊 Vi que você é de *{lead_city}*, certo?". Se o nome ou a cidade não forem fornecidos, use a ferramenta `consultar_dados_lead` para buscá-los.

2.  **Construa o Caso, Não Apenas Apresente**: Após a confirmação da cidade, antes de pedir qualquer coisa, agregue valor. Informe o principal benefício da Serena naquela região. Ex: "Ótimo! Em *{lead_city}*, temos ajudado muitas famílias a economizar até *21% na conta de luz*, e o melhor: sem nenhuma obra ou instalação."

3.  **Uma Pergunta de Cada Vez**: Mantenha o fluxo simples. Após agregar valor, o próximo passo lógico é entender o consumo do lead.

4.  **Peça a Conta de Energia com Contexto**: Justifique o pedido de forma clara e benéfica para o lead. Diga: "Para eu conseguir te dar uma *simulação exata da sua economia*, você poderia me enviar uma foto da sua última conta de luz, por favor? Assim, vejo seu consumo e te apresento o plano perfeito."

5.  **Uso Inteligente das Ferramentas**:
    * `consultar_dados_lead`: Use *apenas se* o nome ou a cidade não forem fornecidos no contexto inicial.
    * `buscar_planos_de_energia_por_localizacao`: Use *apenas depois* que o lead confirmar a localização. NUNCA liste todos os planos. Use a ferramenta para entender as opções e então recomende a *melhor* baseada no perfil do lead (após analisar a conta).
    * `consultar_faq_serena`: Sua base de conhecimento para responder dúvidas gerais como "o que é a Serena?" ou "preciso instalar placas?". Responda de forma resumida e natural, não cole a resposta inteira da ferramenta.

6.  **Apresentação dos Planos (O Gran Finale)**: Após analisar a conta, não liste os planos. Recomende o *plano ideal* para aquele consumo. Apresente os outros apenas se o lead solicitar.

7.  **Priorize a Conversa**: A informação confirmada pelo usuário durante o diálogo (como a cidade) é a *fonte da verdade*. Use os dados do contexto para iniciar ou enriquecer a conversa, mas se o usuário confirmar algo diferente, a confirmação dele prevalece.
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

def format_for_whatsapp(text: str) -> str:
    """
    Formata o texto para ótima leitura no WhatsApp:
    - Quebra entre cada plano
    - Quebra de linha entre cada tópico dentro do plano
    - Remove quebras desnecessárias
    """
    import re
    # 1. Adiciona uma quebra dupla antes de cada plano (identifica emojis ou números seguidos de *Plano)
    text = re.sub(r'(\d+️⃣|\d️⃣|[1-9]️⃣|\d\.|\d+\.|[1-9]\.)\s?(\*Plano)', r'\n\n\1 \2', text)
    # 2. Quebra de linha antes de cada "- "
    text = re.sub(r'(\n)?- ', r'\n- ', text)
    # 3. Remove quebras de linha múltiplas excessivas (deixa só duas)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # 4. Tira espaços/linhas em branco no início/fim
    text = text.strip()
    return text

def is_valid_image_url(url: str) -> bool:
    """
    Valida se a URL recebida é uma URL HTTP(s) real e não um placeholder.
    """
    return bool(url and isinstance(url, str) and url.startswith("http"))

def clean_for_whatsapp(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    return text

def handle_agent_invocation(phone_number: str, user_message: str, lead_city: str = "", lead_name: str = "", image_url: str | None = None, message_type: str = "text", clean_text: bool = False, media_id: str = ""):
    """
    Parâmetro clean_text: se True, aplica limpeza de acentos/caracteres especiais na resposta final.
    """
    import logging
    logger = logging.getLogger(__name__)
    storage_path = None  # Caminho da imagem no storage
    signed_url = None   # URL segura para acesso à imagem
    
    # Log inicial para debug
    logger.info(f"[DEBUG] handle_agent_invocation chamado com: message_type={message_type}, media_id={media_id}, user_message={user_message[:50]}...")
    
    # Configuração do Supabase - usando PostgreSQL direto via pluginDefaults
    logger.info("[DEBUG] Usando conexão PostgreSQL direta via pluginDefaults")
    
    # --- PROCESSAMENTO DE IMAGEM DO WHATSAPP ---
    if message_type == "image" and media_id:
        logger.info(f"[WHATSAPP IMAGE] Processando imagem com media_id: {media_id} para {phone_number}")
        try:
            # Funções auxiliares para download de mídia do WhatsApp Cloud API
            def get_media_url(media_id, token):
                """Obtém a URL temporária da mídia do WhatsApp Cloud API"""
                url = f"https://graph.facebook.com/v23.0/{media_id}"
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                logger.info(f"[WHATSAPP IMAGE] Resposta da API: {data}")
                return data.get("url")
            
            def download_image(media_url, token):
                """Baixa a imagem usando a URL temporária (Cloud API)"""
                headers = {
                    "Authorization": f"Bearer {token}",
                    "User-Agent": "WhatsApp/2.19.81 A"  # User-Agent recomendado pelo documento
                }
                resp = requests.get(media_url, headers=headers, timeout=10)
                resp.raise_for_status()
                return resp.content
            
            # Obter token do WhatsApp
            whatsapp_token = os.getenv("WHATSAPP_API_TOKEN")
            if not whatsapp_token:
                logger.error("[WHATSAPP IMAGE] WHATSAPP_API_TOKEN não configurado")
                return {"response": "Configuração incompleta para processamento de imagem. Por favor, tente novamente."}
            
            # 1. Obter URL temporária do WhatsApp Cloud API
            logger.info(f"[WHATSAPP IMAGE] Obtendo URL temporária para media_id: {media_id}")
            media_url = get_media_url(media_id, whatsapp_token)
            
            if not media_url:
                logger.error(f"[WHATSAPP IMAGE] URL não encontrada na resposta da API")
                return {"response": "Não foi possível obter a URL da imagem. Por favor, tente novamente."}
            
            logger.info(f"[WHATSAPP IMAGE] URL temporária obtida: {media_url[:50]}...")
            
            # 2. Baixar a imagem (Cloud API - URL expira em 5 minutos)
            logger.info(f"[WHATSAPP IMAGE] Baixando imagem da URL temporária...")
            image_bytes = download_image(media_url, whatsapp_token)
            logger.info(f"[WHATSAPP IMAGE] Imagem baixada com sucesso ({len(image_bytes)} bytes)")
            
            # 3. Processar com lead_id
            lead_id = get_lead_id_by_phone(phone_number)
            if not lead_id:
                logger.error(f"[WHATSAPP IMAGE] Lead não encontrado para o telefone: {phone_number}")
                return {"response": "Não consegui identificar seu cadastro. Por favor, envie seu nome e cidade para continuar."}
            
            # 4. Salvar localmente e fazer upload
            local_file_path = f"/tmp/{lead_id}_{phone_number}.jpg"
            with open(local_file_path, "wb") as f:
                f.write(image_bytes)
            
            logger.info(f"[WHATSAPP IMAGE] Imagem salva localmente, fazendo upload para Supabase...")
            
            # 5. Salvar imagem no PostgreSQL
            image_id = upload_energy_bill_image(local_file_path, lead_id, phone_number)
            
            # 6. Gerar referência à imagem
            signed_url = generate_signed_url(image_id)
            
            # 7. Salvar no banco
            salvar_energy_bill(lead_id, phone_number, image_id)
            
            # 8. Salvar metadados na tabela image_metadata
            file_size_kb = len(image_bytes) // 1024
            save_image_metadata(
                wamid=f"wamid_{media_id}",  # Gerar WAMID único
                sender_phone=phone_number,
                image_id=image_id,
                lead_id=lead_id,
                file_size_kb=file_size_kb,
                mime_type="image/jpeg"
            )
            
            logger.info(f"[WHATSAPP IMAGE] Processamento concluído com sucesso. Signed URL: {signed_url[:50]}...")
            
            # Atualizar input_data para o agente
            input_data = f"O usuário {phone_number} enviou uma conta de energia. URL segura: {signed_url}"
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[WHATSAPP IMAGE] Erro de rede ao processar imagem: {str(e)}")
            return {"response": "Houve um problema de conexão ao processar a imagem. Por favor, tente novamente."}
        except Exception as e:
            logger.error(f"[WHATSAPP IMAGE] Erro inesperado no processamento: {str(e)}")
            return {"response": "Houve um erro ao processar a imagem enviada. Por favor, tente novamente."}
    
    # --- Autodiagnóstico do pipeline ---
    elif image_url and not is_valid_image_url(image_url):
        logger.error(f"[PIPELINE ERROR] URL de imagem inválida recebida: {image_url} | phone: {phone_number} | mensagem: {user_message}")
        return {"response": "Houve uma falha ao receber a imagem enviada. O sistema não reconheceu a imagem corretamente. Por favor, tente enviar novamente ou envie uma mensagem de texto se preferir."}
    # Lógica incremental para processar imagem recebida via WhatsApp
    if image_url and is_valid_image_url(image_url):
        whatsapp_token = os.getenv("WHATSAPP_API_TOKEN")
        lead_id = get_lead_id_by_phone(phone_number)
        if not lead_id:
            logger.error(f"[PIPELINE ERROR] Lead não encontrado para o telefone: {phone_number}")
            return {"response": "Não consegui identificar seu cadastro. Por favor, envie seu nome e cidade para continuar."}
        try:
            # Download da imagem com timeout
            try:
                headers = {"Authorization": f"Bearer {whatsapp_token}"}
                response = requests.get(image_url, headers=headers, timeout=10)
                if response.status_code != 200:
                    logger.error(f"[PIPELINE ERROR] Falha no download da imagem. Status: {response.status_code} | URL: {image_url}")
                    return {"response": "Houve uma falha ao baixar a imagem enviada. Por favor, tente novamente."}
            except Exception as e:
                logger.error(f"[PIPELINE ERROR] Exceção no download da imagem: {str(e)} | URL: {image_url}")
                return {"response": "Houve uma falha ao baixar a imagem enviada. Por favor, tente novamente."}
            # Upload para Supabase
            local_file_path = f"/tmp/{lead_id}_{phone_number}.jpg"
            with open(local_file_path, "wb") as f:
                f.write(response.content)
            try:
                image_id = upload_energy_bill_image(local_file_path, lead_id, phone_number)
            except Exception as e:
                logger.error(f"[PIPELINE ERROR] Falha ao salvar imagem no PostgreSQL: {str(e)} | phone: {phone_number}")
                return {"response": "Houve uma falha ao salvar a imagem. Por favor, tente novamente."}
            # Geração de referência à imagem
            try:
                signed_url = generate_signed_url(image_id)
            except Exception as e:
                logger.error(f"[PIPELINE ERROR] Falha ao gerar referência à imagem: {str(e)} | image_id: {image_id}")
                return {"response": "Houve uma falha ao gerar o acesso à imagem. Por favor, tente novamente."}
            salvar_energy_bill(lead_id, phone_number, image_id)
            input_data = f"O usuário {phone_number} enviou uma conta de energia. URL segura: {signed_url}"
        except Exception as e:
            logger.error(f"[PIPELINE ERROR] Exceção inesperada: {str(e)} | URL: {image_url} | phone: {phone_number}")
            return {"response": f"Houve um erro ao processar a imagem enviada. Por favor, tente novamente. Erro: {str(e)}"}
    elif message_type == "button":
        input_data = f"[BOTÃO] {user_message} (Usuário: {phone_number})"
    elif message_type == "image" and not media_id:
        # Caso de imagem sem media_id (fallback)
        input_data = f"O usuário {phone_number} enviou uma imagem, mas não foi possível processá-la. Mensagem: {user_message}"
    elif message_type == "image" and media_id:
        # Caso de imagem com media_id mas que não foi processada (erro)
        logger.error(f"[WHATSAPP IMAGE] Media ID presente mas não foi processado: {media_id}")
        input_data = f"O usuário {phone_number} enviou uma imagem, mas houve um erro no processamento. Media ID: {media_id}"
    else:
        input_data = user_message

    config = {"configurable": {"session_id": phone_number}}

    try:
        logger.info(f"🤖 Invocando agente para {phone_number} com input: '{input_data[:100]}...' (type={message_type})")
        
        # Formata o prompt do sistema com os dados do lead
        formatted_prompt = prompt.partial(lead_name=lead_name, lead_city=lead_city)
        
        # Recria o agente com o prompt formatado
        agent = create_openai_tools_agent(llm, tools, formatted_prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations=10)
        agent_with_chat_history = RunnableWithMessageHistory(
            agent_executor,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        response = agent_with_chat_history.invoke(
            {"input": input_data},
            config=config
        )
        
        output = response.get("output", "Não consegui processar sua solicitação.")
        output = format_for_whatsapp(output)
        if clean_text:
            output = clean_for_whatsapp(output)
        chat_history = get_session_history(phone_number).messages
        return {"response": output, "history": chat_history}
    except Exception as e:
        logger.error(f"[PIPELINE ERROR] Exceção ao executar agente: {str(e)} | phone: {phone_number}")
        return {"response": f"Houve um erro ao processar sua solicitação. Por favor, tente novamente. Erro: {str(e)}"}


# --- PASSO 4: Ponto de Entrada para o Script (para testes) ---

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Orquestrador do Agente Sílvia.')
    parser.add_argument('--phone_number', type=str, required=True, help='Número de telefone do usuário (ID da sessão).')
    parser.add_argument('--message', type=str, required=True, help='Mensagem do usuário.')
    parser.add_argument('--lead_city', type=str, default="", help='Cidade do lead (opcional).')
    parser.add_argument('--lead_name', type=str, default="", help='Nome do lead (opcional).')
    parser.add_argument('--image_url', type=str, help='URL da imagem (opcional).')
    parser.add_argument('--message_type', type=str, default="text", help='Tipo da mensagem (ex: text, button)')
    parser.add_argument('--clean_text', action='store_true', help='Limpa o texto final da resposta para remover acentos e caracteres especiais.')
    
    args = parser.parse_args()

    # Executa a lógica do agente
    result = handle_agent_invocation(
        args.phone_number, args.message, args.lead_city, args.lead_name, args.image_url, args.message_type, args.clean_text
    )
    
    # Imprime o resultado final em formato JSON para ser consumido pelo Kestra
    print(json.dumps(result)) 