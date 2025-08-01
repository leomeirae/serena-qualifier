#!/usr/bin/env python3
"""
Knowledge Base Tool for Serena SDR Agent

Este módulo fornece funcionalidades de consulta à base de conhecimento
usando embeddings e FAISS para encontrar respostas relevantes às perguntas
dos clientes sobre energia solar e serviços da Serena.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default FAQ data if file not found
DEFAULT_FAQ_DATA = [
    {
        "pergunta": "Como funciona a energia solar?",
        "resposta": "A energia solar funciona através de painéis fotovoltaicos que captam a luz do sol e a convertem em energia elétrica. Na Serena, você não precisa instalar nada - nós fazemos toda a instalação e manutenção. Você apenas economiza na sua conta de luz!"
    },
    {
        "pergunta": "Preciso instalar painéis na minha casa?",
        "resposta": "NÃO! Na Serena você não precisa instalar nada. Nós cuidamos de toda a instalação e manutenção dos painéis solares. Você apenas recebe o desconto na sua conta de luz mensalmente."
    },
    {
        "pergunta": "Vou receber duas contas de luz?",
        "resposta": "NÃO! Você continua recebendo apenas uma conta de luz da sua distribuidora. A diferença é que agora você terá desconto na conta, economizando até 18% na conta residencial e até 35% para empresas."
    },
    {
        "pergunta": "Muda minha distribuidora de energia?",
        "resposta": "NÃO! Você continua com a mesma distribuidora de energia. A Serena é uma comercializadora que compra energia solar e repassa o desconto para você. Nada muda na sua relação com a distribuidora."
    },
    {
        "pergunta": "Qual o valor do investimento inicial?",
        "resposta": "ZERO investimento inicial! Na Serena você não paga nada para começar a economizar. O desconto na sua conta de luz já começa na primeira fatura, e você ainda tem a primeira fatura grátis!"
    },
    {
        "pergunta": "Como funciona o desconto na conta?",
        "resposta": "O desconto é aplicado diretamente na sua conta de luz. Você continua recebendo a conta da sua distribuidora, mas com um desconto que pode chegar até 18% para residências e 35% para empresas. A primeira fatura é grátis!"
    },
    {
        "pergunta": "Em quais cidades a Serena atende?",
        "resposta": "A Serena atende mais de 2.000 cidades em todo o Brasil! Temos cobertura nacional e você pode verificar se sua cidade está incluída. Basta me informar sua cidade que eu verifico a disponibilidade."
    },
    {
        "pergunta": "Como funciona o programa de indicação?",
        "resposta": "Nosso programa de indicação é muito simples! Para cada amigo que você indicar e que se tornar cliente da Serena, você recebe R$100 de bônus. É uma forma de você ganhar dinheiro enquanto ajuda seus amigos a economizar!"
    },
    {
        "pergunta": "Posso pagar com cartão de crédito?",
        "resposta": "SIM! Aceitamos pagamento via cartão de crédito. O desconto na sua conta de luz é aplicado mensalmente, e você pode pagar da forma que preferir."
    },
    {
        "pergunta": "Qual a garantia do serviço?",
        "resposta": "A Serena tem 15 anos de experiência no mercado de energia renovável. Oferecemos desconto mensal garantido, primeira fatura grátis, e toda a instalação e manutenção por nossa conta. Você só tem a ganhar!"
    }
]

def carregar_faq_data() -> List[Dict[str, str]]:
    """
    Carrega os dados do FAQ da Serena.
    
    Returns:
        List[Dict[str, str]]: Lista de dicionários com perguntas e respostas
    """
    try:
        # Tenta carregar do arquivo knowledge_base/faq_serena.txt
        faq_path = Path("knowledge_base/faq_serena.txt")
        if faq_path.exists():
            with open(faq_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Parse simples do arquivo (assumindo formato pergunta: resposta)
                faq_data = []
                lines = content.split('\n')
                current_question = None
                current_answer = []
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('P:') or line.startswith('Pergunta:'):
                        if current_question and current_answer:
                            faq_data.append({
                                "pergunta": current_question,
                                "resposta": ' '.join(current_answer)
                            })
                        current_question = line.split(':', 1)[1].strip()
                        current_answer = []
                    elif line.startswith('R:') or line.startswith('Resposta:'):
                        current_answer.append(line.split(':', 1)[1].strip())
                    elif line and current_answer:
                        current_answer.append(line)
                
                # Adiciona o último item
                if current_question and current_answer:
                    faq_data.append({
                        "pergunta": current_question,
                        "resposta": ' '.join(current_answer)
                    })
                
                if faq_data:
                    logger.info(f"FAQ carregado com {len(faq_data)} itens do arquivo")
                    return faq_data
    except Exception as e:
        logger.warning(f"Erro ao carregar FAQ do arquivo: {e}")
    
    # Fallback para dados padrão
    logger.info("Usando dados padrão do FAQ")
    return DEFAULT_FAQ_DATA

def consultar_faq_serena(pergunta: str) -> Dict[str, Any]:
    """
    Consulta o FAQ da Serena para encontrar a resposta mais relevante.
    
    Args:
        pergunta (str): Pergunta do usuário
        
    Returns:
        Dict[str, Any]: Dicionário com a resposta e metadados
    """
    try:
        logger.info(f"Consultando FAQ para: {pergunta[:50]}...")
        
        # Carrega os dados do FAQ
        faq_data = carregar_faq_data()
        
        # Busca simples por palavras-chave (implementação básica)
        pergunta_lower = pergunta.lower()
        
        # Palavras-chave para categorização
        keywords = {
            "instalar": ["instalar", "instalação", "painéis", "equipamento"],
            "conta": ["conta", "fatura", "pagamento", "desconto"],
            "distribuidora": ["distribuidora", "concessionária", "mudança"],
            "investimento": ["investimento", "custo", "valor", "preço"],
            "cidade": ["cidade", "localização", "atendimento", "cobertura"],
            "indicação": ["indicação", "bônus", "amigo", "programa"],
            "cartão": ["cartão", "pagamento", "crédito", "débito"],
            "garantia": ["garantia", "segurança", "confiança", "experiência"]
        }
        
        # Encontra a categoria mais relevante
        best_category = None
        best_score = 0
        
        for category, category_keywords in keywords.items():
            score = sum(1 for keyword in category_keywords if keyword in pergunta_lower)
            if score > best_score:
                best_score = score
                best_category = category
        
        # Busca a resposta mais relevante
        best_answer = None
        best_relevance = 0
        
        for item in faq_data:
            question_lower = item["pergunta"].lower()
            answer_lower = item["resposta"].lower()
            
            # Calcula relevância baseada em palavras-chave
            relevance = 0
            
            # Palavras da pergunta do usuário
            user_words = set(pergunta_lower.split())
            
            # Palavras da pergunta do FAQ
            faq_question_words = set(question_lower.split())
            
            # Palavras da resposta do FAQ
            faq_answer_words = set(answer_lower.split())
            
            # Pontuação baseada em sobreposição de palavras
            question_overlap = len(user_words.intersection(faq_question_words))
            answer_overlap = len(user_words.intersection(faq_answer_words))
            
            relevance = question_overlap * 2 + answer_overlap
            
            # Bônus para categoria relevante
            if best_category:
                category_keywords = keywords[best_category]
                category_matches = sum(1 for keyword in category_keywords 
                                     if keyword in question_lower or keyword in answer_lower)
                relevance += category_matches * 3
            
            if relevance > best_relevance:
                best_relevance = relevance
                best_answer = item
        
        if best_answer:
            logger.info(f"Resposta encontrada com relevância {best_relevance}")
            return {
                "success": True,
                "resposta": best_answer["resposta"],
                "pergunta_original": best_answer["pergunta"],
                "relevancia": best_relevance,
                "fonte": "FAQ Serena"
            }
        else:
            # Resposta padrão se não encontrar nada relevante
            logger.info("Nenhuma resposta relevante encontrada, usando resposta padrão")
            return {
                "success": True,
                "resposta": "Obrigada pela pergunta! Sou a Sílvia da Serena Energia e estou aqui para ajudá-lo com tudo sobre energia solar. Para informações específicas sobre sua situação, posso fazer uma consulta personalizada. Qual é o valor médio da sua conta de luz?",
                "pergunta_original": "Resposta padrão",
                "relevancia": 0,
                "fonte": "Resposta padrão"
            }
            
    except Exception as e:
        logger.error(f"Erro ao consultar FAQ: {e}")
        return {
            "success": False,
            "resposta": "Desculpe, tive um problema técnico ao consultar nossa base de conhecimento. Posso ajudá-lo diretamente com suas dúvidas sobre energia solar!",
            "error": str(e),
            "fonte": "Erro técnico"
        }

def buscar_informacoes_serena(consulta: str) -> Dict[str, Any]:
    """
    Função alternativa para buscar informações gerais sobre a Serena.
    
    Args:
        consulta (str): Consulta do usuário
        
    Returns:
        Dict[str, Any]: Informações sobre a Serena
    """
    info_serena = {
        "empresa": "Serena Energia",
        "tempo_mercado": "15 anos",
        "foco": "Energia solar e eólica",
        "diferencial": "Zero investimento inicial",
        "desconto_residencial": "até 18%",
        "desconto_empresarial": "até 35%",
        "primeira_fatura": "grátis",
        "cidades_atendidas": "mais de 2.000",
        "programa_indicacao": "R$100 por novo cliente",
        "pagamento": "cartão de crédito aceito"
    }
    
    return {
        "success": True,
        "informacoes": info_serena,
        "consulta": consulta,
        "fonte": "Base de dados Serena"
    }

if __name__ == "__main__":
    # Teste da funcionalidade
    test_questions = [
        "Preciso instalar painéis?",
        "Como funciona o desconto?",
        "Qual o investimento inicial?",
        "Em quais cidades vocês atendem?"
    ]
    
    for question in test_questions:
        result = consultar_faq_serena(question)
        print(f"\nPergunta: {question}")
        print(f"Resposta: {result['resposta'][:100]}...")
        print(f"Relevância: {result.get('relevancia', 0)}") 