import os
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.tools import tool

# --- Configuração Inicial e Carregamento do Manual ---

def get_knowledge_base():
    """
    Carrega o manual da Serena, processa o texto e cria uma base de conhecimento vetorial (FAISS).
    Este processo é custoso e deve ser executado apenas uma vez ou quando o manual for atualizado.
    """
    manual_path = "manual_representante_serena.markdown"
    
    if not os.path.exists(manual_path):
        raise FileNotFoundError(f"O arquivo do manual não foi encontrado em: {manual_path}")

    # 1. Carregar o documento
    loader = UnstructuredMarkdownLoader(manual_path)
    documents = loader.load()

    # 2. Dividir o documento em trechos (chunks)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)

    # 3. Converter os trechos em vetores (embeddings)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # 4. Armazenar os vetores em um banco de dados vetorial FAISS
    # O FAISS cria um índice local para buscas rápidas de similaridade.
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    return vector_store.as_retriever()

# O retriever é inicializado uma vez quando o módulo é carregado
# para evitar recriar a base de conhecimento a cada chamada.
knowledge_retriever = get_knowledge_base()


# --- Ferramenta para o Agente ---

@tool
def consultar_manual_serena(pergunta_do_usuario: str) -> str:
    """
    Use esta ferramenta para responder a perguntas gerais sobre a Serena Energia, 
    produtos, comissionamento, energia limpa ou o processo de contratação.
    A entrada para esta ferramenta deve ser a pergunta exata do usuário.
    """
    # Busca por documentos relevantes na base de conhecimento
    docs = knowledge_retriever.invoke(pergunta_do_usuario)
    
    # Concatena o conteúdo dos documentos encontrados para formar a resposta
    resposta_baseada_no_manual = "\n\n".join([doc.page_content for doc in docs])
    
    if not resposta_baseada_no_manual:
        return "Não encontrei informações sobre isso no manual. Tente reformular a pergunta."
        
    return resposta_baseada_no_manual

# Exemplo de como usar a ferramenta (para testes manuais)
if __name__ == '__main__':
    # Teste 1: Pergunta sobre comissionamento
    pergunta1 = "Como funciona o comissionamento?"
    resposta1 = consultar_manual_serena.invoke(pergunta1)
    print(f"Pergunta: {pergunta1}")
    print(f"Resposta do Manual:\n{resposta1}\n---")

    # Teste 2: Pergunta sobre planos
    pergunta2 = "Quais são os planos da Serena?"
    resposta2 = consultar_manual_serena.invoke(pergunta2)
    print(f"Pergunta: {pergunta2}")
    print(f"Resposta do Manual:\n{resposta2}") 