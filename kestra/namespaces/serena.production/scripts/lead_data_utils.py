#!/usr/bin/env python3
"""
Lead Data Utilities for Serena SDR Agent

Este módulo fornece funções utilitárias para normalização, validação
e processamento de dados de leads para o agente SDR da Serena.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import os
import re
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def normalize_phone_number(phone: str) -> str:
    """
    Normaliza número de telefone para formato padrão.
    
    Args:
        phone (str): Número de telefone em qualquer formato
        
    Returns:
        str: Número normalizado (+5581999887766)
    """
    try:
        # Remove todos os caracteres não numéricos
        digits_only = re.sub(r'[^\d]', '', phone)
        
        # Se não começar com 55, adiciona código do Brasil
        if not digits_only.startswith('55'):
            digits_only = '55' + digits_only
        
        # Adiciona o + no início
        if not digits_only.startswith('+'):
            digits_only = '+' + digits_only
        
        logger.info(f"Phone normalized: {phone} -> {digits_only}")
        return digits_only
        
    except Exception as e:
        logger.error(f"Erro ao normalizar telefone {phone}: {e}")
        return phone

def validate_phone_number(phone: str) -> bool:
    """
    Valida se um número de telefone é válido.
    
    Args:
        phone (str): Número de telefone
        
    Returns:
        bool: True se válido, False caso contrário
    """
    try:
        normalized = normalize_phone_number(phone)
        # Remove o + para contar dígitos
        digits = re.sub(r'[^\d]', '', normalized)
        
        # Deve ter 13 dígitos (55 + DDD + número)
        if len(digits) != 13:
            return False
        
        # DDD deve ser válido (11-99)
        ddd = int(digits[2:4])
        if ddd < 11 or ddd > 99:
            return False
        
        # Número deve começar com 9 (formato novo)
        if digits[4] != '9':
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao validar telefone {phone}: {e}")
        return False

def normalize_lead_name(name: str) -> str:
    """
    Normaliza o nome do lead.
    
    Args:
        name (str): Nome do lead
        
    Returns:
        str: Nome normalizado
    """
    try:
        if not name or name.strip() == "":
            return "Lead WhatsApp"
        
        # Remove espaços extras e capitaliza
        normalized = " ".join(name.strip().split())
        
        # Capitaliza cada palavra
        normalized = " ".join(word.capitalize() for word in normalized.split())
        
        logger.info(f"Name normalized: '{name}' -> '{normalized}'")
        return normalized
        
    except Exception as e:
        logger.error(f"Erro ao normalizar nome {name}: {e}")
        return "Lead WhatsApp"

def normalize_city_name(city: str) -> str:
    """
    Normaliza o nome da cidade.
    
    Args:
        city (str): Nome da cidade
        
    Returns:
        str: Cidade normalizada
    """
    try:
        if not city or city.strip() == "":
            return "N/A"
        
        # Remove espaços extras e capitaliza
        normalized = " ".join(city.strip().split())
        
        # Capitaliza cada palavra
        normalized = " ".join(word.capitalize() for word in normalized.split())
        
        logger.info(f"City normalized: '{city}' -> '{normalized}'")
        return normalized
        
    except Exception as e:
        logger.error(f"Erro ao normalizar cidade {city}: {e}")
        return "N/A"

def normalize_state_name(state: str) -> str:
    """
    Normaliza o nome do estado.
    
    Args:
        state (str): Nome do estado
        
    Returns:
        str: Estado normalizado
    """
    try:
        if not state or state.strip() == "":
            return "N/A"
        
        # Remove espaços extras e capitaliza
        normalized = " ".join(state.strip().split())
        
        # Capitaliza cada palavra
        normalized = " ".join(word.capitalize() for word in normalized.split())
        
        logger.info(f"State normalized: '{state}' -> '{normalized}'")
        return normalized
        
    except Exception as e:
        logger.error(f"Erro ao normalizar estado {state}: {e}")
        return "N/A"

def validate_invoice_amount(amount: Any) -> float:
    """
    Valida e normaliza o valor da conta de energia.
    
    Args:
        amount: Valor da conta (string, int, float)
        
    Returns:
        float: Valor normalizado
    """
    try:
        if amount is None or amount == "":
            return 0.0
        
        # Converte para string e remove caracteres não numéricos
        amount_str = str(amount)
        amount_str = re.sub(r'[^\d.,]', '', amount_str)
        
        # Substitui vírgula por ponto
        amount_str = amount_str.replace(',', '.')
        
        # Converte para float
        amount_float = float(amount_str)
        
        # Valida se é um valor razoável (entre 0 e 10000)
        if amount_float < 0 or amount_float > 10000:
            logger.warning(f"Valor de conta suspeito: {amount_float}")
            return 0.0
        
        logger.info(f"Invoice amount normalized: {amount} -> {amount_float}")
        return amount_float
        
    except Exception as e:
        logger.error(f"Erro ao normalizar valor da conta {amount}: {e}")
        return 0.0

def validate_client_type(client_type: str) -> str:
    """
    Valida e normaliza o tipo de cliente.
    
    Args:
        client_type (str): Tipo de cliente
        
    Returns:
        str: Tipo normalizado
    """
    try:
        if not client_type or client_type.strip() == "":
            return "casa"
        
        normalized = client_type.strip().lower()
        
        # Mapeia tipos válidos
        valid_types = {
            "casa": "casa",
            "residencial": "casa",
            "residência": "casa",
            "residencia": "casa",
            "empresa": "empresa",
            "comercial": "empresa",
            "industrial": "empresa"
        }
        
        normalized = valid_types.get(normalized, "casa")
        
        logger.info(f"Client type normalized: '{client_type}' -> '{normalized}'")
        return normalized
        
    except Exception as e:
        logger.error(f"Erro ao normalizar tipo de cliente {client_type}: {e}")
        return "casa"

def normalize_lead_data(lead_data):
    """
    Normalizes lead data from different sources into a consistent format.
    
    Args:
        lead_data: Raw lead data from database or API
    """
    if not lead_data:
        return {
            'id': None,
            'name': 'Lead WhatsApp',
            'phone': None,
            'email': None,
            'city': 'N/A',
            'state': 'N/A',
            'status': 'new',
            'source': 'whatsapp'
        }
    
    # Handle different data formats
    if isinstance(lead_data, str):
        import json
        try:
            lead_data = json.loads(lead_data)
        except:
            return normalize_lead_data(None)
    
    if isinstance(lead_data, dict) and 'result' in lead_data:
        lead_data = lead_data['result']
    
    if isinstance(lead_data, list) and len(lead_data) > 0:
        lead_data = lead_data[0]
    
    return {
        'id': lead_data.get('id') or lead_data.get('lead_id'),
        'name': lead_data.get('name') or lead_data.get('full_name') or 'Lead WhatsApp',
        'phone': lead_data.get('phone') or lead_data.get('phone_number'),
        'email': lead_data.get('email'),
        'city': lead_data.get('city') or 'N/A',
        'state': lead_data.get('state') or 'N/A',
        'status': lead_data.get('status') or 'new',
        'source': lead_data.get('source') or 'whatsapp'
    }

def normalize_lead_data_legacy(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza todos os dados de um lead (versão legacy).
    
    Args:
        lead_data (Dict[str, Any]): Dados do lead
        
    Returns:
        Dict[str, Any]: Dados normalizados
    """
    try:
        logger.info("Normalizando dados do lead")
        
        normalized = {}
        
        # Normaliza telefone
        if "phone_number" in lead_data:
            normalized["phone_number"] = normalize_phone_number(lead_data["phone_number"])
        
        # Normaliza nome
        if "name" in lead_data:
            normalized["name"] = normalize_lead_name(lead_data["name"])
        
        # Normaliza cidade
        if "city" in lead_data:
            normalized["city"] = normalize_city_name(lead_data["city"])
        
        # Normaliza estado
        if "state" in lead_data:
            normalized["state"] = normalize_state_name(lead_data["state"])
        
        # Normaliza valor da conta
        if "invoice_amount" in lead_data:
            normalized["invoice_amount"] = validate_invoice_amount(lead_data["invoice_amount"])
        
        # Normaliza tipo de cliente
        if "client_type" in lead_data:
            normalized["client_type"] = validate_client_type(lead_data["client_type"])
        
        # Adiciona timestamp
        normalized["normalized_at"] = datetime.now().isoformat()
        
        logger.info(f"Dados normalizados: {normalized}")
        return normalized
        
    except Exception as e:
        logger.error(f"Erro ao normalizar dados do lead: {e}")
        return lead_data

