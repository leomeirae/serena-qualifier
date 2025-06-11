#!/usr/bin/env python3
"""
Testes automatizados para a API Serena usando pytest
"""

import pytest
import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv

# Adicionar pasta scripts ao path
sys.path.append('scripts')

# Carregar variáveis de ambiente
load_dotenv()

from scripts.serena_api import SerenaAPI

# Fixtures
@pytest.fixture(scope="module")
def api_client():
    """Fixture para criar instância da API Serena"""
    return SerenaAPI()

@pytest.fixture(scope="module") 
def sp_areas(api_client):
    """Fixture para áreas de operação de São Paulo"""
    return api_client.get_operation_areas(state="SP", city="São Paulo")

@pytest.fixture(scope="module")
def bh_areas(api_client):
    """Fixture para áreas de operação de Belo Horizonte"""
    return api_client.get_operation_areas(state="MG", city="Belo Horizonte")

@pytest.fixture(scope="module")
def bh_plans(api_client):
    """Fixture para planos de Belo Horizonte"""
    return api_client.get_plans(city="Belo Horizonte", state="MG")

# Funções auxiliares para validação
def validate_area_structure(area: Dict[str, Any]) -> None:
    """Valida estrutura de uma área de operação"""
    assert isinstance(area, dict), "Área deve ser um dicionário"
    assert 'energyUtilityName' in area, "Area deve ter energyUtilityName"
    assert 'energyUtilityPublicId' in area, "Area deve ter energyUtilityPublicId"
    assert 'energyUtilityQualified' in area, "Area deve ter energyUtilityQualified"
    assert 'city' in area, "Area deve ter city"
    assert 'state' in area, "Area deve ter state"
    assert 'ibgeCode' in area, "Area deve ter ibgeCode"
    
    # Validar tipos
    assert isinstance(area['energyUtilityName'], str), "energyUtilityName deve ser string"
    assert isinstance(area['energyUtilityPublicId'], str), "energyUtilityPublicId deve ser string"
    assert isinstance(area['energyUtilityQualified'], bool), "energyUtilityQualified deve ser bool"

def validate_plan_structure(plan: Dict[str, Any]) -> None:
    """Valida estrutura de um plano"""
    assert isinstance(plan, dict), "Plano deve ser um dicionário"
    assert 'id' in plan, "Plano deve ter id"
    assert 'name' in plan, "Plano deve ter name"
    assert 'fidelityMonths' in plan, "Plano deve ter fidelityMonths"
    assert 'discount' in plan, "Plano deve ter discount"
    assert 'energyUtilityName' in plan, "Plano deve ter energyUtilityName"
    
    # Validar tipos
    assert isinstance(plan['id'], int), "ID do plano deve ser inteiro"
    assert isinstance(plan['name'], str), "Nome do plano deve ser string"
    assert isinstance(plan['fidelityMonths'], int), "Fidelidade deve ser inteiro"
    assert isinstance(plan['energyUtilityName'], str), "Nome da distribuidora deve ser string"

def validate_formatted_plan_structure(plan: Dict[str, Any]) -> None:
    """Valida estrutura de um plano formatado pela função de conveniência"""
    assert isinstance(plan, dict), "Plano formatado deve ser um dicionário"
    assert 'id' in plan, "Plano formatado deve ter id"
    assert 'name' in plan, "Plano formatado deve ter name" 
    assert 'fidelityMonths' in plan, "Plano formatado deve ter fidelityMonths"
    assert 'discount' in plan, "Plano formatado deve ter discount"
    assert 'energyUtilityName' in plan, "Plano formatado deve ter energyUtilityName"
    assert 'city' in plan, "Plano formatado deve ter city"
    assert 'state' in plan, "Plano formatado deve ter state"
    assert 'details' in plan, "Plano formatado deve ter details"

# Testes de Áreas de Operação
class TestOperationAreas:
    """Testes para consulta de áreas de operação"""
    
    def test_operation_areas_sao_paulo(self, sp_areas):
        """Testa consulta de áreas de operação para São Paulo/SP"""
        assert sp_areas is not None, "Resposta não deve ser None"
        assert isinstance(sp_areas, list), "Resposta deve ser uma lista"
        assert len(sp_areas) > 0, "Deveria retornar pelo menos uma área para SP/São Paulo"
        
        for area in sp_areas:
            validate_area_structure(area)
            assert area['state'] == 'SP', "Estado deve ser SP"
            assert 'SÃO PAULO' in area['city'].upper(), "Cidade deve conter São Paulo"
    
    def test_operation_areas_belo_horizonte(self, bh_areas):
        """Testa consulta de áreas de operação para Belo Horizonte/MG"""
        assert bh_areas is not None, "Resposta não deve ser None"
        assert isinstance(bh_areas, list), "Resposta deve ser uma lista"
        assert len(bh_areas) > 0, "Deveria retornar pelo menos uma área para BH/MG"
        
        for area in bh_areas:
            validate_area_structure(area)
            assert area['state'] == 'MG', "Estado deve ser MG"
    
    def test_operation_areas_invalid_location(self, api_client):
        """Testa consulta para localização inexistente"""
        areas = api_client.get_operation_areas(state="XX", city="CidadeInexistente")
        assert isinstance(areas, list), "Deve retornar lista mesmo para localização inexistente"
        assert len(areas) == 0, "Deve retornar lista vazia para localização inexistente"

