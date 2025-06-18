#!/usr/bin/env python3
"""
Vision Processor Module

Este módulo contém a lógica para processamento de imagens de conta de energia
usando a Vision API do OpenAI GPT-4o-mini.

Author: Serena-Coder AI Agent
Version: 1.0.0 - Refatoração para modularização
Created: 2025-01-17
"""

import re
import json
import logging
import requests
from typing import Dict, Any, Optional
from openai import OpenAI

# Configure logging
logger = logging.getLogger(__name__)


class VisionProcessor:
    """
    Classe responsável pelo processamento de imagens de conta de energia
    usando Vision API e validação dos dados extraídos.
    """
    
    def __init__(self, openai_client: OpenAI, whatsapp_token: str):
        """
        Inicializa o processador de visão.
        
        Args:
            openai_client (OpenAI): Cliente OpenAI configurado
            whatsapp_token (str): Token da API do WhatsApp
        """
        self.openai_client = openai_client
        self.whatsapp_token = whatsapp_token
        
        # Palavras-chave para identificação de conta de energia
        self.energy_keywords = [
            'conta', 'fatura', 'luz', 'energia', 'cemig', 'enel', 'light', 
            'cpfl', 'elektro', 'coelba', 'celpe', 'cosern', 'coelce',
            'celg', 'ceb', 'copel', 'rge', 'ceee', 'celesc', 'energisa',
            'ampla', 'bandeirante', 'piratininga', 'aes', 'distribuidora'
        ]
        
        # Palavras-chave negativas (conversas gerais)
        self.negative_keywords = [
            'como funciona', 'quanto custa', 'sobre energia', 'energia solar',
            'explicar', 'dúvida', 'pergunta', 'informação'
        ]
    
    def is_energy_bill_image(self, message: str) -> bool:
        """
        Verifica se a mensagem indica que uma imagem de conta de energia foi enviada.
        
        Args:
            message (str): Mensagem recebida junto com a imagem
            
        Returns:
            bool: True se é provável que seja uma conta de energia
        """
        message_lower = message.lower()
        
        # Se mensagem contém [FATURA_ENVIADA:] ou [DOCUMENTO_ENVIADO:]
        if '[FATURA_ENVIADA:' in message or '[DOCUMENTO_ENVIADO:' in message:
            return True
        
        # Se mensagem contém palavras-chave de energia
        if any(keyword in message_lower for keyword in self.energy_keywords):
            return True
        
        # Se mensagem é muito curta (provavelmente só imagem)
        if len(message.strip()) < 10:
            return True
        
        # Verificar indicadores negativos
        if any(keyword in message_lower for keyword in self.negative_keywords):
            return False
        
        return False
    
    def get_whatsapp_media_url(self, media_id: str) -> Optional[str]:
        """
        Obtém a URL da mídia do WhatsApp usando o media_id.
        
        Args:
            media_id (str): ID da mídia fornecido pelo webhook
            
        Returns:
            Optional[str]: URL da mídia ou None se falhar
        """
        try:
            # URL da API do WhatsApp para obter informações da mídia
            media_info_url = f"https://graph.facebook.com/v23.0/{media_id}"
            
            headers = {
                "Authorization": f"Bearer {self.whatsapp_token}",
                "Content-Type": "application/json"
            }
            
            # Obter informações da mídia
            response = requests.get(media_info_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                media_info = response.json()
                media_url = media_info.get('url')
                
                if media_url:
                    logger.info(f"✅ URL da mídia obtida: {media_id}")
                    return media_url
                else:
                    logger.error(f"❌ URL não encontrada na resposta da mídia: {media_id}")
                    return None
            else:
                logger.error(f"❌ Falha ao obter informações da mídia: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter URL da mídia: {str(e)}")
            return None
    
    def extract_bill_data_with_vision(
        self,
        image_url: str,
        model: str = "gpt-4o-mini",
        max_tokens: int = 400,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Extrai dados da conta de energia usando Vision API do GPT-4o-mini.
        
        Args:
            image_url (str): URL da imagem da conta
            model (str): Modelo OpenAI
            max_tokens (int): Máximo de tokens
            temperature (float): Temperatura (baixa para precisão)
            
        Returns:
            Dict[str, Any]: Dados extraídos da conta
        """
        try:
            logger.info(f"🔍 Extraindo dados da conta usando Vision API")
            
            # Construir payload multimodal para Vision API
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Esta é uma conta de energia elétrica brasileira. Por favor, extraia as seguintes informações em formato JSON:

{
  "cliente_nome": "Nome do cliente/titular",
  "valor_total": "Valor total a pagar (R$)",
  "consumo_kwh": "Consumo em kWh",
  "distribuidora": "Nome da distribuidora",
  "vencimento": "Data de vencimento",
  "endereco": "Endereço de instalação",
  "numero_instalacao": "Número da instalação"
}

Se não conseguir identificar algum campo, use "NÃO_IDENTIFICADO". Seja preciso com os valores numéricos."""
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
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extrair resposta
            extracted_text = response.choices[0].message.content
            logger.info(f"📄 Resposta da Vision API: {extracted_text}")
            
            # Tentar parsear JSON da resposta
            try:
                # Buscar JSON na resposta
                json_match = re.search(r'\{.*\}', extracted_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    extracted_data = json.loads(json_str)
                    
                    # Validar dados extraídos
                    if self.validate_extracted_data(extracted_data):
                        logger.info(f"✅ Dados extraídos com sucesso")
                        return {
                            "success": True,
                            "data": extracted_data,
                            "raw_response": extracted_text
                        }
                    else:
                        logger.warning(f"⚠️ Dados extraídos não passaram na validação")
                        return {
                            "success": False,
                            "error": "Dados extraídos inválidos",
                            "data": extracted_data,
                            "raw_response": extracted_text
                        }
                else:
                    logger.error(f"❌ Não foi possível encontrar JSON na resposta")
                    return {
                        "success": False,
                        "error": "JSON não encontrado na resposta",
                        "raw_response": extracted_text
                    }
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ Erro ao parsear JSON: {str(e)}")
                return {
                    "success": False,
                    "error": f"Erro ao parsear JSON: {str(e)}",
                    "raw_response": extracted_text
                }
                
        except Exception as e:
            logger.error(f"❌ Erro na Vision API: {str(e)}")
            return {
                "success": False,
                "error": f"Erro na Vision API: {str(e)}"
            }
    
    def validate_extracted_data(self, data: Dict[str, Any]) -> bool:
        """
        Valida os dados extraídos da conta de energia.
        
        Args:
            data (Dict[str, Any]): Dados extraídos
            
        Returns:
            bool: True se dados são válidos
        """
        try:
            # Verificar se campos obrigatórios existem
            required_fields = ['cliente_nome', 'valor_total', 'distribuidora']
            
            for field in required_fields:
                if field not in data or not data[field] or data[field] == "NÃO_IDENTIFICADO":
                    logger.warning(f"⚠️ Campo obrigatório ausente ou inválido: {field}")
                    return False
            
            # Validar valor total (deve conter R$ e números)
            valor_total = str(data['valor_total'])
            if not re.search(r'R?\$?\s*\d+[,.]?\d*', valor_total):
                logger.warning(f"⚠️ Valor total inválido: {valor_total}")
                return False
            
            # Validar nome do cliente (mínimo 3 caracteres)
            if len(str(data['cliente_nome']).strip()) < 3:
                logger.warning(f"⚠️ Nome do cliente muito curto: {data['cliente_nome']}")
                return False
            
            logger.info(f"✅ Dados validados com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na validação: {str(e)}")
            return False
    
    def generate_final_conversation_response(
        self,
        extracted_data: Dict[str, Any],
        model: str = "gpt-4o-mini",
        max_tokens: int = 400,
        temperature: float = 0.7
    ) -> str:
        """
        Gera a resposta final da conversa após processar a conta de energia.
        Implementa a Etapa 6 do MASTER_GUIDE_FINAL.md.
        
        Args:
            extracted_data (Dict[str, Any]): Dados extraídos da conta
            model (str): Modelo OpenAI
            max_tokens (int): Máximo de tokens
            temperature (float): Temperatura da IA
            
        Returns:
            str: Resposta final da conversa
        """
        try:
            # Obter dados extraídos
            data = extracted_data.get('data', {})
            cliente_nome = data.get('cliente_nome', 'Cliente')
            valor_total = data.get('valor_total', 'Não identificado')
            distribuidora = data.get('distribuidora', 'Distribuidora')
            
            # Prompt para resposta final conforme Etapa 6
            prompt = f"""Você é a Serena, assistente virtual da SRna Energia. Você acabou de analisar a conta de energia do lead e extraiu os seguintes dados:

- Cliente: {cliente_nome}
- Valor da conta: {valor_total}
- Distribuidora: {distribuidora}

ESTA É A RESPOSTA FINAL DA CONVERSA. Sua resposta deve seguir exatamente a Etapa 6:

1. ✅ CONFIRMAR que analisou a conta com sucesso
2. 📊 APRESENTAR os dados extraídos de forma clara
3. 🎯 APRESENTAR as promoções disponíveis (que foram consultadas anteriormente)
4. 🙏 AGRADECER o interesse do lead
5. 📞 INFORMAR que um especialista entrará em contato em até 24 horas
6. 👋 SE DESPEDIR de forma amigável

Exemplo de estrutura:
"✅ Perfeito! Analisei sua conta da [DISTRIBUIDORA] com sucesso!

📊 Dados confirmados:
• Cliente: [NOME]
• Valor atual: [VALOR]
• Distribuidora: [DISTRIBUIDORA]

🎯 Com base no seu perfil, você pode economizar significativamente com nossas promoções de energia solar sem instalação!

🙏 Obrigada pelo seu interesse na Serena Energia! Um de nossos especialistas entrará em contato em até 24 horas para calcular sua economia personalizada.

👋 Tenha um ótimo dia!"

Seja entusiasmada, use emojis moderadamente e máximo 4 parágrafos. Gere apenas a resposta:"""
            
            # Gerar resposta usando OpenAI
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            final_response = response.choices[0].message.content.strip()
            logger.info(f"✅ Resposta final gerada com sucesso")
            
            return final_response
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resposta final: {str(e)}")
            # Resposta de fallback
            return f"""✅ Obrigada por enviar sua conta de energia!

Analisei os dados e nossa equipe entrará em contato em até 24 horas para apresentar as melhores opções de economia para você.

🙏 A Serena Energia agradece seu interesse! 

👋 Tenha um ótimo dia!"""
    
    def create_error_response(self, error_message: str) -> str:
        """
        Cria resposta amigável para erros de processamento de imagem.
        
        Args:
            error_message (str): Mensagem de erro técnica
            
        Returns:
            str: Resposta amigável para o lead
        """
        return """Desculpe, tive dificuldades para analisar a imagem da sua conta de energia. 😔

Pode tentar enviar novamente? Algumas dicas:
📸 Foto bem iluminada e nítida
📄 Todos os dados visíveis
📱 Imagem na vertical

Ou se preferir, pode enviar um PDF da conta. Estou aqui para ajudar! 😊"""
