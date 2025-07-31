#!/usr/bin/env python3
"""
Healthcheck Server for Kestra Agent

Este servidor simples responde a healthchecks do Docker e Kestra.
Mantém o container rodando e fornece informações de status.
"""

import os
import sys
import time
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Handler para healthchecks HTTP"""
    
    def do_GET(self):
        """Responde a requisições GET"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Verificar variáveis de ambiente críticas
            env_status = {
                'openai_api_key': 'OK' if os.getenv('OPENAI_API_KEY') else 'MISSING',
                'serena_api_token': 'OK' if os.getenv('SERENA_API_TOKEN') else 'MISSING',
                'whatsapp_api_token': 'OK' if os.getenv('WHATSAPP_API_TOKEN') else 'MISSING',
                'supabase_url': 'OK' if os.getenv('SUPABASE_URL') else 'MISSING',
                'redis_url': 'OK' if os.getenv('REDIS_URL') else 'MISSING',
                'mcp_urls': {
                    'supabase': 'OK' if os.getenv('SUPABASE_MCP_URL') else 'MISSING',
                    'serena': 'OK' if os.getenv('SERENA_MCP_URL') else 'MISSING',
                    'whatsapp': 'OK' if os.getenv('WHATSAPP_MCP_URL') else 'MISSING'
                }
            }
            
            response = {
                'status': 'healthy',
                'service': 'kestra-agent',
                'timestamp': time.time(),
                'environment': env_status,
                'python_path': os.getenv('PYTHONPATH', ''),
                'working_directory': os.getcwd()
            }
            
            import json
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Kestra Agent Healthcheck Server - OK\n')
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found\n')
    
    def log_message(self, format, *args):
        """Customizar logging"""
        logger.info(f"HTTP {format % args}")

def start_healthcheck_server():
    """Inicia o servidor de healthcheck"""
    try:
        port = int(os.getenv('HEALTHCHECK_PORT', '8080'))
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        
        logger.info(f"🚀 Healthcheck server iniciado na porta {port}")
        logger.info(f"📊 Endpoints disponíveis:")
        logger.info(f"   - GET /health - Status detalhado")
        logger.info(f"   - GET / - Status básico")
        
        # Log das variáveis de ambiente (sem valores sensíveis)
        logger.info(f"🔧 Variáveis de ambiente:")
        logger.info(f"   - PYTHONPATH: {os.getenv('PYTHONPATH', 'N/A')}")
        logger.info(f"   - TZ: {os.getenv('TZ', 'N/A')}")
        logger.info(f"   - SUPABASE_MCP_URL: {os.getenv('SUPABASE_MCP_URL', 'N/A')}")
        logger.info(f"   - SERENA_MCP_URL: {os.getenv('SERENA_MCP_URL', 'N/A')}")
        logger.info(f"   - WHATSAPP_MCP_URL: {os.getenv('WHATSAPP_MCP_URL', 'N/A')}")
        
        server.serve_forever()
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar healthcheck server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    logger.info("🔧 Iniciando Kestra Agent Healthcheck Server...")
    start_healthcheck_server() 