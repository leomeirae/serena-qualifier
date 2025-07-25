import logging

# Configuração incremental do logging estruturado
# Criada JUL/2025 conforme AI_UPGRADE_GUIDE.md

logging.basicConfig(
    filename="interaction.log",
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

def log_interaction(phone: str, interaction_type: str, message: str) -> None:
    """
    Registra uma interação no arquivo de log estruturado.
    Parâmetros:
        phone (str): Telefone do lead.
        interaction_type (str): Tipo de interação (ex: 'envio_conta', 'lembrete', 'feedback').
        message (str): Mensagem ou detalhe da interação.
    """
    logging.info(f"{phone} | {interaction_type} | {message}")

# Função incremental de JUL/2025 