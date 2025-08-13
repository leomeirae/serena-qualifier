# =============================================================================
# SERENA SDR - SERENA TOOLS
# =============================================================================

"""
Serena Tools Module

Este módulo contém todas as ferramentas para interação com a API Serena via MCP Server.
Responsável por consulta de planos, qualificação de leads e criação de contratos.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import os
import json
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


class SerenaTools:
    """Ferramentas para interação com API Serena via MCP."""
    
    def __init__(self):
        """Inicializa as ferramentas da Serena."""
        self.mcp_url = os.getenv('SERENA_MCP_URL')
        if not self.mcp_url:
            raise ValueError("SERENA_MCP_URL não encontrado")
        
        # Configurar timeout e retries
        self.timeout = 30
        self.max_retries = 3
    
    def _make_mcp_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Faz requisição para o MCP Server da Serena.
        
        Args:
            method: Método MCP (tools/call)
            params: Parâmetros da requisição
            
        Returns:
            Dict: Resposta do MCP Server
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.mcp_url}/mcp",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                if "error" in result:
                    raise Exception(f"MCP Error: {result['error']}")
                
                return result.get("result", {})
                
            except Exception as e:
                logger.error(f"Tentativa {attempt + 1} falhou: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                continue
    
    def consultar_areas_operacao_gd(self, cidade: str = None, estado: str = None, codigo_ibge: str = None) -> Dict[str, Any]:
        """
        Consulta áreas onde o serviço de Geração Distribuída está disponível.
        
        Args:
            cidade: Nome da cidade (opcional)
            estado: Sigla do estado (opcional)
            codigo_ibge: Código IBGE da localidade (opcional)
            
        Returns:
            Dict: Lista de áreas de operação disponíveis
        """
        try:
            arguments = {}
            if cidade:
                arguments["cidade"] = cidade
            if estado:
                arguments["estado"] = estado
            if codigo_ibge:
                arguments["codigo_ibge"] = codigo_ibge
            
            result = self._make_mcp_request("tools/call", {
                "name": "consultar_areas_operacao_gd",
                "arguments": arguments
            })
            
            return {
                "success": True,
                "areas": result.get("result", []),
                "count": len(result.get("result", []))
            }
            
        except Exception as e:
            logger.error(f"Erro ao consultar áreas de operação: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "areas": [],
                "count": 0
            }
    
    def obter_planos_gd(self, cidade: str = None, estado: str = None, id_distribuidora: str = None) -> Dict[str, Any]:
        """
        Obtém planos de Geração Distribuída disponíveis para uma localidade.
        
        Args:
            cidade: Nome da cidade (opcional)
            estado: Sigla do estado (opcional)
            id_distribuidora: ID da distribuidora (prioridade)
            
        Returns:
            Dict: Lista de planos disponíveis
        """
        try:
            arguments = {}
            if id_distribuidora:
                arguments["id_distribuidora"] = id_distribuidora
            elif cidade and estado:
                arguments["cidade"] = cidade
                arguments["estado"] = estado
            else:
                raise ValueError("Deve fornecer id_distribuidora ou cidade+estado")
            
            result = self._make_mcp_request("tools/call", {
                "name": "obter_planos_gd",
                "arguments": arguments
            })
            
            return {
                "success": True,
                "planos": result.get("result", []),
                "count": len(result.get("result", []))
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter planos GD: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "planos": [],
                "count": 0
            }
    
    def validar_qualificacao_lead(self, cidade: str, estado: str, tipo_pessoa: str, valor_conta: float) -> Dict[str, Any]:
        """
        Valida se um lead está qualificado para produtos de energia solar.
        
        Args:
            cidade: Cidade do lead
            estado: Estado do lead
            tipo_pessoa: "natural" ou "juridical"
            valor_conta: Valor da conta de energia
            
        Returns:
            Dict: Resultado da validação
        """
        try:
            arguments = {
                "cidade": cidade,
                "estado": estado,
                "tipo_pessoa": tipo_pessoa,
                "valor_conta": valor_conta
            }
            
            result = self._make_mcp_request("tools/call", {
                "name": "validar_qualificacao_lead",
                "arguments": arguments
            })
            
            qualification_result = result.get("result", {})
            
            return {
                "success": True,
                "qualificado": qualification_result.get("qualification", False),
                "produto": qualification_result.get("product", "Geração Distribuída"),
                "detalhes": qualification_result
            }
            
        except Exception as e:
            logger.error(f"Erro ao validar qualificação: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "qualificado": False,
                "produto": "Geração Distribuída"
            }
    
    def cadastrar_lead(self, dados_lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cadastra um novo lead na base de dados da Serena.
        
        Args:
            dados_lead: Dados completos do lead
            
        Returns:
            Dict: Resultado do cadastro
        """
        try:
            # Validar dados obrigatórios
            required_fields = [
                "fullName", "personType", "emailAddress", "mobilePhone",
                "utilityBillHolder", "utilityBillingValue", "identificationNumber"
            ]
            
            for field in required_fields:
                if field not in dados_lead:
                    raise ValueError(f"Campo obrigatório ausente: {field}")
            
            result = self._make_mcp_request("tools/call", {
                "name": "cadastrar_lead",
                "arguments": {"dados_lead": dados_lead}
            })
            
            return {
                "success": True,
                "lead_id": result.get("lead_id"),
                "message": "Lead cadastrado com sucesso"
            }
            
        except Exception as e:
            logger.error(f"Erro ao cadastrar lead: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def buscar_lead_por_id(self, id_lead: str) -> Dict[str, Any]:
        """
        Busca informações detalhadas de um lead específico.
        
        Args:
            id_lead: ID único do lead
            
        Returns:
            Dict: Informações completas do lead
        """
        try:
            result = self._make_mcp_request("tools/call", {
                "name": "buscar_lead_por_id",
                "arguments": {"id_lead": id_lead}
            })
            
            return {
                "success": True,
                "lead": result.get("result", {})
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar lead: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "lead": {}
            }
    
    def atualizar_lead(self, id_lead: str, dados_atualizacao: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza informações de um lead existente.
        
        Args:
            id_lead: ID do lead
            dados_atualizacao: Dados a serem atualizados
            
        Returns:
            Dict: Confirmação da atualização
        """
        try:
            result = self._make_mcp_request("tools/call", {
                "name": "atualizar_lead",
                "arguments": {
                    "id_lead": id_lead,
                    "dados_atualizacao": dados_atualizacao
                }
            })
            
            return {
                "success": True,
                "message": "Lead atualizado com sucesso"
            }
            
        except Exception as e:
            logger.error(f"Erro ao atualizar lead: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def criar_contrato(self, id_lead: str, plano: Dict[str, Any] = None, representantes_legais: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Cria um contrato de geração distribuída para um lead.
        
        Args:
            id_lead: ID do lead
            plano: Dados do plano (opcional)
            representantes_legais: Lista de representantes legais (opcional)
            
        Returns:
            Dict: ID do contrato criado e status
        """
        try:
            arguments = {"id_lead": id_lead}
            
            if plano:
                arguments["plano"] = plano
            if representantes_legais:
                arguments["representantes_legais"] = representantes_legais
            
            result = self._make_mcp_request("tools/call", {
                "name": "criar_contrato",
                "arguments": arguments
            })
            
            return {
                "success": True,
                "contrato_id": result.get("contrato_id"),
                "message": "Contrato criado com sucesso"
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar contrato: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def processar_fatura_energia(self, image_url: str) -> Dict[str, Any]:
        """
        Processa imagem de fatura de energia via OCR.
        
        Args:
            image_url: URL da imagem da fatura
            
        Returns:
            Dict: Dados extraídos da fatura
        """
        try:
            result = self._make_mcp_request("tools/call", {
                "name": "process_energy_bill_image",
                "arguments": {"image_url": image_url}
            })
            
            return {
                "success": True,
                "dados_extraidos": result.get("result", {}),
                "valor_conta": result.get("result", {}).get("valor", 0),
                "data_vencimento": result.get("result", {}).get("vencimento"),
                "consumo_kwh": result.get("result", {}).get("consumo")
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar fatura: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "dados_extraidos": {},
                "valor_conta": 0
            }
    
    def buscar_leads(self, filtros: str = None, pagina: int = 1, limite: int = 10) -> Dict[str, Any]:
        """
        Busca leads com filtros e paginação.
        
        Args:
            filtros: Filtros para busca (opcional)
            pagina: Número da página (padrão: 1)
            limite: Limite de resultados por página (padrão: 10)
            
        Returns:
            Dict: Lista paginada de leads
        """
        try:
            arguments = {
                "pagina": pagina,
                "limite": limite
            }
            
            if filtros:
                arguments["filtros"] = filtros
            
            result = self._make_mcp_request("tools/call", {
                "name": "buscar_leads",
                "arguments": arguments
            })
            
            return {
                "success": True,
                "leads": result.get("result", {}).get("leads", []),
                "total": result.get("result", {}).get("total", 0),
                "pagina": pagina,
                "limite": limite
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar leads: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "leads": [],
                "total": 0
            }
    
    def atualizar_credenciais_distribuidora(self, id_lead: str, login: str, senha: str) -> Dict[str, Any]:
        """
        Atualiza credenciais de acesso à distribuidora de energia.
        
        Args:
            id_lead: ID do lead
            login: Login da distribuidora
            senha: Senha da distribuidora
            
        Returns:
            Dict: Confirmação da atualização
        """
        try:
            result = self._make_mcp_request("tools/call", {
                "name": "atualizar_credenciais_distribuidora",
                "arguments": {
                    "id_lead": id_lead,
                    "login": login,
                    "senha": senha
                }
            })
            
            return {
                "success": True,
                "message": "Credenciais atualizadas com sucesso"
            }
            
        except Exception as e:
            logger.error(f"Erro ao atualizar credenciais: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_energy_plans_for_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtém planos de energia apropriados para um lead específico.
        
        Args:
            lead_data: Dados do lead
            
        Returns:
            Dict: Planos disponíveis para o lead
        """
        try:
            cidade = lead_data.get('city', '')
            estado = lead_data.get('state', '')
            
            if not cidade or not estado:
                return {
                    "success": False,
                    "error": "Cidade e estado são obrigatórios",
                    "planos": []
                }
            
            # Primeiro verificar se a área tem cobertura
            areas_result = self.consultar_areas_operacao_gd(cidade=cidade, estado=estado)
            
            if not areas_result["success"] or areas_result["count"] == 0:
                return {
                    "success": False,
                    "error": "Área não possui cobertura para GD",
                    "planos": []
                }
            
            # Obter planos disponíveis
            planos_result = self.obter_planos_gd(cidade=cidade, estado=estado)
            
            return {
                "success": True,
                "areas_cobertura": areas_result["areas"],
                "planos": planos_result["planos"],
                "cidade": cidade,
                "estado": estado
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter planos para lead: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "planos": []
            }
    
    def buscar_planos_de_energia_por_localizacao(self, cidade: str, estado: str) -> Dict[str, Any]:
        """
        Busca planos de energia disponíveis para uma localização específica.
        
        Args:
            cidade: Nome da cidade
            estado: Sigla do estado
            
        Returns:
            Dict: Lista de planos disponíveis para a localização
        """
        try:
            # Primeiro verificar se a área tem cobertura
            areas_result = self.consultar_areas_operacao_gd(cidade=cidade, estado=estado)
            
            if not areas_result["success"] or areas_result["count"] == 0:
                return {
                    "success": False,
                    "error": "Área não possui cobertura para Geração Distribuída",
                    "planos": [],
                    "cidade": cidade,
                    "estado": estado
                }
            
            # Obter planos disponíveis
            planos_result = self.obter_planos_gd(cidade=cidade, estado=estado)
            
            return {
                "success": True,
                "areas_cobertura": areas_result["areas"],
                "planos": planos_result["planos"],
                "cidade": cidade,
                "estado": estado,
                "total_planos": planos_result["count"]
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar planos por localização: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "planos": [],
                "cidade": cidade,
                "estado": estado
            }
    
    def analisar_conta_de_energia_de_imagem(self, image_url: str) -> Dict[str, Any]:
        """
        Analisa uma imagem de conta de energia para extrair informações relevantes.
        
        Args:
            image_url: URL da imagem da conta de energia
            
        Returns:
            Dict: Dados extraídos da conta de energia
        """
        try:
            # Usar o método existente processar_fatura_energia
            result = self.processar_fatura_energia(image_url)
            
            if result["success"]:
                return {
                    "success": True,
                    "valor_conta": result["valor_conta"],
                    "data_vencimento": result["data_vencimento"],
                    "consumo_kwh": result["consumo_kwh"],
                    "dados_extraidos": result["dados_extraidos"],
                    "message": "Conta de energia analisada com sucesso"
                }
            else:
                return {
                    "success": False,
                    "error": result["error"],
                    "valor_conta": 0,
                    "data_vencimento": None,
                    "consumo_kwh": 0,
                    "dados_extraidos": {}
                }
                
        except Exception as e:
            logger.error(f"Erro ao analisar conta de energia: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "valor_conta": 0,
                "data_vencimento": None,
                "consumo_kwh": 0,
                "dados_extraidos": {}
            }


# =============================================================================
# FUNÇÕES WRAPPER PARA COMPATIBILIDADE COM AGENT_ORCHESTRATOR
# =============================================================================

# Instância global da classe SerenaTools
_serena_tools_instance = None

def _get_serena_tools_instance():
    """Retorna uma instância da classe SerenaTools."""
    global _serena_tools_instance
    if _serena_tools_instance is None:
        _serena_tools_instance = SerenaTools()
    return _serena_tools_instance

@tool
def buscar_planos_de_energia_por_localizacao(cidade: str, estado: str) -> Dict[str, Any]:
    """Função wrapper para buscar planos de energia por localização.
    
    Args:
        cidade: Nome da cidade
        estado: Sigla do estado
    """
    try:
        serena_tools = _get_serena_tools_instance()
        return serena_tools.buscar_planos_de_energia_por_localizacao(cidade, estado)
    except Exception as e:
        logger.error(f"Erro na função wrapper buscar_planos_de_energia_por_localizacao: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "planos": [],
            "cidade": cidade,
            "estado": estado
        }

@tool
def analisar_conta_de_energia_de_imagem(image_url: str) -> Dict[str, Any]:
    """Função wrapper para analisar conta de energia de imagem.
    
    Args:
        image_url: URL da imagem da conta de energia
    """
    try:
        serena_tools = _get_serena_tools_instance()
        return serena_tools.analisar_conta_de_energia_de_imagem(image_url)
    except Exception as e:
        logger.error(f"Erro na função wrapper analisar_conta_de_energia_de_imagem: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "valor_conta": 0,
            "data_vencimento": None,
            "consumo_kwh": 0,
            "dados_extraidos": {}
        }