[byterover-mcp]

# important 
always use byterover-retrive-knowledge tool to get the related context before any tasks 
always use byterover-store-knowledge to store all the critical informations after sucessful tasks

Linguagem e estrutura: O código deve ser em Python 3.12, seguindo a estrutura app/ definida no módulo modificado. Utilizar indentação de 4 espaços e nomes de variáveis em snake_case

docs.trae.ai
.

Integração com MCP: Todas as chamadas a serviços externos devem usar o protocolo JSON‑RPC via MCP; não criar endpoints REST sem necessidade. Manter os wrappers em mcp_clients.py e reutilizar funções existentes.

Fluxo de conversação: Respeitar o roteiro do agente Sílvia: saudar o lead, buscar planos via MCP Serena, oferecer o melhor plano, pedir confirmação, só então solicitar foto da conta de energia e gravá‑la no Supabase; não apressar a solicitação de documentos.

Persistência e logs: Gravar interações no Supabase e/ou nas tabelas existentes; não alterar diretamente a estrutura do banco sem aprovação.

Frameworks e dependências: Usar apenas as bibliotecas listadas em requirements.txt (FastAPI, LangChain, openai, supabase, requests); evitar introduzir novos frameworks sem justificar.

Segurança: Nunca registrar chaves de API em arquivos; acessar variáveis de ambiente via config.py e .env.