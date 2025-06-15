"""
Configuração global para testes pytest.
Garante carregamento das variáveis de ambiente .env.
"""
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Carrega variáveis de ambiente do .env
try:
    from dotenv import load_dotenv
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Variáveis .env carregadas de: {env_path}")
    else:
        print(f"⚠️  Arquivo .env não encontrado em: {env_path}")
except ImportError:
    print("⚠️  python-dotenv não instalado, variáveis .env não carregadas")

# Verifica variáveis críticas
critical_vars = [
    'SUPABASE_URL', 
    'SUPABASE_ANON_KEY', 
    'OPENAI_API_KEY',
    'WHATSAPP_API_TOKEN',
    'SERENA_API_TOKEN'
]

missing_vars = []
for var in critical_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f"⚠️  Variáveis de ambiente ausentes: {missing_vars}")
else:
    print("✅ Todas as variáveis críticas estão carregadas") 