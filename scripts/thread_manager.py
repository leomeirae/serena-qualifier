#!/usr/bin/env python3
"""
OpenAI Threads Manager with Supabase Integration for Serena Energia Lead Qualification System

This module manages OpenAI Thread creation, retrieval, and persistence using Supabase
as the storage backend. It ensures each lead (identified by phone_number) has a 
persistent thread for conversation continuity across multiple interactions.

Key Features:
- Thread-per-lead mapping via new Supabase table 'conversation_threads'
- Automatic thread creation for new leads
- Thread persistence and retrieval
- Integration with existing ConversationManager and leads table
- Compatible with existing conversation_history table

Author: Serena-Coder AI Agent
Version: 1.0.0
Created: 2025-01-17
Based on: Existing Supabase structure analysis (leads, conversation_history, disqualified_leads)
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from openai import OpenAI
from openai.types.beta import Thread
from supabase import create_client, Client
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ThreadManager:
    """
    Manager class for OpenAI Threads with Supabase persistence.
    
    Handles the creation, retrieval, and management of OpenAI conversation threads
    for leads in the Serena Energy qualification system. Uses Supabase to maintain
    the mapping between phone numbers and thread IDs for conversation continuity.
    
    Database Integration:
    - Uses existing 'leads' table for lead data
    - Uses existing 'conversation_history' table for message history
    - Creates new 'conversation_threads' table for thread mapping
    """
    
    def __init__(self):
        """Initialize the ThreadManager with OpenAI and Supabase clients."""
        # OpenAI API setup
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        # Supabase setup
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Table names (based on existing Supabase structure)
        self.threads_table = 'conversation_threads'  # New table for thread mapping
        self.leads_table = 'leads'  # Existing table
        self.history_table = 'conversation_history'  # Existing table
        
        # Ensure threads table exists
        self._ensure_threads_table()
        
    def _ensure_threads_table(self):
        """
        Ensure the conversation_threads table exists in Supabase.
        Creates it if it doesn't exist, compatible with existing schema.
        """
        try:
            # Check if table exists by trying to select from it
            result = self.supabase.table(self.threads_table).select('id').limit(1).execute()
            logger.info(f"Table {self.threads_table} already exists")
            
        except Exception as e:
            logger.info(f"Creating table {self.threads_table}: {e}")
            # Table doesn't exist, create it
            self._create_threads_table()
    
    def _create_threads_table(self):
        """
        Create the conversation_threads table in Supabase.
        """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS conversation_threads (
            id BIGSERIAL PRIMARY KEY,
            phone_number VARCHAR NOT NULL,
            thread_id VARCHAR NOT NULL UNIQUE,
            assistant_id VARCHAR,
            status VARCHAR DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            last_used_at TIMESTAMPTZ DEFAULT NOW(),
            metadata JSONB DEFAULT '{}',
            
            -- Index for fast lookups
            CONSTRAINT unique_active_thread_per_phone 
                EXCLUDE (phone_number WITH =) 
                WHERE (status = 'active')
        );
        
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_conversation_threads_phone 
            ON conversation_threads(phone_number);
        CREATE INDEX IF NOT EXISTS idx_conversation_threads_thread_id 
            ON conversation_threads(thread_id);
        CREATE INDEX IF NOT EXISTS idx_conversation_threads_status 
            ON conversation_threads(status);
            
        -- Comments for documentation
        COMMENT ON TABLE conversation_threads IS 
            'Maps phone numbers to OpenAI thread IDs for conversation continuity';
        COMMENT ON COLUMN conversation_threads.phone_number IS 
            'Lead phone number (format: +5581999887766)';
        COMMENT ON COLUMN conversation_threads.thread_id IS 
            'OpenAI Thread ID (format: thread_xxx)';
        """
        
        try:
            # Execute table creation (Supabase handles this via SQL execution)
            result = self.supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
            logger.info("Created conversation_threads table successfully")
            
        except Exception as e:
            # Try alternative approach using migration
            logger.warning(f"Direct table creation failed: {e}")
            logger.info("Table may already exist or will be created on first use")

    def get_or_create_thread(self, phone_number: str, assistant_id: str = None) -> str:
        """
        Get existing thread ID or create a new one for the given phone number.
        
        This is the main function specified in the task requirements. It:
        1. Checks if a thread already exists for the phone_number in Supabase
        2. If yes, returns the stored thread_id (after validating it exists in OpenAI)
        3. If no, creates a new OpenAI thread and stores the mapping in Supabase
        
        Args:
            phone_number (str): The lead's phone number (+5581999887766 format)
            assistant_id (str, optional): Assistant ID for context (logging purposes)
            
        Returns:
            str: The OpenAI Thread ID
            
        Raises:
            Exception: If thread creation or retrieval fails
        """
        logger.info(f"Getting or creating thread for phone_number: {phone_number}")
        
        # Reason: Normalize phone number format for consistency
        phone_number = self._normalize_phone_number(phone_number)
        
        try:
            # Step 1: Check if thread already exists in Supabase
            existing_thread = self._get_active_thread_from_supabase(phone_number)
            
            if existing_thread:
                thread_id = existing_thread['thread_id']
                logger.info(f"Found existing thread: {thread_id}")
                
                # Validate thread still exists in OpenAI
                if self._validate_thread_exists(thread_id):
                    # Update last_used_at timestamp
                    self._update_thread_usage(thread_id)
                    logger.info(f"Thread {thread_id} validated and updated")
                    return thread_id
                else:
                    logger.warning(f"Thread {thread_id} not found in OpenAI, deactivating and creating new")
                    self._deactivate_thread_in_supabase(thread_id)
                    # Continue to create new thread
            
            # Step 2: Create new OpenAI thread
            logger.info("Creating new OpenAI thread")
            new_thread = self._create_openai_thread(phone_number, assistant_id)
            thread_id = new_thread.id
            
            # Step 3: Store thread mapping in Supabase
            self._store_thread_mapping(phone_number, thread_id, assistant_id)
            
            logger.info(f"Created and stored new thread: {thread_id} for {phone_number}")
            return thread_id
            
        except Exception as e:
            logger.error(f"Failed to get/create thread for {phone_number}: {e}")
            raise Exception(f"Thread management failed: {e}")

    def _normalize_phone_number(self, phone_number: str) -> str:
        """
        Normalize phone number to consistent format.
        
        Args:
            phone_number (str): Raw phone number
            
        Returns:
            str: Normalized phone number (+5581999887766 format)
        """
        # Remove non-digits
        digits_only = ''.join(filter(str.isdigit, phone_number))
        
        # Add +55 if not present (Brazil country code)
        if not digits_only.startswith('55'):
            digits_only = '55' + digits_only
        
        return '+' + digits_only

    def _get_active_thread_from_supabase(self, phone_number: str) -> Optional[Dict]:
        """
        Retrieve active thread mapping from Supabase by phone number.
        
        Args:
            phone_number (str): The lead's phone number
            
        Returns:
            Optional[Dict]: Thread record or None if not found
        """
        try:
            result = self.supabase.table(self.threads_table)\
                .select('*')\
                .eq('phone_number', phone_number)\
                .eq('status', 'active')\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving thread from Supabase: {e}")
            return None

    def _validate_thread_exists(self, thread_id: str) -> bool:
        """
        Validate that a thread still exists in OpenAI.
        
        Args:
            thread_id (str): The OpenAI Thread ID to validate
            
        Returns:
            bool: True if thread exists, False otherwise
        """
        try:
            thread = self.openai_client.beta.threads.retrieve(thread_id)
            return thread is not None
            
        except Exception as e:
            logger.warning(f"Thread validation failed for {thread_id}: {e}")
            return False

    def _create_openai_thread(self, phone_number: str, assistant_id: str = None) -> Thread:
        """
        Create a new OpenAI thread with metadata.
        
        Args:
            phone_number (str): Lead's phone number for metadata
            assistant_id (str, optional): Assistant ID for context
            
        Returns:
            Thread: The newly created OpenAI Thread object
        """
        try:
            # Create thread with metadata for tracking
            thread_params = {
                'metadata': {
                    'phone_number': phone_number,
                    'system': 'serena-qualifier',
                    'created_by': 'thread_manager',
                    'version': '1.0.0'
                }
            }
            
            if assistant_id:
                thread_params['metadata']['assistant_id'] = assistant_id
            
            thread = self.openai_client.beta.threads.create(**thread_params)
            logger.info(f"Created OpenAI thread: {thread.id} for {phone_number}")
            return thread
            
        except Exception as e:
            logger.error(f"Failed to create OpenAI thread: {e}")
            raise Exception(f"OpenAI thread creation failed: {e}")

    def _store_thread_mapping(self, phone_number: str, thread_id: str, assistant_id: str = None) -> bool:
        """
        Store thread mapping in Supabase conversation_threads table.
        
        Args:
            phone_number (str): The lead's phone number
            thread_id (str): The OpenAI Thread ID
            assistant_id (str, optional): Assistant ID for reference
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            thread_data = {
                'phone_number': phone_number,
                'thread_id': thread_id,
                'assistant_id': assistant_id,
                'status': 'active',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'last_used_at': datetime.utcnow().isoformat(),
                'metadata': {
                    'system': 'serena-qualifier',
                    'version': '1.0.0',
                    'integration': 'openai_assistants'
                }
            }
            
            result = self.supabase.table(self.threads_table)\
                .insert(thread_data)\
                .execute()
            
            if result.data:
                logger.info(f"Stored thread mapping: {phone_number} -> {thread_id}")
                return True
            else:
                logger.error(f"Failed to store thread mapping: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error storing thread mapping: {e}")
            return False

    def _update_thread_usage(self, thread_id: str) -> bool:
        """
        Update the last_used_at timestamp for a thread.
        
        Args:
            thread_id (str): The OpenAI Thread ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = self.supabase.table(self.threads_table)\
                .update({
                    'last_used_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                })\
                .eq('thread_id', thread_id)\
                .execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error updating thread usage: {e}")
            return False

    def _deactivate_thread_in_supabase(self, thread_id: str) -> bool:
        """
        Mark a thread as inactive in Supabase.
        
        Args:
            thread_id (str): The OpenAI Thread ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = self.supabase.table(self.threads_table)\
                .update({
                    'status': 'inactive',
                    'updated_at': datetime.utcnow().isoformat()
                })\
                .eq('thread_id', thread_id)\
                .execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error deactivating thread: {e}")
            return False

    def get_thread_info(self, thread_id: str) -> Optional[Thread]:
        """
        Get detailed information about a thread from OpenAI.
        
        Args:
            thread_id (str): The OpenAI Thread ID
            
        Returns:
            Optional[Thread]: Thread object or None if not found
        """
        try:
            thread = self.openai_client.beta.threads.retrieve(thread_id)
            return thread
            
        except Exception as e:
            logger.error(f"Error retrieving thread info: {e}")
            return None

    def list_user_threads(self, phone_number: str) -> List[Dict]:
        """
        List all threads associated with a phone number.
        
        Args:
            phone_number (str): The lead's phone number
            
        Returns:
            List[Dict]: List of thread records from Supabase
        """
        try:
            phone_number = self._normalize_phone_number(phone_number)
            
            result = self.supabase.table(self.threads_table)\
                .select('*')\
                .eq('phone_number', phone_number)\
                .order('created_at', desc=True)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error listing user threads: {e}")
            return []

    def get_lead_context(self, phone_number: str) -> Dict:
        """
        Get lead context from existing leads table for thread creation.
        
        Args:
            phone_number (str): The lead's phone number
            
        Returns:
            Dict: Lead context data or empty dict
        """
        try:
            phone_number = self._normalize_phone_number(phone_number)
            
            result = self.supabase.table(self.leads_table)\
                .select('name, city, qualification_status, conversation_state')\
                .eq('phone_number', phone_number)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting lead context: {e}")
            return {}

    def cleanup_inactive_threads(self, days_old: int = 30) -> int:
        """
        Clean up threads that haven't been used for specified days.
        
        Args:
            days_old (int): Number of days to consider a thread inactive
            
        Returns:
            int: Number of threads cleaned up
        """
        try:
            from datetime import timedelta
            
            # Calculate cutoff date
            cutoff_date = (datetime.utcnow() - timedelta(days=days_old)).isoformat()
            
            # Find inactive threads
            result = self.supabase.table(self.threads_table)\
                .select('thread_id, phone_number')\
                .eq('status', 'active')\
                .lt('last_used_at', cutoff_date)\
                .execute()
            
            cleanup_count = 0
            if result.data:
                for thread_record in result.data:
                    if self._deactivate_thread_in_supabase(thread_record['thread_id']):
                        cleanup_count += 1
            
            logger.info(f"Cleaned up {cleanup_count} inactive threads")
            return cleanup_count
            
        except Exception as e:
            logger.error(f"Error during thread cleanup: {e}")
            return 0


def main():
    """
    Main function for command-line usage.
    
    This allows the script to be run directly from Kestra workflows
    or command line for testing purposes.
    """
    parser = argparse.ArgumentParser(description='Manage OpenAI threads for Serena leads')
    parser.add_argument('--phone', required=True, help='Phone number of the lead')
    parser.add_argument('--assistant-id', help='OpenAI Assistant ID')
    parser.add_argument('--action', choices=['get', 'create', 'list', 'cleanup', 'context'], 
                       default='get', help='Action to perform')
    
    args = parser.parse_args()
    
    try:
        manager = ThreadManager()
        
        if args.action == 'get' or args.action == 'create':
            thread_id = manager.get_or_create_thread(args.phone, args.assistant_id)
            lead_context = manager.get_lead_context(args.phone)
            
            result = {
                "thread_id": thread_id,
                "phone_number": args.phone,
                "lead_context": lead_context,
                "status": "success",
                "message": f"Thread ready: {thread_id}"
            }
            
        elif args.action == 'list':
            threads = manager.list_user_threads(args.phone)
            result = {
                "threads": threads,
                "phone_number": args.phone,
                "count": len(threads),
                "status": "success"
            }
            
        elif args.action == 'cleanup':
            count = manager.cleanup_inactive_threads()
            result = {
                "cleaned_up": count,
                "status": "success",
                "message": f"Cleaned up {count} inactive threads"
            }
            
        elif args.action == 'context':
            context = manager.get_lead_context(args.phone)
            result = {
                "lead_context": context,
                "phone_number": args.phone,
                "status": "success"
            }
        
        print(json.dumps(result, indent=2))
        return result
        
    except Exception as e:
        error_result = {
            "thread_id": None,
            "phone_number": args.phone,
            "status": "error",
            "message": f"Failed to manage thread: {str(e)}"
        }
        
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 