import os
import json
import logging
from kestra import Kestra

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # Obter variáveis de ambiente
        phone = os.environ.get('PHONE', '5511999999999')
        message = os.environ.get('MESSAGE', 'Mensagem vazia')
        logger.info(f"Processando mensagem para {phone}: {message[:50]}...")

        # Detectar tipo de mensagem
        message_type = "text"
        message_content = message

        # Verificar se é mensagem de botão
        button_keywords = [
            "Botão:", "botão", "Ativar Perfil", "ativar perfil", "tipo button", "mensagem do tipo button",
            "Clique de botão", "Sim, confirmar cidade!", "Confirmar", "Sim", "Não"
        ]
        if any(keyword.lower() in message.lower() for keyword in button_keywords):
            message_type = "button"
            # Identificar o tipo de botão
            if "Ativar Perfil" in message or "ativar perfil" in message.lower():
                message_content = "Usuário clicou no botão 'Ativar Perfil' para iniciar o cadastro"
                logger.info(f"Detectado botão de ativação de perfil: {message}")
            elif "mensagem do tipo button" in message.lower():
                message_content = "Usuário clicou em um botão do template"
                logger.info(f"Detectada mensagem de tipo button: {message}")
            elif "Sim, confirmar cidade!" in message:
                message_content = "Usuário confirmou a cidade clicando no botão"
                logger.info(f"Detectado botão de confirmação de cidade: {message}")
            else:
                logger.info(f"Detectada mensagem de botão genérica: {message}")

        result = {
            'message_type': message_type,
            'message_content': message_content,
            'phone': phone
        }
        logger.info(f"Resultado da extração: {result}")
        Kestra.outputs(result)

    except Exception as e:
        logger.error(f"Erro ao extrair conteúdo: {str(e)}")
        Kestra.outputs({
            'message_type': 'text',
            'message_content': f'Erro ao processar mensagem: {str(e)}',
            'phone': os.environ.get('PHONE', '5511999999999')
        })

if __name__ == "__main__":
    main() 