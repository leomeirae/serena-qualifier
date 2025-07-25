import os
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

logger = logging.getLogger(__name__)

def process_energy_bill_image(image_path: str, lead_phone: str) -> dict:
    """
    Processa imagem de conta de energia usando OpenAI Vision API e salva resultado no Supabase.
    Parâmetros:
        image_path (str): Caminho da imagem da conta de energia.
        lead_phone (str): Telefone do lead associado.
    Retorna:
        dict: Resultado do processamento com status e dados extraídos
    """
    try:
        # Usar variáveis de ambiente corretas
        openai_api_key = os.getenv("OPENAI_API_KEY")
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not all([openai_api_key, supabase_url, supabase_key]):
            logger.error("Variáveis de ambiente não configuradas para processamento de imagem")
            return {
                "success": False,
                "error": "Configuração incompleta para processamento de imagem"
            }
        
        # Importar OpenAI apenas quando necessário
        import openai
        from supabase import create_client
        
        openai.api_key = openai_api_key
        supabase = create_client(supabase_url, supabase_key)

        # Verificar se o arquivo existe
        if not os.path.exists(image_path):
            logger.error(f"Arquivo de imagem não encontrado: {image_path}")
            return {
                "success": False,
                "error": f"Arquivo de imagem não encontrado: {image_path}"
            }

        with open(image_path, "rb") as img:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": img.read()}]
            )
            extracted_data = response['choices'][0]['message']['content']

        # Salva dados extraídos no Supabase
        result = supabase.table("energy_bills").insert({
            "phone": lead_phone,
            "image_path": image_path,
            "extracted_data": extracted_data
        }).execute()

        logger.info(f"Imagem processada com sucesso para {lead_phone}")
        
        return {
            "success": True,
            "extracted_data": extracted_data,
            "phone": lead_phone
        }

    except ImportError as e:
        logger.error(f"Erro ao importar dependências: {e}")
        return {
            "success": False,
            "error": f"Erro de dependência: {e}"
        }
    except Exception as e:
        logger.error(f"Erro ao processar imagem: {e}")
        return {
            "success": False,
            "error": f"Erro interno: {e}"
        } 