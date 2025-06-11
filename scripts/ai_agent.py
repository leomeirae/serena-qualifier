import os
import json
import openai
from typing import Dict, List, Optional, Any
from utils.conversation_manager import ConversationManager
import logging
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAgent:
    def __init__(self):
        """Inicializar agente de IA com OpenAI GPT-4o-mini"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"
        self.conversation_manager = ConversationManager()
        
        # Configurações do modelo
        self.temperature = 0.3  # Consistência para classificação
        self.max_tokens = 500   # Controle de custo
        
        # Intenções possíveis
        self.intentions = [
            "informou_cidade",
            "informou_valor_conta", 
            "informou_tipo_imovel",
            "fez_pergunta_geral",
            "pediu_para_parar",
            "solicitou_fatura",
            "enviou_fatura",      # Nova intenção para quando envia imagem/documento
            "iniciou_ativacao",
            "saudacao_inicial",
            "incompreensivel"
        ]

    def classify_intention(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Classificar intenção da mensagem do usuário
        """
        try:
            # Recuperar histórico da conversa
            conversation_history = self.conversation_manager.get_conversation_history(phone_number)
            
            # Construir prompt para classificação
            prompt = self._build_intention_prompt(message, conversation_history)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=prompt,
                temperature=self.temperature,
                max_tokens=100
            )
            
            intention = response.choices[0].message.content.strip().lower()
            
            # Validar se intenção está na lista permitida
            if intention not in self.intentions:
                intention = "incompreensivel"
            
            logger.info(f"Intenção classificada para {phone_number}: {intention}")
            
            return {
                "intention": intention,
                "confidence": "high",  # GPT-4o-mini é confiável
                "raw_response": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Erro ao classificar intenção: {str(e)}")
            return {
                "intention": "incompreensivel", 
                "confidence": "low",
                "error": str(e)
            }

    def extract_data(self, phone_number: str, message: str, data_type: str) -> Dict[str, Any]:
        """
        Extrair dados específicos da mensagem
        data_type: 'cidade', 'valor_conta', 'tipo_imovel'
        """
        try:
            conversation_history = self.conversation_manager.get_conversation_history(phone_number)
            
            prompt = self._build_extraction_prompt(message, conversation_history, data_type)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=prompt,
                temperature=0.1,  # Máxima consistência para extração
                max_tokens=100
            )
            
            extracted_data = response.choices[0].message.content.strip()
            
            logger.info(f"Dados extraídos ({data_type}) para {phone_number}: {extracted_data}")
            
            return {
                "data_type": data_type,
                "extracted_value": extracted_data,
                "success": True,
                "raw_response": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados: {str(e)}")
            return {
                "data_type": data_type,
                "extracted_value": None,
                "success": False,
                "error": str(e)
            }

    def generate_response(self, phone_number: str, user_message: str, context: Dict = None) -> Dict[str, Any]:
        """
        Gerar resposta conversacional contextualizada
        """
        try:
            conversation_history = self.conversation_manager.get_conversation_history(phone_number)
            
            # Adicionar mensagem do usuário ao histórico
            self.conversation_manager.add_message(
                phone_number, 
                "user", 
                user_message
            )
            
            prompt = self._build_response_prompt(user_message, conversation_history, context)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=prompt,
                temperature=0.7,  # Criatividade para respostas naturais
                max_tokens=300
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Adicionar resposta da IA ao histórico
            self.conversation_manager.add_message(
                phone_number,
                "assistant", 
                ai_response
            )
            
            logger.info(f"Resposta gerada para {phone_number}")
            
            return {
                "response": ai_response,
                "success": True,
                "tokens_used": response.usage.total_tokens if response.usage else None
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {str(e)}")
            return {
                "response": "Desculpe, tive um problema técnico. Pode repetir sua mensagem?",
                "success": False,
                "error": str(e)
            }

    def _build_intention_prompt(self, message: str, history: List[Dict]) -> List[Dict]:
        """Construir prompt para classificação de intenção"""
        
        history_text = self._format_conversation_history(history)
        
        system_prompt = f"""Você é um assistente especializado em classificar intenções de mensagens em um sistema de qualificação de leads para energia solar.

INTENÇÕES POSSÍVEIS:
- informou_cidade: usuário informou cidade/localização
- informou_valor_conta: usuário informou valor da conta de energia
- informou_tipo_imovel: usuário informou tipo de imóvel (casa, apartamento, etc)
- fez_pergunta_geral: pergunta sobre energia solar, processo, etc
- pediu_para_parar: quer parar conversa ou cancelar
- solicitou_fatura: quer enviar foto da fatura
- enviou_fatura: enviou imagem/documento da conta de energia
- iniciou_ativacao: quer prosseguir com instalação
- saudacao_inicial: primeira mensagem/cumprimento
- incompreensivel: mensagem confusa ou fora do contexto

HISTÓRICO DA CONVERSA:
{history_text}

INSTRUÇÕES:
- Responda APENAS com uma das intenções listadas
- Considere o contexto completo da conversa
- Seja preciso na classificação"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Classifique esta mensagem: '{message}'"}
        ]

    def _build_extraction_prompt(self, message: str, history: List[Dict], data_type: str) -> List[Dict]:
        """Construir prompt para extração de dados"""
        
        history_text = self._format_conversation_history(history)
        
        extraction_rules = {
            "cidade": "Extraia apenas o nome da cidade mencionada. Se não houver cidade clara, responda 'não_identificado'",
            "valor_conta": "Extraia apenas o valor numérico da conta de energia (ex: '150', '89.50'). Se não houver valor, responda 'não_identificado'", 
            "tipo_imovel": "Extraia apenas o tipo de imóvel (casa, apartamento, comercial, etc). Se não houver tipo, responda 'não_identificado'"
        }
        
        system_prompt = f"""Você é um extrator de dados especializado em conversas sobre energia solar.

HISTÓRICO DA CONVERSA:
{history_text}

TAREFA: {extraction_rules.get(data_type, 'Extrair informação relevante')}

INSTRUÇÕES:
- Responda APENAS com o dado solicitado
- Se não conseguir extrair, responda 'não_identificado'
- Seja preciso e conciso"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Extraia {data_type} desta mensagem: '{message}'"}
        ]

    def _build_response_prompt(self, message: str, history: List[Dict], context: Dict = None) -> List[Dict]:
        """Construir prompt para geração de resposta"""
        
        history_text = self._format_conversation_history(history)
        context_text = json.dumps(context, indent=2) if context else "Nenhum contexto adicional"
        
        system_prompt = f"""Você é Serena, assistente especializada em qualificação de leads para energia solar. Seu objetivo é coletar informações do cliente de forma natural e amigável.

INFORMAÇÕES NECESSÁRIAS:
1. Cidade onde mora
2. Valor médio da conta de energia
3. Tipo de imóvel (casa, apartamento, etc)

HISTÓRICO DA CONVERSA:
{history_text}

CONTEXTO ADICIONAL:
{context_text}

DIRETRIZES:
- Seja conversacional e amigável
- Faça uma pergunta por vez
- Use linguagem simples e clara
- Se o cliente fez pergunta, responda primeiro
- Guie naturalmente para coletar as informações necessárias
- Mantenha foco em energia solar
- Limite respostas a 2-3 frases"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]

    def _format_conversation_history(self, history: List[Dict]) -> str:
        """Formatar histórico para inclusão nos prompts"""
        if not history:
            return "Nenhum histórico anterior"
        
        formatted = []
        for msg in history[-10:]:  # Últimas 10 mensagens para controlar tokens
            role = "Cliente" if msg['role'] == 'user' else "Serena"
            formatted.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted)

# Função principal para uso no Kestra
def process_ai_request(phone_number: str, message: str, action: str, **kwargs) -> Dict[str, Any]:
    """
    Função principal para processar requisições de IA no Kestra
    
    Actions disponíveis:
    - classify: classificar intenção
    - extract: extrair dados (requer data_type)
    - respond: gerar resposta
    """
    try:
        agent = AIAgent()
        
        if action == "classify":
            return agent.classify_intention(phone_number, message)
        
        elif action == "extract":
            data_type = kwargs.get('data_type')
            if not data_type:
                raise ValueError("data_type é obrigatório para ação extract")
            return agent.extract_data(phone_number, message, data_type)
        
        elif action == "respond":
            context = kwargs.get('context', {})
            return agent.generate_response(phone_number, message, context)
        
        else:
            raise ValueError(f"Ação '{action}' não reconhecida")
    
    except Exception as e:
        logger.error(f"Erro em process_ai_request: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Teste básico
    import sys
    if len(sys.argv) >= 4:
        phone = sys.argv[1]
        message = sys.argv[2] 
        action = sys.argv[3]
        result = process_ai_request(phone, message, action)
        print(json.dumps(result, indent=2, ensure_ascii=False)) 