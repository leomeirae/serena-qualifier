"""
OCR Tool - Wrapper LangChain sobre ocr_processor com Extração Estruturada

Este tool permite usar scripts.ocr_processor através da interface LangChain,
mantendo toda funcionalidade de processamento de faturas existente e adicionando
extração estruturada de dados com validação robusta.
"""

from typing import Dict, Any, Optional
import logging
import sys
import os
import asyncio
# from langchain.tools import tool
# from pydantic import BaseModel

# Import do módulo existente (será preservado)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

logger = logging.getLogger(__name__)

# Tenta importar as funções reais do ocr_processor
try:
    from scripts.ocr_processor import (
        process_conta_energia_file, 
        validate_conta_energia, 
        extract_conta_energia_fields,
        identify_distribuidora,
        validate_extracted_data,
        DISTRIBUIDORAS_CONHECIDAS
    )
    OCR_PROCESSOR_AVAILABLE = True
    logger.info("✅ OCR Processor com extração estruturada carregado com sucesso")
except ImportError as e:
    OCR_PROCESSOR_AVAILABLE = False
    logger.warning(f"⚠️ OCR Processor não disponível - usando simulação: {e}")

class OCRToolInput:
    """
    Schema de entrada para o OCR Tool com suporte a extração estruturada.
    

    """
    action: str  # process_image, extract_fields, validate_invoice, identify_distributor, validate_structured
    media_id: Optional[str] = None
    phone_number: Optional[str] = None
    ocr_text: Optional[str] = None
    ocr_data: Optional[dict] = None


def get_supported_distributors() -> Dict[str, Any]:
    """
    Retorna lista de distribuidoras suportadas
    
    Returns:
        Dict com distribuidoras conhecidas e suas variações
    """
    if OCR_PROCESSOR_AVAILABLE:
        return {
            "supported_distributors": list(DISTRIBUIDORAS_CONHECIDAS.keys()),
            "total_count": len(DISTRIBUIDORAS_CONHECIDAS),
            "coverage_info": "Cobertura nacional com principais distribuidoras brasileiras"
        }
    else:
        return {
            "supported_distributors": ["CEMIG", "ENEL", "LIGHT", "CPFL"],
            "total_count": 4,
            "coverage_info": "Simulação - dados limitados"
        }


