#!/usr/bin/env python3
"""
Testes para o módulo ConversationContext

Author: Serena-Coder AI Agent
Version: 1.0.0 - Refatoração para modularização
Created: 2025-01-17
"""

import pytest
import sys
import os
from datetime import datetime

# Adicionar o diretório scripts ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from conversation_context import ConversationContext


class TestConversationContextBasic:
    """Testes básicos para gerenciamento de contexto."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.context_manager = ConversationContext()
        self.test_phone = "+5511999887766"
    
    def test_save_and_get_context_basic(self):
        """Testa salvamento e recuperação básica de contexto."""
        # Salvar contexto inicial
        self.context_manager.save_context(
            self.test_phone,
            city="São Paulo",
            state="SP"
        )
        
        # Recuperar e verificar
        context = self.context_manager.get_context(self.test_phone)
        
        assert context is not None
        assert context["city"] == "São Paulo"
        assert context["state"] == "SP"
        assert "created_at" in context
        assert "last_updated" in context
    
    def test_save_context_with_promotions(self):
        """Testa salvamento de contexto com promoções."""
        promotions = [
            {"energyUtilityName": "ENEL", "discountPercentage": 15},
            {"energyUtilityName": "ENEL", "discountPercentage": 18}
        ]
        
        self.context_manager.save_context(
            self.test_phone,
            city="São Paulo",
            state="SP",
            promotions=promotions
        )
        
        context = self.context_manager.get_context(self.test_phone)
        
        assert context["promotions"] == promotions
        assert len(context["promotions"]) == 2
    
    def test_save_context_with_extracted_data(self):
        """Testa salvamento de contexto com dados extraídos."""
        extracted_data = {
            "cliente_nome": "João Silva",
            "valor_total": "R$ 245,67",
            "distribuidora": "ENEL"
        }
        
        self.context_manager.save_context(
            self.test_phone,
            extracted_data=extracted_data
        )
        
        context = self.context_manager.get_context(self.test_phone)
        
        assert context["extracted_data"] == extracted_data
    
    def test_save_context_conversation_completed(self):
        """Testa marcação de conversa como finalizada."""
        self.context_manager.save_context(
            self.test_phone,
            conversation_completed=True
        )
        
        context = self.context_manager.get_context(self.test_phone)
        
        assert context["conversation_completed"] is True
    
    def test_get_context_nonexistent(self):
        """Testa recuperação de contexto inexistente."""
        context = self.context_manager.get_context("+5511000000000")
        
        assert context == {}


class TestConversationContextCheckers:
    """Testes para métodos de verificação de estado."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.context_manager = ConversationContext()
        self.test_phone = "+5511999887766"
    
    def test_has_location_true(self):
        """Testa verificação de localização presente."""
        self.context_manager.save_context(
            self.test_phone,
            city="Recife",
            state="PE"
        )
        
        assert self.context_manager.has_location(self.test_phone) is True
    
    def test_has_location_false(self):
        """Testa verificação de localização ausente."""
        assert self.context_manager.has_location(self.test_phone) is False
        
        # Salvar contexto sem localização
        self.context_manager.save_context(self.test_phone)
        assert self.context_manager.has_location(self.test_phone) is False
    
    def test_has_promotions_true(self):
        """Testa verificação de promoções presentes."""
        promotions = [{"energyUtilityName": "CEMIG", "discountPercentage": 16}]
        
        self.context_manager.save_context(
            self.test_phone,
            promotions=promotions
        )
        
        assert self.context_manager.has_promotions(self.test_phone) is True
    
    def test_has_promotions_false(self):
        """Testa verificação de promoções ausentes."""
        assert self.context_manager.has_promotions(self.test_phone) is False
        
        # Salvar contexto com lista vazia
        self.context_manager.save_context(
            self.test_phone,
            promotions=[]
        )
        assert self.context_manager.has_promotions(self.test_phone) is True  # Lista vazia ainda conta como "tem promoções"
    
    def test_is_conversation_completed_true(self):
        """Testa verificação de conversa finalizada."""
        self.context_manager.save_context(
            self.test_phone,
            conversation_completed=True
        )
        
        assert self.context_manager.is_conversation_completed(self.test_phone) is True
    
    def test_is_conversation_completed_false(self):
        """Testa verificação de conversa não finalizada."""
        assert self.context_manager.is_conversation_completed(self.test_phone) is False
        
        # Salvar contexto sem marcar como finalizada
        self.context_manager.save_context(self.test_phone)
        assert self.context_manager.is_conversation_completed(self.test_phone) is False


