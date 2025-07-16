import os
import psycopg2
import json
from dotenv import load_dotenv
from langchain_core.tools import tool

# Carrega variáveis de ambiente
load_dotenv()

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