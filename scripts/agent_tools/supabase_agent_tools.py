import os
import psycopg2
import json
import re
from dotenv import load_dotenv
from langchain_core.tools import tool

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
    conn_string = os.getenv("DB_CONNECTION_STRING")
    
    if not conn_string:
        # Tenta com o prefixo SECRET_ se a variável normal não existir
        conn_string = os.getenv("SECRET_DB_CONNECTION_STRING")
        if not conn_string:
            return "Erro: A variável de ambiente DB_CONNECTION_STRING ou SECRET_DB_CONNECTION_STRING não foi encontrada."

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

        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                additional_data_payload = {"email": email, "source": "silvia_agent"}
                additional_data_json = json.dumps(additional_data_payload)

                cur.execute(
                    """
                    INSERT INTO leads (phone_number, name, invoice_amount, client_type, state, city, additional_data, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (phone_number) 
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        invoice_amount = EXCLUDED.invoice_amount,
                        client_type = EXCLUDED.client_type,
                        state = EXCLUDED.state,
                        city = EXCLUDED.city,
                        additional_data = leads.additional_data || %s::jsonb,
                        updated_at = CURRENT_TIMESTAMP;
                    """,
                    (phone, name, account_value, client_type, state, city, additional_data_json, additional_data_json)
                )
        return "Dados do lead salvos com sucesso no sistema."

    except json.JSONDecodeError:
        return "Erro: A entrada para a ferramenta não é um JSON válido."
    except psycopg2.Error as e:
        return f"Erro ao interagir com o banco de dados: {e}"
    except Exception as e:
        return f"Ocorreu um erro inesperado: {e}" 