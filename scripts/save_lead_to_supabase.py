#!/usr/bin/env python3
"""
Script para salvar dados de lead no Supabase
MAPEAMENTO DEFINITIVO DOS CAMPOS:
- nomeCompleto → name
- whatsapp → phone_number  
- email → additional_data.email (NÃO existe coluna email na tabela)
- faixaConta → additional_data.faixaConta
- tipoCliente → additional_data.tipoCliente
- city → NULL (será perguntado depois)
"""

import os
import sys
import json
import argparse
from datetime import datetime
from supabase import create_client, Client

# Tentar carregar .env como fallback se as variáveis não estiverem disponíveis
try:
    from dotenv import load_dotenv
    # Carregar .env do diretório raiz do projeto
    load_dotenv('/app/.env')
except ImportError:
    # Se python-dotenv não estiver disponível, continuar sem ele
    pass


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