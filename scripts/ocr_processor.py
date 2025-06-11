"""
OCR Processor para Contas de Energia
Extrai campos importantes: TOTAL A PAGAR, nome do cliente, endereço
"""

import os
import re
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dados simulados para demonstração
SIMULATED_OCR_DATA = {
    "cpf_9876": {
        "nome_cliente": "MARIA SILVA SANTOS",
        "endereco": "RUA DAS FLORES, 123 - CENTRO",
        "cidade": "BELO HORIZONTE",
        "total_a_pagar": "R$ 387,45",
        "valor_numerico": 387.45,
        "mes_referencia": "DEZ/2024",
        "consumo_kwh": "450"
    },
    "cpf_1234": {
        "nome_cliente": "JOÃO PEREIRA LIMA", 
        "endereco": "AV PAULISTA, 1000 - BELA VISTA",
        "cidade": "SÃO PAULO",
        "total_a_pagar": "R$ 156,78",
        "valor_numerico": 156.78,
        "mes_referencia": "DEZ/2024",
        "consumo_kwh": "280"
    },
    "cpf_5555": {
        "nome_cliente": "CARLOS EDUARDO ROCHA",
        "endereco": "RUA BOA VISTA, 456 - COPACABANA",
        "cidade": "RIO DE JANEIRO",
        "total_a_pagar": "R$ 623,12",
        "valor_numerico": 623.12,
        "mes_referencia": "DEZ/2024",
        "consumo_kwh": "720"
    }
}


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
    Extrai campos específicos de conta de energia usando regex
    
    Args:
        ocr_text: Texto extraído da conta via OCR
        
    Returns:
        Dict com campos extraídos
    """
    try:
        resultado = {
            "nome_cliente": None,
            "cpf": None,
            "endereco": None,
            "cidade": None,
            "total_a_pagar": None,
            "valor_numerico": 0.0,
            "mes_referencia": None,
            "consumo_kwh": None,
            "vencimento": None,
            "ocr_confidence": 0.85  # Simulado
        }
        
        # Padrões regex para extrair campos
        patterns = {
            "total_a_pagar": r"TOTAL\s+A?\s*PAGAR[:\s]*(R\$\s*[\d.,]+)",
            "nome_cliente": r"CLIENTE[:\s]*([A-Z\s]{10,50})",
            "cpf": r"CPF[:\s]*([\d*.\-]+)",
            "endereco": r"ENDEREÇO[:\s]*([A-Z0-9\s,.-]+)",
            "mes_referencia": r"REFERÊNCIA[:\s]*([A-Z]{3}/\d{4})",
            "consumo_kwh": r"CONSUMO[:\s]*(\d+)\s*kWh",
            "vencimento": r"VENCIMENTO[:\s]*(\d{2}/\d{2}/\d{4})"
        }
        
        for campo, pattern in patterns.items():
            match = re.search(pattern, ocr_text.upper())
            if match:
                resultado[campo] = match.group(1).strip()
        
        # Processar valor numérico
        if resultado["total_a_pagar"]:
            resultado["valor_numerico"] = extract_valor_numerico(resultado["total_a_pagar"])
        
        logger.info(f"📊 Campos extraídos: {json.dumps(resultado, indent=2, ensure_ascii=False)}")
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro ao extrair campos: {str(e)}")
        return {"error": str(e), "valor_numerico": 0.0}


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
                "endereco": "RUA EXEMPLO, 123",
                "cidade": "CIDADE EXEMPLO",
                "total_a_pagar": "R$ 325,50",
                "valor_numerico": 325.50,
                "mes_referencia": "DEZ/2024",
                "consumo_kwh": "380"
            }
        
        # Adicionar metadados do processamento
        simulated_data.update({
            "processing_timestamp": datetime.now().isoformat(),
            "ocr_method": "simulated",
            "confidence_score": 0.92
        })
        
        logger.info(f"🎭 OCR simulado para {phone_number}: {simulated_data['nome_cliente']}")
        return simulated_data
        
    except Exception as e:
        logger.error(f"❌ Erro na simulação OCR: {str(e)}")
        return {"error": str(e), "valor_numerico": 0.0}


def validate_conta_energia(ocr_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida dados extraídos da conta de energia
    
    Args:
        ocr_data: Dados extraídos via OCR
        
    Returns:
        Dict com resultado da validação
    """
    try:
        validacao = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "qualification_score": 0
        }
        
        valor_numerico = ocr_data.get("valor_numerico", 0.0)
        
        # VALIDAÇÃO PRINCIPAL: Valor mínimo R$ 200
        if valor_numerico < 200.0:
            validacao["is_valid"] = False
            validacao["errors"].append(f"Valor da conta muito baixo: R$ {valor_numerico:.2f} (mínimo R$ 200,00)")
            validacao["qualification_score"] = 10  # Score baixo
        else:
            # Score baseado no valor da conta
            if valor_numerico >= 500:
                validacao["qualification_score"] = 95
            elif valor_numerico >= 350:
                validacao["qualification_score"] = 85
            elif valor_numerico >= 250:
                validacao["qualification_score"] = 75
            else:
                validacao["qualification_score"] = 65
        
        # Validações opcionais
        if not ocr_data.get("nome_cliente"):
            validacao["warnings"].append("Nome do cliente não identificado")
        
        if not ocr_data.get("endereco"):
            validacao["warnings"].append("Endereço não identificado")
            
        if not ocr_data.get("consumo_kwh"):
            validacao["warnings"].append("Consumo kWh não identificado")
        
        # Validação de CPF mascarado
        cpf = ocr_data.get("cpf", "")
        if not cpf or len(cpf) < 10:
            validacao["warnings"].append("CPF não identificado ou inválido")
        
        logger.info(f"✅ Validação concluída - Score: {validacao['qualification_score']}")
        return validacao
        
    except Exception as e:
        logger.error(f"❌ Erro na validação: {str(e)}")
        return {
            "is_valid": False,
            "errors": [f"Erro na validação: {str(e)}"],
            "qualification_score": 0
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