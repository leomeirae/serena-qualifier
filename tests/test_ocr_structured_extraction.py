"""
Testes para Extração Estruturada de Dados da Conta de Energia
Valida as novas funcionalidades implementadas na task-249
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Imports das funções a serem testadas
from scripts.ocr_processor import (
    extract_conta_energia_fields,
    validate_extracted_data,
    identify_distribuidora,
    validate_conta_energia,
    extract_with_multiple_patterns,
    DISTRIBUIDORAS_CONHECIDAS,
    EXTRACTION_PATTERNS
)

from scripts.serena_agent.tools.ocr_tool import (
    ocr_tool_function,
    get_supported_distributors
)


class TestDistribuidoraIdentification:
    """Testes para identificação de distribuidoras"""
    
    def test_identify_cemig(self):
        """Testa identificação da CEMIG"""
        texto_cemig = "CEMIG DISTRIBUIÇÃO S.A. - COMPANHIA ENERGÉTICA DE MINAS GERAIS"
        result = identify_distribuidora(texto_cemig)
        assert result == "CEMIG"
    
    def test_identify_enel(self):
        """Testa identificação da ENEL"""
        texto_enel = "ENEL DISTRIBUIÇÃO SÃO PAULO"
        result = identify_distribuidora(texto_enel)
        assert result == "ENEL"
    
    def test_identify_light(self):
        """Testa identificação da LIGHT"""
        texto_light = "LIGHT SERVIÇOS DE ELETRICIDADE S.A."
        result = identify_distribuidora(texto_light)
        assert result == "LIGHT"
    
    def test_identify_unknown_distributor(self):
        """Testa texto sem distribuidora conhecida"""
        texto_desconhecido = "EMPRESA DESCONHECIDA DE ENERGIA"
        result = identify_distribuidora(texto_desconhecido)
        assert result is None
    
    def test_case_insensitive_identification(self):
        """Testa identificação case-insensitive"""
        texto_lower = "cemig distribuição s.a."
        result = identify_distribuidora(texto_lower)
        assert result == "CEMIG"


class TestMultiplePatternExtraction:
    """Testes para extração com múltiplos padrões"""
    
    def test_extract_valor_multiple_patterns(self):
        """Testa extração de valor com diferentes padrões"""
        patterns = EXTRACTION_PATTERNS["total_a_pagar"]
        
        # Teste padrão 1: TOTAL A PAGAR
        texto1 = "TOTAL A PAGAR: R$ 387,45"
        result1 = extract_with_multiple_patterns(texto1, patterns)
        assert result1 == "R$ 387,45"
        
        # Teste padrão 2: VALOR TOTAL
        texto2 = "VALOR TOTAL R$ 156,78"
        result2 = extract_with_multiple_patterns(texto2, patterns)
        assert result2 == "R$ 156,78"
        
        # Teste padrão 3: TOTAL GERAL
        texto3 = "TOTAL GERAL: R$ 623,12"
        result3 = extract_with_multiple_patterns(texto3, patterns)
        assert result3 == "R$ 623,12"
    
    def test_extract_nome_cliente_patterns(self):
        """Testa extração de nome com diferentes padrões"""
        patterns = EXTRACTION_PATTERNS["nome_cliente"]
        
        # Teste padrão CLIENTE
        texto1 = "CLIENTE: MARIA SILVA SANTOS"
        result1 = extract_with_multiple_patterns(texto1, patterns)
        assert result1 == "MARIA SILVA SANTOS"
        
        # Teste padrão NOME
        texto2 = "NOME JOÃO PEREIRA LIMA"
        result2 = extract_with_multiple_patterns(texto2, patterns)
        assert result2 == "JOÃO PEREIRA LIMA"
        
        # Teste padrão TITULAR
        texto3 = "TITULAR: CARLOS EDUARDO ROCHA"
        result3 = extract_with_multiple_patterns(texto3, patterns)
        assert result3 == "CARLOS EDUARDO ROCHA"
    
    def test_extract_no_match(self):
        """Testa quando nenhum padrão encontra match"""
        patterns = EXTRACTION_PATTERNS["total_a_pagar"]
        texto_sem_valor = "TEXTO SEM VALOR MONETÁRIO"
        result = extract_with_multiple_patterns(texto_sem_valor, patterns)
        assert result is None


class TestStructuredExtraction:
    """Testes para extração estruturada completa"""
    
    def test_extract_complete_invoice_data(self):
        """Testa extração completa de dados da fatura"""
        texto_fatura = """CEMIG DISTRIBUIÇÃO S.A.
