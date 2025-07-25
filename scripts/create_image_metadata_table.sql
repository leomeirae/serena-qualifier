-- Criação da tabela image_metadata conforme documento técnico
-- Execute este SQL no Supabase SQL Editor

CREATE TABLE IF NOT EXISTS image_metadata (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    wamid TEXT UNIQUE NOT NULL,
    sender_phone TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    mime_type TEXT DEFAULT 'image/jpeg',
    file_size_kb INTEGER,
    original_caption TEXT,
    lead_id INTEGER REFERENCES leads(id),
    processing_status TEXT DEFAULT 'completed',
    error_message TEXT
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_image_metadata_sender_phone ON image_metadata(sender_phone);
CREATE INDEX IF NOT EXISTS idx_image_metadata_lead_id ON image_metadata(lead_id);
CREATE INDEX IF NOT EXISTS idx_image_metadata_created_at ON image_metadata(created_at);

-- Comentários para documentação
COMMENT ON TABLE image_metadata IS 'Metadados de imagens processadas do WhatsApp';
COMMENT ON COLUMN image_metadata.wamid IS 'ID único da mensagem do WhatsApp (WAMID)';
COMMENT ON COLUMN image_metadata.storage_path IS 'Caminho do arquivo no Supabase Storage';
COMMENT ON COLUMN image_metadata.processing_status IS 'Status do processamento: completed, failed, processing'; 