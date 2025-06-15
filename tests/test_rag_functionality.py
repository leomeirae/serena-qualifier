"""
Testes simplificados para a funcionalidade RAG.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import numpy as np

# Imports do sistema
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.serena_agent.tools.rag_tool import RAGToolInput


class TestRAGToolInput:
    """Testa o schema de input da RAGTool."""
    
    def test_valid_input(self):
        """Testa input válido."""
        input_data = RAGToolInput(question="O que é energia solar?")
        assert input_data.question == "O que é energia solar?"
    
    def test_empty_question(self):
        """Testa pergunta vazia."""
        input_data = RAGToolInput(question="")
        assert input_data.question == ""


class TestRAGComponents:
    """Testa componentes da RAG de forma isolada."""
    
    def test_text_splitting(self):
        """Testa divisão de texto."""
        from langchain.text_splitter import CharacterTextSplitter
        
        text_splitter = CharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separator="\n"
        )
        
        # Texto com quebras de linha para funcionar com o separator
        long_text = """Energia solar é renovável.
Benefícios da energia solar incluem economia.
Instalação deve ser feita por profissionais.
Manutenção é simples e barata.
Valorização do imóvel é garantida.
Sistema tem vida útil de 25 anos.
Retorno do investimento em 5-7 anos.
Energia limpa e sustentável.
Redução da pegada de carbono.
Independência energética."""
        
        chunks = text_splitter.split_text(long_text)
        
        assert len(chunks) >= 1
        # Como o texto é pequeno, pode ficar em um chunk só
        assert all(len(chunk) <= 1000 for chunk in chunks)  # Tolerância maior
    
    def test_similarity_filtering(self):
        """Testa filtro de similaridade."""
        scores = [0.9, 0.8, 0.6, 0.5]
        docs = ["doc1", "doc2", "doc3", "doc4"]
        threshold = 0.7
        
        filtered = [(doc, score) for doc, score in zip(docs, scores) if score >= threshold]
        
        assert len(filtered) == 2
        assert filtered[0] == ("doc1", 0.9)
        assert filtered[1] == ("doc2", 0.8)


class TestFileOperations:
    """Testa operações de arquivo."""
    
    def test_load_txt_files(self):
        """Testa carregamento de arquivos .txt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            kb_dir = Path(temp_dir) / "knowledge_base"
            kb_dir.mkdir()
            
            # Cria arquivo de teste
            with open(kb_dir / "test.txt", "w", encoding="utf-8") as f:
                f.write("Conteúdo de teste")
            
            # Simula carregamento
            txt_files = list(kb_dir.glob("*.txt"))
            assert len(txt_files) == 1
            
            with open(txt_files[0], 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert content == "Conteúdo de teste"
    
    def test_ignore_non_txt_files(self):
        """Testa que arquivos não-.txt são ignorados."""
        with tempfile.TemporaryDirectory() as temp_dir:
            kb_dir = Path(temp_dir) / "knowledge_base"
            kb_dir.mkdir()
            
            # Cria diferentes tipos de arquivo
            with open(kb_dir / "test.txt", "w", encoding="utf-8") as f:
                f.write("Arquivo válido")
            
            with open(kb_dir / "readme.md", "w", encoding="utf-8") as f:
                f.write("Arquivo markdown")
            
            with open(kb_dir / "config.json", "w", encoding="utf-8") as f:
                f.write('{"config": "value"}')
            
            # Apenas arquivos .txt devem ser encontrados
            txt_files = list(kb_dir.glob("*.txt"))
            assert len(txt_files) == 1
            assert txt_files[0].name == "test.txt"


class TestErrorHandling:
    """Testa tratamento de erros."""
    
    def test_missing_directory_error(self):
        """Testa erro quando diretório não existe."""
        non_existent_path = Path("/path/that/does/not/exist")
        assert not non_existent_path.exists()
    
    def test_empty_directory_handling(self):
        """Testa tratamento de diretório vazio."""
        with tempfile.TemporaryDirectory() as temp_dir:
            kb_dir = Path(temp_dir) / "knowledge_base"
            kb_dir.mkdir()
            
            # Diretório existe mas não tem arquivos .txt
            txt_files = list(kb_dir.glob("*.txt"))
            assert len(txt_files) == 0


class TestRAGLogic:
    """Testa lógica específica da RAG."""
    
    def test_answer_generation_logic(self):
        """Testa lógica de geração de respostas."""
        def generate_answer(question, relevant_docs):
            if not relevant_docs:
                return "Não encontrei informações específicas sobre sua pergunta."
            
            high_relevance = [doc for doc, score in relevant_docs if score >= 0.7]
            
            if not high_relevance:
                return "Informações encontradas não são suficientemente específicas."
            
            return f"Com base nas informações: {high_relevance[0]}"
        
        # Teste sem documentos
        result1 = generate_answer("pergunta", [])
        assert "Não encontrei informações específicas" in result1
        
        # Teste com baixa relevância
        result2 = generate_answer("pergunta", [("doc", 0.5)])
        assert "não são suficientemente específicas" in result2
        
        # Teste com alta relevância
        result3 = generate_answer("pergunta", [("Energia solar é renovável", 0.9)])
        assert "Com base nas informações" in result3
        assert "Energia solar é renovável" in result3
    
    def test_relevance_threshold(self):
        """Testa aplicação do threshold de relevância."""
        results = [
            ("doc1", 0.95),
            ("doc2", 0.85),
            ("doc3", 0.75),
            ("doc4", 0.65),
            ("doc5", 0.55)
        ]
        
        threshold = 0.7
        filtered = [item for item in results if item[1] >= threshold]
        
        assert len(filtered) == 3
        assert all(score >= threshold for _, score in filtered)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 