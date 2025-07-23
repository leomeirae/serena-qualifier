import os
import psycopg2
import json
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

def get_lead_additional_data(phone_number: str) -> Optional[Dict]:
    """
    Busca o campo additional_data da tabela leads para um phone_number específico.
    Retorna um dicionário Python ou None se não encontrado.
    """
    conn_string = os.getenv("DB_CONNECTION_STRING") or os.getenv("SECRET_DB_CONNECTION_STRING")
    if not conn_string:
        raise RuntimeError("DB_CONNECTION_STRING não configurada.")
    try:
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT additional_data FROM leads WHERE phone_number = %s",
                    (phone_number,)
                )
                result = cur.fetchone()
                if result and result[0]:
                    return json.loads(result[0])
                return {}
    except Exception as e:
        print(f"Erro ao buscar additional_data: {e}")
        return None

def update_lead_additional_data(phone_number: str, new_data: dict) -> bool:
    """
    Faz merge do dicionário new_data com o additional_data existente do lead e salva no banco.
    Retorna True em caso de sucesso.
    """
    conn_string = os.getenv("DB_CONNECTION_STRING") or os.getenv("SECRET_DB_CONNECTION_STRING")
    if not conn_string:
        raise RuntimeError("DB_CONNECTION_STRING não configurada.")
    try:
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                # Buscar o additional_data atual
                cur.execute(
                    "SELECT additional_data FROM leads WHERE phone_number = %s",
                    (phone_number,)
                )
                result = cur.fetchone()
                current_data = json.loads(result[0]) if result and result[0] else {}
                # Merge
                merged_data = {**current_data, **new_data}
                merged_json = json.dumps(merged_data)
                # Atualizar no banco
                cur.execute(
                    "UPDATE leads SET additional_data = %s, updated_at = CURRENT_TIMESTAMP WHERE phone_number = %s",
                    (merged_json, phone_number)
                )
                conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao atualizar additional_data: {e}")
        return False 