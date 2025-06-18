#!/usr/bin/env python3
"""
OpenAI Assistant Manager for Serena Energia Lead Qualification System

This module manages the OpenAI Assistant creation and retrieval for the 
serena-qualifier project. It implements a singleton pattern for Assistant 
management, ensuring consistent configuration and avoiding duplicate creation.

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from openai import OpenAI
from openai.types.beta import Assistant
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AssistantManager:
    """
    Manager class for OpenAI Assistant operations.
    
    Handles creation, retrieval, and configuration of the Serena Energy
    sales specialist assistant with proper knowledge base and tools.
    """
    
    def __init__(self):
        """Initialize the AssistantManager with OpenAI client."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=self.api_key)
        # Reason: Use /app/ path for Kestra container environment compatibility
        self.assistant_id_file = Path("/app/assistant_id.txt") if os.path.exists("/app") else Path("assistant_id.txt")
        self.knowledge_base_path = Path("knowledge_base")
        
    def _get_serena_sales_prompt(self) -> str:
        """
        Load the specialized sales prompt for Serena Energy assistant.
        Updated for GPT-4o Vision capabilities, removing OCR dependencies.
        
        Returns:
            str: The comprehensive system prompt for the assistant
        """
        # Try to load from external file first
        prompt_file = os.path.join(os.path.dirname(__file__), 'serena_agent', 'prompts', 'assistant_sales_prompt.txt')
        
        if os.path.exists(prompt_file):
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except Exception as e:
                logger.warning(f"Could not load prompt from file: {e}")
        
        # Fallback to embedded prompt (updated for GPT-4o Vision)
        return """Você é a **Serena**, uma assistente virtual especializada em vendas da empresa **SRna Energia**. Sua missão é **ajudar leads interessados a entender, qualificar e contratar o serviço de energia limpa e mais barata da Serena**, de forma consultiva, clara e empática.

## ANÁLISE DE IMAGENS
**Quando o usuário enviar uma imagem, analise-a diretamente usando sua capacidade de 'vision'. Assuma que é uma conta de energia e extraia as seguintes informações em um formato JSON:**
```json
{
  "nome_titular": "...",
  "valor_total": "...",
  "consumo_kwh": "...",
  "distribuidora": "...",
  "endereco": "..."
}
```
**Após a extração, use esses dados para continuar a conversa de qualificação de forma natural, comentando sobre os valores encontrados.**

## 🧭 Contexto e Missão da Empresa
A SRna Energia é uma empresa de Geração Distribuída Compartilhada. Ela gera energia solar em fazendas próprias e converte isso em **créditos de energia** que são aplicados diretamente na conta de luz dos clientes, proporcionando **descontos garantidos**, **sem necessidade de obras ou instalação**, e com **adesão 100% digital**.

## 🧑‍💼 Seu Papel
Você atua como **vendedora digital da Serena**, com os seguintes objetivos:
1. Esclarecer dúvidas sobre o funcionamento do serviço;
2. Qualificar leads com base em critérios de consumo e titularidade da conta;
3. Processar automaticamente imagens de contas de luz via OCR;
4. Confirmar a elegibilidade do lead e, se qualificado, encaminhá‑lo para o time de consultores humanos.

## 🧰 Ferramentas à Sua Disposição
- `query_serena_api` — Verifica área de cobertura, planos e promoções disponíveis.
- `save_and_fetch_conversation` — Busca e registra histórico de conversas no Supabase.
- `rag_tool` — Responde dúvidas recorrentes com base na base de conhecimento oficial.

## 🧠 Regras de Qualificação
- Consumo mínimo recomendado: **R$ 200,00/mês** (ideal a partir de R$ 500).
- Titular da conta de luz deve ser o mesmo que assinará o contrato.
- Unidade consumidora deve estar dentro da área de cobertura da Serena.

## ✅ Argumentos de Vendas Exemplos
- "Você não precisa instalar nada na sua casa. Toda energia vem das nossas fazendas solares e é abatida direto na sua conta."
- "Você continuará recebendo sua conta da distribuidora, mas ela virá com desconto. A Serena envia um segundo boleto já com valor reduzido. A soma dos dois é sempre menor que sua conta atual."
- "Nosso processo é 100% digital, sem burocracia e sem visitas técnicas."

## 🛡️ Tratamento de Objeções
- "E se eu me mudar de endereço?" → "Sem problemas, fazemos transferência enquanto for na mesma área de concessão da distribuidora."
- "Se minha conta for abaixo de R$ 200?" → "Neste momento nosso modelo exige R$ 200 mínimos para viabilizar a economia, mas podemos entrar em contato quando seu consumo subir."
- "Como sei que é confiável?" → "Somos regulamentados pela ANEEL (Lei 14.300/2022) e temos centenas de clientes satisfeitos."
- "E se quiser cancelar?" → "Nosso contrato é transparente, com processo de cancelamento simples descrito em contrato."

## 🤖 Estilo e Tom
- Empático, consultivo e educativo.
- Use linguagem simples, sem jargões técnicos.
- Insira emojis de forma moderada para humanizar (por exemplo: ✅, 💡, 📊).
- Sempre proponha próximos passos claros antes de encerrar a interação.

## ❗ Instruções Especiais
1. Ao detectar mensagem com imagem de conta de luz, analise diretamente com sua capacidade de vision.
2. Use `query_serena_api` para confirmar cobertura geográfica e planos.
3. Salve cada interação via `save_and_fetch_conversation` no Supabase.
4. Caso o lead não seja qualificado, explique por que ("consumo abaixo de R$ 200" ou "fora de área de cobertura") e ofereça um canal de recontato futuro.
5. **Não** invente dados — apoie‑se apenas na base de conhecimento e nas respostas do `rag_tool`.

## 🛑 Limites
- Não prometa economia exata sem análise detalhada da fatura.
- Não finalize ou confirme adesão; direcione sempre ao time comercial.
- Cite a regulamentação ANEEL (Resolução 482/2012 e Lei 14.300/2022) ao falar de legalidade, mas **não** faça promessas jurídicas.

---
Pronto para começar a atender seus leads!"""

    def _get_assistant_config(self) -> Dict[str, Any]:
        """
        Get the configuration for creating the OpenAI Assistant.
        
        Returns:
            Dict[str, Any]: Configuration parameters for assistant creation
        """
        return {
            "name": "Serena Sales Specialist",
            "description": "Assistente virtual da SRna Energia para qualificação de leads",
            "instructions": self._get_serena_sales_prompt(),
            "model": "gpt-4o",
            "tools": [
                {"type": "retrieval"},  # For RAG functionality with knowledge base
                {
                    "type": "function", 
                    "function": {
                        "name": "query_serena_api",
                        "description": "Query Serena API for coverage, plans and pricing information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "city": {
                                    "type": "string",
                                    "description": "City name to check coverage"
                                },
                                "state": {
                                    "type": "string", 
                                    "description": "State abbreviation (e.g., SP, RJ, MG)"
                                },
                                "action": {
                                    "type": "string",
                                    "enum": ["check_coverage", "get_plans", "calculate_savings"],
                                    "description": "Type of API query to perform"
                                }
                            },
                            "required": ["city", "state", "action"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "rag_tool",
                        "description": "Responder dúvidas recorrentes usando a base de conhecimento FAQ da Serena",
                        "parameters": {
                            "type": "object", 
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Pergunta ou termo de busca na base de conhecimento"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "save_and_fetch_conversation",
                        "description": "Registrar e recuperar histórico de conversas no Supabase",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "phone_number": {
                                    "type": "string",
                                    "description": "Número de telefone do lead (+5581...)"
                                },
                                "action": {
                                    "type": "string",
                                    "enum": ["save_message", "get_history", "update_lead_status"],
                                    "description": "Ação a ser executada no Supabase"
                                },
                                "message": {
                                    "type": "string",
                                    "description": "Mensagem a ser salva (quando action=save_message)"
                                },
                                "status": {
                                    "type": "string",
                                    "description": "Status do lead (quando action=update_lead_status)"
                                }
                            },
                            "required": ["phone_number", "action"]
                        }
                    }
                }
            ],
            "temperature": 0.7,
            "top_p": 1.0
        }

    def get_or_create_assistant(self) -> str:
        """
        Get existing assistant ID or create a new one.
        
        This function implements the core logic specified in the task:
        1. Check if assistant_id.txt exists
        2. If yes, return the stored ID
        3. If no, create new assistant and save ID
        
        Returns:
            str: The OpenAI Assistant ID
            
        Raises:
            Exception: If assistant creation fails
        """
        logger.info("Starting get_or_create_assistant process")
        
        # Check if assistant_id.txt exists
        if self.assistant_id_file.exists():
            try:
                assistant_id = self.assistant_id_file.read_text().strip()
                logger.info(f"Found existing assistant ID: {assistant_id}")
                
                # Verify the assistant still exists in OpenAI
                try:
                    assistant = self.client.beta.assistants.retrieve(assistant_id)
                    logger.info(f"Verified assistant exists: {assistant.name}")
                    return assistant_id
                except Exception as verify_error:
                    logger.warning(f"Stored assistant ID invalid: {verify_error}")
                    # Continue to create new assistant
                    
            except Exception as read_error:
                logger.error(f"Error reading assistant_id.txt: {read_error}")
                # Continue to create new assistant
        
        # Create new assistant
        logger.info("Creating new OpenAI assistant")
        try:
            config = self._get_assistant_config()
            assistant = self.client.beta.assistants.create(**config)
            
            # Save the assistant ID
            self.assistant_id_file.write_text(assistant.id)
            logger.info(f"Created and saved new assistant: {assistant.id}")
            
            return assistant.id
            
        except Exception as create_error:
            logger.error(f"Failed to create assistant: {create_error}")
            raise Exception(f"Assistant creation failed: {create_error}")

    def get_assistant_info(self, assistant_id: str) -> Optional[Assistant]:
        """
        Get detailed information about an assistant.
        
        Args:
            assistant_id (str): The OpenAI Assistant ID
            
        Returns:
            Optional[Assistant]: Assistant object or None if not found
        """
        try:
            assistant = self.client.beta.assistants.retrieve(assistant_id)
            return assistant
        except Exception as e:
            logger.error(f"Error retrieving assistant info: {e}")
            return None

    def update_assistant(self, assistant_id: str, **kwargs) -> Optional[Assistant]:
        """
        Update an existing assistant configuration.
        
        Args:
            assistant_id (str): The OpenAI Assistant ID
            **kwargs: Parameters to update
            
        Returns:
            Optional[Assistant]: Updated assistant object or None if failed
        """
        try:
            assistant = self.client.beta.assistants.update(assistant_id, **kwargs)
            logger.info(f"Updated assistant: {assistant_id}")
            return assistant
        except Exception as e:
            logger.error(f"Error updating assistant: {e}")
            return None

    def delete_assistant(self, assistant_id: str) -> bool:
        """
        Delete an assistant and clean up local files.
        
        Args:
            assistant_id (str): The OpenAI Assistant ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.client.beta.assistants.delete(assistant_id)
            
            # Remove local assistant_id.txt file
            if self.assistant_id_file.exists():
                self.assistant_id_file.unlink()
                
            logger.info(f"Deleted assistant: {assistant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting assistant: {e}")
            return False


def main():
    """
    Main function for command-line usage.
    
    This allows the script to be run directly from Kestra workflows
    or command line for testing purposes.
    """
    try:
        manager = AssistantManager()
        assistant_id = manager.get_or_create_assistant()
        
        # Output for Kestra workflow consumption
        result = {
            "assistant_id": assistant_id,
            "status": "success",
            "message": f"Assistant ready: {assistant_id}"
        }
        
        print(json.dumps(result))
        return assistant_id
        
    except Exception as e:
        error_result = {
            "assistant_id": None,
            "status": "error", 
            "message": f"Failed to get/create assistant: {str(e)}"
        }
        
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 