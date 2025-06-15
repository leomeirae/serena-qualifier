"""
Testes para Integração OCR Melhorado ao Core Agent
Valida a integração implementada na task-251
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Adicionar o diretório raiz ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scripts.serena_agent.core_agent import SerenaAIAgent, process_ai_request


class TestCoreAgentOCRIntegration:
    """Testes para integração OCR no core agent"""
    
    def test_agent_initialization_with_ocr(self):
        """Testa se o agente inicializa com OCR tool melhorada"""
        agent = SerenaAIAgent()
        
        # Verifica se o agente foi inicializado
        assert agent is not None
        
        # Se LangChain disponível, verifica se OCR tool está nas tools
        if agent.tools:
            ocr_tool_found = any("ocr_processor" in str(tool) for tool in agent.tools)
            assert ocr_tool_found, "OCR tool deve estar disponível no agente"
    
    def test_energy_bill_context_detection(self):
        """Testa detecção de contexto de conta de energia"""
        agent = SerenaAIAgent()
        
        # Contextos que devem ser detectados como conta de energia
        energy_contexts = [
            "aqui está minha conta de luz",
            "enviei a fatura da CEMIG",
            "conta energia",
            "boleto luz",
            "kwh consumo",
            ""  # Mensagem vazia (apenas imagem)
        ]
        
        for context in energy_contexts:
            assert agent._is_energy_bill_context(context), f"Deveria detectar '{context}' como contexto de energia"
        
        # Contextos que NÃO devem ser detectados
        non_energy_contexts = [
            "oi, tudo bem?",
            "quero saber sobre energia solar",
            "quanto custa a instalação?",
            "vocês atendem em São Paulo?"
        ]
        
        for context in non_energy_contexts:
            assert not agent._is_energy_bill_context(context), f"NÃO deveria detectar '{context}' como contexto de energia"
    
    @patch('scripts.serena_agent.core_agent.ocr_tool_function')
    def test_process_energy_bill_image_success(self, mock_ocr_tool):
        """Testa processamento bem-sucedido de imagem de conta"""
        # Mock do resultado OCR
        mock_ocr_tool.return_value = {
            "success": True,
            "extracted_data": {
                "nome_cliente": "MARIA SILVA SANTOS",
                "distribuidora": "CEMIG",
                "total_a_pagar": "R$ 387,45",
                "consumo_kwh": "450"
            },
            "validation": {
                "is_valid": True,
                "confidence_score": 0.9
            },
            "is_qualified": True
        }
        
        agent = SerenaAIAgent()
        result = agent._process_energy_bill_image("+5511999999999", "minha conta", "media_123")
        
        # Verifica se OCR foi chamado corretamente
        mock_ocr_tool.assert_called_once_with({
            "action": "process_image",
            "media_id": "media_123",
            "phone_number": "+5511999999999"
        })
        
        # Verifica resultado
        assert result["method"] == "ocr_structured"
        assert result["data"]["ocr_processed"] is True
        assert result["data"]["is_qualified"] is True
        assert "CEMIG" in result["response"]
        assert "R$ 387,45" in result["response"]
    
    @patch('scripts.serena_agent.core_agent.ocr_tool_function')
    def test_process_energy_bill_image_unqualified(self, mock_ocr_tool):
        """Testa processamento de conta com lead não qualificado"""
        # Mock do resultado OCR para lead não qualificado
        mock_ocr_tool.return_value = {
            "success": True,
            "extracted_data": {
                "nome_cliente": "JOÃO SILVA",
                "distribuidora": "ENEL",
                "total_a_pagar": "R$ 150,00",
                "consumo_kwh": "200"
            },
            "validation": {
                "is_valid": True,
                "confidence_score": 0.8
            },
            "is_qualified": False
        }
        
        agent = SerenaAIAgent()
        result = agent._process_energy_bill_image("+5511888888888", "conta", "media_456")
        
        # Verifica resultado para lead não qualificado
        assert result["data"]["is_qualified"] is False
        assert "R$ 200/mês" in result["response"]  # Deve mencionar valor mínimo
        assert "financiamento" in result["response"].lower()
    
    @patch('scripts.serena_agent.core_agent.ocr_tool_function')
    def test_process_energy_bill_image_error(self, mock_ocr_tool):
        """Testa tratamento de erro no processamento OCR"""
        # Mock de erro no OCR
        mock_ocr_tool.return_value = {
            "success": False,
            "error": "Imagem não processável"
        }
        
        agent = SerenaAIAgent()
        result = agent._process_energy_bill_image("+5511777777777", "conta", "media_error")
        
        # Verifica tratamento de erro
        assert result["method"] == "ocr_error"
        assert result["data"]["ocr_error"] is True
        assert "foto mais clara" in result["response"]
    
    def test_process_conversation_with_media(self):
        """Testa processamento de conversa com mídia"""
        agent = SerenaAIAgent()
        
        # Simula conversa com imagem de conta
        with patch.object(agent, '_process_energy_bill_image') as mock_process_bill:
            mock_process_bill.return_value = {
                "response": "Conta processada com sucesso",
                "data": {"ocr_processed": True},
                "method": "ocr_structured"
            }
            
            result = agent.process_conversation(
                phone="+5511999999999",
                message="minha conta de luz",
                action="respond",
                media_id="media_123"
            )
            
            # Verifica se processamento de conta foi chamado
            mock_process_bill.assert_called_once_with("+5511999999999", "minha conta de luz", "media_123")
            assert result["media_processed"] is True
    
    def test_process_conversation_without_media(self):
        """Testa processamento normal sem mídia"""
        agent = SerenaAIAgent()
        
        result = agent.process_conversation(
            phone="+5511999999999",
            message="oi, quero saber sobre energia solar",
            action="respond"
        )
        
        # Verifica processamento normal
        assert result["media_processed"] is False
        assert result["result"] == "success"
    
    def test_generate_ocr_response_qualified(self):
        """Testa geração de resposta para lead qualificado"""
        agent = SerenaAIAgent()
        
        extracted_data = {
            "nome_cliente": "MARIA SILVA",
            "distribuidora": "CEMIG",
            "total_a_pagar": "R$ 387,45",
            "consumo_kwh": "450"
        }
        
        validation = {"confidence_score": 0.9}
        
        response = agent._generate_ocr_response(extracted_data, validation, is_qualified=True)
        
        # Verifica elementos da resposta
        assert "✅" in response
        assert "MARIA SILVA" in response
        assert "CEMIG" in response
        assert "R$ 387,45" in response
        assert "450 kWh" in response
        assert "economizar significativamente" in response
    
    def test_generate_ocr_response_unqualified(self):
        """Testa geração de resposta para lead não qualificado"""
        agent = SerenaAIAgent()
        
        extracted_data = {
            "distribuidora": "ENEL",
            "total_a_pagar": "R$ 150,00"
        }
        
        validation = {"confidence_score": 0.8}
        
        response = agent._generate_ocr_response(extracted_data, validation, is_qualified=False)
        
        # Verifica elementos da resposta
        assert "ENEL" in response
        assert "R$ 150,00" in response
        assert "R$ 200/mês" in response
        assert "financiamento" in response
    
    def test_process_ai_request_compatibility(self):
        """Testa função de compatibilidade com media_id"""
        with patch('scripts.serena_agent.core_agent.SerenaAIAgent') as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent.process_conversation.return_value = {"result": "success"}
            mock_agent_class.return_value = mock_agent
            
            # Testa chamada com media_id
            result = process_ai_request(
                phone="+5511999999999",
                message="conta energia",
                action="respond",
                media_id="media_123"
            )
            
            # Verifica se foi chamado corretamente
            mock_agent.process_conversation.assert_called_once_with(
                "+5511999999999", "conta energia", "respond", "media_123"
            )
            assert result["result"] == "success"


class TestOCRToolDescription:
    """Testes para verificar descrição melhorada da OCR tool"""
    
    def test_ocr_tool_description_includes_actions(self):
        """Testa se descrição da OCR tool inclui todas as ações"""
        agent = SerenaAIAgent()
        
        if agent.tools:
            ocr_tool = None
            for tool in agent.tools:
                if hasattr(tool, 'name') and tool.name == "ocr_processor":
                    ocr_tool = tool
                    break
            
            if ocr_tool:
                description = ocr_tool.description
                
                # Verifica se todas as ações estão documentadas
                expected_actions = [
                    "process_image",
                    "extract_fields", 
                    "validate_invoice",
                    "identify_distributor",
                    "validate_structured",
                    "get_supported_distributors"
                ]
                
                for action in expected_actions:
                    assert action in description, f"Ação '{action}' deve estar na descrição"
                
                # Verifica se menciona campos extraídos
                expected_fields = ["nome_cliente", "distribuidora", "valor_conta", "consumo_kwh"]
                for field in expected_fields:
                    assert field in description, f"Campo '{field}' deve estar na descrição"
                
                # Verifica se menciona distribuidoras suportadas
                assert "CEMIG" in description
                assert "ENEL" in description
                assert "20+" in description


if __name__ == "__main__":
    # Executar testes específicos para task-251
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-k", "test_energy_bill_context_detection or test_process_energy_bill_image_success"
    ]) 