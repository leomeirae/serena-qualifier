import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self):
        """Inicializar gerenciador de conversas com Supabase"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_ANON_KEY são obrigatórias")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.max_history_length = 20  # Controlar contexto para custos
        
    def add_message(self, phone_number: str, role: str, content: str, metadata: Dict = None) -> bool:
        """
        Adicionar mensagem ao histórico da conversa
        
        Args:
            phone_number: Número de telefone do usuário
            role: 'user' ou 'assistant'
            content: Conteúdo da mensagem
            metadata: Dados adicionais (intenção, dados extraídos, etc)
        """
        try:
            message_data = {
                'phone_number': phone_number,
                'role': role,
                'content': content,
                'metadata': metadata or {},
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('conversation_history').insert(message_data).execute()
            
            if result.data:
                logger.info(f"Mensagem salva para {phone_number}: {role}")
                return True
            else:
                logger.error(f"Falha ao salvar mensagem: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem: {str(e)}")
            return False

    def get_conversation_history(self, phone_number: str, limit: int = None) -> List[Dict]:
        """
        Recuperar histórico de conversa do usuário
        
        Args:
            phone_number: Número de telefone
            limit: Limite de mensagens (padrão: max_history_length)
        """
        try:
            limit = limit or self.max_history_length
            
            result = self.supabase.table('conversation_history')\
                .select('*')\
                .eq('phone_number', phone_number)\
                .order('created_at', desc=False)\
                .limit(limit)\
                .execute()
            
            if result.data:
                # Filtrar campos necessários para o prompt
                history = []
                for msg in result.data:
                    history.append({
                        'role': msg['role'],
                        'content': msg['content'],
                        'created_at': msg['created_at'],
                        'metadata': msg.get('metadata', {})
                    })
                
                logger.info(f"Recuperado histórico de {len(history)} mensagens para {phone_number}")
                return history
            else:
                logger.info(f"Nenhum histórico encontrado para {phone_number}")
                return []
                
        except Exception as e:
            logger.error(f"Erro ao recuperar histórico: {str(e)}")
            return []

    def get_lead_qualification_data(self, phone_number: str) -> Dict:
        """
        Extrair dados de qualificação do histórico
        Busca cidade, valor da conta, tipo de imóvel nos metadados
        """
        try:
            # Buscar mensagens com dados extraídos
            result = self.supabase.table('conversation_history')\
                .select('metadata')\
                .eq('phone_number', phone_number)\
                .not_.is_('metadata', 'null')\
                .execute()
            
            qualification_data = {
                'cidade': None,
                'valor_conta': None,
                'tipo_imovel': None,
                'status': 'incompleto'
            }
            
            if result.data:
                for msg in result.data:
                    metadata = msg.get('metadata', {})
                    
                    # Verificar se há dados extraídos
                    if 'extracted_data' in metadata:
                        extracted = metadata['extracted_data']
                        data_type = extracted.get('data_type')
                        value = extracted.get('extracted_value')
                        
                        if data_type and value and value != 'não_identificado':
                            qualification_data[data_type] = value
            
            # Verificar se qualificação está completa
            if all(qualification_data[key] for key in ['cidade', 'valor_conta', 'tipo_imovel']):
                qualification_data['status'] = 'completo'
            
            logger.info(f"Dados de qualificação para {phone_number}: {qualification_data}")
            return qualification_data
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados de qualificação: {str(e)}")
            return {'status': 'erro', 'error': str(e)}

    def update_lead_status(self, phone_number: str, status: str, additional_data: Dict = None) -> bool:
        """
        Atualizar status do lead (qualificado, solicitou_parada, etc)
        """
        try:
            lead_data = {
                'phone_number': phone_number,
                'status': status,
                'updated_at': datetime.utcnow().isoformat(),
                'additional_data': additional_data or {}
            }
            
            # Verificar se lead já existe
            existing = self.supabase.table('leads')\
                .select('id')\
                .eq('phone_number', phone_number)\
                .execute()
            
            if existing.data:
                # Atualizar lead existente
                result = self.supabase.table('leads')\
                    .update(lead_data)\
                    .eq('phone_number', phone_number)\
                    .execute()
            else:
                # Criar novo lead
                lead_data['created_at'] = datetime.utcnow().isoformat()
                result = self.supabase.table('leads')\
                    .insert(lead_data)\
                    .execute()
            
            if result.data:
                logger.info(f"Status do lead atualizado para {phone_number}: {status}")
                return True
            else:
                logger.error(f"Falha ao atualizar status: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao atualizar status do lead: {str(e)}")
            return False

    def clear_conversation_history(self, phone_number: str) -> bool:
        """
        Limpar histórico de conversa (usar com cuidado)
        """
        try:
            result = self.supabase.table('conversation_history')\
                .delete()\
                .eq('phone_number', phone_number)\
                .execute()
            
            if result.data is not None:  # DELETE pode retornar lista vazia
                logger.info(f"Histórico limpo para {phone_number}")
                return True
            else:
                logger.error(f"Falha ao limpar histórico: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao limpar histórico: {str(e)}")
            return False

    def get_conversation_summary(self, phone_number: str) -> Dict:
        """
        Gerar resumo da conversa para relatórios
        """
        try:
            history = self.get_conversation_history(phone_number, limit=100)
            qualification_data = self.get_lead_qualification_data(phone_number)
            
            if not history:
                return {'status': 'sem_historico'}
            
            # Calcular estatísticas
            total_messages = len(history)
            user_messages = len([msg for msg in history if msg['role'] == 'user'])
            ai_messages = len([msg for msg in history if msg['role'] == 'assistant'])
            
            first_message = history[0]['created_at'] if history else None
            last_message = history[-1]['created_at'] if history else None
            
            summary = {
                'phone_number': phone_number,
                'total_messages': total_messages,
                'user_messages': user_messages,
                'ai_messages': ai_messages,
                'first_message_at': first_message,
                'last_message_at': last_message,
                'qualification_data': qualification_data,
                'conversation_active': True if history else False
            }
            
            logger.info(f"Resumo gerado para {phone_number}")
            return summary
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {str(e)}")
            return {'status': 'erro', 'error': str(e)}

# Função utilitária para usar no Kestra
def manage_conversation(action: str, phone_number: str, **kwargs) -> Dict:
    """
    Função principal para gerenciar conversas no Kestra
    
    Actions disponíveis:
    - add_message: adicionar mensagem (requer role, content)
    - get_history: recuperar histórico
    - get_qualification: obter dados de qualificação
    - update_status: atualizar status do lead (requer status)
    - get_summary: obter resumo da conversa
    """
    try:
        manager = ConversationManager()
        
        if action == "add_message":
            role = kwargs.get('role')
            content = kwargs.get('content')
            metadata = kwargs.get('metadata')
            
            if not role or not content:
                raise ValueError("role e content são obrigatórios")
                
            success = manager.add_message(phone_number, role, content, metadata)
            return {'success': success}
        
        elif action == "get_history":
            limit = kwargs.get('limit')
            history = manager.get_conversation_history(phone_number, limit)
            return {'history': history, 'count': len(history)}
        
        elif action == "get_qualification":
            data = manager.get_lead_qualification_data(phone_number)
            return data
        
        elif action == "update_status":
            status = kwargs.get('status')
            additional_data = kwargs.get('additional_data')
            
            if not status:
                raise ValueError("status é obrigatório")
                
            success = manager.update_lead_status(phone_number, status, additional_data)
            return {'success': success}
        
        elif action == "get_summary":
            summary = manager.get_conversation_summary(phone_number)
            return summary
        
        else:
            raise ValueError(f"Ação '{action}' não reconhecida")
    
    except Exception as e:
        logger.error(f"Erro em manage_conversation: {str(e)}")
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    # Teste básico
    import sys
    if len(sys.argv) >= 3:
        action = sys.argv[1]
        phone = sys.argv[2]
        result = manage_conversation(action, phone)
        print(json.dumps(result, indent=2, ensure_ascii=False)) 