"""
RAG Tool para responder dúvidas gerais usando knowledge base.

Este módulo implementa uma ferramenta de Retrieval-Augmented Generation (RAG)
que utiliza FAISS para busca semântica em uma base de conhecimento local.
"""

import os
import pickle
import logging
from typing import List, Optional, Type
from pathlib import Path

import faiss
import numpy as np
from langchain.tools import BaseTool
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)


class RAGToolInput(BaseModel):
    """Input schema para RAGTool."""
    question: str = Field(description="Pergunta ou dúvida do usuário sobre energia solar")


class RAGTool(BaseTool):
    """
    Ferramenta RAG para responder dúvidas gerais usando knowledge base local.
    
    Esta ferramenta:
    1. Carrega documentos da knowledge_base/
    2. Cria embeddings usando OpenAI
    3. Armazena em índice FAISS para busca rápida
    4. Persiste o índice em disco para otimização
    5. Realiza busca semântica para encontrar informações relevantes
    """
    
    name: str = "rag_tool"
    description: str = (
        "Ferramenta para responder dúvidas gerais sobre energia solar, "
        "financiamento, instalação e benefícios usando base de conhecimento local. "
        "Use esta ferramenta quando o usuário fizer perguntas que não sejam "
        "específicas sobre planos de energia ou análise de conta."
    )
    args_schema: Type[BaseModel] = RAGToolInput
    
    # Variáveis de classe para armazenar estado
    _initialized: bool = False
    _knowledge_base_dir: Path = Path("knowledge_base")
    _faiss_index_path: Path = Path("knowledge_base/faiss_index.pkl")
    _documents_path: Path = Path("knowledge_base/documents.pkl")
    _embeddings: Optional[OpenAIEmbeddings] = None
    _text_splitter: Optional[RecursiveCharacterTextSplitter] = None
    _faiss_index = None
    _documents: List[str] = []
    _document_embeddings = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Inicializa apenas uma vez
        if not RAGTool._initialized:
            self._initialize_rag_system()
            RAGTool._initialized = True
    
    def _initialize_rag_system(self):
        """Inicializa o sistema RAG apenas uma vez."""
        # Inicializa embeddings OpenAI
        RAGTool._embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Configuração do text splitter
        RAGTool._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # Chunks menores para melhor precisão
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        # Carrega ou cria o índice
        self._load_or_create_index()
    
    def _load_knowledge_base(self) -> List[str]:
        """
        Carrega todos os arquivos de texto da knowledge_base.
        
        Returns:
            List[str]: Lista de documentos carregados
        """
        documents = []
        
        if not RAGTool._knowledge_base_dir.exists():
            raise FileNotFoundError(f"Diretório {RAGTool._knowledge_base_dir} não encontrado")
        
        # Carrega todos os arquivos .txt da knowledge_base
        for file_path in RAGTool._knowledge_base_dir.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        documents.append(content)
                        logger.info(f"✅ Carregado: {file_path.name}")
            except Exception as e:
                logger.error(f"❌ Erro ao carregar {file_path}: {e}")
        
        if not documents:
            raise ValueError("Nenhum documento encontrado na knowledge_base")
        
        return documents
    
    def _split_documents(self, documents: List[str]) -> List[str]:
        """
        Divide documentos em chunks menores para melhor processamento.
        
        Args:
            documents: Lista de documentos originais
            
        Returns:
            List[str]: Lista de chunks de texto
        """
        document_chunks = []
        
        for doc in documents:
            chunks = RAGTool._text_splitter.split_text(doc)
            document_chunks.extend(chunks)
        
        logger.info(f"📄 Documentos divididos em {len(document_chunks)} chunks")
        return document_chunks
    
    def _create_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Cria embeddings para os textos usando OpenAI.
        
        Args:
            texts: Lista de textos para criar embeddings
            
        Returns:
            np.ndarray: Array de embeddings
        """
        logger.info("🔄 Criando embeddings...")
        
        # Reason: Processa em batches para evitar limites de API
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = RAGTool._embeddings.embed_documents(batch)
            all_embeddings.extend(batch_embeddings)
            logger.info(f"✅ Processado batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
        
        return np.array(all_embeddings, dtype=np.float32)
    
    def _create_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """
        Cria índice FAISS para busca semântica.
        
        Args:
            embeddings: Array de embeddings
            
        Returns:
            faiss.Index: Índice FAISS criado
        """
        logger.info("🔍 Criando índice FAISS...")
        
        # Reason: Usa IndexFlatIP para busca por similaridade de cosseno
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        
        # Normaliza embeddings para usar produto interno como similaridade de cosseno
        faiss.normalize_L2(embeddings)
        index.add(embeddings)
        
        logger.info(f"✅ Índice FAISS criado com {index.ntotal} vetores")
        return index
    
    def _save_index(self):
        """Salva o índice FAISS e documentos em disco."""
        try:
            # Salva índice FAISS
            with open(RAGTool._faiss_index_path, 'wb') as f:
                pickle.dump({
                    'index': faiss.serialize_index(RAGTool._faiss_index),
                    'embeddings': RAGTool._document_embeddings
                }, f)
            
            # Salva documentos
            with open(RAGTool._documents_path, 'wb') as f:
                pickle.dump(RAGTool._documents, f)
            
            logger.info("💾 Índice e documentos salvos em disco")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar índice: {e}")
    
    def _load_index(self) -> bool:
        """
        Carrega índice FAISS e documentos do disco.
        
        Returns:
            bool: True se carregado com sucesso, False caso contrário
        """
        try:
            if not (RAGTool._faiss_index_path.exists() and RAGTool._documents_path.exists()):
                return False
            
            # Carrega índice FAISS
            with open(RAGTool._faiss_index_path, 'rb') as f:
                data = pickle.load(f)
                RAGTool._faiss_index = faiss.deserialize_index(data['index'])
                RAGTool._document_embeddings = data['embeddings']
            
            # Carrega documentos
            with open(RAGTool._documents_path, 'rb') as f:
                RAGTool._documents = pickle.load(f)
            
            logger.info("📂 Índice e documentos carregados do disco")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar índice: {e}")
            return False
    
    def _load_or_create_index(self):
        """Carrega índice existente ou cria um novo."""
        logger.info("🚀 Inicializando RAG Tool...")
        
        # Tenta carregar índice existente
        if self._load_index():
            logger.info("✅ Usando índice existente")
            return
        
        logger.info("🔨 Criando novo índice...")
        
        # Carrega e processa documentos
        raw_documents = self._load_knowledge_base()
        RAGTool._documents = self._split_documents(raw_documents)
        
        # Cria embeddings e índice
        RAGTool._document_embeddings = self._create_embeddings(RAGTool._documents)
        RAGTool._faiss_index = self._create_faiss_index(RAGTool._document_embeddings)
        
        # Salva para uso futuro
        self._save_index()
        
        logger.info("✅ RAG Tool inicializado com sucesso")
    
    def _search_similar_documents(self, query: str, k: int = 3) -> List[tuple]:
        """
        Busca documentos similares à query.
        
        Args:
            query: Pergunta do usuário
            k: Número de documentos similares a retornar
            
        Returns:
            List[tuple]: Lista de (documento, score) ordenada por relevância
        """
        # Cria embedding da query
        query_embedding = np.array([RAGTool._embeddings.embed_query(query)], dtype=np.float32)
        faiss.normalize_L2(query_embedding)
        
        # Busca documentos similares
        scores, indices = RAGTool._faiss_index.search(query_embedding, k)
        
        # Retorna documentos com scores
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(RAGTool._documents):  # Verifica se índice é válido
                results.append((RAGTool._documents[idx], float(score)))
        
        return results
    
    def _generate_answer(self, query: str, relevant_docs: List[tuple]) -> str:
        """
        Gera resposta usando LLM baseada nos documentos relevantes (RAG real).
        
        Args:
            query: Pergunta original
            relevant_docs: Lista de (documento, score)
            
        Returns:
            str: Resposta gerada pelo LLM
        """
        if not relevant_docs:
            return (
                "Desculpe, não encontrei informações específicas sobre sua pergunta "
                "na minha base de conhecimento. Posso ajudá-lo com outras dúvidas "
                "sobre energia solar, financiamento ou benefícios?"
            )
        
        # Reason: Filtra apenas documentos com score relevante (> 0.7)
        relevant_content = []
        for doc, score in relevant_docs:
            if score > 0.7:  # Threshold de relevância
                relevant_content.append(doc)
        
        if not relevant_content:
            return (
                "Encontrei algumas informações relacionadas, mas não são "
                "suficientemente específicas para sua pergunta. Poderia "
                "reformular ou ser mais específico?"
            )
        
        # Constrói contexto para o LLM
        context = "\n\n".join(relevant_content[:3])  # Usa até 3 documentos mais relevantes
        
        # Reason: Prompt estruturado para RAG com contexto e instrução clara
        rag_prompt = f"""Você é um assistente especializado da Serena Energia. Sua tarefa é responder à pergunta do usuário de forma clara, amigável e precisa, usando APENAS as informações fornecidas no contexto abaixo.

