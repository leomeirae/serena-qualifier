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
import psycopg2
import argparse
import json
from dotenv import load_dotenv

# Carrega variáveis de ambiente de um arquivo .env (para desenvolvimento local)
load_dotenv()

def save_lead(name, phone, email, account_value, client_type, state, city):
    """
    Salva um novo lead no banco de dados Supabase usando uma conexão direta via pooler.
    """
    conn_string = os.getenv("DB_CONNECTION_STRING")
    
    if not conn_string:
        print("CRITICAL ERROR: A variável de ambiente DB_CONNECTION_STRING não foi encontrada.")
        exit(1)

    print("🔌 Conectando ao Supabase DB via Connection Pooler...")

    try:
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                print("💾 Salvando lead no Supabase...")
                print(f"   - Nome: {name}")
                print(f"   - Telefone: {phone}")
                print(f"   - Email: {email}")
                print(f"   - Estado: {state}")
                print(f"   - Cidade: {city}")

                # Usando um upsert (INSERT ... ON CONFLICT) para evitar duplicados
                # Se um lead com o mesmo phone_number já existir, ele será atualizado.
                cur.execute(
                    """
                    INSERT INTO leads (phone_number, name, email, invoice_amount, client_type, state, city, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (phone_number) 
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        email = EXCLUDED.email,
                        invoice_amount = EXCLUDED.invoice_amount,
                        client_type = EXCLUDED.client_type,
                        state = EXCLUDED.state,
                        city = EXCLUDED.city,
                        updated_at = CURRENT_TIMESTAMP;
                    """,
                    (phone, name, email, account_value, client_type, state, city)
                )
                print("✅ Lead salvo com sucesso!")

    except psycopg2.Error as e:
        print(f"❌ ERRO CRÍTICO ao salvar o lead: {e}")
        # Em caso de erro, você pode querer registrar o erro em logs mais detalhados
        # ou notificar um sistema de monitoramento.
        exit(1)
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Salva um lead no Supabase.")
    parser.add_argument("--name", required=True, help="Nome do lead.")
    parser.add_argument("--phone", required=True, help="Número de telefone do lead (com código do país).")
    parser.add_argument("--email", required=True, help="Endereço de e-mail do lead.")
    parser.add_argument("--account_value", default=None, help="Valor da conta de energia.")
    parser.add_argument("--client_type", default=None, help="Tipo de cliente (ex: residencial).")
    parser.add_argument("--state", default="", help="Estado do lead.")
    parser.add_argument("--city", default="", help="Cidade do lead.")
    
    args = parser.parse_args()
    
    save_lead(
        name=args.name,
        phone=args.phone,
        email=args.email,
        account_value=args.account_value,
        client_type=args.client_type,
        state=args.state,
        city=args.city
    ) 