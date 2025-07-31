#!/usr/bin/env python3
"""
Script de teste para integração do Serena SDR Agent no projeto existente
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mcp_connectivity():
    """Testa conectividade com os MCPs"""
    logger.info("🧪 Testando conectividade com MCPs...")
    
    mcp_servers = {
        "supabase": "http://localhost:3001",
        "serena": "http://localhost:3002", 
        "whatsapp": "http://localhost:3003"
    }
    
    results = {}
    
    for name, url in mcp_servers.items():
        try:
            # Teste de health check
            if name == "serena":
                health_url = f"{url}/"
            else:
                health_url = f"{url}/health"
                
            response = requests.get(health_url, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ {name.upper()} MCP: Conectado")
                results[name] = "OK"
            else:
                logger.warning(f"⚠️ {name.upper()} MCP: Status {response.status_code}")
                results[name] = f"Status {response.status_code}"
                
        except Exception as e:
            logger.error(f"❌ {name.upper()} MCP: Erro - {str(e)}")
            results[name] = f"Erro: {str(e)}"
    
    return results

def test_kestra_workflow():
    """Testa o workflow do SDR no Kestra"""
    logger.info("🧪 Testando workflow SDR no Kestra...")
    
    try:
        # URL do Kestra
        kestra_url = "https://kestra.darwinai.com.br"
        
        # Teste de health check do Kestra
        response = requests.get(f"{kestra_url}/api/v1/health", timeout=10)
        if response.status_code == 200:
            logger.info("✅ Kestra: Conectado")
        else:
            logger.warning(f"⚠️ Kestra: Status {response.status_code}")
            return False
            
        # Teste do webhook do SDR
        webhook_url = f"{kestra_url}/api/v1/main/executions/serena.production/2_sdr_conversation_flow"
        
        test_payload = {
            "phone": "+5581997498268",
            "message": "Olá, gostaria de saber mais sobre energia solar",
            "type": "text",
            "lead_id": "test_lead_001"
        }
        
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code in [200, 201, 202]:
            logger.info("✅ Workflow SDR: Executado com sucesso")
            execution_data = response.json()
            execution_id = execution_data.get('id')
            logger.info(f"📋 Execution ID: {execution_id}")
            return True
        else:
            logger.error(f"❌ Workflow SDR: Erro {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao testar Kestra: {str(e)}")
        return False

def test_scripts_import():
    """Testa se os scripts do SDR podem ser importados"""
    logger.info("🧪 Testando importação dos scripts SDR...")
    
    try:
        # Adicionar scripts ao path
        scripts_path = os.path.join(os.path.dirname(__file__), 'scripts')
        sys.path.insert(0, scripts_path)
        
        # Testar imports
        from ai_sdr_agent import SerenaSDRAgent
        from follow_up_agent import FollowUpAgent
        from utils.config import SDRConfig
        from utils.logger import SDRLogger
        from agent_tools.supabase_tools import SupabaseTools
        from agent_tools.serena_tools import SerenaTools
        from agent_tools.whatsapp_tools import WhatsAppTools
        
        logger.info("✅ Scripts SDR: Imports funcionando")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao importar scripts SDR: {str(e)}")
        return False

def main():
    """Função principal de teste"""
    logger.info("🚀 Iniciando testes de integração do Serena SDR Agent")
    logger.info("=" * 60)
    
    # Teste 1: Conectividade MCP
    mcp_results = test_mcp_connectivity()
    
    # Teste 2: Scripts
    scripts_ok = test_scripts_import()
    
    # Teste 3: Kestra Workflow
    kestra_ok = test_kestra_workflow()
    
    # Resumo
    logger.info("=" * 60)
    logger.info("📊 RESUMO DOS TESTES")
    logger.info("=" * 60)
    
    logger.info("MCP Servers:")
    for name, status in mcp_results.items():
        status_icon = "✅" if status == "OK" else "❌"
        logger.info(f"  {status_icon} {name.upper()}: {status}")
    
    logger.info(f"\nScripts SDR: {'✅ OK' if scripts_ok else '❌ ERRO'}")
    logger.info(f"Kestra Workflow: {'✅ OK' if kestra_ok else '❌ ERRO'}")
    
    # Verificação final
    all_mcps_ok = all(status == "OK" for status in mcp_results.values())
    
    if all_mcps_ok and scripts_ok and kestra_ok:
        logger.info("\n🎉 TODOS OS TESTES PASSARAM! SDR Agent integrado com sucesso!")
        return True
    else:
        logger.error("\n⚠️ ALGUNS TESTES FALHARAM. Verifique os logs acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
