from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool

# Importa a lista de FAQ do nosso novo arquivo de dados
from scripts.agent_tools.faq_data import FAQ_LIST

def get_faq_retriever():
    """
    Cria um retriever FAISS a partir de uma lista de FAQs pré-definida.
    """
    # Converte a lista de FAQ em documentos LangChain para indexação
    documents = [
        Document(page_content=f"Pergunta: {item['pergunta']}\nResposta: {item['resposta']}")
        for item in FAQ_LIST
    ]
    
    if not documents:
        raise ValueError("A lista de FAQ está vazia. Não é possível criar a base de conhecimento.")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Cria o índice vetorial em memória
    vector_store = FAISS.from_documents(documents, embeddings)
    
    return vector_store.as_retriever(search_kwargs={"k": 3}) # Retorna os 3 resultados mais relevantes

# O retriever é criado uma vez quando o módulo é importado para otimizar a performance
faq_retriever = get_faq_retriever()

@tool
def consultar_faq_serena(pergunta_do_usuario: str) -> str:
    """
    Use esta ferramenta para responder a perguntas comuns dos clientes sobre a Serena Energia, 
    como funciona o serviço, custos, instalação e cobertura. A entrada deve ser a 
    pergunta do usuário.
    """
    docs = faq_retriever.invoke(pergunta_do_usuario)
    
    if not docs:
        return "Não encontrei uma resposta para isso em nosso FAQ. Você poderia tentar reformular a pergunta?"
        
    # Concatena o conteúdo dos documentos encontrados para formar o contexto
    contexto = "\n\n".join([doc.page_content for doc in docs])
    
    return contexto 