CLIENTE: MARIA SILVA SANTOS
CPF: 123.456.789-00
ENDEREÇO: RUA DAS FLORES, 123 - CENTRO
CIDADE: BELO HORIZONTE - MG
TOTAL A PAGAR: R$ 387,45
CONSUMO: 450 kWh
VENCIMENTO: 15/01/2025
REFERÊNCIA: DEZ/2024
INSTALAÇÃO: 123456789"""
        
        result = extract_conta_energia_fields(texto_fatura)
        
        # Verificar campos extraídos
        assert result["nome_cliente"] == "MARIA SILVA SANTOS"
        assert result["cpf_cnpj"] == "123.456.789-00"
        assert result["endereco"] == "RUA DAS FLORES, 123 - CENTRO"
        assert result["distribuidora"] == "CEMIG"
        assert result["total_a_pagar"] == "R$ 387,45"
        assert result["valor_numerico"] == 387.45
        assert result["consumo_kwh"] == "450"
        assert result["vencimento"] == "15/01/2025"
        assert result["mes_referencia"] == "DEZ/2024"
        assert result["numero_instalacao"] == "123456789"
        
        # Verificar metadados
        assert result["ocr_method"] == "structured_extraction"
        assert "extraction_timestamp" in result
        assert result["confidence_score"] > 0.8
        assert result["is_valid_extraction"] is True
    
    def test_extract_partial_data(self):
        """Testa extração com dados parciais"""
        texto_parcial = """ENEL DISTRIBUIÇÃO
