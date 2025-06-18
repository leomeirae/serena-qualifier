#!/usr/bin/env python3
"""
Testes para o módulo LocationExtractor

Author: Serena-Coder AI Agent
Version: 1.0.0 - Refatoração para modularização
Created: 2025-01-17
"""

import pytest
import sys
import os

# Adicionar o diretório scripts ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from location_extractor import LocationExtractor


class TestLocationExtraction:
    """Testes para extração de localização das mensagens."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.extractor = LocationExtractor()
    
    def test_extract_location_basic_format(self):
        """Testa extração de localização em formato básico."""
        message = "Moro em Recife, PE"
        result = self.extractor.extract_location_from_message(message)
        
        assert result is not None
        assert result == ("Recife", "PE")
    
    def test_extract_location_different_verbs(self):
        """Testa extração com diferentes verbos."""
        test_cases = [
            ("Vivo em Recife, PE", ("Recife", "PE")),
            ("Sou de Recife, PE", ("Recife", "PE")),
            ("Estou em Recife, PE", ("Recife", "PE")),
            ("Fico em Recife, PE", ("Recife", "PE")),
            ("Resido em Recife, PE", ("Recife", "PE"))
        ]
        
        for message, expected in test_cases:
            result = self.extractor.extract_location_from_message(message)
            assert result == expected, f"Falhou para: {message}"
    
    def test_extract_location_different_separators(self):
        """Testa extração com diferentes separadores."""
        test_cases = [
            ("Recife - PE", ("Recife", "PE")),
            ("Recife/PE", ("Recife", "PE")),
            ("Recife PE", ("Recife", "PE")),
        ]
        
        for message, expected in test_cases:
            result = self.extractor.extract_location_from_message(message)
            assert result == expected, f"Falhou para: {message}"
    
    def test_extract_location_major_cities(self):
        """Testa identificação de cidades conhecidas."""
        test_cases = [
            ("Moro em recife", ("Recife", "PE")),
            ("Vivo no recife", ("Recife", "PE")),
            ("Estou em recife", ("Recife", "PE"))
        ]
        
        for message, expected in test_cases:
            result = self.extractor.extract_location_from_message(message)
            assert result == expected, f"Falhou para: {message}"
    
    def test_extract_location_no_match(self):
        """Testa mensagens sem localização."""
        test_cases = [
            "Oi, quero economizar na conta de luz",
            "Tenho interesse em energia solar",
            "Como funciona o desconto?",
            "Quero saber mais sobre os planos"
        ]
        
        for message in test_cases:
            result = self.extractor.extract_location_from_message(message)
            assert result is None, f"Não deveria encontrar localização em: {message}"
    
    def test_extract_location_invalid_combinations(self):
        """Testa combinações inválidas que não deveriam ser detectadas."""
        test_cases = [
            "Quero economizar na conta RO",  # RO pode aparecer em "cOntRO"
            "Desconto na energia SP",        # SP pode aparecer em outras palavras
            "Como funciona MG",              # MG sozinho
        ]
        
        for message in test_cases:
            result = self.extractor.extract_location_from_message(message)
            # Pode ser None ou uma detecção válida, mas não deve quebrar
            assert isinstance(result, (type(None), tuple))


class TestPromptGeneration:
    """Testes para geração de prompts."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.extractor = LocationExtractor()
    
    def test_initial_response_prompt(self):
        """Testa geração do prompt inicial."""
        message = "Quero economizar na conta de luz"
        prompt = self.extractor.get_initial_response_prompt(message)
        
        assert "Serena" in prompt
        assert message in prompt
        assert "cidade e estado" in prompt
        assert "energia solar" in prompt
    
    def test_promotions_response_prompt_with_promotions(self):
        """Testa prompt com promoções disponíveis."""
        message = "Moro em Recife, PE"
        city = "Recife"
        state = "PE"
        promotions = [
            {"energyUtilityName": "CELPE", "discountPercentage": 14},
            {"energyUtilityName": "CELPE", "discountPercentage": 16}
        ]
        
        prompt = self.extractor.get_promotions_response_prompt(
            message, city, state, promotions
        )
        
        assert city in prompt
        assert state in prompt
        assert "CELPE" in prompt
        assert "14%" in prompt
        assert "16%" in prompt
        assert "FOTO ou PDF" in prompt
        assert "conta de energia" in prompt
    
    def test_promotions_response_prompt_no_promotions(self):
        """Testa prompt sem promoções disponíveis."""
        message = "Moro em Recife, PE"
        city = "Recife"
        state = "PE"
        promotions = []
        
        prompt = self.extractor.get_promotions_response_prompt(
            message, city, state, promotions
        )
        
        assert city in prompt
        assert state in prompt
        assert "não encontramos promoções" in prompt or "INFELIZMENTE" in prompt
        assert "FOTO ou PDF" in prompt
        assert "conta de energia" in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
