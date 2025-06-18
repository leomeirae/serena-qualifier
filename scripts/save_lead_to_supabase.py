#!/usr/bin/env python3
"""
Script para salvar dados de lead no Supabase

Este script contém duas funções principais:
1. main() - Para salvar dados iniciais do formulário (usado pelos workflows Kestra)
2. save_qualified_lead() - Para salvar dados consolidados após qualificação completa

MAPEAMENTO DEFINITIVO DOS CAMPOS:
- nomeCompleto → name
- whatsapp → phone_number  
- email → additional_data.email (NÃO existe coluna email na tabela)
- faixaConta → additional_data.faixaConta
- tipoCliente → additional_data.tipoCliente
- city → city (preenchido durante conversa)
- invoice_amount → invoice_amount (extraído do OCR)

Author: Serena-Coder AI Agent
Version: 2.0.0 - Task-2006: Adicionada função save_qualified_lead()
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, Any, Optional
from supabase import create_client, Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Tentar carregar .env como fallback se as variáveis não estiverem disponíveis
try:
    from dotenv import load_dotenv
    # Carregar .env do diretório raiz do projeto
    load_dotenv('/app/.env')
except ImportError:
    # Se python-dotenv não estiver disponível, continuar sem ele
    pass


def get_supabase_client() -> Client:
    """
    Cria e retorna cliente Supabase configurado.
    
    Returns:
        Client: Cliente Supabase configurado
        
    Raises:
        ValueError: Se credenciais não estiverem disponíveis
    """
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar configuradas nas variáveis de ambiente")
    
    return create_client(supabase_url, supabase_key)


def save_qualified_lead(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Salva dados consolidados de um lead após processo completo de qualificação.
    
    Esta função é chamada ao final do fluxo de conversação quando todos os dados
    foram coletados: localização, dados da conta de energia, promoções consultadas.
    
    Args:
        lead_data (Dict[str, Any]): Dicionário com dados consolidados do lead:
            - phone_number (str): Número do lead (obrigatório)
            - name (str): Nome extraído da conta ou fornecido
            - city (str): Cidade detectada na conversa
            - state (str): Estado detectado na conversa
            - extracted_data (Dict): Dados extraídos da conta de energia
            - promotions (List): Promoções encontradas para a localização
            - conversation_completed (bool): Se a conversa foi finalizada
            
    Returns:
        Dict[str, Any]: Resultado da operação:
            - success (bool): Se a operação foi bem-sucedida
            - lead_id (str): ID do lead atualizado (se sucesso)
            - error (str): Mensagem de erro (se falha)
            
    Raises:
        Exception: Para erros críticos de conexão ou dados inválidos
    """
    try:
        logger.info(f"💾 Salvando lead qualificado: {lead_data.get('phone_number')}")
        
        # Validar dados obrigatórios
        if not lead_data.get('phone_number'):
            raise ValueError("phone_number é obrigatório")
        
        # Extrair dados da conta de energia
        extracted_data = lead_data.get('extracted_data', {})
        if isinstance(extracted_data, dict) and 'data' in extracted_data:
            bill_data = extracted_data['data']
        else:
            bill_data = {}
        
        # Preparar dados para atualização
        update_data = {
            'city': lead_data.get('city'),
            'state': lead_data.get('state'),
            'qualification_status': 'QUALIFIED' if lead_data.get('conversation_completed') else 'IN_PROGRESS',
            'conversation_state': 'COMPLETED' if lead_data.get('conversation_completed') else 'BILL_PROCESSED',
            'updated_at': datetime.now().isoformat()
        }
        
        # Adicionar valor da conta se extraído
        if bill_data.get('valor_total'):
            # Extrair valor numérico do formato "R$ 245,67"
            import re
            valor_match = re.search(r'[\d,]+', str(bill_data['valor_total']))
            if valor_match:
                valor_str = valor_match.group().replace(',', '.')
                try:
                    update_data['invoice_amount'] = float(valor_str)
                except ValueError:
                    logger.warning(f"⚠️ Não foi possível converter valor: {bill_data['valor_total']}")
        
        # Atualizar nome se extraído da conta
        if bill_data.get('cliente_nome') and bill_data['cliente_nome'] != 'NÃO_IDENTIFICADO':
            update_data['name'] = bill_data['cliente_nome']
        
        # Consolidar dados adicionais
        current_additional_data = lead_data.get('additional_data', {})
        
        # Dados da conta de energia
        if bill_data:
            current_additional_data['conta_energia'] = {
                'cliente_nome': bill_data.get('cliente_nome'),
                'valor_total': bill_data.get('valor_total'),
                'consumo_kwh': bill_data.get('consumo_kwh'),
                'distribuidora': bill_data.get('distribuidora'),
                'vencimento': bill_data.get('vencimento'),
                'endereco': bill_data.get('endereco'),
                'numero_instalacao': bill_data.get('numero_instalacao'),
                'data_processamento': datetime.now().isoformat()
            }
        
        # Dados das promoções
        promotions = lead_data.get('promotions', [])
        if promotions:
            current_additional_data['promocoes'] = {
                'total_encontradas': len(promotions),
                'lista_promocoes': promotions,
                'data_consulta': datetime.now().isoformat()
            }
        
        # Dados da conversa
        current_additional_data['conversa'] = {
            'finalizada': lead_data.get('conversation_completed', False),
            'data_finalizacao': datetime.now().isoformat() if lead_data.get('conversation_completed') else None,
            'modelo_usado': lead_data.get('model_used', 'gpt-4o-mini'),
            'processamento_imagem': lead_data.get('media_processed', False)
        }
        
        update_data['additional_data'] = current_additional_data
        
        # Conectar ao Supabase e atualizar lead
        supabase = get_supabase_client()
        
        logger.info(f"🔄 Atualizando lead no Supabase: {lead_data['phone_number']}")
        
        result = supabase.table('leads').update(update_data).eq(
            'phone_number', lead_data['phone_number']
        ).execute()
        
        if result.data and len(result.data) > 0:
            lead_record = result.data[0]
            logger.info(f"✅ Lead qualificado salvo com sucesso! ID: {lead_record['id']}")
            
            return {
                'success': True,
                'lead_id': lead_record['id'],
                'phone_number': lead_record['phone_number'],
                'qualification_status': lead_record['qualification_status'],
                'conversation_state': lead_record['conversation_state'],
                'updated_fields': list(update_data.keys())
            }
        else:
            logger.error(f"❌ Nenhum lead encontrado para atualizar: {lead_data['phone_number']}")
            return {
                'success': False,
                'error': f"Lead não encontrado: {lead_data['phone_number']}"
            }
            
    except Exception as e:
        logger.error(f"❌ Erro ao salvar lead qualificado: {str(e)}")
        return {
            'success': False,
            'error': f"Erro ao salvar lead: {str(e)}"
        }


