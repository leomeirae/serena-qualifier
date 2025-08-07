# =============================================================================
# SERENA SDR - OCR TOOLS
# =============================================================================

"""
OCR Tools Module

Este módulo contém todas as ferramentas para processamento de imagens de faturas
de energia usando OpenAI Vision API e extração de dados relevantes.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import os
import json
import logging
import requests
import base64
from typing import Dict, Any, Optional, List
from datetime import datetime
import openai

logger = logging.getLogger(__name__)


class OCRTools:
    """Ferramentas para processamento OCR de faturas de energia."""
    
    def __init__(self):
        """Inicializa as ferramentas OCR."""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY não encontrado")
        
        openai.api_key = self.openai_api_key
        
        # Configurar timeout e retries
        self.timeout = 60
        self.max_retries = 3
    
    def process_energy_bill_image(self, image_url: str) -> Dict[str, Any]:
        """
        Processa imagem de fatura de energia via OpenAI Vision.
        
        Args:
            image_url: URL da imagem da fatura
            
        Returns:
            Dict: Dados extraídos da fatura
        """
        try:
            # Prompt específico para faturas de energia
            system_prompt = """
            Você é um especialista em análise de faturas de energia elétrica.
            
            Analise a imagem da fatura e extraia as seguintes informações em formato JSON:
            
            {
                "valor_total": "valor total da fatura (número)",
                "data_vencimento": "data de vencimento (YYYY-MM-DD)",
                "consumo_kwh": "consumo em kWh (número)",
                "distribuidora": "nome da distribuidora de energia",
                "numero_cliente": "número do cliente/instalação",
                "endereco": "endereço da instalação",
                "periodo_faturamento": "período de faturamento (mês/ano)",
                "valor_energia": "valor da energia (sem impostos)",
                "valor_impostos": "valor dos impostos",
                "valor_iluminacao": "valor da iluminação pública (se houver)",
                "valor_outros": "outros valores",
                "confianca": "nível de confiança da extração (0-100)"
            }
            
            IMPORTANTE:
            - Extraia apenas valores numéricos para campos de valor (sem R$, vírgulas, etc.)
            - Use formato YYYY-MM-DD para datas
            - Se algum campo não for encontrado, use null
            - Confiança deve ser um número entre 0 e 100
            - Retorne APENAS o JSON, sem texto adicional
            """
            
            # Chamar OpenAI Vision API
            response = openai.ChatCompletion.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analise esta fatura de energia e extraia os dados solicitados:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            # Extrair resposta
            content = response.choices[0].message.content.strip()
            
            # Tentar parsear JSON
            try:
                extracted_data = json.loads(content)
                
                # Validar e limpar dados
                cleaned_data = self._clean_extracted_data(extracted_data)
                
                return {
                    "success": True,
                    "dados_extraidos": cleaned_data,
                    "valor_conta": cleaned_data.get("valor_total", 0),
                    "data_vencimento": cleaned_data.get("data_vencimento"),
                    "consumo_kwh": cleaned_data.get("consumo_kwh", 0),
                    "distribuidora": cleaned_data.get("distribuidora"),
                    "confianca": cleaned_data.get("confianca", 0)
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao parsear JSON da resposta: {str(e)}")
                logger.error(f"Conteúdo recebido: {content}")
                
                # Fallback: tentar extrair informações básicas
                return self._fallback_extraction(content, image_url)
                
        except Exception as e:
            logger.error(f"Erro ao processar imagem: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "dados_extraidos": {},
                "valor_conta": 0,
                "confianca": 0
            }
    
    def _clean_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Limpa e valida dados extraídos.
        
        Args:
            data: Dados extraídos
            
        Returns:
            Dict: Dados limpos
        """
        cleaned = {}
        
        # Limpar valor total
        valor_total = data.get("valor_total")
        if valor_total:
            try:
                # Remover R$, espaços, vírgulas e converter para float
                valor_str = str(valor_total).replace("R$", "").replace(" ", "").replace(",", ".")
                cleaned["valor_total"] = float(valor_str)
            except (ValueError, TypeError):
                cleaned["valor_total"] = 0
        else:
            cleaned["valor_total"] = 0
        
        # Limpar consumo kWh
        consumo = data.get("consumo_kwh")
        if consumo:
            try:
                consumo_str = str(consumo).replace(" ", "").replace(",", ".")
                cleaned["consumo_kwh"] = float(consumo_str)
            except (ValueError, TypeError):
                cleaned["consumo_kwh"] = 0
        else:
            cleaned["consumo_kwh"] = 0
        
        # Limpar data de vencimento
        data_venc = data.get("data_vencimento")
        if data_venc:
            # Tentar diferentes formatos de data
            try:
                # Se já está no formato YYYY-MM-DD
                if len(data_venc) == 10 and data_venc[4] == "-" and data_venc[7] == "-":
                    cleaned["data_vencimento"] = data_venc
                else:
                    # Tentar converter outros formatos
                    cleaned["data_vencimento"] = self._parse_date(data_venc)
            except:
                cleaned["data_vencimento"] = None
        else:
            cleaned["data_vencimento"] = None
        
        # Outros campos
        cleaned["distribuidora"] = data.get("distribuidora", "").strip()
        cleaned["numero_cliente"] = data.get("numero_cliente", "").strip()
        cleaned["endereco"] = data.get("endereco", "").strip()
        cleaned["periodo_faturamento"] = data.get("periodo_faturamento", "").strip()
        cleaned["valor_energia"] = data.get("valor_energia", 0)
        cleaned["valor_impostos"] = data.get("valor_impostos", 0)
        cleaned["valor_iluminacao"] = data.get("valor_iluminacao", 0)
        cleaned["valor_outros"] = data.get("valor_outros", 0)
        cleaned["confianca"] = min(100, max(0, data.get("confianca", 0)))
        
        return cleaned
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Tenta parsear diferentes formatos de data.
        
        Args:
            date_str: String da data
            
        Returns:
            str: Data no formato YYYY-MM-DD ou None
        """
        try:
            # Remover espaços extras
            date_str = date_str.strip()
            
            # Se já está no formato correto
            if len(date_str) == 10 and date_str[4] == "-" and date_str[7] == "-":
                return date_str
            
            # Tentar formato DD/MM/YYYY
            if "/" in date_str:
                parts = date_str.split("/")
                if len(parts) == 3:
                    day, month, year = parts
                    if len(year) == 2:
                        year = "20" + year
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            # Tentar formato DD-MM-YYYY
            if "-" in date_str and len(date_str.split("-")) == 3:
                parts = date_str.split("-")
                if len(parts) == 3:
                    day, month, year = parts
                    if len(year) == 2:
                        year = "20" + year
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            return None
            
        except:
            return None
    
    def _fallback_extraction(self, content: str, image_url: str) -> Dict[str, Any]:
        """
        Extração de fallback quando o JSON não pode ser parseado.
        
        Args:
            content: Conteúdo da resposta da API
            image_url: URL da imagem
            
        Returns:
            Dict: Dados extraídos com fallback
        """
        try:
            # Tentar extrair informações básicas do texto
            import re
            
            # Procurar por valores monetários
            valor_pattern = r'R?\$?\s*([0-9.,]+)'
            valores = re.findall(valor_pattern, content)
            
            valor_total = 0
            if valores:
                try:
                    valor_str = valores[0].replace(",", ".")
                    valor_total = float(valor_str)
                except:
                    pass
            
            # Procurar por consumo kWh
            consumo_pattern = r'(\d+(?:[.,]\d+)?)\s*kWh'
            consumos = re.findall(consumo_pattern, content)
            
            consumo_kwh = 0
            if consumos:
                try:
                    consumo_str = consumos[0].replace(",", ".")
                    consumo_kwh = float(consumo_str)
                except:
                    pass
            
            # Procurar por datas
            data_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
            datas = re.findall(data_pattern, content)
            
            data_vencimento = None
            if datas:
                data_vencimento = self._parse_date(datas[0])
            
            return {
                "success": True,
                "dados_extraidos": {
                    "valor_total": valor_total,
                    "consumo_kwh": consumo_kwh,
                    "data_vencimento": data_vencimento,
                    "distribuidora": "",
                    "numero_cliente": "",
                    "endereco": "",
                    "periodo_faturamento": "",
                    "valor_energia": 0,
                    "valor_impostos": 0,
                    "valor_iluminacao": 0,
                    "valor_outros": 0,
                    "confianca": 30  # Baixa confiança para fallback
                },
                "valor_conta": valor_total,
                "data_vencimento": data_vencimento,
                "consumo_kwh": consumo_kwh,
                "distribuidora": "",
                "confianca": 30
            }
            
        except Exception as e:
            logger.error(f"Erro no fallback extraction: {str(e)}")
            return {
                "success": False,
                "error": "Falha na extração de dados",
                "dados_extraidos": {},
                "valor_conta": 0,
                "confianca": 0
            }
    
    def validate_energy_bill(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida se os dados extraídos são de uma fatura de energia válida.
        
        Args:
            extracted_data: Dados extraídos
            
        Returns:
            Dict: Resultado da validação
        """
        try:
            valor_total = extracted_data.get("valor_total", 0)
            consumo_kwh = extracted_data.get("consumo_kwh", 0)
            confianca = extracted_data.get("confianca", 0)
            
            # Critérios de validação
            is_valid = True
            issues = []
            
            # Verificar se tem valor
            if valor_total <= 0:
                is_valid = False
                issues.append("Valor total não encontrado ou inválido")
            
            # Verificar se tem consumo
            if consumo_kwh <= 0:
                is_valid = False
                issues.append("Consumo kWh não encontrado ou inválido")
            
            # Verificar confiança
            if confianca < 50:
                is_valid = False
                issues.append("Baixa confiança na extração")
            
            # Verificar se parece ser uma fatura de energia
            distribuidora = extracted_data.get("distribuidora", "").lower()
            if not any(keyword in distribuidora for keyword in ["energia", "eletrica", "light", "power", "energy"]):
                issues.append("Pode não ser uma fatura de energia")
            
            return {
                "success": True,
                "is_valid": is_valid,
                "issues": issues,
                "valor_total": valor_total,
                "consumo_kwh": consumo_kwh,
                "confianca": confianca
            }
            
        except Exception as e:
            logger.error(f"Erro na validação: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "is_valid": False,
                "issues": ["Erro na validação"]
            }
    
    def extract_lead_info_from_bill(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrai informações do lead a partir dos dados da fatura.
        
        Args:
            extracted_data: Dados extraídos da fatura
            
        Returns:
            Dict: Informações do lead
        """
        try:
            endereco = extracted_data.get("endereco", "")
            distribuidora = extracted_data.get("distribuidora", "")
            
            # Tentar extrair cidade e estado do endereço
            cidade = ""
            estado = ""
            
            if endereco:
                # Padrão comum: "Cidade - Estado" ou "Cidade, Estado"
                import re
                
                # Procurar por padrão de cidade e estado
                cidade_estado_pattern = r'([A-Za-zÀ-ÿ\s]+)[\s-]*([A-Z]{2})'
                match = re.search(cidade_estado_pattern, endereco)
                
                if match:
                    cidade = match.group(1).strip()
                    estado = match.group(2).strip()
            
            return {
                "success": True,
                "cidade": cidade,
                "estado": estado,
                "distribuidora": distribuidora,
                "numero_cliente": extracted_data.get("numero_cliente", ""),
                "endereco_completo": endereco
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair informações do lead: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "cidade": "",
                "estado": "",
                "distribuidora": "",
                "numero_cliente": "",
                "endereco_completo": ""
            }
    
    def process_whatsapp_media(self, media_id: str, whatsapp_mcp_url: str) -> Dict[str, Any]:
        """
        Processa mídia recebida via WhatsApp.
        
        Args:
            media_id: ID da mídia no WhatsApp
            whatsapp_mcp_url: URL do MCP do WhatsApp
            
        Returns:
            Dict: Resultado do processamento
        """
        try:
            # Primeiro, obter URL da mídia via WhatsApp MCP
            # (Esta funcionalidade depende da implementação do WhatsApp MCP)
            
            # Por enquanto, assumir que a URL já foi fornecida
            # Em uma implementação completa, seria necessário:
            # 1. Chamar WhatsApp MCP para obter URL da mídia
            # 2. Fazer download da imagem
            # 3. Fazer upload para um storage público
            # 4. Processar com OCR
            
            return {
                "success": False,
                "error": "Funcionalidade de processamento de mídia WhatsApp não implementada",
                "dados_extraidos": {},
                "valor_conta": 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar mídia WhatsApp: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "dados_extraidos": {},
                "valor_conta": 0
            } 