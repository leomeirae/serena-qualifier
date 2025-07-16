#!/usr/bin/env python3
"""
Upload Script Files to Kestra Namespace Files Storage

This script uploads the required script files to the Kestra namespace files storage
so they can be accessed by the 2_ai_conversation_flow workflow using the read() function.
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
    files_to_upload = {
        'scripts/ai_conversation_handler.py': 'scripts/ai_conversation_handler.py',
        'scripts/location_extractor.py': 'scripts/location_extractor.py',
        'scripts/conversation_context.py': 'scripts/conversation_context.py',
        'scripts/serena_api.py': 'scripts/serena_api.py',
        'scripts/save_lead_to_supabase.py': 'scripts/save_lead_to_supabase.py'
    }
    
    success_count = 0
    total_files = len(files_to_upload)
    
    logger.info(f"🚀 Starting upload of {total_files} files to Kestra namespace files storage...")
    
    for local_path, namespace_path in files_to_upload.items():
        if os.path.exists(local_path):
            if upload_file_to_namespace(local_path, namespace_path, kestra_url):
                success_count += 1
        else:
            logger.warning(f"⚠️ File not found: {local_path}")
    
    logger.info(f"📊 Upload completed: {success_count}/{total_files} files uploaded successfully")
    
    if success_count == total_files:
        logger.info("🎉 All files uploaded successfully! The 2_ai_conversation_flow workflow should now work.")
        return True
    else:
        logger.error("❌ Some files failed to upload. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 