def extract_lead_from_message(message_data):
    """
    Extracts lead information from WhatsApp message data.
    
    Args:
        message_data: WhatsApp webhook message data
    """
    return {
        'phone': message_data.get('phone'),
        'message': message_data.get('message'),
        'type': message_data.get('type', 'text'),
        'timestamp': message_data.get('timestamp')
    }

def extract_lead_from_message_legacy(message: str) -> Dict[str, Any]:
    """
    Extrai informações de lead de uma mensagem de texto (versão legacy).
    
    Args:
        message (str): Mensagem do usuário
        
    Returns:
        Dict[str, Any]: Dados extraídos
    """
    try:
        logger.info(f"Extraindo dados de lead da mensagem: {message[:100]}...")
        
        extracted_data = {}
        
        # Padrões para extração
        patterns = {
            "name": [
                r"meu nome é (\w+)",
                r"chamo (\w+)",
                r"sou (\w+)",
                r"nome (\w+)"
            ],
            "city": [
                r"moro em (\w+)",
                r"cidade (\w+)",
                r"em (\w+)",
                r"de (\w+)"
            ],
            "invoice_amount": [
                r"conta de (\d+)",
                r"pago (\d+)",
                r"valor (\d+)",
                r"R\$ (\d+)"
            ]
        }
        
        message_lower = message.lower()
        
        # Extrai nome
        for pattern in patterns["name"]:
            match = re.search(pattern, message_lower)
            if match:
                extracted_data["name"] = match.group(1).capitalize()
                break
        
        # Extrai cidade
        for pattern in patterns["city"]:
            match = re.search(pattern, message_lower)
            if match:
                extracted_data["city"] = match.group(1).capitalize()
                break
        
        # Extrai valor da conta
        for pattern in patterns["invoice_amount"]:
            match = re.search(pattern, message_lower)
            if match:
                extracted_data["invoice_amount"] = float(match.group(1))
                break
        
        logger.info(f"Dados extraídos: {extracted_data}")
        return extracted_data
        
    except Exception as e:
        logger.error(f"Erro ao extrair dados da mensagem: {e}")
        return {}

