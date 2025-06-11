#!/usr/bin/env python3
import base64
import json

# JWT fornecido
jwt = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImprbXF0d29yenZycGJucmVubHlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkyMjkzNjgsImV4cCI6MjA2NDgwNTM2OH0.t2wYbTf0qbBmFnTKO-kcHF3PG2ovVMgXuvw_kzFJGus'

# Decodificar payload do JWT
payload = jwt.split('.')[1]
payload += '=' * (4 - len(payload) % 4)  # Adicionar padding
decoded = json.loads(base64.b64decode(payload))

# Extrair informações
ref = decoded['ref']
url = f'https://{ref}.supabase.co'

print(f"🔍 Informações extraídas do JWT:")
print(f"📍 Ref: {ref}")
print(f"🌐 URL: {url}")
print(f"🔑 Role: {decoded['role']}")

# Preparar novo .env
anon_key = jwt

print(f"\n✅ Credenciais do Supabase:")
print(f"SUPABASE_URL={url}")
print(f"SUPABASE_ANON_KEY={anon_key}") 