# @tool("ocr_processor")
def ocr_tool_function(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper LangChain sobre scripts.ocr_processor com extração estruturada.
    
    Permite processar faturas de energia através da interface
    padronizada LangChain, mantendo toda funcionalidade existente
    e adicionando capacidades de extração estruturada.
    
    Args:
        input_data: Dict com action e parâmetros específicos
        
    Returns:
        Dict com resultado do processamento OCR estruturado
    """
    action = input_data.get("action", "")
    logger.info(f"🔧 OCRTool executando ação: {action}")
    
    try:
        # Chamada real das funções do ocr_processor
        if OCR_PROCESSOR_AVAILABLE:
            
            if action == "process_image":
                media_id = input_data.get("media_id")
                phone_number = input_data.get("phone_number")
                logger.info(f"📸 Processando imagem: {media_id} para {phone_number}")
                # process_conta_energia_file é async
                result = asyncio.run(process_conta_energia_file(media_id, phone_number))
                
            elif action == "validate_invoice":
                ocr_data = input_data.get("ocr_data", {})
                logger.info("✅ Validando dados da fatura")
                result = validate_conta_energia(ocr_data)
                
            elif action == "extract_fields":
                ocr_text = input_data.get("ocr_text", "")
                logger.info("🔍 Extraindo campos estruturados do texto OCR")
                result = extract_conta_energia_fields(ocr_text)
                
            elif action == "identify_distributor":
                ocr_text = input_data.get("ocr_text", "")
                logger.info("🏢 Identificando distribuidora")
                distribuidora = identify_distribuidora(ocr_text)
                result = {
                    "distribuidora_identificada": distribuidora,
                    "is_supported": distribuidora in DISTRIBUIDORAS_CONHECIDAS if distribuidora else False,
                    "confidence": 0.9 if distribuidora else 0.0
                }
                
            elif action == "validate_structured":
                ocr_data = input_data.get("ocr_data", {})
                logger.info("📊 Executando validação estruturada")
                result = validate_extracted_data(ocr_data)
                
            elif action == "get_supported_distributors":
                logger.info("📋 Listando distribuidoras suportadas")
                result = get_supported_distributors()
                
            else:
                result = {
                    "error": f"Ação não reconhecida: {action}",
                    "available_actions": [
                        "process_image", "validate_invoice", "extract_fields", 
                        "identify_distributor", "validate_structured", "get_supported_distributors"
                    ]
                }
                
        else:
            # Fallback simulado com extração estruturada
            logger.warning("🎭 Usando simulação - OCR Processor não disponível")
            
            if action == "process_image":
                result = {
                    "success": True,
                    "extracted_data": {
                        "nome_cliente": "CLIENTE SIMULADO",
                        "distribuidora": "CEMIG",
                        "total_a_pagar": "R$ 325,50",
                        "valor_numerico": 325.50,
                        "consumo_kwh": "380",
                        "endereco": "RUA EXEMPLO, 123",
                        "cidade": "BELO HORIZONTE - MG",
                        "vencimento": "25/01/2025"
                    },
                    "validation": {
                        "is_valid": True,
                        "confidence_score": 0.85,
                        "qualification_score": 85
                    },
                    "is_qualified": True,
                    "processing_method": "simulated_structured"
                }
                
            elif action == "validate_invoice":
                result = {
                    "is_valid": True,
                    "qualification_score": 85,
                    "extraction_confidence": 0.85,
                    "distribuidora_identificada": True,
                    "dados_completos": True,
                    "warnings": ["Dados simulados"]
                }
                
            elif action == "extract_fields":
                result = {
                    "nome_cliente": "CLIENTE SIMULADO",
                    "distribuidora": "CEMIG",
                    "total_a_pagar": "R$ 325,50",
                    "valor_numerico": 325.50,
                    "confidence_score": 0.85,
                    "is_valid_extraction": True,
                    "ocr_method": "simulated_structured"
                }
                
            elif action == "identify_distributor":
                result = {
                    "distribuidora_identificada": "CEMIG",
                    "is_supported": True,
                    "confidence": 0.85
                }
                
            elif action == "validate_structured":
                result = {
                    "is_valid": True,
                    "confidence_score": 0.85,
                    "validation_errors": [],
                    "warnings": ["Dados simulados"]
                }
                
            elif action == "get_supported_distributors":
                result = get_supported_distributors()
                
            else:
                result = {
                    "error": f"Ação não reconhecida: {action}",
                    "available_actions": [
                        "process_image", "validate_invoice", "extract_fields", 
                        "identify_distributor", "validate_structured", "get_supported_distributors"
                    ]
                }
            
        return {
            "success": True,
            "result": result,
            "action": action,
            "ocr_processor_available": OCR_PROCESSOR_AVAILABLE,
            "extraction_method": "structured" if OCR_PROCESSOR_AVAILABLE else "simulated_structured"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no OCRTool: {e}")
        return {
            "success": False,
            "error": str(e),
            "action": action,
            "ocr_processor_available": OCR_PROCESSOR_AVAILABLE
        }


# Instância do tool que será usada pelo AgentExecutor
ocr_tool = {
    "name": "ocr_processor",
    "description": """Processa faturas de energia via OCR com extração estruturada para extrair valores, 
    identificar distribuidoras, validar documentos e qualificar leads. Suporte a múltiplas distribuidoras 
    brasileiras com validação robusta e score de confiança.""",
    "function": ocr_tool_function,
    "args_schema": OCRToolInput
} 