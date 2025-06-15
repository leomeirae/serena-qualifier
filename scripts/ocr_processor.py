"""
OCR Processor para Contas de Energia - Versão Estruturada
Extrai campos importantes: TOTAL A PAGAR, nome do cliente, endereço, distribuidora, consumo, vencimento
Implementa validação robusta e suporte a múltiplas distribuidoras
"""

import os
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Distribuidoras conhecidas no Brasil
DISTRIBUIDORAS_CONHECIDAS = {
    "CEMIG": ["CEMIG", "COMPANHIA ENERGÉTICA DE MINAS GERAIS"],
    "CPFL": ["CPFL", "COMPANHIA PAULISTA DE FORÇA E LUZ"],
    "ENEL": ["ENEL", "ENEL DISTRIBUIÇÃO"],
    "LIGHT": ["LIGHT", "LIGHT SERVIÇOS DE ELETRICIDADE"],
    "COPEL": ["COPEL", "COMPANHIA PARANAENSE DE ENERGIA"],
    "CELPE": ["CELPE", "COMPANHIA ENERGÉTICA DE PERNAMBUCO"],
    "COELBA": ["COELBA", "COMPANHIA DE ELETRICIDADE DO ESTADO DA BAHIA"],
    "ENERGISA": ["ENERGISA", "ENERGISA DISTRIBUIÇÃO"],
    "ELEKTRO": ["ELEKTRO", "ELEKTRO REDES"],
    "BANDEIRANTE": ["BANDEIRANTE", "EDP BANDEIRANTE"],
    "EDP": ["EDP", "EDP BRASIL"],
    "CELESC": ["CELESC", "CENTRAIS ELÉTRICAS DE SANTA CATARINA"],
    "RGE": ["RGE", "RIO GRANDE ENERGIA"],
    "CEEE": ["CEEE", "COMPANHIA ESTADUAL DE ENERGIA ELÉTRICA"],
    "AMAZONAS": ["AMAZONAS ENERGIA", "AMAZONAS DISTRIBUIDORA"],
    "BOA_VISTA": ["BOA VISTA ENERGIA", "RORAIMA ENERGIA"],
    "CERON": ["CERON", "CENTRAIS ELÉTRICAS DE RONDÔNIA"],
    "ELETROACRE": ["ELETROACRE", "COMPANHIA DE ELETRICIDADE DO ACRE"],
    "CELG": ["CELG", "COMPANHIA ENERGÉTICA DE GOIÁS"],
    "CEB": ["CEB", "COMPANHIA ENERGÉTICA DE BRASÍLIA"]
}

