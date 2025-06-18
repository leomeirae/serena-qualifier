#!/usr/bin/env python3
"""
Location Extractor Module

Este módulo contém a lógica para extrair localização (cidade/estado) das mensagens
dos leads e gerar prompts personalizados baseados na localização.

Author: Serena-Coder AI Agent
Version: 1.0.0 - Refatoração para modularização
Created: 2025-01-17
"""

import re
import logging
from typing import Optional, Tuple, List, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)


class LocationExtractor:
    """
    Classe responsável pela extração de localização das mensagens dos leads
    e geração de prompts personalizados.
    """
    
    def __init__(self):
        """Inicializa o extrator de localização."""
        # Lista de estados válidos do Brasil
        self.valid_states = {
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        }
        
        # Dicionário de cidades conhecidas com seus estados
        self.major_cities = {
            'são paulo': 'SP', 'rio de janeiro': 'RJ', 'belo horizonte': 'MG',
            'salvador': 'BA', 'brasília': 'DF', 'fortaleza': 'CE',
            'recife': 'PE', 'porto alegre': 'RS', 'manaus': 'AM',
            'curitiba': 'PR', 'goiânia': 'GO', 'vitória': 'ES',
            'belém': 'PA', 'guarulhos': 'SP', 'campinas': 'SP',
            'nova iguaçu': 'RJ', 'maceió': 'AL', 'são luís': 'MA',
            'duque de caxias': 'RJ', 'natal': 'RN', 'teresina': 'PI',
            'campo grande': 'MS', 'são bernardo do campo': 'SP',
            'joão pessoa': 'PB', 'santo andré': 'SP', 'osasco': 'SP'
        }
        
        # Padrões regex para extração de localização
        self.location_patterns = [
            # Padrão: "moro em São Paulo, SP" ou "vivo em Rio de Janeiro/RJ"
            r'(?i)(?:moro|vivo|estou|fico|resido)\s+em\s+([a-záêçõãüé\s]+?)[\s,\/\-]+([A-Z]{2})\b',
            # Padrão: "sou de São Paulo, SP" (captura depois do "de")
            r'(?i)sou\s+de\s+([a-záêçõãüé\s]+?)[\s,\/\-]+([A-Z]{2})\b',
            # Padrão geral: "verbo cidade, estado"
            r'(?i)(?:moro|vivo|estou|fico|resido)\s+([a-záêçõãüé\s]+?)[\s,\/\-]+([A-Z]{2})\b',
            # Padrão: "São Paulo - SP" ou "Belo Horizonte/MG"
            r'(?i)\b([a-záêçõãüé\s]{3,})[\s,\/\-]+([A-Z]{2})\b',
            # Padrão: "SP - São Paulo" (estado primeiro)
            r'(?i)\b([A-Z]{2})[\s,\/\-]+([a-záêçõãüé\s]{3,})\b'
        ]
    
    def extract_location_from_message(self, message: str) -> Optional[Tuple[str, str]]:
        """
        Extrai cidade e estado de uma mensagem do lead.
        
        Args:
            message (str): Mensagem enviada pelo lead
            
        Returns:
            Optional[Tuple[str, str]]: (cidade, estado) ou None se não encontrado
        """
        try:
            # Primeira tentativa: usar padrões regex
            for pattern in self.location_patterns:
                matches = re.findall(pattern, message)
                for match in matches:
                    part1, part2 = match[0].strip(), match[1].strip()
                    
                    # Determinar qual é cidade e qual é estado
                    if len(part1) == 2 and part1.upper() in self.valid_states:
                        # part1 é estado, part2 é cidade
                        state, city = part1.upper(), part2.title()
                    elif len(part2) == 2 and part2.upper() in self.valid_states:
                        # part2 é estado, part1 é cidade
                        city, state = part1.title(), part2.upper()
                    else:
                        continue  # Não conseguiu identificar estado válido
                    
                    # Validações adicionais
                    if self._is_valid_city_name(city) and state in self.valid_states:
                        logger.info(f"✅ Localização extraída: {city}/{state}")
                        return (city, state)
            
            # Segunda tentativa: buscar por cidades conhecidas
            result = self._extract_from_known_cities(message)
            if result:
                return result
            
            logger.info("ℹ️ Localização não identificada na mensagem")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair localização: {str(e)}")
            return None
    
    def _is_valid_city_name(self, city: str) -> bool:
        """
        Valida se o nome da cidade é válido.
        
        Args:
            city (str): Nome da cidade
            
        Returns:
            bool: True se válido
        """
        return (
            len(city) >= 3 and 
            len(city) <= 50 and
            not any(word in city.lower() for word in ['conta', 'luz', 'energia', 'economizar', 'desconto'])
        )
    
    def _extract_from_known_cities(self, message: str) -> Optional[Tuple[str, str]]:
        """
        Tenta extrair localização usando lista de cidades conhecidas.
        
        Args:
            message (str): Mensagem do lead
            
        Returns:
            Optional[Tuple[str, str]]: (cidade, estado) ou None
        """
        message_lower = message.lower()
        for city_lower, state in self.major_cities.items():
            # Busca por palavra completa da cidade
            if re.search(rf'\b{re.escape(city_lower)}\b', message_lower):
                city = city_lower.title()
                logger.info(f"✅ Cidade conhecida identificada: {city}/{state}")
                return (city, state)
        return None
    
    def get_initial_response_prompt(self, lead_message: str) -> str:
        """
        Gera o prompt para a primeira resposta da IA ao lead.
        
        Args:
            lead_message (str): Mensagem enviada pelo lead
            
        Returns:
            str: Prompt formatado para a OpenAI
        """
        return f"""Você é a Serena, assistente virtual da SRna Energia. Um lead interessado em economizar na conta de luz acabou de enviar a mensagem: "{lead_message}"

Sua resposta deve:
1. Agradecer o interesse em economizar com a Serena Energia
2. Explicar brevemente que a Serena oferece energia solar sem instalação
3. Solicitar a cidade e estado do lead para verificar disponibilidade
4. Ser amigável, clara e concisa (máximo 2 parágrafos)
5. Usar emojis moderadamente para humanizar

Exemplo de tom: "Olá! 😊 Que bom que você tem interesse em economizar com a Serena Energia! Nós oferecemos desconto na sua conta de luz através da nossa energia solar, sem precisar instalar nada na sua casa..."

Gere apenas a resposta que será enviada ao lead via WhatsApp:"""

    def get_promotions_response_prompt(
        self, 
        lead_message: str, 
        city: str, 
        state: str, 
        promotions: List[Dict[str, Any]]
    ) -> str:
        """
        Gera prompt para resposta com promoções da API Serena.
        
        Args:
            lead_message (str): Mensagem do lead
            city (str): Cidade detectada
            state (str): Estado detectado
            promotions (List[Dict[str, Any]]): Lista de promoções da API Serena
            
        Returns:
            str: Prompt formatado para a OpenAI
        """
        if promotions:
            # Formatar promoções para o prompt
            promotions_text = []
            for i, promo in enumerate(promotions, 1):
                distributor = promo.get('energyUtilityName', 'Distribuidora')
                discount = promo.get('discountPercentage', 0)
                promotions_text.append(f"{i}. {distributor} - {discount}% de desconto")
            
            promotions_str = "\n".join(promotions_text)
            
            return f"""O lead enviou: "{lead_message}" e você identificou que mora em {city}/{state}.

ÓTIMA NOTÍCIA! Encontramos {len(promotions)} promoções disponíveis para {city}/{state}:

{promotions_str}

Sua resposta deve:
1. Confirmar a localização ({city}/{state})
2. Apresentar as promoções de forma clara e atrativa
3. Explicar que são descontos na conta de luz com energia solar sem instalação
4. Solicitar que envie uma FOTO ou PDF da conta de energia atual
5. Ser entusiasmada e usar emojis moderadamente
6. Máximo 3 parágrafos

Gere apenas a resposta que será enviada ao lead via WhatsApp:"""
        else:
            return f"""O lead enviou: "{lead_message}" e você identificou que mora em {city}/{state}.

INFELIZMENTE não encontramos promoções ativas para {city}/{state} no momento.

Sua resposta deve:
1. Confirmar a localização ({city}/{state})
2. Explicar que não há promoções ativas no momento
3. Pedir para enviar uma FOTO ou PDF da conta de energia mesmo assim
4. Explicar que vamos analisar e buscar alternativas
5. Manter tom positivo e esperançoso
6. Máximo 2 parágrafos

Gere apenas a resposta que será enviada ao lead via WhatsApp:""" 