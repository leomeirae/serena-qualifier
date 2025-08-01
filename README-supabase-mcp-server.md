# 🚀 Supabase MCP Server - Deploy no Coolify

Este repositório contém a configuração completa para deploy do **Supabase MCP Server** no Coolify, permitindo que agentes de IA acessem e gerenciem projetos Supabase através do Model Context Protocol (MCP).

## 🌐 **Servidor Ativo**

**URL do Servidor**: http://hwg4ks4ooooc04wsosookoog.157.180.32.249.sslip.io/

### 📡 **Endpoints Disponíveis**

- **Root**: `GET /` - Informações do servidor
- **Health**: `GET /health` - Verificação de saúde
- **Status**: `GET /status` - Status detalhado
- **Test**: `GET /test` e `POST /test` - Testes de conectividade
- **MCP**: `POST /mcp` - **Endpoint principal para agentes de IA**

## 🛠️ **Tools Disponíveis para Agentes de IA**

### 🗄️ **Database Tools**

#### `list_tables`
Lista todas as tabelas no banco de dados.
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "list_tables",
    "arguments": {
      "schemas": ["public"]
    }
  }
}
```

#### `execute_sql`
Executa SQL raw no banco de dados.
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "execute_sql",
    "arguments": {
      "query": "SELECT * FROM leads WHERE phone_number = '5511999999999'"
    }
  }
}
```

#### `apply_migration`
Aplica migrações DDL no banco.
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "apply_migration",
    "arguments": {
      "name": "create_new_table",
      "query": "CREATE TABLE new_table (id SERIAL PRIMARY KEY, name VARCHAR(255))"
    }
  }
}
```

### 📊 **Gestão de Leads (Tabela: `leads`)**

#### Consultar Leads
```sql
-- Buscar lead por telefone
SELECT * FROM leads WHERE phone_number = '5511999999999';

-- Buscar leads por cidade
SELECT * FROM leads WHERE city = 'São Paulo';

-- Buscar leads qualificados
SELECT * FROM leads WHERE qualification_status = 'QUALIFIED';
```

#### Inserir/Atualizar Lead
```sql
-- Inserir novo lead
INSERT INTO leads (phone_number, name, city, state, client_type, additional_data)
VALUES ('5511999999999', 'João Silva', 'São Paulo', 'SP', 'RESIDENTIAL', '{"source": "whatsapp", "campaign": "energia"}');

-- Atualizar lead existente
UPDATE leads 
SET name = 'João Silva Santos', 
    additional_data = additional_data || '{"last_contact": "2024-01-15"}'
WHERE phone_number = '5511999999999';
```

#### Campos da Tabela `leads`:
- `id` (SERIAL PRIMARY KEY)
- `phone_number` (VARCHAR, UNIQUE)
- `name` (VARCHAR)
- `city` (VARCHAR)
- `state` (VARCHAR)
- `invoice_amount` (NUMERIC)
- `client_type` (VARCHAR)
- `qualification_status` (VARCHAR, DEFAULT 'NEW')
- `conversation_state` (VARCHAR, DEFAULT 'INITIAL')
- `additional_data` (JSONB, DEFAULT '{}')
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### 📸 **Gestão de Imagens (Tabelas: `energy_bills`, `image_metadata`)**

#### Tabela `energy_bills`:
- `id` (SERIAL PRIMARY KEY)
- `lead_id` (INTEGER, FK para leads)
- `phone` (VARCHAR)
- `image_path` (VARCHAR)
- `extracted_data` (TEXT)
- `created_at` (TIMESTAMP)

#### Tabela `image_metadata`:
- `id` (UUID PRIMARY KEY)
- `wamid` (TEXT, UNIQUE)
- `sender_phone` (TEXT)
- `storage_path` (TEXT)
- `mime_type` (TEXT, DEFAULT 'image/jpeg')
- `file_size_kb` (INTEGER)
- `original_caption` (TEXT)
- `lead_id` (INTEGER, FK para leads)
- `processing_status` (TEXT, DEFAULT 'completed')
- `error_message` (TEXT)
- `created_at` (TIMESTAMPTZ)

### 🔍 **Debug & Monitoring**

#### `get_logs`
Obtém logs do projeto Supabase.
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "get_logs",
    "arguments": {
      "service": "api"
    }
  }
}
```

