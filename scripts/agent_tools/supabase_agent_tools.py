import os
import psycopg2
import json
import re
from dotenv import load_dotenv
from langchain_core.tools import tool
from scripts.lead_data_utils import get_lead_additional_data, update_lead_additional_data
from supabase import create_client

# Carrega variáveis de ambiente
load_dotenv()

@tool
def consultar_dados_lead(phone_number: str) -> str:
    """
    Consulta os dados de um lead existente no banco de dados usando o número de telefone.
    Use esta ferramenta no início de cada conversa para carregar o contexto do lead, 
    como nome e cidade, antes de interagir com ele.
    """
    conn_string = os.getenv("DB_CONNECTION_STRING")
    if not conn_string:
        # Tenta com o prefixo SECRET_ se a variável normal não existir
        conn_string = os.getenv("SECRET_DB_CONNECTION_STRING")
        if not conn_string:
            return "Erro: A variável de ambiente DB_CONNECTION_STRING ou SECRET_DB_CONNECTION_STRING não foi encontrada."

    try:
        # Normaliza o número de telefone para busca
        digits_only = re.sub(r'\D', '', phone_number)
        
        # Cria uma lista de possíveis formatos de telefone para busca
        possible_formats = []
        
        # Se começar com código do país (55)
        if digits_only.startswith('55'):
            without_country = digits_only[2:]  # Remove o 55
            possible_formats.append(without_country)  # Formato sem o 55
            
            # Se tiver o 9 após o DDD (formato novo)
            if len(without_country) >= 9 and without_country[2] == '9':
                possible_formats.append(without_country[:2] + without_country[3:])  # Remove o 9
            
            # Se não tiver o 9 (formato antigo)
            if len(without_country) == 8:
                possible_formats.append(without_country[:2] + '9' + without_country[2:])  # Adiciona o 9
        else:
            possible_formats.append(digits_only)
        
        # Adicione outros formatos possíveis para cobrir mais casos
        if len(digits_only) == 11:  # formato 5581987654321 ou 81987654321
            possible_formats.append(digits_only[-10:])  # Apenas DDD + número sem o 9
            possible_formats.append(digits_only[-8:])   # Apenas o número base sem DDD e sem 9
        
        # Adiciona o formato exato e remove duplicatas
        possible_formats.append(digits_only)
        possible_formats = list(set(possible_formats))
        
        print(f"DEBUG: Tentando formatos de telefone: {possible_formats}")
        
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                for format_to_try in possible_formats:
                    cur.execute(
                        "SELECT name, city, state, invoice_amount, client_type FROM leads WHERE phone_number = %s",
                        (format_to_try,)
                    )
                    result = cur.fetchone()
                    if result:
                        lead_data = {
                            "name": result[0],
                            "city": result[1],
                            "state": result[2],
                            "invoice_amount": float(result[3]) if result[3] is not None else 0.0,
                            "client_type": result[4],
                            "phone_format": format_to_try  # Para debug
                        }
                        return json.dumps(lead_data)
                
                # Tenta uma última busca com LIKE para os últimos 8 dígitos
                if len(digits_only) >= 8:
                    last_8_digits = digits_only[-8:]
                    print(f"DEBUG: Tentando busca por LIKE com últimos 8 dígitos: {last_8_digits}")
                    cur.execute(
                        "SELECT name, city, state, invoice_amount, client_type, phone_number FROM leads WHERE phone_number LIKE %s",
                        (f"%{last_8_digits}",)
                    )
                    result = cur.fetchone()
                    if result:
                        lead_data = {
                            "name": result[0],
                            "city": result[1],
                            "state": result[2],
                            "invoice_amount": float(result[3]) if result[3] is not None else 0.0,
                            "client_type": result[4],
                            "phone_number": result[5]  # O número encontrado no banco
                        }
                        return json.dumps(lead_data)
                
                return "Nenhum dado encontrado para este número de telefone."

    except psycopg2.Error as e:
        return f"Erro ao consultar o banco de dados: {e}"
    except Exception as e:
        return f"Ocorreu um erro inesperado: {e}"

@tool
def salvar_ou_atualizar_lead_silvia(dados_lead: str) -> str:
    """
    Salva ou atualiza os dados de um lead no banco de dados. 
    A entrada deve ser um dicionário em formato de string JSON contendo as chaves: 
    'name', 'phone', 'email', 'city', 'state', e um dicionário aninhado 
    'energy_bill_data' com 'valor_total' e 'client_type'.
    Use esta ferramenta após confirmar os dados com o usuário.
    """
    try:
        dados_dict = json.loads(dados_lead)
        energy_data = dados_dict.get('energy_bill_data', {})

        phone = dados_dict.get('phone')
        name = dados_dict.get('name')
        email = dados_dict.get('email', '')
        account_value = energy_data.get('valor_total')
        client_type = energy_data.get('client_type', 'Residencial')
        city = dados_dict.get('city')
        state = dados_dict.get('state')

        # Atualiza os campos principais do lead
        conn_string = os.getenv("DB_CONNECTION_STRING") or os.getenv("SECRET_DB_CONNECTION_STRING")
        if not conn_string:
            return "Erro: A variável de ambiente DB_CONNECTION_STRING ou SECRET_DB_CONNECTION_STRING não foi encontrada."
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO leads (phone_number, name, invoice_amount, client_type, state, city, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (phone_number) 
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        invoice_amount = EXCLUDED.invoice_amount,
                        client_type = EXCLUDED.client_type,
                        state = EXCLUDED.state,
                        city = EXCLUDED.city,
                        updated_at = CURRENT_TIMESTAMP;
                    """,
                    (phone, name, account_value, client_type, state, city)
                )
        # Atualiza o campo additional_data usando a função utilitária
        additional_data_payload = {"email": email, "source": "silvia_agent"}
        update_success = update_lead_additional_data(phone, additional_data_payload)
        if update_success:
            return "Dados do lead salvos com sucesso no sistema."
        else:
            return "Erro ao atualizar o campo additional_data do lead."
    except json.JSONDecodeError:
        return "Erro: A entrada para a ferramenta não é um JSON válido."
    except psycopg2.Error as e:
        return f"Erro ao interagir com o banco de dados: {e}"
    except Exception as e:
        return f"Ocorreu um erro inesperado: {e}" 

# Função incremental para upload de imagem ao Supabase Storage (bucket privado)
def upload_energy_bill_image(local_file_path: str, lead_id: int, phone: str) -> str:
    """
    Faz upload de uma imagem para o bucket privado 'energy-bills' no Supabase Storage.
    Retorna o caminho (storage_path) salvo no banco.
    """
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise Exception("SUPABASE_URL ou SUPABASE_KEY não configurados nas variáveis de ambiente.")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    bucket_name = "energy-bills"
    storage_path = f"{lead_id}_{phone}.jpg"
    with open(local_file_path, "rb") as f:
        supabase.storage.from_(bucket_name).upload(storage_path, f)
    return storage_path

# Função incremental para gerar signed URL para imagem privada
def generate_signed_url(storage_path: str, expires_in: int = 3600) -> str:
    """
    Gera uma URL temporária (signed URL) para acessar uma imagem privada no Supabase Storage.
    expires_in: tempo de validade em segundos (padrão: 1 hora)
    """
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise Exception("SUPABASE_URL ou SUPABASE_KEY não configurados nas variáveis de ambiente.")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    bucket_name = "energy-bills"
    signed_url = supabase.storage.from_(bucket_name).create_signed_url(storage_path, expires_in)
    return signed_url['signedURL'] if isinstance(signed_url, dict) and 'signedURL' in signed_url else signed_url 