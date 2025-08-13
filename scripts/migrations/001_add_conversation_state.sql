-- Migration: Add conversation state and messaging tables
-- Author: Serena SDR System
-- Date: 2025-01-20

-- NOTA: A tabela leads já possui conversation_state
-- NOTA: As tabelas image_metadata e energy_bills já existem para gerenciar imagens

-- Create lead_messages table for conversation history
CREATE TABLE IF NOT EXISTS lead_messages (
  id SERIAL PRIMARY KEY,
  phone_number VARCHAR NOT NULL,
  message_direction TEXT NOT NULL CHECK (message_direction IN ('user', 'bot')),
  message_content TEXT NOT NULL,
  message_type TEXT DEFAULT 'text',
  media_id TEXT,
  timestamp TIMESTAMP DEFAULT NOW(),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_lead_messages_phone ON lead_messages(phone_number);
CREATE INDEX IF NOT EXISTS idx_lead_messages_timestamp ON lead_messages(timestamp DESC);

-- Create follow_up_queue table
CREATE TABLE IF NOT EXISTS follow_up_queue (
  id SERIAL PRIMARY KEY,
  phone_number VARCHAR NOT NULL,
  scheduled_at TIMESTAMP NOT NULL,
  status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'SENT', 'CANCELLED')),
  follow_up_type TEXT DEFAULT 'NO_RESPONSE',
  message_template TEXT,
  attempts INT DEFAULT 0,
  last_attempt_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for follow-up queries
CREATE INDEX IF NOT EXISTS idx_follow_up_queue_status ON follow_up_queue(status);
CREATE INDEX IF NOT EXISTS idx_follow_up_queue_scheduled ON follow_up_queue(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_follow_up_queue_phone ON follow_up_queue(phone_number);

-- Add conversation metrics to leads table
ALTER TABLE leads
ADD COLUMN IF NOT EXISTS last_message_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS total_messages INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS qualification_score FLOAT,
ADD COLUMN IF NOT EXISTS ai_notes TEXT;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for follow_up_queue
CREATE TRIGGER update_follow_up_queue_updated_at BEFORE UPDATE
ON follow_up_queue FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