#### `get_advisors`
Obtém avisos de segurança e performance.
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "get_advisors",
    "arguments": {
      "type": "security"
    }
  }
}
```

### 📚 **Documentação**

#### `search_docs`
Busca na documentação Supabase.
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tools/call",
  "params": {
    "name": "search_docs",
    "arguments": {
      "graphql_query": "query { searchDocs(query: \"authentication\", limit: 5) { nodes { title href content } } }"
    }
  }
}
```

### ⚡ **Edge Functions**

#### `list_edge_functions`
Lista todas as edge functions.
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "tools/call",
  "params": {
    "name": "list_edge_functions",
    "arguments": {}
  }
}
```

#### `deploy_edge_function`
Deploy de nova edge function.
```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "method": "tools/call",
  "params": {
    "name": "deploy_edge_function",
    "arguments": {
      "name": "process-lead",
      "files": [
        {
          "name": "index.ts",
          "content": "Deno.serve(async (req) => { return new Response('Hello from edge function!') })"
        }
      ]
    }
  }
}
```

### 🗄️ **Storage**

#### `list_storage_buckets`
Lista buckets de storage.
```json
{
  "jsonrpc": "2.0",
  "id": 9,
  "method": "tools/call",
  "params": {
    "name": "list_storage_buckets",
    "arguments": {}
  }
}
```

## 🎯 **Casos de Uso Específicos**

### 1. **Gestão Completa de Lead**

```bash
# 1. Buscar lead existente
curl -X POST http://hwg4ks4ooooc04wsosookoog.157.180.32.249.sslip.io/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "execute_sql",
      "arguments": {
        "query": "SELECT * FROM leads WHERE phone_number = '\''5511999999999'\''"
      }
    }
  }'

# 2. Inserir novo lead se não existir
curl -X POST http://hwg4ks4ooooc04wsosookoog.157.180.32.249.sslip.io/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "execute_sql",
      "arguments": {
        "query": "INSERT INTO leads (phone_number, name, city, state, client_type, additional_data) VALUES ('\''5511999999999'\'', '\''Maria Silva'\'', '\''São Paulo'\'', '\''SP'\'', '\''RESIDENTIAL'\'', '\''{\"source\": \"whatsapp\", \"campaign\": \"energia\"}'\'') ON CONFLICT (phone_number) DO UPDATE SET name = EXCLUDED.name, updated_at = CURRENT_TIMESTAMP"
      }
    }
  }'
```

### 2. **Processamento de Imagem de Conta de Energia**

```bash
# 1. Salvar metadados da imagem
curl -X POST http://hwg4ks4ooooc04wsosookoog.157.180.32.249.sslip.io/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "execute_sql",
      "arguments": {
        "query": "INSERT INTO image_metadata (wamid, sender_phone, storage_path, mime_type, file_size_kb, original_caption, lead_id) VALUES ('\''wamid_123'\'', '\''5511999999999'\'', '\''energy_bills/2024/01/bill_123.jpg'\'', '\''image/jpeg'\'', 256, '\''Conta de energia'\'', 1)"
      }
    }
  }'

# 2. Registrar conta processada
curl -X POST http://hwg4ks4ooooc04wsosookoog.157.180.32.249.sslip.io/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "execute_sql",
      "arguments": {
        "query": "INSERT INTO energy_bills (lead_id, phone, image_path, extracted_data) VALUES (1, '\''5511999999999'\'', '\''energy_bills/2024/01/bill_123.jpg'\'', '\''{\"valor\": 150.50, \"vencimento\": \"2024-01-15\", \"consumo\": 250}\'')"
      }
    }
  }'
```

### 3. **Atualização de Dados Adicionais**

```bash
# Atualizar dados adicionais do lead
curl -X POST http://hwg4ks4ooooc04wsosookoog.157.180.32.249.sslip.io/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "execute_sql",
      "arguments": {
        "query": "UPDATE leads SET additional_data = additional_data || '\''{\"last_bill_amount\": 150.50, \"last_bill_date\": \"2024-01-15\", \"processing_status\": \"completed\"}'\''::jsonb WHERE phone_number = '\''5511999999999'\''"
      }
    }
  }'