class TestConversationContextGetters:
    """Testes para métodos getter específicos."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.context_manager = ConversationContext()
        self.test_phone = "+5511999887766"
    
    def test_get_location_with_data(self):
        """Testa recuperação de localização quando presente."""
        self.context_manager.save_context(
            self.test_phone,
            city="Belo Horizonte",
            state="MG"
        )
        
        location = self.context_manager.get_location(self.test_phone)
        
        assert location == ("Belo Horizonte", "MG")
    
    def test_get_location_without_data(self):
        """Testa recuperação de localização quando ausente."""
        location = self.context_manager.get_location(self.test_phone)
        
        assert location is None
    
    def test_get_promotions_with_data(self):
        """Testa recuperação de promoções quando presentes."""
        promotions = [
            {"energyUtilityName": "CEMIG", "discountPercentage": 14},
            {"energyUtilityName": "CEMIG", "discountPercentage": 16}
        ]
        
        self.context_manager.save_context(
            self.test_phone,
            promotions=promotions
        )
        
        retrieved_promotions = self.context_manager.get_promotions(self.test_phone)
        
        assert retrieved_promotions == promotions
        assert len(retrieved_promotions) == 2
    
    def test_get_promotions_without_data(self):
        """Testa recuperação de promoções quando ausentes."""
        promotions = self.context_manager.get_promotions(self.test_phone)
        
        assert promotions == []
    
    def test_get_extracted_data_with_data(self):
        """Testa recuperação de dados extraídos quando presentes."""
        extracted_data = {
            "cliente_nome": "Maria Santos",
            "valor_total": "R$ 189,45",
            "distribuidora": "CELPE"
        }
        
        self.context_manager.save_context(
            self.test_phone,
            extracted_data=extracted_data
        )
        
        retrieved_data = self.context_manager.get_extracted_data(self.test_phone)
        
        assert retrieved_data == extracted_data
    
    def test_get_extracted_data_without_data(self):
        """Testa recuperação de dados extraídos quando ausentes."""
        extracted_data = self.context_manager.get_extracted_data(self.test_phone)
        
        assert extracted_data is None


class TestConversationContextManagement:
    """Testes para gerenciamento avançado de contexto."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.context_manager = ConversationContext()
        self.test_phone = "+5511999887766"
    
    def test_clear_context(self):
        """Testa limpeza de contexto."""
        # Criar contexto completo
        self.context_manager.save_context(
            self.test_phone,
            city="Salvador",
            state="BA",
            promotions=[{"energyUtilityName": "COELBA", "discountPercentage": 12}],
            conversation_completed=True
        )
        
        # Verificar que existe
        assert self.context_manager.has_location(self.test_phone) is True
        
        # Limpar contexto
        self.context_manager.clear_context(self.test_phone)
        
        # Verificar que foi removido
        assert self.context_manager.has_location(self.test_phone) is False
        assert self.context_manager.get_context(self.test_phone) == {}
    
    def test_get_conversation_stage(self):
        """Testa recuperação do estágio da conversa."""
        # Estágio inicial (sem contexto)
        stage = self.context_manager.get_conversation_stage(self.test_phone)
        assert stage == "initial"
        
        # Após detectar localização
        self.context_manager.save_context(
            self.test_phone,
            city="Fortaleza",
            state="CE"
        )
        stage = self.context_manager.get_conversation_stage(self.test_phone)
        assert stage == "location_detected"
        
        # Após enviar promoções
        self.context_manager.save_context(
            self.test_phone,
            promotions=[{"energyUtilityName": "ENEL", "discountPercentage": 15}]
        )
        stage = self.context_manager.get_conversation_stage(self.test_phone)
        assert stage == "promotions_shown"
        
        # Após processar imagem
        self.context_manager.save_context(
            self.test_phone,
            extracted_data={"cliente_nome": "José Silva"}
        )
        stage = self.context_manager.get_conversation_stage(self.test_phone)
        assert stage == "image_processed"
        
        # Após finalizar conversa
        self.context_manager.save_context(
            self.test_phone,
            conversation_completed=True
        )
        stage = self.context_manager.get_conversation_stage(self.test_phone)
        assert stage == "completed"
    
    def test_get_stats(self):
        """Testa recuperação de estatísticas."""
        # Criar múltiplos contextos
        phones = ["+5511111111111", "+5511222222222", "+5511333333333"]
        
        # Primeiro: apenas localização
        self.context_manager.save_context(
            phones[0],
            city="Rio de Janeiro",
            state="RJ"
        )
        
        # Segundo: localização + promoções
        self.context_manager.save_context(
            phones[1],
            city="Brasília",
            state="DF",
            promotions=[{"energyUtilityName": "CEB", "discountPercentage": 10}]
        )
        
        # Terceiro: conversa completa
        self.context_manager.save_context(
            phones[2],
            city="Curitiba",
            state="PR",
            promotions=[{"energyUtilityName": "COPEL", "discountPercentage": 18}],
            extracted_data={"cliente_nome": "Ana Costa"},
            conversation_completed=True
        )
        
        stats = self.context_manager.get_stats()
        
        assert stats["current_conversations"] == 3
        assert "timestamp" in stats
    
    def test_context_update_preserves_existing_data(self):
        """Testa que atualizações preservam dados existentes."""
        # Salvar dados iniciais
        self.context_manager.save_context(
            self.test_phone,
            city="Natal",
            state="RN"
        )
        
        # Adicionar promoções (deve preservar localização)
        self.context_manager.save_context(
            self.test_phone,
            promotions=[{"energyUtilityName": "COSERN", "discountPercentage": 13}]
        )
        
        context = self.context_manager.get_context(self.test_phone)
        
        # Verificar que ambos os dados estão presentes
        assert context["city"] == "Natal"
        assert context["state"] == "RN"
        assert len(context["promotions"]) == 1
        assert context["promotions"][0]["energyUtilityName"] == "COSERN"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
