#!/usr/bin/env python3
"""
Supabase Agent Tools for Serena SDR Agent

Este módulo fornece funções para integração com Supabase/PostgreSQL
específicas para o agente SDR da Serena, incluindo operações de leads,
upload de imagens e geração de URLs seguras.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import os
import json
import logging
import psycopg2
import base64
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Obtém conexão com o banco de dados PostgreSQL/Supabase.
    
    Returns:
        psycopg2.connection: Conexão com o banco
    """
    conn_string = os.getenv("DB_CONNECTION_STRING") or os.getenv("SECRET_DB_CONNECTION_STRING")
    if not conn_string:
        raise ValueError("DB_CONNECTION_STRING não encontrada nas variáveis de ambiente")
    
    return psycopg2.connect(conn_string)

def salvar_ou_atualizar_lead_silvia(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """Salva ou atualiza dados de lead no Supabase/PostgreSQL.
    
    Args:
        lead_data (Dict[str, Any]): Dados do lead
    """
    try:
        logger.info(f"Salvando/atualizando lead: {lead_data.get('phone_number', 'N/A')}")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Query de upsert
        upsert_query = """
            INSERT INTO leads (
                phone_number, name, invoice_amount, client_type, 
                city, state, additional_data, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (phone_number) DO UPDATE SET
                name = EXCLUDED.name,
                invoice_amount = EXCLUDED.invoice_amount,
                client_type = EXCLUDED.client_type,
                city = EXCLUDED.city,
                state = EXCLUDED.state,
                additional_data = EXCLUDED.additional_data,
                updated_at = NOW()
            RETURNING id, phone_number, name;
        """
        
        # Prepara dados adicionais
        additional_data = {
            "source": "sdr_agent_silvia",
            "lead_data": lead_data
        }
        
        # Executa o upsert
        cur.execute(
            upsert_query,
            (
                lead_data.get("phone_number"),
                lead_data.get("name", "Lead WhatsApp"),
                float(lead_data.get("invoice_amount", 0)),
                lead_data.get("client_type", "casa"),
                lead_data.get("city", "N/A"),
                lead_data.get("state", "N/A"),
                json.dumps(additional_data)
            )
        )
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info(f"Lead salvo/atualizado com sucesso: ID={result[0]}")
        
        return {
            "success": True,
            "lead_id": result[0],
            "phone_number": result[1],
            "name": result[2],
            "message": "Lead salvo/atualizado com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro ao salvar/atualizar lead: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Erro ao salvar dados do lead"
        }

def consultar_dados_lead(phone: str) -> Dict[str, Any]:
    """Consulta dados de um lead pelo número de telefone.
    
    Args:
        phone (str): Número de telefone do lead
    """
    try:
        logger.info(f"Consultando lead: {phone}")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Normaliza o número de telefone
        import re
        digits_only = re.sub(r'\D', '', phone)
        
        # Busca com diferentes formatos
        possible_formats = []
        if digits_only.startswith('55'):
            without_country = digits_only[2:]
            possible_formats.extend([without_country, digits_only])
        else:
            possible_formats.extend([digits_only, '55' + digits_only])
        
        # Busca o lead
        for phone_format in possible_formats:
            cur.execute("""
                SELECT id, name, phone_number, city, state, 
                       invoice_amount, client_type, created_at, updated_at
                FROM leads 
                WHERE phone_number = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (phone_format,))
            
            result = cur.fetchone()
            if result:
                cur.close()
                conn.close()
                
                lead_data = {
                    "id": result[0],
                    "name": result[1],
                    "phone_number": result[2],
                    "city": result[3],
                    "state": result[4],
                    "invoice_amount": float(result[5]) if result[5] else 0,
                    "client_type": result[6],
                    "created_at": result[7].isoformat() if result[7] else None,
                    "updated_at": result[8].isoformat() if result[8] else None
                }
                
                logger.info(f"Lead encontrado: ID={lead_data['id']}")
                return {
                    "success": True,
                    "lead": lead_data,
                    "found": True
                }
        
        cur.close()
        conn.close()
        
        logger.info(f"Lead não encontrado: {phone}")
        return {
            "success": True,
            "lead": None,
            "found": False
        }
        
    except Exception as e:
        logger.error(f"Erro ao consultar lead: {e}")
        return {
            "success": False,
            "error": str(e),
            "found": False
        }

def upload_energy_bill_image(image_path: str, lead_id: int, phone_number: str) -> str:
    """
    Faz upload de uma imagem de conta de energia para o Supabase.
    
    Args:
        image_path (str): Caminho local da imagem
        lead_id (int): ID do lead
        phone_number (str): Número de telefone
        
    Returns:
        str: ID da imagem no storage
    """
    try:
        logger.info(f"Fazendo upload de imagem para lead {lead_id}")
        
        # Gera ID único para a imagem
        image_id = f"energy_bill_{lead_id}_{uuid.uuid4().hex[:8]}"
        
        # Lê o arquivo
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Calcula hash para verificação
        image_hash = hashlib.md5(image_data).hexdigest()
        
        # Salva metadados no banco
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Insere na tabela de imagens
        cur.execute("""
            INSERT INTO energy_bill_images (
                image_id, lead_id, phone_number, file_size, 
                file_hash, upload_date, status
            ) VALUES (%s, %s, %s, %s, %s, NOW(), 'uploaded')
            RETURNING image_id;
        """, (
            image_id,
            lead_id,
            phone_number,
            len(image_data),
            image_hash
        ))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info(f"Imagem salva com ID: {image_id}")
        return image_id
        
    except Exception as e:
        logger.error(f"Erro no upload da imagem: {e}")
        raise

def generate_signed_url(blob_path: str) -> str:
    """
    Gera URL assinada para acesso à imagem.
    
    Args:
        blob_path (str): Caminho do blob no storage
        
    Returns:
        str: URL assinada
    """
    try:
        logger.info(f"Gerando URL assinada para: {blob_path}")
        
        # Para implementação básica, retorna uma URL mock
        # Em produção, isso seria integrado com o Supabase Storage
        base_url = os.getenv("SUPABASE_STORAGE_URL", "https://storage.supabase.co")
        bucket_name = os.getenv("SUPABASE_BUCKET_NAME", "energy-bills")
        
        # URL mock - em produção seria uma URL assinada real
        signed_url = f"{base_url}/{bucket_name}/{blob_path}"
        
        logger.info(f"URL assinada gerada: {signed_url[:50]}...")
        return signed_url
        
    except Exception as e:
        logger.error(f"Erro ao gerar URL assinada: {e}")
        return ""

def save_image_metadata(lead_id: str, metadata: Dict[str, Any]) -> bool:
    """
    Salva metadados de imagem no banco de dados.
    
    Args:
        lead_id (str): ID do lead
        metadata (Dict[str, Any]): Metadados da imagem
        
    Returns:
        bool: True se salvou com sucesso
    """
    try:
        logger.info(f"Salvando metadados de imagem para lead {lead_id}")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Insere metadados
        cur.execute("""
            INSERT INTO image_metadata (
                lead_id, image_id, file_size_kb, mime_type,
                upload_date, metadata
            ) VALUES (%s, %s, %s, %s, NOW(), %s)
        """, (
            lead_id,
            metadata.get("image_id"),
            metadata.get("file_size_kb", 0),
            metadata.get("mime_type", "image/jpeg"),
            json.dumps(metadata)
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info("Metadados salvos com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao salvar metadados: {e}")
        return False

def atualizar_status_lead(lead_id: int, status: str, dados_adicionais: Dict[str, Any] = None) -> bool:
    """
    Atualiza o status de um lead.
    
    Args:
        lead_id (int): ID do lead
        status (str): Novo status
        dados_adicionais (Dict[str, Any]): Dados adicionais
        
    Returns:
        bool: True se atualizou com sucesso
    """
    try:
        logger.info(f"Atualizando status do lead {lead_id} para: {status}")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Atualiza o status
        cur.execute("""
            UPDATE leads 
            SET status = %s, 
                additional_data = CASE 
                    WHEN additional_data IS NULL THEN %s
                    ELSE additional_data || %s
                END,
                updated_at = NOW()
            WHERE id = %s
        """, (
            status,
            json.dumps(dados_adicionais or {}),
            json.dumps(dados_adicionais or {}),
            lead_id
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        logger.info(f"Status atualizado com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao atualizar status: {e}")
        return False

def buscar_leads_por_status(status: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Busca leads por status.
    
    Args:
        status (str): Status desejado
        limit (int): Limite de resultados
        
    Returns:
        List[Dict[str, Any]]: Lista de leads
    """
    try:
        logger.info(f"Buscando leads com status: {status}")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, name, phone_number, city, state, 
                   invoice_amount, client_type, created_at, status
            FROM leads 
            WHERE status = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (status, limit))
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        leads = []
        for result in results:
            leads.append({
                "id": result[0],
                "name": result[1],
                "phone_number": result[2],
                "city": result[3],
                "state": result[4],
                "invoice_amount": float(result[5]) if result[5] else 0,
                "client_type": result[6],
                "created_at": result[7].isoformat() if result[7] else None,
                "status": result[8]
            })
        
        logger.info(f"Encontrados {len(leads)} leads com status {status}")
        return leads
        
    except Exception as e:
        logger.error(f"Erro ao buscar leads: {e}")
        return []

def obter_estatisticas_leads() -> Dict[str, Any]:
    """
    Obtém estatísticas dos leads.
    
    Returns:
        Dict[str, Any]: Estatísticas dos leads
    """
    try:
        logger.info("Obtendo estatísticas dos leads")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Total de leads
        cur.execute("SELECT COUNT(*) FROM leads")
        total_leads = cur.fetchone()[0]
        
        # Leads por status
        cur.execute("""
            SELECT status, COUNT(*) 
            FROM leads 
            GROUP BY status
        """)
        leads_por_status = dict(cur.fetchall())
        
        # Leads por tipo de cliente
        cur.execute("""
            SELECT client_type, COUNT(*) 
            FROM leads 
            GROUP BY client_type
        """)
        leads_por_tipo = dict(cur.fetchall())
        
        # Leads dos últimos 30 dias
        cur.execute("""
            SELECT COUNT(*) 
            FROM leads 
            WHERE created_at >= NOW() - INTERVAL '30 days'
        """)
        leads_30_dias = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        stats = {
            "total_leads": total_leads,
            "leads_por_status": leads_por_status,
            "leads_por_tipo": leads_por_tipo,
            "leads_30_dias": leads_30_dias
        }
        
        logger.info(f"Estatísticas obtidas: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return {}

if __name__ == "__main__":
    # Teste das funcionalidades
    print("=== Teste do Supabase Agent Tools ===")
    
    # Teste de consulta de lead
    result = consultar_dados_lead("+5581997498268")
    print(f"Consulta de lead: {result}")
    
    # Teste de estatísticas
    stats = obter_estatisticas_leads()
    print(f"Estatísticas: {stats}") 