CLIENTE: JOÃO PEREIRA LIMA
TOTAL A PAGAR: R$ 156,78"""
        
        result = extract_conta_energia_fields(texto_parcial)
        
        # Verificar campos extraídos
        assert result["nome_cliente"] == "JOÃO PEREIRA LIMA"
        assert result["distribuidora"] == "ENEL"
        assert result["total_a_pagar"] == "R$ 156,78"
        assert result["valor_numerico"] == 156.78
        
        # Campos não encontrados devem ser None
        assert result["endereco"] is None
        assert result["consumo_kwh"] is None
        assert result["vencimento"] is None
        
        # Confiança deve ser menor
        assert result["confidence_score"] < 0.8
    
    def test_extract_invalid_data(self):
        """Testa extração com dados inválidos"""
        texto_invalido = "TEXTO SEM DADOS DE FATURA"
        
        result = extract_conta_energia_fields(texto_invalido)
        
        # Verificar que não extraiu dados válidos
        assert result["nome_cliente"] is None
        assert result["distribuidora"] is None
        assert result["valor_numerico"] == 0.0
        assert result["confidence_score"] < 0.5
        assert result["is_valid_extraction"] is False


class TestDataValidation:
    """Testes para validação de dados extraídos"""
    
    def test_validate_complete_valid_data(self):
        """Testa validação de dados completos e válidos"""
        dados_validos = {
            "nome_cliente": "MARIA SILVA SANTOS",
            "distribuidora": "CEMIG",
            "valor_numerico": 387.45,
            "consumo_kwh": "450",
            "vencimento": "15/01/2025",
            "endereco": "RUA DAS FLORES, 123 - CENTRO"
        }
        
        result = validate_extracted_data(dados_validos)
        
        assert result["is_valid"] is True
        assert result["confidence_score"] >= 0.8
        assert len(result["validation_errors"]) == 0
    
    def test_validate_missing_critical_data(self):
        """Testa validação com dados críticos faltando"""
        dados_incompletos = {
            "distribuidora": "CEMIG",
            "valor_numerico": 0.0,  # Valor inválido
            "nome_cliente": "AB"     # Nome muito curto
        }
        
        result = validate_extracted_data(dados_incompletos)
        
        assert result["is_valid"] is False
        assert result["confidence_score"] < 0.5
        assert len(result["validation_errors"]) > 0
        assert "Valor monetário não encontrado" in str(result["validation_errors"])
        assert "Nome do cliente não encontrado" in str(result["validation_errors"])
    
    def test_validate_high_value_warning(self):
        """Testa warning para valores muito altos"""
        dados_alto_valor = {
            "nome_cliente": "CLIENTE TESTE VALOR ALTO",
            "distribuidora": "CEMIG",
            "valor_numerico": 1500.0,  # Valor alto
            "endereco": "RUA TESTE, 123 - CENTRO"
        }
        
        result = validate_extracted_data(dados_alto_valor)
        
        assert result["is_valid"] is True
        assert "Valor muito alto" in str(result["warnings"])


class TestQualificationValidation:
    """Testes para validação de qualificação de leads"""
    
    def test_validate_qualified_lead(self):
        """Testa validação de lead qualificado"""
        dados_qualificado = {
            "nome_cliente": "MARIA SILVA SANTOS",
            "distribuidora": "CEMIG",
            "valor_numerico": 387.45,
            "endereco": "RUA DAS FLORES, 123 - CENTRO",
            "consumo_kwh": "450",
            "validation": {
                "is_valid": True,
                "confidence_score": 0.9
            }
        }
        
        result = validate_conta_energia(dados_qualificado)
        
        assert result["is_valid"] is True
        assert result["qualification_score"] >= 65
        assert result["distribuidora_identificada"] is True
        assert result["dados_completos"] is True
    
    def test_validate_low_value_disqualification(self):
        """Testa desqualificação por valor baixo"""
        dados_valor_baixo = {
            "nome_cliente": "CLIENTE VALOR BAIXO",
            "distribuidora": "CEMIG",
            "valor_numerico": 150.0,  # Abaixo do mínimo R$ 200
            "endereco": "RUA TESTE, 123"
        }
        
        result = validate_conta_energia(dados_valor_baixo)
        
        assert result["is_valid"] is False
        assert result["qualification_score"] < 65
        assert "Valor da conta muito baixo" in str(result["errors"])


class TestOCRToolIntegration:
    """Testes para integração da OCR Tool"""
    
    def test_ocr_tool_process_image(self):
        """Testa processamento de imagem via OCR Tool"""
        input_data = {
            "action": "process_image",
            "media_id": "test_media_123",
            "phone_number": "+5511999999876"
        }
        
        result = ocr_tool_function(input_data)
        
        assert result["success"] is True
        assert result["action"] == "process_image"
        assert "result" in result
        assert "extraction_method" in result
    
    def test_ocr_tool_extract_fields(self):
        """Testa extração de campos via OCR Tool"""
        input_data = {
            "action": "extract_fields",
            "ocr_text": "CEMIG CLIENTE: TESTE TOTAL A PAGAR: R$ 300,00"
        }
        
        result = ocr_tool_function(input_data)
        
        assert result["success"] is True
        assert result["action"] == "extract_fields"
        assert "result" in result
    
    def test_ocr_tool_identify_distributor(self):
        """Testa identificação de distribuidora via OCR Tool"""
        input_data = {
            "action": "identify_distributor",
            "ocr_text": "CEMIG DISTRIBUIÇÃO S.A."
        }
        
        result = ocr_tool_function(input_data)
        
        assert result["success"] is True
        assert result["action"] == "identify_distributor"
        assert "distribuidora_identificada" in result["result"]
    
    def test_ocr_tool_get_supported_distributors(self):
        """Testa listagem de distribuidoras suportadas"""
        input_data = {
            "action": "get_supported_distributors"
        }
        
        result = ocr_tool_function(input_data)
        
        assert result["success"] is True
        assert "supported_distributors" in result["result"]
        assert result["result"]["total_count"] > 0


class TestSupportedDistributors:
    """Testes para distribuidoras suportadas"""
    
    def test_get_supported_distributors_structure(self):
        """Testa estrutura da resposta de distribuidoras suportadas"""
        result = get_supported_distributors()
        
        assert "supported_distributors" in result
        assert "total_count" in result
        assert "coverage_info" in result
        assert isinstance(result["supported_distributors"], list)
        assert result["total_count"] > 0
    
    def test_major_distributors_included(self):
        """Testa se principais distribuidoras estão incluídas"""
        result = get_supported_distributors()
        distributors = result["supported_distributors"]
        
        # Principais distribuidoras devem estar presentes
        expected_distributors = ["CEMIG", "ENEL", "LIGHT", "CPFL"]
        for distributor in expected_distributors:
            assert distributor in distributors


if __name__ == "__main__":
    # Executar testes específicos para task-249
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-k", "test_extract_complete_invoice_data or test_validate_qualified_lead or test_identify_cemig"
    ])
 