# Testes de Planos
class TestPlans:
    """Testes para consulta de planos"""
    
    def test_plans_belo_horizonte_qualified(self, bh_plans):
        """Testa consulta de planos para Belo Horizonte (distribuidora qualificada)"""
        assert bh_plans is not None, "Resposta não deve ser None"
        assert isinstance(bh_plans, list), "Resposta deve ser uma lista"
        assert len(bh_plans) > 0, "BH/MG deveria ter planos disponíveis (CEMIG qualificada)"
        
        for plan in bh_plans:
            validate_plan_structure(plan)
            assert plan['energyUtilityName'] == 'CEMIG', "Distribuidora deveria ser CEMIG para BH/MG"
            
            # Validar ranges esperados
            assert 0 <= plan['fidelityMonths'] <= 120, "Fidelidade deve estar em range válido"
            discount_value = float(plan['discount'])
            assert 0.0 <= discount_value <= 1.0, "Desconto deve estar entre 0 e 1"
    
    def test_plans_sao_paulo_unqualified(self, api_client):
        """Testa consulta de planos para São Paulo (distribuidora não qualificada)"""
        plans = api_client.get_plans(city="São Paulo", state="SP")
        assert isinstance(plans, list), "Deve retornar lista mesmo se não houver planos"

# Testes das Funções de Conveniência
class TestConvenienceFunctions:
    """Testes para funções de conveniência"""
    
    def test_get_plans_by_city_belo_horizonte(self, api_client):
        """Testa função de conveniência get_plans_by_city para BH"""
        formatted_plans = api_client.get_plans_by_city("Belo Horizonte", "MG")
        
        assert formatted_plans is not None, "Resultado não deve ser None"
        assert isinstance(formatted_plans, list), "Deve retornar lista"
        assert len(formatted_plans) > 0, "BH/MG deve ter planos formatados"
        
        for plan in formatted_plans:
            validate_formatted_plan_structure(plan)
            assert plan['city'] == "Belo Horizonte", "Cidade deve ser Belo Horizonte"
            assert plan['state'] == "MG", "Estado deve ser MG"
    
    def test_check_city_coverage_qualified(self, api_client):
        """Testa verificação de cobertura para cidade com distribuidora qualificada"""
        has_coverage = api_client.check_city_coverage("Belo Horizonte", "MG")
        assert isinstance(has_coverage, bool), "Deve retornar boolean"
        assert has_coverage is True, "BH/MG deve ter cobertura (CEMIG qualificada)"

# Testes de Validação e Qualidade dos Dados
class TestDataQuality:
    """Testes para validar qualidade dos dados retornados"""
    
    def test_plan_discount_values(self, bh_plans):
        """Testa se valores de desconto estão em formato válido"""
        for plan in bh_plans:
            discount = plan['discount']
            discount_float = float(discount)
            assert 0.0 <= discount_float <= 1.0, f"Desconto {discount} deve estar entre 0 e 1"
    
    def test_plan_names_not_empty(self, bh_plans):
        """Testa se nomes de planos não estão vazios"""
        for plan in bh_plans:
            assert plan['name'].strip() != "", "Nome do plano não deve estar vazio"
            assert len(plan['name']) > 3, "Nome do plano deve ter mais de 3 caracteres"
    
    def test_utility_ids_valid_uuid_format(self, sp_areas, bh_areas):
        """Testa se IDs das distribuidoras são UUIDs válidos"""
        import re
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
        
        all_areas = sp_areas + bh_areas
        for area in all_areas:
            utility_id = area['energyUtilityPublicId']
            assert uuid_pattern.match(utility_id), f"ID {utility_id} deve ser UUID válido"

# Testes de Erro e Edge Cases
class TestErrorHandling:
    """Testes para tratamento de erros e casos extremos"""
    
    def test_empty_city_name(self, api_client):
        """Testa comportamento com nome de cidade vazio"""
        with pytest.raises(ValueError, match="Cidade é obrigatória"):
            api_client.get_plans_by_city("")
    
    def test_none_city_name(self, api_client):
        """Testa comportamento com cidade None"""
        with pytest.raises(ValueError, match="Cidade é obrigatória"):
            api_client.get_plans_by_city(None)
    
    def test_api_credentials_present(self):
        """Testa se credenciais da API estão configuradas"""
        token = os.getenv("SERENA_API_TOKEN")
        base_url = os.getenv("SERENA_API_BASE_URL")
        
        assert token is not None, "SERENA_API_TOKEN deve estar configurado"
        assert token.strip() != "", "SERENA_API_TOKEN não deve estar vazio"
        assert base_url is not None, "SERENA_API_BASE_URL deve estar configurado"
        assert base_url.startswith("https://"), "SERENA_API_BASE_URL deve usar HTTPS"

if __name__ == "__main__":
    # Executar testes se arquivo for chamado diretamente
    pytest.main([__file__, "-v", "-s"]) 