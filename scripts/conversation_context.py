#!/usr/bin/env python3
"""
Conversation Context Module

Este módulo contém a lógica para gerenciar o estado e contexto das conversas
com os leads, incluindo armazenamento de localização, promoções e histórico.

Author: Serena-Coder AI Agent
Version: 1.0.0 - Refatoração para modularização
Created: 2025-01-17
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class ConversationContext:
    """
    Classe responsável pelo gerenciamento do contexto das conversas
    com os leads durante o processo de qualificação.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de contexto."""
        # Dicionário para armazenar contexto de cada conversa
        # Chave: phone_number, Valor: dados da conversa
        self.conversations: Dict[str, Dict[str, Any]] = {}
        
        # Estatísticas de uso
        self.stats = {
            'total_conversations': 0,
            'active_conversations': 0,
            'completed_conversations': 0
        }
    
    def save_context(
        self, 
        phone_number: str, 
        city: Optional[str] = None, 
        state: Optional[str] = None, 
        promotions: Optional[List[Dict[str, Any]]] = None,
        extracted_data: Optional[Dict[str, Any]] = None,
        conversation_completed: Optional[bool] = None
    ) -> None:
        """
        Salva contexto da conversa em memória.
        
        Args:
            phone_number (str): Número do lead
            city (Optional[str]): Cidade detectada
            state (Optional[str]): Estado detectado
            promotions (Optional[List[Dict[str, Any]]]): Promoções encontradas
            extracted_data (Optional[Dict[str, Any]]): Dados extraídos da conta
            conversation_completed (Optional[bool]): Se a conversa foi finalizada
        """
        try:
            # Inicializar contexto se não existir
            if phone_number not in self.conversations:
                self.conversations[phone_number] = {
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'interactions_count': 0,
                    'status': 'active'
                }
                self.stats['total_conversations'] += 1
                self.stats['active_conversations'] += 1
            
            context = self.conversations[phone_number]
            
            # Atualizar dados do contexto
            if city:
                context['city'] = city
            if state:
                context['state'] = state
            if promotions is not None:
                context['promotions'] = promotions
                context['promotions_count'] = len(promotions)
            if extracted_data is not None:
                context['extracted_data'] = extracted_data
            if conversation_completed is not None:
                context['conversation_completed'] = conversation_completed
                if conversation_completed:
                    context['status'] = 'completed'
                    context['completed_at'] = datetime.now().isoformat()
                    self.stats['active_conversations'] -= 1
                    self.stats['completed_conversations'] += 1
            
            # Atualizar metadados
            context['last_updated'] = datetime.now().isoformat()
            context['interactions_count'] = context.get('interactions_count', 0) + 1
            
            logger.info(f"💾 Contexto salvo para {phone_number}: {self._get_context_summary(context)}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar contexto: {str(e)}")
    
    def get_context(self, phone_number: str) -> Dict[str, Any]:
        """
        Recupera contexto da conversa.
        
        Args:
            phone_number (str): Número do lead
            
        Returns:
            Dict[str, Any]: Contexto da conversa
        """
        try:
            context = self.conversations.get(phone_number, {})
            if context:
                logger.info(f"📖 Contexto recuperado para {phone_number}: {self._get_context_summary(context)}")
            else:
                logger.info(f"📖 Nenhum contexto encontrado para {phone_number}")
            return context
        except Exception as e:
            logger.error(f"❌ Erro ao recuperar contexto: {str(e)}")
            return {}
    
    def has_location(self, phone_number: str) -> bool:
        """
        Verifica se o lead já informou sua localização.
        
        Args:
            phone_number (str): Número do lead
            
        Returns:
            bool: True se localização foi informada
        """
        context = self.get_context(phone_number)
        return 'city' in context and 'state' in context
    
    def has_promotions(self, phone_number: str) -> bool:
        """
        Verifica se já foram consultadas promoções para o lead.
        
        Args:
            phone_number (str): Número do lead
            
        Returns:
            bool: True se promoções foram consultadas
        """
        context = self.get_context(phone_number)
        return 'promotions' in context
    
    def is_conversation_completed(self, phone_number: str) -> bool:
        """
        Verifica se a conversa foi finalizada.
        
        Args:
            phone_number (str): Número do lead
            
        Returns:
            bool: True se conversa foi finalizada
        """
        context = self.get_context(phone_number)
        return context.get('conversation_completed', False)
    
    def get_location(self, phone_number: str) -> Optional[tuple]:
        """
        Obtém localização do lead.
        
        Args:
            phone_number (str): Número do lead
            
        Returns:
            Optional[tuple]: (cidade, estado) ou None
        """
        context = self.get_context(phone_number)
        if 'city' in context and 'state' in context:
            return (context['city'], context['state'])
        return None
    
    def get_promotions(self, phone_number: str) -> List[Dict[str, Any]]:
        """
        Obtém promoções do lead.
        
        Args:
            phone_number (str): Número do lead
            
        Returns:
            List[Dict[str, Any]]: Lista de promoções
        """
        context = self.get_context(phone_number)
        return context.get('promotions', [])
    
    def get_extracted_data(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        Obtém dados extraídos da conta de energia.
        
        Args:
            phone_number (str): Número do lead
            
        Returns:
            Optional[Dict[str, Any]]: Dados extraídos ou None
        """
        context = self.get_context(phone_number)
        return context.get('extracted_data')
    
    def clear_context(self, phone_number: str) -> bool:
        """
        Remove contexto de uma conversa.
        
        Args:
            phone_number (str): Número do lead
            
        Returns:
            bool: True se removido com sucesso
        """
        try:
            if phone_number in self.conversations:
                context = self.conversations[phone_number]
                if context.get('status') == 'active':
                    self.stats['active_conversations'] -= 1
                del self.conversations[phone_number]
                logger.info(f"🗑️ Contexto removido para {phone_number}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao remover contexto: {str(e)}")
            return False
    
    def get_conversation_stage(self, phone_number: str) -> str:
        """
        Determina o estágio atual da conversa.
        
        Args:
            phone_number (str): Número do lead
            
        Returns:
            str: Estágio da conversa
        """
        context = self.get_context(phone_number)
        
        if not context:
            return 'initial'
        
        if context.get('conversation_completed'):
            return 'completed'
        
        if context.get('extracted_data'):
            return 'image_processed'
        
        if context.get('promotions') is not None:
            return 'promotions_shown'
        
        if context.get('city') and context.get('state'):
            return 'location_detected'
        
        return 'in_progress'
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de uso do sistema.
        
        Returns:
            Dict[str, Any]: Estatísticas do sistema
        """
        return {
            **self.stats,
            'current_conversations': len(self.conversations),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_all_conversations(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtém todas as conversas (para debug/monitoramento).
        
        Returns:
            Dict[str, Dict[str, Any]]: Todas as conversas
        """
        return self.conversations
    
    def _get_context_summary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria resumo do contexto para logs.
        
        Args:
            context (Dict[str, Any]): Contexto completo
            
        Returns:
            Dict[str, Any]: Resumo do contexto
        """
        summary = {
            'status': context.get('status', 'unknown'),
            'interactions': context.get('interactions_count', 0),
            'stage': 'initial'
        }
        
        if context.get('city') and context.get('state'):
            summary['location'] = f"{context['city']}/{context['state']}"
            summary['stage'] = 'location_detected'
        
        if context.get('promotions') is not None:
            summary['promotions_count'] = len(context.get('promotions', []))
            summary['stage'] = 'promotions_shown'
        
        if context.get('extracted_data'):
            summary['image_processed'] = True
            summary['stage'] = 'image_processed'
        
        if context.get('conversation_completed'):
            summary['stage'] = 'completed'
        
        return summary


# =============================================================================
# FUNÇÕES HELPER PARA USO EXTERNO
# =============================================================================

# Instância global para uso em workflows
_global_context = ConversationContext()

def save_conversation_context(phone_number: str, context_data: Dict[str, Any]) -> bool:
    """
    Função helper para salvar contexto de conversa.
    
    Args:
        phone_number (str): Número do telefone do lead
        context_data (Dict[str, Any]): Dados do contexto a serem salvos
        
    Returns:
        bool: True se salvou com sucesso, False caso contrário
    """
    try:
        # Usar a instância global para salvar o contexto
        _global_context.save_context(
            phone_number=phone_number,
            city=context_data.get('city'),
            state=context_data.get('state'),
            promotions=context_data.get('promotions'),
            extracted_data=context_data.get('extracted_data'),
            conversation_completed=context_data.get('conversation_completed')
        )
        logger.info(f"💾 Contexto salvo para {phone_number}: {context_data}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao salvar contexto para {phone_number}: {str(e)}")
        return False

def get_conversation_context(phone_number: str) -> Dict[str, Any]:
    """
    Função helper para recuperar contexto de conversa.
    
    Args:
        phone_number (str): Número do telefone do lead
        
    Returns:
        Dict[str, Any]: Contexto da conversa
    """
    try:
        return _global_context.get_context(phone_number)
    except Exception as e:
        logger.error(f"❌ Erro ao recuperar contexto para {phone_number}: {str(e)}")
        return {}

def clear_conversation_context(phone_number: str) -> bool:
    """
    Função helper para limpar contexto de conversa.
    
    Args:
        phone_number (str): Número do telefone do lead
        
    Returns:
        bool: True se limpou com sucesso, False caso contrário
    """
    try:
        return _global_context.clear_context(phone_number)
    except Exception as e:
        logger.error(f"❌ Erro ao limpar contexto para {phone_number}: {str(e)}")
        return False
