from langchain_core.documents import Document
from langchain_core.tools import tool
import logging

# Importa a lista de FAQ do nosso novo arquivo de dados
from scripts.agent_tools.faq_data import FAQ_LIST

logger = logging.getLogger(__name__)

def get_faq_retriever():
    """
    Cria um retriever FAISS a partir de uma lista de FAQs pré-definida.
    """
    try:
        # Importações protegidas para evitar crashes
        from langchain_openai import OpenAIEmbeddings
        from langchain_community.vectorstores import FAISS
        
        # Converte a lista de FAQ em documentos LangChain para indexação
        documents = [
            Document(page_content=f"Pergunta: {item['pergunta']}\nResposta: {item['resposta']}")
            for item in FAQ_LIST
        ]
        
        if not documents:
            logger.warning("A lista de FAQ está vazia. Usando fallback simples.")
            return None

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # Cria o índice vetorial em memória
        vector_store = FAISS.from_documents(documents, embeddings)
        
        return vector_store.as_retriever(search_kwargs={"k": 3}) # Retorna os 3 resultados mais relevantes
        
    except ImportError as e:
        logger.error(f"Erro ao importar FAISS ou OpenAIEmbeddings: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro ao criar retriever FAISS: {e}")
        return None

# O retriever é criado uma vez quando o módulo é importado para otimizar a performance
faq_retriever = get_faq_retriever()

@tool
def consultar_faq_serena(pergunta_do_usuario: str) -> str:
    """
    Use esta ferramenta para responder a perguntas comuns dos clientes sobre a Serena Energia, 
    como funciona o serviço, custos, instalação e cobertura. A entrada deve ser a 
    pergunta do usuário.
    """
    try:
        if faq_retriever is None:
            # Fallback: busca simples na lista de FAQ
            logger.warning("FAISS não disponível, usando busca simples")
            pergunta_lower = pergunta_do_usuario.lower()
            
            for item in FAQ_LIST:
                if any(keyword in pergunta_lower for keyword in item['pergunta'].lower().split()):
                    return f"Pergunta: {item['pergunta']}\nResposta: {item['resposta']}"
            
            return "Não encontrei uma resposta para isso em nosso FAQ. Você poderia tentar reformular a pergunta?"
        
        docs = faq_retriever.invoke(pergunta_do_usuario)
        
        if not docs:
            return "Não encontrei uma resposta para isso em nosso FAQ. Você poderia tentar reformular a pergunta?"
            
        # Concatena o conteúdo dos documentos encontrados para formar o contexto
        contexto = "\n\n".join([doc.page_content for doc in docs])
        
        return contexto
        
    except Exception as e:
        logger.error(f"Erro ao consultar FAQ: {e}")
        return "Desculpe, houve um erro ao consultar nosso FAQ. Você poderia tentar novamente?" 