CONTEXTO DA BASE DE CONHECIMENTO:
{context}

PERGUNTA DO USUÁRIO:
{query}

INSTRUÇÕES:
- Responda de forma natural e conversacional
- Use apenas informações do contexto fornecido
- Se a pergunta não puder ser respondida com o contexto, diga que não tem essa informação específica
- Seja conciso mas completo
- Mantenha o tom amigável e profissional da Serena Energia
- Termine oferecendo ajuda adicional se necessário

RESPOSTA:"""

        try:
            # Reason: Usa OpenAI para gerar resposta baseada no contexto (RAG real)
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.3,  # Baixa temperatura para respostas mais consistentes
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            
            # Gera resposta usando o LLM
            response = llm.invoke(rag_prompt)
            
            # Extrai o conteúdo da resposta
            if hasattr(response, 'content'):
                return response.content.strip()
            else:
                return str(response).strip()
                
        except Exception as e:
            print(f"❌ Erro ao gerar resposta com LLM: {e}")
            # Fallback: retorna resposta formatada se LLM falhar
            return (
                f"Com base nas informações da Serena Energia:\n\n"
                f"{context[:500]}...\n\n"
                f"Esta informação está relacionada à sua pergunta sobre: '{query}'. "
                f"Posso esclarecer algum ponto específico?"
            )
    
    def _run(self, question: str) -> str:
        """
        Executa a busca RAG e retorna resposta.
        
        Args:
            question: Pergunta do usuário
            
        Returns:
            str: Resposta baseada na knowledge base
        """
        try:
            print(f"🔍 Processando pergunta: {question}")
            
            # Busca documentos similares
            similar_docs = self._search_similar_documents(question, k=5)
            
            # Gera resposta
            answer = self._generate_answer(question, similar_docs)
            
            print("✅ Resposta gerada com sucesso")
            return answer
            
        except Exception as e:
            error_msg = f"Erro ao processar pergunta: {str(e)}"
            print(f"❌ {error_msg}")
            return (
                "Desculpe, ocorreu um erro ao processar sua pergunta. "
                "Tente novamente ou reformule sua dúvida."
            )


# Instância global da ferramenta para uso no agente
rag_tool = RAGTool() 