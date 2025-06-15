"""
Classification Prompt Template

Template padronizado para classificação de intenções em conversas
com leads sobre energia solar.
"""

CLASSIFICATION_TEMPLATE = """
Você é um especialista em energia solar da Serena Energia.

Analise a mensagem do lead e classifique a intenção:

INTENÇÕES POSSÍVEIS:
- greeting: Saudação inicial ou cumprimento
- interest: Interesse em energia solar ou economia
- question_plans: Pergunta sobre planos ou preços
- question_coverage: Pergunta sobre cobertura/disponibilidade
- send_invoice: Envio de fatura/conta de energia
- objection: Objeção ou resistência à proposta
- ready_to_buy: Pronto para fechar negócio
- not_interested: Não tem interesse
- unclear: Mensagem não clara ou fora do contexto

HISTÓRICO DA CONVERSA:
{conversation_history}

MENSAGEM ATUAL:
{current_message}

TELEFONE DO LEAD: {phone}

Responda APENAS com a classificação (uma das intenções acima).
"""

def get_classification_prompt(phone: str, current_message: str, conversation_history: str = "") -> str:
    """
    Gera prompt formatado para classificação de intenção.
    
    Args:
        phone: Telefone do lead
        current_message: Mensagem atual para classificar
        conversation_history: Histórico da conversa
        
    Returns:
        Prompt formatado para o modelo LLM
    """
    return CLASSIFICATION_TEMPLATE.format(
        phone=phone,
        current_message=current_message,
        conversation_history=conversation_history or "Primeira mensagem da conversa"
    ) 