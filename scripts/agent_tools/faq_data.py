#!/usr/bin/env python3
"""
FAQ Data Loader for Serena SDR Agent

Este módulo carrega os dados do FAQ da Serena a partir do arquivo
knowledge_base/faq_serena.txt e fornece funções para acessar essas informações.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default FAQ data structure
DEFAULT_FAQ_STRUCTURE = [
    {
        "id": 1,
        "categoria": "instalacao",
        "pergunta": "Preciso instalar painéis na minha casa?",
        "resposta": "NÃO! Na Serena você não precisa instalar nada. Nós cuidamos de toda a instalação e manutenção dos painéis solares. Você apenas recebe o desconto na sua conta de luz mensalmente.",
        "palavras_chave": ["instalar", "painéis", "equipamento", "obra", "manutenção"]
    },
    {
        "id": 2,
        "categoria": "conta",
        "pergunta": "Vou receber duas contas de luz?",
        "resposta": "NÃO! Você continua recebendo apenas uma conta de luz da sua distribuidora. A diferença é que agora você terá desconto na conta, economizando até 18% na conta residencial e até 35% para empresas.",
        "palavras_chave": ["conta", "fatura", "duas", "distribuidora", "desconto"]
    },
    {
        "id": 3,
        "categoria": "distribuidora",
        "pergunta": "Muda minha distribuidora de energia?",
        "resposta": "NÃO! Você continua com a mesma distribuidora de energia. A Serena é uma comercializadora que compra energia solar e repassa o desconto para você. Nada muda na sua relação com a distribuidora.",
        "palavras_chave": ["distribuidora", "concessionária", "mudança", "relação", "comercializadora"]
    },
    {
        "id": 4,
        "categoria": "investimento",
        "pergunta": "Qual o valor do investimento inicial?",
        "resposta": "ZERO investimento inicial! Na Serena você não paga nada para começar a economizar. O desconto na sua conta de luz já começa na primeira fatura, e você ainda tem a primeira fatura grátis!",
        "palavras_chave": ["investimento", "custo", "valor", "preço", "inicial", "zero"]
    },
    {
        "id": 5,
        "categoria": "desconto",
        "pergunta": "Como funciona o desconto na conta?",
        "resposta": "O desconto é aplicado diretamente na sua conta de luz. Você continua recebendo a conta da sua distribuidora, mas com um desconto que pode chegar até 18% para residências e 35% para empresas. A primeira fatura é grátis!",
        "palavras_chave": ["desconto", "conta", "fatura", "aplicado", "economia"]
    },
    {
        "id": 6,
        "categoria": "cobertura",
        "pergunta": "Em quais cidades a Serena atende?",
        "resposta": "A Serena atende mais de 2.000 cidades em todo o Brasil! Temos cobertura nacional e você pode verificar se sua cidade está incluída. Basta me informar sua cidade que eu verifico a disponibilidade.",
        "palavras_chave": ["cidade", "localização", "atendimento", "cobertura", "brasil"]
    },
    {
        "id": 7,
        "categoria": "indicacao",
        "pergunta": "Como funciona o programa de indicação?",
        "resposta": "Nosso programa de indicação é muito simples! Para cada amigo que você indicar e que se tornar cliente da Serena, você recebe R$100 de bônus. É uma forma de você ganhar dinheiro enquanto ajuda seus amigos a economizar!",
        "palavras_chave": ["indicação", "bônus", "amigo", "programa", "R$100"]
    },
    {
        "id": 8,
        "categoria": "pagamento",
        "pergunta": "Posso pagar com cartão de crédito?",
        "resposta": "SIM! Aceitamos pagamento via cartão de crédito. O desconto na sua conta de luz é aplicado mensalmente, e você pode pagar da forma que preferir.",
        "palavras_chave": ["cartão", "pagamento", "crédito", "débito", "aceitamos"]
    },
    {
        "id": 9,
        "categoria": "garantia",
        "pergunta": "Qual a garantia do serviço?",
        "resposta": "A Serena tem 15 anos de experiência no mercado de energia renovável. Oferecemos desconto mensal garantido, primeira fatura grátis, e toda a instalação e manutenção por nossa conta. Você só tem a ganhar!",
        "palavras_chave": ["garantia", "segurança", "confiança", "experiência", "15 anos"]
    },
    {
        "id": 10,
        "categoria": "funcionamento",
        "pergunta": "Como funciona a energia solar?",
        "resposta": "A energia solar funciona através de painéis fotovoltaicos que captam a luz do sol e a convertem em energia elétrica. Na Serena, você não precisa instalar nada - nós fazemos toda a instalação e manutenção. Você apenas economiza na sua conta de luz!",
        "palavras_chave": ["energia", "solar", "painéis", "fotovoltaicos", "funciona"]
    }
]

def carregar_faq_data() -> List[Dict[str, Any]]:
    """
    Carrega os dados do FAQ da Serena.
    
    Tenta carregar do arquivo knowledge_base/faq_serena.txt primeiro,
    se não encontrar, usa os dados padrão.
    
    Returns:
        List[Dict[str, Any]]: Lista de dicionários com dados do FAQ
    """
    try:
        # Tenta carregar do arquivo knowledge_base/faq_serena.txt
        faq_path = Path("knowledge_base/faq_serena.txt")
        if faq_path.exists():
            logger.info(f"Carregando FAQ do arquivo: {faq_path}")
            with open(faq_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse do arquivo de texto
            faq_data = []
            lines = content.split('\n')
            current_item = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('ID:'):
                    if current_item:
                        faq_data.append(current_item)
                    current_item = {"id": int(line.split(':', 1)[1].strip())}
                elif line.startswith('Categoria:'):
                    current_item["categoria"] = line.split(':', 1)[1].strip()
                elif line.startswith('Pergunta:'):
                    current_item["pergunta"] = line.split(':', 1)[1].strip()
                elif line.startswith('Resposta:'):
                    current_item["resposta"] = line.split(':', 1)[1].strip()
                elif line.startswith('Palavras-chave:'):
                    keywords = line.split(':', 1)[1].strip()
                    current_item["palavras_chave"] = [k.strip() for k in keywords.split(',')]
            
            # Adiciona o último item
            if current_item:
                faq_data.append(current_item)
            
            if faq_data:
                logger.info(f"FAQ carregado com {len(faq_data)} itens do arquivo")
                return faq_data
                
    except Exception as e:
        logger.warning(f"Erro ao carregar FAQ do arquivo: {e}")
    
    # Fallback para dados padrão
    logger.info("Usando dados padrão do FAQ")
    return DEFAULT_FAQ_STRUCTURE

def buscar_faq_por_categoria(categoria: str) -> List[Dict[str, Any]]:
    """
    Busca itens do FAQ por categoria.
    
    Args:
        categoria (str): Categoria desejada
        
    Returns:
        List[Dict[str, Any]]: Lista de itens da categoria
    """
    faq_data = carregar_faq_data()
    return [item for item in faq_data if item.get("categoria") == categoria]

def buscar_faq_por_palavra_chave(palavra: str) -> List[Dict[str, Any]]:
    """
    Busca itens do FAQ por palavra-chave.
    
    Args:
        palavra (str): Palavra-chave para busca
        
    Returns:
        List[Dict[str, Any]]: Lista de itens que contêm a palavra-chave
    """
    faq_data = carregar_faq_data()
    palavra_lower = palavra.lower()
    
    resultados = []
    for item in faq_data:
        # Busca na pergunta
        if palavra_lower in item.get("pergunta", "").lower():
            resultados.append(item)
            continue
            
        # Busca na resposta
        if palavra_lower in item.get("resposta", "").lower():
            resultados.append(item)
            continue
            
        # Busca nas palavras-chave
        palavras_chave = item.get("palavras_chave", [])
        if any(palavra_lower in kw.lower() for kw in palavras_chave):
            resultados.append(item)
    
    return resultados

def obter_categorias_disponiveis() -> List[str]:
    """
    Retorna lista de categorias disponíveis no FAQ.
    
    Returns:
        List[str]: Lista de categorias
    """
    faq_data = carregar_faq_data()
    categorias = list(set(item.get("categoria", "") for item in faq_data))
    return [cat for cat in categorias if cat]

def obter_estatisticas_faq() -> Dict[str, Any]:
    """
    Retorna estatísticas do FAQ.
    
    Returns:
        Dict[str, Any]: Estatísticas do FAQ
    """
    faq_data = carregar_faq_data()
    
    # Conta por categoria
    categorias = {}
    for item in faq_data:
        categoria = item.get("categoria", "sem_categoria")
        categorias[categoria] = categorias.get(categoria, 0) + 1
    
    return {
        "total_itens": len(faq_data),
        "categorias": categorias,
        "categorias_disponiveis": list(categorias.keys())
    }

def exportar_faq_para_json(caminho_arquivo: str = "faq_serena.json") -> bool:
    """
    Exporta os dados do FAQ para um arquivo JSON.
    
    Args:
        caminho_arquivo (str): Caminho do arquivo JSON
        
    Returns:
        bool: True se exportou com sucesso, False caso contrário
    """
    try:
        faq_data = carregar_faq_data()
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(faq_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"FAQ exportado para {caminho_arquivo}")
        return True
    except Exception as e:
        logger.error(f"Erro ao exportar FAQ: {e}")
        return False

if __name__ == "__main__":
    # Teste da funcionalidade
    print("=== Teste do FAQ Data ===")
    
    # Carrega dados
    faq_data = carregar_faq_data()
    print(f"Total de itens carregados: {len(faq_data)}")
    
    # Mostra categorias
    categorias = obter_categorias_disponiveis()
    print(f"Categorias disponíveis: {categorias}")
    
    # Busca por palavra-chave
    resultados = buscar_faq_por_palavra_chave("instalar")
    print(f"Resultados para 'instalar': {len(resultados)} itens")
    
    # Estatísticas
    stats = obter_estatisticas_faq()
    print(f"Estatísticas: {stats}")
    
    # Exporta para JSON
    exportar_faq_para_json("teste_faq.json") 