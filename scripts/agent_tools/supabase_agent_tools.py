import os
import psycopg2
import json
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
        return "Erro: A variável de ambiente DB_CONNECTION_STRING não foi encontrada."

    try:
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT name, city, state, invoice_amount, client_type FROM leads WHERE phone_number = %s",
                    (phone_number,)
                )
                result = cur.fetchone()
                
                if result:
                    lead_data = {
                        "name": result[0],
                        "city": result[1],
                        "state": result[2],
                        "invoice_amount": result[3],
                        "client_type": result[4]
                    }
                    return json.dumps(lead_data)
                else:
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
        return "Erro: A variável de ambiente DB_CONNECTION_STRING não foi encontrada."

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