# Padrões regex melhorados para extração estruturada
EXTRACTION_PATTERNS = {
    # Valores monetários - múltiplos padrões
    "total_a_pagar": [
        r"TOTAL\s+A?\s*PAGAR[:\s]*(R\$\s*[\d.,]+)",
        r"VALOR\s+TOTAL[:\s]*(R\$\s*[\d.,]+)",
        r"TOTAL\s+GERAL[:\s]*(R\$\s*[\d.,]+)",
        r"VALOR\s+A\s+PAGAR[:\s]*(R\$\s*[\d.,]+)"
    ],
    
    # Nome do cliente - padrões variados
    "nome_cliente": [
        r"CLIENTE[:\s]*([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ\s]{10,60})(?:\s+[A-Z]{3}|$|\n)",
        r"NOME[:\s]*([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ\s]{10,60})(?:\s+[A-Z]{3}|$|\n)",
        r"TITULAR[:\s]*([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ\s]{10,60})(?:\s+[A-Z]{3}|$|\n)",
        r"CONSUMIDOR[:\s]*([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ\s]{10,60})(?:\s+[A-Z]{3}|$|\n)"
    ],
    
    # CPF/CNPJ
    "cpf_cnpj": [
        r"CPF[:\s]*([\d*.\-/]+)",
        r"CNPJ[:\s]*([\d*.\-/]+)",
        r"DOC[:\s]*([\d*.\-/]+)"
    ],
    
    # Endereço
    "endereco": [
        r"ENDEREÇO[:\s]*([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ0-9\s,.\-/]+?)(?:\s+CIDADE|\n|$)",
        r"END[:\s]*([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ0-9\s,.\-/]+?)(?:\s+CIDADE|\n|$)",
        r"LOGRADOURO[:\s]*([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ0-9\s,.\-/]+?)(?:\s+CIDADE|\n|$)"
    ],
    
    # Cidade/Estado
    "cidade": [
        r"CIDADE[:\s]*([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ\s\-]+)",
        r"MUNICÍPIO[:\s]*([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ\s\-]+)",
        r"([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ\s]+)\s*-\s*([A-Z]{2})"  # Formato "CIDADE - UF"
    ],
    
    # Mês de referência
    "mes_referencia": [
        r"REFERÊNCIA[:\s]*([A-Z]{3}/\d{4})",
        r"MÊS[:\s]*([A-Z]{3}/\d{4})",
        r"PERÍODO[:\s]*([A-Z]{3}/\d{4})",
        r"(\d{2}/\d{4})"  # MM/YYYY
    ],
    
    # Consumo em kWh
    "consumo_kwh": [
        r"CONSUMO[:\s]*(\d+)\s*kWh",
        r"ENERGIA\s+ELÉTRICA[:\s]*(\d+)\s*kWh",
        r"kWh[:\s]*(\d+)",
        r"(\d+)\s*kWh"
    ],
    
    # Data de vencimento
    "vencimento": [
        r"VENCIMENTO[:\s]*(\d{2}/\d{2}/\d{4})",
        r"VENCE\s+EM[:\s]*(\d{2}/\d{2}/\d{4})",
        r"DATA\s+LIMITE[:\s]*(\d{2}/\d{2}/\d{4})"
    ],
    
    # Número da instalação/UC
    "numero_instalacao": [
        r"INSTALAÇÃO[:\s]*(\d+)",
        r"UC[:\s]*(\d+)",
        r"UNIDADE\s+CONSUMIDORA[:\s]*(\d+)"
    ]
}

# Dados simulados para demonstração (mantidos para compatibilidade)
SIMULATED_OCR_DATA = {
    "cpf_9876": {
        "nome_cliente": "MARIA SILVA SANTOS",
        "endereco": "RUA DAS FLORES, 123 - CENTRO",
        "cidade": "BELO HORIZONTE - MG",
        "distribuidora": "CEMIG",
        "total_a_pagar": "R$ 387,45",
        "valor_numerico": 387.45,
        "mes_referencia": "DEZ/2024",
        "consumo_kwh": "450",
        "vencimento": "15/01/2025",
        "numero_instalacao": "123456789"
    },
    "cpf_1234": {
        "nome_cliente": "JOÃO PEREIRA LIMA", 
        "endereco": "AV PAULISTA, 1000 - BELA VISTA",
        "cidade": "SÃO PAULO - SP",
        "distribuidora": "ENEL",
        "total_a_pagar": "R$ 156,78",
        "valor_numerico": 156.78,
        "mes_referencia": "DEZ/2024",
        "consumo_kwh": "280",
        "vencimento": "20/01/2025",
        "numero_instalacao": "987654321"
    },
    "cpf_5555": {
        "nome_cliente": "CARLOS EDUARDO ROCHA",
        "endereco": "RUA BOA VISTA, 456 - COPACABANA",
        "cidade": "RIO DE JANEIRO - RJ",
        "distribuidora": "LIGHT",
        "total_a_pagar": "R$ 623,12",
        "valor_numerico": 623.12,
        "mes_referencia": "DEZ/2024",
        "consumo_kwh": "720",
        "vencimento": "10/01/2025",
        "numero_instalacao": "555666777"
    }
}


def identify_distribuidora(ocr_text: str) -> Optional[str]:
    """
    Identifica a distribuidora de energia com base no texto OCR
    
    Args:
        ocr_text: Texto extraído da conta via OCR
        
    Returns:
        str: Nome da distribuidora identificada ou None
    """
    ocr_upper = ocr_text.upper()
    
    for distribuidora, aliases in DISTRIBUIDORAS_CONHECIDAS.items():
        for alias in aliases:
            if alias in ocr_upper:
                logger.info(f"✅ Distribuidora identificada: {distribuidora} (via '{alias}')")
                return distribuidora
    
    logger.warning("⚠️ Distribuidora não identificada no texto OCR")
    return None


