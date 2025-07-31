# =============================================================================
# SERENA SDR - WHATSAPP TOOLS
# =============================================================================

"""
WhatsApp Tools Module

Este módulo contém todas as ferramentas para interação com o WhatsApp MCP Server.
Responsável por envio de mensagens, templates e gestão de conversas.

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

logger = logging.getLogger(__name__)


class WhatsAppTools:
    """Ferramentas para interação com WhatsApp via MCP."""
    
    def __init__(self):
        """Inicializa as ferramentas do WhatsApp."""
        self.mcp_url = os.getenv('WHATSAPP_MCP_URL')
        if not self.mcp_url:
            raise ValueError("WHATSAPP_MCP_URL não encontrado")
        
        # Configurar timeout e retries
        self.timeout = 30
        self.max_retries = 3
    
    def _make_mcp_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Faz requisição para o MCP Server do WhatsApp.
        
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
    
    def send_text_message(self, to: str, message: str) -> Dict[str, Any]:
        """
        Envia mensagem de texto via WhatsApp.
        
        Args:
            to: Número de telefone no formato internacional (ex: "5511999999999")
            message: Conteúdo da mensagem de texto
            
        Returns:
            Dict: Resultado do envio
        """
        try:
            # Validar formato do número
            if not to.startswith('55'):
                to = f"55{to.replace('+', '').replace('-', '').replace(' ', '')}"
            
            result = self._make_mcp_request("tools/call", {
                "name": "sendTextMessage",
                "arguments": {
                    "to": to,
                    "message": message
                }
            })
            
            return {
                "success": True,
                "message_id": result.get("content", [{}])[0].get("text", ""),
                "response": result
            }
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem de texto: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_template_message(self, to: str, template_name: str, language: str = "pt_BR", components: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Envia mensagem usando template aprovado pelo WhatsApp.
        
        Args:
            to: Número de telefone no formato internacional
            template_name: Nome do template aprovado
            language: Código do idioma (ex: "pt_BR", "en_US")
            components: Componentes do template (parâmetros dinâmicos)
            
        Returns:
            Dict: Resultado do envio
        """
        try:
            # Validar formato do número
            if not to.startswith('55'):
                to = f"55{to.replace('+', '').replace('-', '').replace(' ', '')}"
            
            arguments = {
                "to": to,
                "templateName": template_name,
                "language": language
            }
            
            if components:
                arguments["components"] = components
            
            result = self._make_mcp_request("tools/call", {
                "name": "sendTemplateMessage",
                "arguments": arguments
            })
            
            return {
                "success": True,
                "message_id": result.get("content", [{}])[0].get("text", ""),
                "response": result
            }
            
        except Exception as e:
            logger.error(f"Erro ao enviar template: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_image_message(self, to: str, image_url: str, caption: str = None) -> Dict[str, Any]:
        """
        Envia imagem com legenda via WhatsApp.
        
        Args:
            to: Número de telefone no formato internacional
            image_url: URL pública da imagem
            caption: Legenda da imagem (opcional)
            
        Returns:
            Dict: Resultado do envio
        """
        try:
            # Validar formato do número
            if not to.startswith('55'):
                to = f"55{to.replace('+', '').replace('-', '').replace(' ', '')}"
            
            arguments = {
                "to": to,
                "imageUrl": image_url
            }
            
            if caption:
                arguments["caption"] = caption
            
            result = self._make_mcp_request("tools/call", {
                "name": "sendImageMessage",
                "arguments": arguments
            })
            
            return {
                "success": True,
                "message_id": result.get("content", [{}])[0].get("text", ""),
                "response": result
            }
            
        except Exception as e:
            logger.error(f"Erro ao enviar imagem: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def mark_message_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Marca uma mensagem como lida no WhatsApp.
        
        Args:
            message_id: ID da mensagem a ser marcada como lida
            
        Returns:
            Dict: Resultado da operação
        """
        try:
            result = self._make_mcp_request("tools/call", {
                "name": "markMessageAsRead",
                "arguments": {
                    "messageId": message_id
                }
            })
            
            return {
                "success": True,
                "response": result
            }
            
        except Exception as e:
            logger.error(f"Erro ao marcar mensagem como lida: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_welcome_message(self, to: str, lead_name: str = None) -> Dict[str, Any]:
        """
        Envia mensagem de boas-vindas personalizada.
        
        Args:
            to: Número de telefone
            lead_name: Nome do lead (opcional)
            
        Returns:
            Dict: Resultado do envio
        """
        try:
            if lead_name:
                message = f"""👋 Olá {lead_name}! 

Sou a Sílvia, sua consultora virtual da Serena Energia! 🌞

Estou aqui para te ajudar a economizar até 95% na sua conta de luz com energia solar.

Para começarmos, você poderia me enviar uma foto da sua última conta de energia? 📸

Assim posso te mostrar exatamente quanto você pode economizar! 💰"""
            else:
                message = """👋 Olá! 

Sou a Sílvia, sua consultora virtual da Serena Energia! 🌞

Estou aqui para te ajudar a economizar até 95% na sua conta de luz com energia solar.

Para começarmos, você poderia me enviar uma foto da sua última conta de energia? 📸

Assim posso te mostrar exatamente quanto você pode economizar! 💰"""
            
            return self.send_text_message(to, message)
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem de boas-vindas: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_qualification_message(self, to: str, lead_name: str, city: str, invoice_amount: float) -> Dict[str, Any]:
        """
        Envia mensagem de qualificação com planos disponíveis.
        
        Args:
            to: Número de telefone
            lead_name: Nome do lead
            city: Cidade do lead
            invoice_amount: Valor da conta de energia
            
        Returns:
            Dict: Resultado do envio
        """
        try:
            message = f"""🎉 Perfeito, {lead_name}!

Analisei sua conta de R$ {invoice_amount:.2f} e você está QUALIFICADO para nossa solução de energia solar! ✅

Em {city}, temos planos especiais que podem reduzir sua conta em até 95%! 🌞

Gostaria que eu te apresente os planos disponíveis para sua região?

Responda "SIM" que te mostro as opções! 💚"""
            
            return self.send_text_message(to, message)
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem de qualificação: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_plans_message(self, to: str, lead_name: str, plans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Envia mensagem com planos disponíveis.
        
        Args:
            to: Número de telefone
            lead_name: Nome do lead
            plans: Lista de planos disponíveis
            
        Returns:
            Dict: Resultado do envio
        """
        try:
            if not plans:
                message = f"""Desculpe, {lead_name}! 😔

No momento não temos planos disponíveis para sua região.

Mas não se preocupe! Vou te manter informado quando chegarmos por aí! 🌞

Obrigada pelo interesse! 💚"""
            else:
                message = f"""📋 Aqui estão os planos disponíveis para você, {lead_name}:

"""
                
                for i, plan in enumerate(plans[:3], 1):  # Limitar a 3 planos
                    plan_name = plan.get('name', 'Plano')
                    discount = plan.get('discount', '0')
                    fidelity = plan.get('fidelityMonths', 0)
                    
                    discount_percent = float(discount) * 100 if discount else 0
                    
                    message += f"""🔸 {i}. {plan_name}
   💰 Desconto: {discount_percent:.0f}%
   📅 Fidelidade: {fidelity} meses

"""
                
                message += """Qual plano te interessou mais?

Responda com o número do plano (1, 2 ou 3) que te ajudo com os próximos passos! 🚀"""
            
            return self.send_text_message(to, message)
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem de planos: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_follow_up_message(self, to: str, lead_name: str, city: str) -> Dict[str, Any]:
        """
        Envia mensagem de follow-up após 2 horas sem resposta.
        
        Args:
            to: Número de telefone
            lead_name: Nome do lead
            city: Cidade do lead
            
        Returns:
            Dict: Resultado do envio
        """
        try:
            message = f"""Oi {lead_name}! 😊

Só passando para lembrar que temos uma proposta especial de energia solar para você em {city}.

Quer economizar até 95% na sua conta de luz? 💰

Responda aqui que te ajudo! 🌞

Ou se preferir, pode me enviar sua conta de energia que faço uma análise personalizada! 📸"""
            
            return self.send_text_message(to, message)
            
        except Exception as e:
            logger.error(f"Erro ao enviar follow-up: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_contract_message(self, to: str, lead_name: str, plan_name: str) -> Dict[str, Any]:
        """
        Envia mensagem de confirmação de contrato.
        
        Args:
            to: Número de telefone
            lead_name: Nome do lead
            plan_name: Nome do plano escolhido
            
        Returns:
            Dict: Resultado do envio
        """
        try:
            message = f"""🎉 Parabéns, {lead_name}!

Você escolheu o {plan_name}! Excelente escolha! 🌞

Agora vou criar seu contrato e em breve nossa equipe entrará em contato para finalizar os detalhes.

Você receberá um email com todos os documentos e próximos passos! 📧

Obrigada por escolher a Serena Energia! 💚

Em breve você estará economizando muito na sua conta de luz! 💰"""
            
            return self.send_text_message(to, message)
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem de contrato: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_error_message(self, to: str) -> Dict[str, Any]:
        """
        Envia mensagem de erro/fallback.
        
        Args:
            to: Número de telefone
            
        Returns:
            Dict: Resultado do envio
        """
        try:
            message = """Desculpe, tivemos um problema técnico momentâneo! 😔

Mas não se preocupe, vou resolver rapidinho e retorno em breve! ⚡

Obrigada pela compreensão! 💚

Sílvia - Serena Energia 🌞"""
            
            return self.send_text_message(to, message)
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem de erro: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_bill_analysis_message(self, to: str, lead_name: str, invoice_amount: float, savings_percentage: float) -> Dict[str, Any]:
        """
        Envia mensagem com análise da conta de energia.
        
        Args:
            to: Número de telefone
            lead_name: Nome do lead
            invoice_amount: Valor da conta atual
            savings_percentage: Percentual de economia estimado
            
        Returns:
            Dict: Resultado do envio
        """
        try:
            estimated_savings = invoice_amount * (savings_percentage / 100)
            new_bill = invoice_amount - estimated_savings
            
            message = f"""📊 Análise da sua conta, {lead_name}:

💰 Conta atual: R$ {invoice_amount:.2f}
🌞 Com energia solar: R$ {new_bill:.2f}
💸 Economia mensal: R$ {estimated_savings:.2f}
📈 Economia anual: R$ {estimated_savings * 12:.2f}

Isso representa uma economia de {savings_percentage:.0f}% na sua conta! 🎉

Gostaria de conhecer os planos disponíveis para você?

Responda "SIM" que te mostro as opções! 💚"""
            
            return self.send_text_message(to, message)
            
        except Exception as e:
            logger.error(f"Erro ao enviar análise da conta: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            } 