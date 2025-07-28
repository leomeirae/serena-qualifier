#!/usr/bin/env python3
"""
Upload Script Files to Kestra Namespace Files Storage

This script uploads the required script files to the Kestra namespace files storage
so they can be accessed by the AI conversation workflows using the read() function.

Atualizado: Inclui todos os scripts necessários para o workflow 3_ai_conversation_optimized.yml
e scripts de suporte que podem ser usados indiretamente.

Última atualização: Refatoração de segredos KESTRA_SECRETS_* e centralização de conexão DB
"""

import os
import requests
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_file_to_namespace(file_path: str, namespace_path: str, kestra_url: str) -> bool:
    """
    Upload a file to Kestra namespace files storage.
    
    Args:
        file_path: Local path to the file
        namespace_path: Path in the namespace files storage
        kestra_url: Base URL of the Kestra API
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the file content
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Prepare the multipart form data
        files = {
            'fileContent': (namespace_path, file_content, 'application/octet-stream')
        }
        
        # Upload to Kestra API
        upload_url = f"{kestra_url}/namespaces/serena.production/files"
        params = {'path': namespace_path}
        
        response = requests.post(upload_url, files=files, params=params)
        
        if response.status_code in [200, 201]:
            logger.info(f"✅ Successfully uploaded {namespace_path}")
            return True
        else:
            logger.error(f"❌ Failed to upload {namespace_path}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error uploading {namespace_path}: {str(e)}")
        return False

def main():
    """Main function to upload all script files."""
    # Kestra API URL (external access)
    kestra_url = "https://kestra.darwinai.com.br/api/v1"
    
    # Files to upload (local path -> namespace path)
    # Organizados por categoria e prioridade de uso
    files_to_upload = {
        # ========================================
        # SCRIPTS ESSENCIAIS PARA O WORKFLOW 3_ai_conversation_optimized.yml
        # ========================================
        
        # Scripts do Agente Sílvia (USADOS DIRETAMENTE pelo workflow)
        'scripts/agent_orchestrator.py': 'scripts/agent_orchestrator.py',
        'scripts/agent_tools/knowledge_base_tool.py': 'scripts/agent_tools/knowledge_base_tool.py',
        'scripts/agent_tools/faq_data.py': 'scripts/agent_tools/faq_data.py',
        'scripts/agent_tools/serena_tools.py': 'scripts/agent_tools/serena_tools.py',
        'scripts/agent_tools/supabase_agent_tools.py': 'scripts/agent_tools/supabase_agent_tools.py',
        'scripts/serena_api.py': 'scripts/serena_api.py',
        'scripts/lead_data_utils.py': 'scripts/lead_data_utils.py',
        'scripts/__init__.py': 'scripts/__init__.py',
        'scripts/agent_tools/__init__.py': 'scripts/agent_tools/__init__.py',
        
        # ========================================
        # SCRIPTS DE COMUNICAÇÃO E INTEGRAÇÃO
        # ========================================
        
        # Scripts Essenciais para Comunicação WhatsApp
        'scripts/send_whatsapp_template.py': 'scripts/send_whatsapp_template.py',
        'scripts/webhook_service.py': 'scripts/webhook_service.py',
        
        # ========================================
        # SCRIPTS DE SUPORTE E UTILITÁRIOS
        # ========================================
        
        # Scripts de suporte que podem ser usados indiretamente
        'scripts/interaction_logger.py': 'scripts/interaction_logger.py',
        'scripts/conversational_memory.py': 'scripts/conversational_memory.py',
        'scripts/followup.py': 'scripts/followup.py',
        'scripts/energy_bill_processor.py': 'scripts/energy_bill_processor.py',
        'scripts/agent_tools/feedback_request.py': 'scripts/agent_tools/feedback_request.py',
        
        # ========================================
        # SCRIPTS SQL E CONFIGURAÇÃO
        # ========================================
        
        # Scripts SQL para criação de tabelas (útil para referência)
        'scripts/create_image_metadata_table.sql': 'scripts/create_image_metadata_table.sql',
        'scripts/remove_conversation_states.sql': 'scripts/remove_conversation_states.sql',
    }
    
    success_count = 0
    total_files = len(files_to_upload)
    
    logger.info(f"🚀 Starting upload of {total_files} files to Kestra namespace...")
    logger.info(f"📁 Target namespace: serena.production")
    logger.info(f"🌐 Kestra API URL: {kestra_url}")
    
    # Contadores por categoria
    essential_count = 0
    communication_count = 0
    support_count = 0
    sql_count = 0
    
    for local_path, namespace_path in files_to_upload.items():
        if os.path.exists(local_path):
            if upload_file_to_namespace(local_path, namespace_path, kestra_url):
                success_count += 1
                # Contar por categoria
                if 'agent_orchestrator' in local_path or 'agent_tools' in local_path or 'serena_api' in local_path or 'lead_data_utils' in local_path:
                    essential_count += 1
                elif 'whatsapp' in local_path or 'webhook' in local_path:
                    communication_count += 1
                elif '.sql' in local_path:
                    sql_count += 1
                else:
                    support_count += 1
        else:
            logger.warning(f"⚠️ File not found: {local_path}")
    
    # Relatório detalhado
    logger.info(f"📊 Upload completed: {success_count}/{total_files} files uploaded successfully")
    logger.info(f"   🔧 Essential scripts: {essential_count}")
    logger.info(f"   📡 Communication scripts: {communication_count}")
    logger.info(f"   🛠️ Support scripts: {support_count}")
    logger.info(f"   🗄️ SQL scripts: {sql_count}")
    
    if success_count == total_files:
        logger.info("🎉 All necessary files are now in the Kestra namespace.")
        logger.info("✅ The AI conversation workflow should work correctly.")
        return True
    else:
        logger.error("❌ Some files failed to upload. The agent may not work correctly.")
        logger.error("🔍 Check the logs above for specific failures.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 