def extract_with_multiple_patterns(text: str, patterns: List[str]) -> Optional[str]:
    """
    Tenta extrair informação usando múltiplos padrões regex
    
    Args:
        text: Texto para buscar
        patterns: Lista de padrões regex para tentar
        
    Returns:
        str: Primeiro match encontrado ou None
    """
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            result = match.group(1).strip()
            if result:  # Não retornar strings vazias
                # Limpeza adicional para nomes - remover palavras-chave comuns no final
                if any(keyword in pattern.upper() for keyword in ["CLIENTE", "NOME", "TITULAR"]):
                    # Remove palavras comuns que podem aparecer após o nome
                    cleanup_words = ["CPF", "CNPJ", "TOTAL", "VALOR", "ENDEREÇO", "END"]
                    for word in cleanup_words:
                        if word in result.upper():
                            result = result[:result.upper().find(word)].strip()
                            break
                return result
    return None


def validate_extracted_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida e normaliza dados extraídos
    
    Args:
        data: Dados extraídos do OCR
        
    Returns:
        Dict com dados validados e score de confiança
    """
    validation_result = {
        "is_valid": True,
        "confidence_score": 0.0,
        "validation_errors": [],
        "warnings": []
    }
    
    confidence_points = 0
    max_points = 8
    
    # Validar valor monetário
    if data.get("valor_numerico", 0) > 0:
        confidence_points += 2
        if data["valor_numerico"] > 1000:
            validation_result["warnings"].append("Valor muito alto (>R$ 1000)")
    else:
        validation_result["validation_errors"].append("Valor monetário não encontrado ou inválido")
    
    # Validar nome do cliente
    if data.get("nome_cliente") and len(data["nome_cliente"]) >= 10:
        confidence_points += 2
    else:
        validation_result["validation_errors"].append("Nome do cliente não encontrado ou muito curto")
    
    # Validar distribuidora
    if data.get("distribuidora"):
        confidence_points += 1
    else:
        validation_result["warnings"].append("Distribuidora não identificada")
    
    # Validar consumo
    if data.get("consumo_kwh"):
        try:
            consumo = int(data["consumo_kwh"])
            if 0 < consumo < 10000:  # Range razoável
                confidence_points += 1
            else:
                validation_result["warnings"].append(f"Consumo fora do range esperado: {consumo} kWh")
        except ValueError:
            validation_result["warnings"].append("Consumo em formato inválido")
    
    # Validar vencimento
    if data.get("vencimento"):
        try:
            venc_date = datetime.strptime(data["vencimento"], "%d/%m/%Y")
            hoje = datetime.now()
            if venc_date < hoje - timedelta(days=365):  # Muito antigo
                validation_result["warnings"].append("Data de vencimento muito antiga")
            elif venc_date > hoje + timedelta(days=365):  # Muito futuro
                validation_result["warnings"].append("Data de vencimento muito no futuro")
            else:
                confidence_points += 1
        except ValueError:
            validation_result["warnings"].append("Data de vencimento em formato inválido")
    
    # Validar endereço
    if data.get("endereco") and len(data["endereco"]) >= 15:
        confidence_points += 1
    else:
        validation_result["warnings"].append("Endereço não encontrado ou muito curto")
    
    # Calcular score de confiança
    validation_result["confidence_score"] = confidence_points / max_points
    
    # Determinar se é válido (pelo menos 50% de confiança)
    if validation_result["confidence_score"] < 0.5:
        validation_result["is_valid"] = False
    
    logger.info(f"📊 Validação: {confidence_points}/{max_points} pontos (confiança: {validation_result['confidence_score']:.2%})")
    
    return validation_result


async def download_whatsapp_media(media_id: str, access_token: str) -> Optional[bytes]:
    """
    Download media file from WhatsApp Business API
    
    Args:
        media_id: WhatsApp media ID
        access_token: WhatsApp API access token
        
    Returns:
        bytes: Media file content or None if failed
    """
    try:
        # Step 1: Get media URL
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        media_info = response.json()
        media_url = media_info.get("url")
        
        if not media_url:
            logger.error("❌ Media URL not found in response")
            return None
            
        # Step 2: Download media content
        media_response = requests.get(media_url, headers=headers)
        media_response.raise_for_status()
        
        logger.info(f"✅ Media downloaded successfully: {len(media_response.content)} bytes")
        return media_response.content
        
    except Exception as e:
        logger.error(f"❌ Error downloading media {media_id}: {str(e)}")
        return None


def extract_valor_numerico(texto_valor: str) -> float:
    """
    Extrai valor numérico de string monetária brasileira
    
    Args:
        texto_valor: String como "R$ 387,45"
        
    Returns:
        float: Valor numérico ou 0.0 se não conseguir extrair
    """
    try:
        # Remove R$, espaços, pontos (milhares)
        cleaned = re.sub(r'[R$\s\.]', '', texto_valor)
        # Substitui vírgula por ponto decimal
        cleaned = cleaned.replace(',', '.')
        return float(cleaned)
    except:
        return 0.0


def extract_conta_energia_fields(ocr_text: str) -> Dict[str, Any]:
    """
    Extrai campos específicos de conta de energia usando regex estruturado
    
    Args:
        ocr_text: Texto extraído da conta via OCR
        
    Returns:
        Dict com campos extraídos e metadados de validação
    """
    try:
        logger.info("🔍 Iniciando extração estruturada de dados da conta de energia")
        
        resultado = {
            "nome_cliente": None,
            "cpf_cnpj": None,
            "endereco": None,
            "cidade": None,
            "distribuidora": None,
            "total_a_pagar": None,
            "valor_numerico": 0.0,
            "mes_referencia": None,
            "consumo_kwh": None,
            "vencimento": None,
            "numero_instalacao": None,
            "extraction_timestamp": datetime.now().isoformat(),
            "ocr_method": "structured_extraction"
        }
        
        # Normalizar texto para melhor extração
        ocr_normalized = ocr_text.upper().replace('\n', ' ').replace('\r', ' ')
        
        # Identificar distribuidora primeiro
        resultado["distribuidora"] = identify_distribuidora(ocr_text)
        
        # Extrair cada campo usando múltiplos padrões
        for campo, patterns in EXTRACTION_PATTERNS.items():
            extracted_value = extract_with_multiple_patterns(ocr_normalized, patterns)
            if extracted_value:
                resultado[campo] = extracted_value.strip()
                logger.info(f"✅ {campo}: {extracted_value[:50]}...")
        
        # Processar valor numérico
        if resultado["total_a_pagar"]:
            resultado["valor_numerico"] = extract_valor_numerico(resultado["total_a_pagar"])
        
        # Validar dados extraídos
        validation = validate_extracted_data(resultado)
        resultado.update({
            "validation": validation,
            "confidence_score": validation["confidence_score"],
            "is_valid_extraction": validation["is_valid"]
        })
        
        logger.info(f"📊 Extração concluída - Confiança: {validation['confidence_score']:.2%}")
        logger.info(f"📋 Campos extraídos: {json.dumps({k: v for k, v in resultado.items() if v and k not in ['validation']}, indent=2, ensure_ascii=False)}")
        
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro na extração estruturada: {str(e)}")
        return {
            "error": str(e), 
            "valor_numerico": 0.0,
            "extraction_timestamp": datetime.now().isoformat(),
            "ocr_method": "structured_extraction_failed"
        }


def simulate_ocr_processing(phone_number: str) -> Dict[str, Any]:
    """
    Simula processamento OCR baseado no telefone do lead
    Para demonstração até termos OCR real
    
    Args:
        phone_number: Número do telefone do lead
        
    Returns:
        Dict com dados simulados da conta
    """
    try:
        # Determinar qual conta simular baseado no telefone
        if "9876" in phone_number:
            simulated_data = SIMULATED_OCR_DATA["cpf_9876"].copy()
        elif "1234" in phone_number:
            simulated_data = SIMULATED_OCR_DATA["cpf_1234"].copy()
        elif "5555" in phone_number:
            simulated_data = SIMULATED_OCR_DATA["cpf_5555"].copy()
        else:
            # Dados padrão para outros números
            simulated_data = {
                "nome_cliente": "CLIENTE TESTE",
                "endereco": "RUA EXEMPLO, 123 - CENTRO",
                "cidade": "CIDADE EXEMPLO - UF",
                "distribuidora": "CEMIG",
                "total_a_pagar": "R$ 325,50",
                "valor_numerico": 325.50,
                "mes_referencia": "DEZ/2024",
                "consumo_kwh": "380",
                "vencimento": "25/01/2025",
                "numero_instalacao": "111222333"
            }
        
        # Adicionar metadados do processamento estruturado
        simulated_data.update({
            "extraction_timestamp": datetime.now().isoformat(),
            "ocr_method": "simulated_structured",
            "confidence_score": 0.95,
            "is_valid_extraction": True,
            "validation": {
                "is_valid": True,
                "confidence_score": 0.95,
                "validation_errors": [],
                "warnings": ["Dados simulados para demonstração"]
            }
        })
        
        logger.info(f"🎭 Simulação OCR para {phone_number}: {simulated_data['nome_cliente']}")
        return simulated_data
        
    except Exception as e:
        logger.error(f"❌ Erro na simulação OCR: {str(e)}")
        return {
            "error": str(e),
            "valor_numerico": 0.0,
            "extraction_timestamp": datetime.now().isoformat(),
            "ocr_method": "simulated_failed"
        }


def validate_conta_energia(ocr_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida dados extraídos da conta de energia usando validação estruturada
    
    Args:
        ocr_data: Dados extraídos via OCR
        
    Returns:
        Dict com resultado da validação e score de qualificação
    """
    try:
        logger.info("🔍 Iniciando validação estruturada da conta de energia")
        
        # Se já tem validação interna, usar como base
        if "validation" in ocr_data:
            base_validation = ocr_data["validation"]
        else:
            # Executar validação estruturada
            base_validation = validate_extracted_data(ocr_data)
        
        # Validação específica para qualificação de leads
        validacao = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "qualification_score": 0,
            "extraction_confidence": base_validation.get("confidence_score", 0.0),
            "distribuidora_identificada": bool(ocr_data.get("distribuidora")),
            "dados_completos": False
        }
        
        valor_numerico = ocr_data.get("valor_numerico", 0.0)
        
        # VALIDAÇÃO PRINCIPAL: Valor mínimo R$ 200 (regra de negócio Serena)
        if valor_numerico < 200.0:
            validacao["is_valid"] = False
            validacao["errors"].append(f"Valor da conta muito baixo: R$ {valor_numerico:.2f} (mínimo R$ 200,00)")
            validacao["qualification_score"] = 10  # Score baixo
        else:
            # Score baseado no valor da conta (regra Serena)
            if valor_numerico >= 500:
                validacao["qualification_score"] = 95
            elif valor_numerico >= 350:
                validacao["qualification_score"] = 85
            elif valor_numerico >= 250:
                validacao["qualification_score"] = 75
            else:
                validacao["qualification_score"] = 65
        
        # Validação de nome do cliente (crítico para qualificação)
        nome_cliente = ocr_data.get("nome_cliente", "")
        if not nome_cliente or len(nome_cliente) < 10:
            validacao["errors"].append("Nome do cliente não identificado ou muito curto")
            validacao["qualification_score"] = max(0, validacao["qualification_score"] - 20)
        
        # Validação de distribuidora (importante para cobertura)
        if not ocr_data.get("distribuidora"):
            validacao["warnings"].append("Distribuidora não identificada - verificar cobertura manualmente")
            validacao["qualification_score"] = max(0, validacao["qualification_score"] - 5)
        
        # Validações complementares
        if not ocr_data.get("endereco"):
            validacao["warnings"].append("Endereço não identificado")
            
        if not ocr_data.get("consumo_kwh"):
            validacao["warnings"].append("Consumo kWh não identificado")
        
        # Validação de CPF/CNPJ
        cpf_cnpj = ocr_data.get("cpf_cnpj", "")
        if not cpf_cnpj or len(cpf_cnpj) < 10:
            validacao["warnings"].append("CPF/CNPJ não identificado ou inválido")
        
        # Verificar se tem dados completos para qualificação
        campos_essenciais = ["nome_cliente", "valor_numerico", "endereco"]
        campos_presentes = sum(1 for campo in campos_essenciais if ocr_data.get(campo))
        validacao["dados_completos"] = campos_presentes >= 2
        
        # Ajustar score baseado na confiança da extração
        confidence_bonus = int(base_validation.get("confidence_score", 0.0) * 10)
        validacao["qualification_score"] = min(100, validacao["qualification_score"] + confidence_bonus)
        
        # Determinar se é válido para qualificação (score >= 65 e sem erros críticos)
        if validacao["qualification_score"] < 65 or validacao["errors"]:
            validacao["is_valid"] = False
        
        logger.info(f"✅ Validação estruturada concluída:")
        logger.info(f"   📊 Score de qualificação: {validacao['qualification_score']}")
        logger.info(f"   🎯 Válido para qualificação: {validacao['is_valid']}")
        logger.info(f"   🏢 Distribuidora: {ocr_data.get('distribuidora', 'Não identificada')}")
        logger.info(f"   💰 Valor: R$ {valor_numerico:.2f}")
        
        return validacao
        
    except Exception as e:
        logger.error(f"❌ Erro na validação estruturada: {str(e)}")
        return {
            "is_valid": False,
            "errors": [f"Erro na validação: {str(e)}"],
            "qualification_score": 0,
            "extraction_confidence": 0.0,
            "distribuidora_identificada": False,
            "dados_completos": False
        }