def validate_lead_completeness(lead_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida se os dados do lead estão completos.
    
    Args:
        lead_data (Dict[str, Any]): Dados do lead
        
    Returns:
        Tuple[bool, List[str]]: (está completo, campos faltantes)
    """
    try:
        required_fields = ["phone_number", "name"]
        optional_fields = ["city", "state", "invoice_amount", "client_type"]
        
        missing_fields = []
        
        # Verifica campos obrigatórios
        for field in required_fields:
            if field not in lead_data or not lead_data[field]:
                missing_fields.append(field)
        
        is_complete = len(missing_fields) == 0
        
        logger.info(f"Validação de completude: {is_complete}, campos faltantes: {missing_fields}")
        return is_complete, missing_fields
        
    except Exception as e:
        logger.error(f"Erro ao validar completude: {e}")
        return False, ["erro_na_validacao"]

def create_lead_summary(lead_data: Dict[str, Any]) -> str:
    """
    Cria um resumo dos dados do lead.
    
    Args:
        lead_data (Dict[str, Any]): Dados do lead
        
    Returns:
        str: Resumo formatado
    """
    try:
        summary_parts = []
        
        if "name" in lead_data and lead_data["name"]:
            summary_parts.append(f"Nome: {lead_data['name']}")
        
        if "phone_number" in lead_data and lead_data["phone_number"]:
            summary_parts.append(f"Telefone: {lead_data['phone_number']}")
        
        if "city" in lead_data and lead_data["city"] != "N/A":
            summary_parts.append(f"Cidade: {lead_data['city']}")
        
        if "state" in lead_data and lead_data["state"] != "N/A":
            summary_parts.append(f"Estado: {lead_data['state']}")
        
        if "invoice_amount" in lead_data and lead_data["invoice_amount"] > 0:
            summary_parts.append(f"Conta: R$ {lead_data['invoice_amount']:.2f}")
        
        if "client_type" in lead_data and lead_data["client_type"]:
            summary_parts.append(f"Tipo: {lead_data['client_type']}")
        
        summary = " | ".join(summary_parts)
        logger.info(f"Resumo do lead criado: {summary}")
        return summary
        
    except Exception as e:
        logger.error(f"Erro ao criar resumo: {e}")
        return "Dados do lead não disponíveis"

def sanitize_lead_data(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitiza dados do lead removendo informações sensíveis.
    
    Args:
        lead_data (Dict[str, Any]): Dados do lead
        
    Returns:
        Dict[str, Any]: Dados sanitizados
    """
    try:
        sanitized = lead_data.copy()
        
        # Mascara telefone (mantém apenas últimos 4 dígitos)
        if "phone_number" in sanitized:
            phone = sanitized["phone_number"]
            if len(phone) > 4:
                sanitized["phone_number"] = "*" * (len(phone) - 4) + phone[-4:]
        
        # Remove dados sensíveis
        sensitive_fields = ["cpf", "cnpj", "rg", "passport"]
        for field in sensitive_fields:
            if field in sanitized:
                del sanitized[field]
        
        logger.info("Dados sanitizados com sucesso")
        return sanitized
        
    except Exception as e:
        logger.error(f"Erro ao sanitizar dados: {e}")
        return lead_data

if __name__ == "__main__":
    # Teste das funcionalidades
    print("=== Teste do Lead Data Utils ===")
    
    # Teste de normalização de telefone
    phone = "81999887766"
    normalized_phone = normalize_phone_number(phone)
    print(f"Telefone normalizado: {phone} -> {normalized_phone}")
    
    # Teste de validação
    is_valid = validate_phone_number(normalized_phone)
    print(f"Telefone válido: {is_valid}")
    
    # Teste de normalização de dados
    lead_data = {
        "phone_number": "81999887766",
        "name": "joão silva",
        "city": "recife",
        "state": "pernambuco",
        "invoice_amount": "150,50",
        "client_type": "residencial"
    }
    
    normalized = normalize_lead_data_legacy(lead_data)
    print(f"Dados normalizados: {normalized}")
    
    # Teste de extração de mensagem
    message = "Olá, meu nome é Maria e moro em São Paulo, minha conta é de 200 reais"
    extracted = extract_lead_from_message_legacy(message)
    print(f"Dados extraídos: {extracted}")
    
    # Teste de validação de completude
    is_complete, missing = validate_lead_completeness(normalized)
    print(f"Está completo: {is_complete}, campos faltantes: {missing}")
    
    # Teste de resumo
    summary = create_lead_summary(normalized)
    print(f"Resumo: {summary}") 