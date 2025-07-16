from langchain_core.tools import tool
import json
import os
import base64
from openai import OpenAI
from scripts.serena_api import SerenaAPI
from scripts.save_lead_to_supabase import save_lead

# --- Instâncias de Clientes ---
serena_api_client = SerenaAPI()
# Inicializa o cliente OpenAI para a ferramenta de visão
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# --- Funções Auxiliares ---

def _analyze_bill_with_vision(image_url: str) -> dict:
    """
    Função extraída e adaptada de ai_conversation_handler.py para usar o modelo de visão.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analise a imagem desta conta de energia e extraia o nome do titular, o valor total e o consumo em kWh. Retorne apenas um JSON com as chaves 'nome_cliente', 'valor_total' e 'consumo_kwh'."},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        max_tokens=300,
    )
    # Supondo que a resposta seja um JSON bem formatado
    try:
        content = response.choices[0].message.content
        if content:
            return json.loads(content)
        return {}
    except (json.JSONDecodeError, IndexError):
        return {}


# --- Ferramentas para o Agente ---

@tool
def buscar_planos_de_energia_por_localizacao(localizacao: str) -> str:
    """
    Use esta ferramenta quando um usuário perguntar sobre planos, descontos ou 
    cobertura em uma cidade específica. A entrada deve ser a localização no 
    formato 'cidade, estado'. Retorna os planos disponíveis ou uma mensagem 
    de que a área não é atendida.
    """
    try:
        cidade, estado = localizacao.split(',')
        cidade = cidade.strip()
        estado = estado.strip()
        
        planos = serena_api_client.get_plans(cidade, estado)
        
        if planos:
            return json.dumps(planos)
        else:
            return f"A Serena Energia ainda não atende a região de {cidade}, {estado}."
    except ValueError:
        return "Formato de localização inválido. Por favor, use 'cidade, estado'."
    except Exception as e:
        return f"Ocorreu um erro ao buscar os planos: {e}"

@tool
def analisar_conta_de_energia_de_imagem(image_url: str) -> str:
    """
    Use esta ferramenta APENAS quando o usuário enviar uma imagem de uma 
    conta de luz. Ela recebe a URL da imagem, extrai dados como valor, 
    consumo e nome do cliente, e retorna essas informações estruturadas em JSON.
    """
    try:
        dados_extraidos = _analyze_bill_with_vision(image_url)
        
        if dados_extraidos and all(k in dados_extraidos for k in ['nome_cliente', 'valor_total', 'consumo_kwh']):
            return json.dumps(dados_extraidos)
        else:
            return "Não foi possível extrair todos os dados necessários da imagem. Peça ao usuário para enviar uma imagem mais nítida."
            
    except Exception as e:
        return f"Ocorreu um erro ao processar a imagem da conta de energia: {e}"

# Exemplo de como usar as ferramentas (para testes manuais)
if __name__ == '__main__':
    # Teste 1: Buscar planos
    print("--- Teste: Buscar Planos ---")
    local = "São Paulo, SP"
    print(f"Buscando planos para: {local}")
    print(buscar_planos_de_energia_por_localizacao.invoke(local))
    
    # Teste 2: Simulação de análise de imagem (requer uma URL de imagem válida)
    # print("\n--- Teste: Analisar Imagem ---")
    # image_url_teste = "URL_DE_UMA_CONTA_DE_LUZ.jpg"
    # print(analisar_conta_de_energia_de_imagem.invoke(image_url_teste)) 