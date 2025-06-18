#!/usr/bin/env python3
"""
Assistant Function Handler - Ponte entre OpenAI Assistant e ferramentas Python

Responsabilidade:
- Receber function calls do OpenAI Assistant
- Executar ferramentas Python correspondentes (RAG, Serena API, OCR, etc.)
- Retornar resultados em formato JSON padronizado
- Submeter tool outputs de volta para OpenAI

Author: Serena-Coder
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List
from dotenv import load_dotenv
from openai import OpenAI

# Importa as ferramentas do projeto
sys.path.append('/app')
from scripts.serena_agent.tools.rag_tool import RAGTool
from scripts.serena_agent.tools.serena_api_tool import SerenaAPITool
from scripts.serena_agent.tools.ocr_tool import OCRTool
from scripts.serena_agent.tools.conversation_tool import ConversationTool

# Carrega variáveis de ambiente
load_dotenv()

class AssistantFunctionHandler:
    """Handler para executar function calls do OpenAI Assistant"""
    
    def __init__(self):
        """Inicializa cliente OpenAI e ferramentas disponíveis"""
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Inicializa ferramentas disponíveis
        self.tools = {
            'search_knowledge_base': RAGTool(),
            'get_energy_plans': SerenaAPITool(),
            'extract_text_from_image': OCRTool(),
            'save_and_fetch_conversation': ConversationTool()
        }
        
        # Schema das ferramentas para o Assistant
        self.tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Busca informações na base de conhecimento da Serena sobre energia solar, instalação, preços, etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Pergunta ou termo de busca sobre energia solar"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_energy_plans",
                    "description": "Obtém planos de energia solar disponíveis para uma cidade específica",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "Nome da cidade (ex: Belo Horizonte)"
                            },
                            "state": {
                                "type": "string",
                                "description": "Sigla do estado (ex: MG)"
                            }
                        },
                        "required": ["city", "state"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "extract_text_from_image",
                    "description": "Extrai texto de imagem de conta de energia para análise de consumo",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "image_url": {
                                "type": "string",
                                "description": "URL da imagem da conta de energia"
                            }
                        },
                        "required": ["image_url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "save_and_fetch_conversation",
                    "description": "Salva mensagens da conversa ou recupera histórico",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "phone_number": {
                                "type": "string",
                                "description": "Número de telefone do lead"
                            },
                            "action": {
                                "type": "string",
                                "enum": ["save_message", "get_history"],
                                "description": "Ação a ser executada"
                            },
                            "message": {
                                "type": "string",
                                "description": "Mensagem a ser salva (se action=save_message)"
                            },
                            "role": {
                                "type": "string",
                                "enum": ["user", "assistant"],
                                "description": "Papel do remetente da mensagem"
                            }
                        },
                        "required": ["phone_number", "action"]
                    }
                }
            }
        ]
    
    def execute_function_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma function call específica
        
        Args:
            tool_call: Objeto da OpenAI com função a ser executada
            
        Returns:
            Dict com resultado da execução
        """
        try:
            function_name = tool_call['function']['name']
            function_args = json.loads(tool_call['function']['arguments'])
            
            print(f"Executando função: {function_name} com args: {function_args}")
            
            # Verifica se a função existe
            if function_name not in self.tools:
                return {
                    "success": False,
                    "error": f"Função '{function_name}' não encontrada",
                    "available_functions": list(self.tools.keys())
                }
            
            # Executa a função
            tool = self.tools[function_name]
            result = tool.run(**function_args)
            
            return {
                "success": True,
                "data": result,
                "function": function_name
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Erro ao decodificar argumentos JSON: {str(e)}",
                "function": tool_call.get('function', {}).get('name', 'unknown')
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na execução: {str(e)}",
                "function": tool_call.get('function', {}).get('name', 'unknown')
            }
    
    def process_run_with_tool_calls(self, thread_id: str, run_id: str) -> Dict[str, Any]:
        """
        Processa Run que requer function calls
        
        Args:
            thread_id: ID da thread OpenAI
            run_id: ID da run OpenAI
            
        Returns:
            Dict com resultado do processamento
        """
        try:
            # 1. Recuperar run e tool calls
            run = self.openai_client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            
            if run.status != 'requires_action':
                return {
                    "success": False,
                    "error": f"Run não requer ação. Status: {run.status}"
                }
            
            if not run.required_action or not run.required_action.submit_tool_outputs:
                return {
                    "success": False,
                    "error": "Run não possui tool calls para processar"
                }
            
            # 2. Executar cada tool call
            tool_outputs = []
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            
            for tool_call in tool_calls:
                print(f"Processando tool call: {tool_call.id}")
                
                # Converte tool_call para dict
                tool_call_dict = {
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                }
                
                # Executa função
                function_result = self.execute_function_call(tool_call_dict)
                
                # Prepara output para OpenAI
                output_content = json.dumps(function_result, ensure_ascii=False)
                
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": output_content
                })
            
            # 3. Submeter tool outputs para OpenAI
            updated_run = self.openai_client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=tool_outputs
            )
            
            return {
                "success": True,
                "tool_outputs_submitted": len(tool_outputs),
                "run_status": updated_run.status,
                "tool_outputs": tool_outputs
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao processar tool calls: {str(e)}",
                "tool_outputs_submitted": 0
            }

def main():
    """Função principal para uso via CLI"""
    parser = argparse.ArgumentParser(description='Processa function calls do OpenAI Assistant')
    parser.add_argument('--thread-id', required=True, help='ID da thread OpenAI')
    parser.add_argument('--run-id', required=True, help='ID da run OpenAI')
    
    args = parser.parse_args()
    
    try:
        handler = AssistantFunctionHandler()
        result = handler.process_run_with_tool_calls(args.thread_id, args.run_id)
        
        # Output no formato Kestra
        if result['success']:
            print(f'::kestra::outputs::{{"status": "success", "tool_outputs_submitted": {result["tool_outputs_submitted"]}, "run_status": "{result["run_status"]}"}}::')
        else:
            print(f'::kestra::outputs::{{"status": "error", "error": "{result["error"]}", "tool_outputs_submitted": {result.get("tool_outputs_submitted", 0)}}}::')
            sys.exit(1)
            
    except Exception as e:
        print(f'::kestra::outputs::{{"status": "error", "error": "{str(e)}", "tool_outputs_submitted": 0}}::')
        sys.exit(1)

if __name__ == "__main__":
    main() 