def main():
    """Função principal para salvar lead no Supabase"""
    
    # Parser para os campos REAIS do formulário da landing page
    parser = argparse.ArgumentParser(description='Salva dados de lead no Supabase')
    parser.add_argument('--name', required=True, help='nomeCompleto do formulário')
    parser.add_argument('--phone', required=True, help='whatsapp do formulário')
    parser.add_argument('--email', required=False, help='email do formulário')
    parser.add_argument('--account_value', required=False, help='faixaConta do formulário')
    parser.add_argument('--client_type', required=False, help='tipoCliente do formulário')
    
    args = parser.parse_args()
    
    # Credenciais Supabase
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ ERRO: Variáveis SUPABASE_URL e SUPABASE_KEY não encontradas")
        sys.exit(1)
    
    print("💾 SALVANDO LEAD NO SUPABASE:")
    print(f"📝 Nome: {args.name}")
    print(f"📱 WhatsApp: {args.phone}")
    print(f"📧 Email: {args.email}")
    print(f"💰 Faixa Conta: {args.account_value}")
    print(f"🏠 Tipo Cliente: {args.client_type}")
    
    try:
        # Conectar ao Supabase
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # ESTRUTURA DEFINITIVA DA TABELA LEADS:
        lead_data = {
            # CAMPOS DIRETOS DA TABELA
            'phone_number': args.phone,           # Campo obrigatório único
            'name': args.name,                    # nomeCompleto → name
            'city': None,                         # Será perguntado DEPOIS na conversa
            'invoice_amount': None,               # Será processado pelo OCR
            'conversation_state': 'FORM_SUBMITTED',
            
            # DADOS DO FORMULÁRIO NO CAMPO JSON
            'additional_data': {
                'email': args.email,              # email NÃO tem coluna própria
                'faixaConta': args.account_value, # valor bruto do formulário
                'tipoCliente': args.client_type,  # casa/empresa
                'source': 'landing_page',
                'form_timestamp': datetime.now().isoformat(),
                'status_formulario': 'completo'
            }
        }
        
        print("🔄 Inserindo dados na tabela 'leads'...")
        
        # Inserir no Supabase
        result = supabase.table('leads').insert(lead_data).execute()
        
        if result.data and len(result.data) > 0:
            lead_record = result.data[0]
            print(f"✅ SUCESSO! Lead salvo com ID: {lead_record['id']}")
            print(f"📞 Phone Number: {lead_record['phone_number']}")
            print(f"👤 Name: {lead_record['name']}")
            print(f"🏢 Status: {lead_record['qualification_status']}")
            
            # Outputs para o próximo task do Kestra
            print(f"::set-output name=lead_id::{lead_record['id']}")
            print(f"::set-output name=phone_number::{lead_record['phone_number']}")
            print(f"::set-output name=lead_name::{lead_record['name']}")
            
        else:
            print("❌ ERRO: Nenhum dado retornado após inserção")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO ao salvar lead: {e}")
        print(f"🔍 Detalhes do erro: {type(e).__name__}")
        sys.exit(1)


if __name__ == "__main__":
    main() 