```

## 🔧 **Configuração Técnica**

### **Variáveis de Ambiente (Coolify)**

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `SUPABASE_ACCESS_TOKEN` | Token de acesso Supabase | `sbp_...` |
| `PROJECT_REF` | Referência do projeto | `ynyvrnasvcxyvjzhzbwf` |
| `FEATURES` | Features habilitadas | `database,docs,functions,storage,debug,development` |
| `PORT` | Porta do servidor | `45678` |

### **Features Habilitadas**
- ✅ `database` - Acesso completo ao banco de dados
- ✅ `docs` - Busca na documentação
- ✅ `functions` - Deploy de edge functions
- ✅ `storage` - Gerenciamento de storage
- ✅ `debug` - Logs e debugging
- ✅ `development` - Ferramentas de desenvolvimento

### **Configuração de Porta**
- **Interna**: 45678 (container)
- **Externa**: Gerenciada automaticamente pelo Coolify
- **Acesso**: Via proxy reverso do Coolify (sem configuração manual de porta)

## 🚀 **Deploy no Coolify**

### **Pré-requisitos**
1. Conta no Coolify
2. Projeto Supabase ativo
3. Personal Access Token (PAT) do Supabase
4. Repositório Git configurado

### **Passos para Deploy**
1. **Clone o repositório** no Coolify
2. **Configure as variáveis de ambiente**:
   - `SUPABASE_ACCESS_TOKEN`: Seu PAT do Supabase
   - `PROJECT_REF`: ID do seu projeto Supabase
   - `FEATURES`: `database,docs,functions,storage,debug,development`
3. **Deploy automático** via Coolify

### **Verificação do Deploy**
```bash
# Testar conectividade
curl http://hwg4ks4ooooc04wsosookoog.157.180.32.249.sslip.io/health

# Testar endpoint MCP
curl -X POST http://hwg4ks4ooooc04wsosookoog.157.180.32.249.sslip.io/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'
```

## 🔒 **Segurança**

### **⚠️ Avisos Importantes**
- **Modo Write**: Este servidor está configurado para **acesso completo** (não read-only)
- **Permissões**: O agente de IA terá acesso total ao banco de dados
- **Monitoramento**: Recomenda-se monitorar logs regularmente
- **Backup**: Mantenha backups regulares do banco de dados

### **Recomendações de Segurança**
1. **Use RLS (Row Level Security)** no Supabase
2. **Monitore logs** regularmente
3. **Configure alertas** para operações críticas
4. **Mantenha tokens seguros** e rotacione periodicamente

## 🐛 **Troubleshooting**

### **Problemas Comuns**

#### **"Bad Gateway" no endpoint /mcp**
- Verifique se as variáveis de ambiente estão configuradas
- Confirme se o projeto Supabase está ativo
- Verifique logs do container no Coolify

#### **"Unknown method"**
- Use métodos válidos: `tools/list`, `tools/call`
- Verifique a sintaxe JSON-RPC 2.0

#### **Erro de conexão com banco**
- Confirme se o `PROJECT_REF` está correto
- Verifique se o `SUPABASE_ACCESS_TOKEN` é válido
- Teste conectividade com o projeto Supabase

### **Logs Úteis**
```bash
# Verificar status do servidor
curl http://hwg4ks4ooooc04wsosookoog.157.180.32.249.sslip.io/status

# Testar conectividade básica
curl http://hwg4ks4ooooc04wsosookoog.157.180.32.249.sslip.io/test
```

## 📞 **Suporte**

Para suporte técnico ou dúvidas sobre o uso do MCP Server:

1. **Verifique os logs** do container no Coolify
2. **Teste os endpoints** de diagnóstico
3. **Consulte a documentação** Supabase
4. **Use as tools de debug** disponíveis

---

**🎉 O Supabase MCP Server está funcionando plenamente e pronto para uso com agentes de IA!** 