async def process_conta_energia_file(media_id: str, phone_number: str) -> Dict[str, Any]:
    """
    Processa arquivo de conta de energia completo
    
    Args:
        media_id: ID da mídia no WhatsApp
        phone_number: Telefone do lead
        
    Returns:
        Dict com resultado completo do processamento
    """
    try:
        resultado = {
            "success": False,
            "media_id": media_id,
            "phone_number": phone_number,
            "processing_method": "simulation",
            "timestamp": datetime.now().isoformat()
        }
        
        # Usar dados simulados para demonstração
        logger.info(f"🎭 Processando conta simulada para {phone_number}")
        ocr_data = simulate_ocr_processing(phone_number)
        
        if ocr_data.get("error"):
            resultado["error"] = ocr_data["error"]
            return resultado
        
        # Validar dados extraídos
        validacao = validate_conta_energia(ocr_data)
        
        # Consolidar resultado final
        resultado.update({
            "success": True,
            "extracted_data": ocr_data,
            "validation": validacao,
            "is_qualified": validacao["is_valid"] and validacao["qualification_score"] >= 65,
            "qualification_score": validacao["qualification_score"],
            "valor_conta": ocr_data.get("valor_numerico", 0.0),
            "nome_cliente": ocr_data.get("nome_cliente"),
            "endereco": ocr_data.get("endereco"),
            "cidade": ocr_data.get("cidade")
        })
        
        logger.info(f"🎯 Processamento concluído - Qualificado: {resultado['is_qualified']}")
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro no processamento da conta: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "media_id": media_id,
            "phone_number": phone_number,
            "timestamp": datetime.now().isoformat()
        }


# Função para teste direto
if __name__ == "__main__":
    import asyncio
    
    async def test_ocr():
        print("🧪 Testando OCR Processor")
        
        # Teste com diferentes números
        test_phones = ["+5511999999876", "+5511888881234", "+5511777775555"]
        
        for phone in test_phones:
            print(f"\n📱 Testando {phone}:")
            result = await process_conta_energia_file("test_media_id", phone)
            print(f"✅ Qualificado: {result.get('is_qualified')}")
            print(f"💰 Valor: R$ {result.get('valor_conta', 0):.2f}")
            print(f"👤 Cliente: {result.get('nome_cliente')}")
    
    asyncio.run(test_ocr()) 