"""
Extraction Prompt Template

Template padronizado para extração de dados estruturados
das conversas com leads.
"""



EXTRACTION_TEMPLATE = """
Você é um especialista em energia solar da Serena Energia.

Extraia as seguintes informações da conversa com o lead:

DADOS PARA EXTRAIR:
- name: Nome completo do lead
- city: Cidade onde mora
- state: Estado (sigla como MG, SP, RJ)
- current_bill_amount: Valor atual da conta de energia (apenas números)
- property_type: Tipo de imóvel (casa, apartamento, empresa)
- roof_type: Tipo de telhado se mencionado
- interest_level: Nível de interesse (alto, médio, baixo)

HISTÓRICO DA CONVERSA:
{conversation_history}

MENSAGEM ATUAL:
{current_message}

TELEFONE DO LEAD: {phone}

Responda em formato JSON válido com apenas os dados encontrados.
Se alguma informação não estiver disponível, não inclua no JSON.

Exemplo:
{{"name": "João Silva", "city": "Belo Horizonte", "state": "MG", "current_bill_amount": 250.00}}
"""

def get_extraction_prompt(phone: str, current_message: str, conversation_history: str = "") -> str:
    """
    Gera prompt formatado para extração de dados.
    
    Args:
        phone: Telefone do lead
        current_message: Mensagem atual para analisar
        conversation_history: Histórico da conversa
        
    Returns:
        Prompt formatado para o modelo LLM
    """
    return EXTRACTION_TEMPLATE.format(
        phone=phone,
        current_message=current_message,
        conversation_history=conversation_history or "Primeira mensagem da conversa"
    ) 