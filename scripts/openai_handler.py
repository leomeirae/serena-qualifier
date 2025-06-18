#!/usr/bin/env python3
"""
OpenAI Handler - Centraliza interações com a API de Assistentes OpenAI

Responsabilidade:
- add_message_to_thread: Adiciona mensagem do usuário à thread
- create_run: Cria e executa run do assistant
- check_run_status: Verifica status da run
- get_final_response: Obtém resposta final do assistant

Author: Serena-Coder
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI

# Carrega variáveis de ambiente
load_dotenv()

class OpenAIHandler:
    """Centraliza operações com a API de Assistentes OpenAI"""
    
    def __init__(self):
        """Inicializa cliente OpenAI"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY é obrigatória")
            
        self.client = OpenAI(api_key=api_key)
    
    def add_message_to_thread(self, thread_id: str, content: str, role: str = "user") -> Dict[str, Any]:
        """
        Adiciona mensagem à thread OpenAI
        
        Args:
            thread_id: ID da thread OpenAI
            content: Conteúdo da mensagem
            role: Papel do remetente (user/assistant)
            
        Returns:
            Dict com resultado da operação
        """
        try:
            message = self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role=role,
                content=content
            )
            
            return {
                "success": True,
                "message_id": message.id,
                "thread_id": thread_id,
                "content": content,
                "role": role
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao adicionar mensagem: {str(e)}",
                "thread_id": thread_id
            }
    
    def create_run(self, thread_id: str, assistant_id: str, instructions: Optional[str] = None) -> Dict[str, Any]:
        """
        Cria e executa run do assistant
        
        Args:
            thread_id: ID da thread OpenAI
            assistant_id: ID do assistant OpenAI
            instructions: Instruções específicas para esta run (opcional)
            
        Returns:
            Dict com resultado da operação
        """
        try:
            run_params = {
                "thread_id": thread_id,
                "assistant_id": assistant_id
            }
            
            if instructions:
                run_params["instructions"] = instructions
            
            run = self.client.beta.threads.runs.create(**run_params)
            
            return {
                "success": True,
                "run_id": run.id,
                "thread_id": thread_id,
                "assistant_id": assistant_id,
                "status": run.status,
                "created_at": run.created_at
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao criar run: {str(e)}",
                "thread_id": thread_id,
                "assistant_id": assistant_id
            }
    
    def check_run_status(self, thread_id: str, run_id: str) -> Dict[str, Any]:
        """
        Verifica status da run
        
        Args:
            thread_id: ID da thread OpenAI
            run_id: ID da run OpenAI
            
        Returns:
            Dict com status e dados da run
        """
        try:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            
            result = {
                "success": True,
                "run_id": run_id,
                "thread_id": thread_id,
                "status": run.status,
                "completed_at": run.completed_at,
                "failed_at": run.failed_at,
                "last_error": run.last_error.message if run.last_error else None
            }
            
            # Se requer ação, incluir tool calls
            if run.status == 'requires_action' and run.required_action:
                tool_calls = []
                if run.required_action.submit_tool_outputs:
                    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                        tool_calls.append({
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        })
                result["tool_calls"] = tool_calls
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao verificar status: {str(e)}",
                "run_id": run_id,
                "thread_id": thread_id,
                "status": "error"
            }
    
    def get_final_response(self, thread_id: str, limit: int = 1) -> Dict[str, Any]:
        """
        Obtém resposta final do assistant da thread
        
        Args:
            thread_id: ID da thread OpenAI
            limit: Número de mensagens a recuperar
            
        Returns:
            Dict com a resposta final
        """
        try:
            messages = self.client.beta.threads.messages.list(
                thread_id=thread_id,
                order="desc",
                limit=limit
            )
            
            if not messages.data:
                return {
                    "success": False,
                    "error": "Nenhuma mensagem encontrada na thread",
                    "thread_id": thread_id
                }
            
            # Procura a última mensagem do assistant
            assistant_message = None
            for message in messages.data:
                if message.role == "assistant":
                    assistant_message = message
                    break
            
            if not assistant_message:
                return {
                    "success": False,
                    "error": "Nenhuma mensagem do assistant encontrada",
                    "thread_id": thread_id
                }
            
            # Extrai conteúdo da mensagem
            content = ""
            for content_block in assistant_message.content:
                if content_block.type == "text":
                    content += content_block.text.value
            
            return {
                "success": True,
                "final_response": content,
                "message_id": assistant_message.id,
                "thread_id": thread_id,
                "created_at": assistant_message.created_at
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter resposta: {str(e)}",
                "thread_id": thread_id
            }

def main():
    """Função principal para uso via CLI"""
    parser = argparse.ArgumentParser(description='Handler para operações OpenAI Assistant')
    parser.add_argument('--action', required=True, 
                       choices=['add_message', 'create_run', 'check_run', 'get_response'],
                       help='Ação a ser executada')
    parser.add_argument('--thread-id', required=True, help='ID da thread OpenAI')
    parser.add_argument('--content', help='Conteúdo da mensagem (para add_message)')
    parser.add_argument('--assistant-id', help='ID do assistant (para create_run)')
    parser.add_argument('--run-id', help='ID da run (para check_run)')
    parser.add_argument('--role', default='user', help='Papel do remetente (para add_message)')
    parser.add_argument('--instructions', help='Instruções específicas (para create_run)')
    
    args = parser.parse_args()
    
    try:
        handler = OpenAIHandler()
        result = None
        
        if args.action == 'add_message':
            if not args.content:
                raise ValueError("--content é obrigatório para add_message")
            result = handler.add_message_to_thread(args.thread_id, args.content, args.role)
            
        elif args.action == 'create_run':
            if not args.assistant_id:
                raise ValueError("--assistant-id é obrigatório para create_run")
            result = handler.create_run(args.thread_id, args.assistant_id, args.instructions)
            
        elif args.action == 'check_run':
            if not args.run_id:
                raise ValueError("--run-id é obrigatório para check_run")
            result = handler.check_run_status(args.thread_id, args.run_id)
            
        elif args.action == 'get_response':
            result = handler.get_final_response(args.thread_id)
        
        # Output no formato Kestra
        if result and result.get('success'):
            # Remove campos desnecessários e formata para Kestra
            kestra_output = {}
            
            if args.action == 'add_message':
                kestra_output = {
                    "message_id": result["message_id"],
                    "status": "success"
                }
            elif args.action == 'create_run':
                kestra_output = {
                    "run_id": result["run_id"],
                    "status": result["status"],
                    "success": "true"
                }
            elif args.action == 'check_run':
                kestra_output = {
                    "status": result["status"],
                    "completed_at": result.get("completed_at"),
                    "last_error": result.get("last_error"),
                    "tool_calls": result.get("tool_calls", [])
                }
            elif args.action == 'get_response':
                kestra_output = {
                    "final_response": result["final_response"],
                    "message_id": result["message_id"],
                    "status": "success"
                }
            
            print(f'::kestra::outputs::{json.dumps(kestra_output)}::')
        else:
            error_msg = result.get('error', 'Erro desconhecido') if result else 'Nenhum resultado'
            print(f'::kestra::outputs::{{"status": "error", "error": "{error_msg}"}}::')
            sys.exit(1)
            
    except Exception as e:
        print(f'::kestra::outputs::{{"status": "error", "error": "{str(e)}"}}::')
        sys.exit(1)

if __name__ == "__main__":
    main() 