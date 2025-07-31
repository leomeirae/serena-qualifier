# Guia de Integração MCP Supabase - Serena Qualifier

## Visão Geral

Este documento descreve a integração do **MCP Server Supabase** com o projeto **Serena Qualifier**, permitindo uma comunicação padronizada e mais robusta com o banco de dados Supabase.

## O que é MCP?

**MCP (Model Context Protocol)** é um protocolo padronizado para comunicação entre agentes de IA e serviços externos. No contexto do Supabase, o MCP Server oferece:

- **Comunicação padronizada** via JSON-RPC
- **Gestão de branches** de desenvolvimento
- **Operações de banco** simplificadas
- **Monitoramento** e debugging integrados
- **Edge Functions** deployment

## Arquitetura da Integração

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Agent Silvia  │───▶│  MCP Integration │───▶│  MCP Server     │
│   (LangChain)   │    │   (Python)       │    │   (HTTP)        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Direct PostgreSQL│    │   Supabase      │
                       │   (Fallback)     │    │   Database      │
                       └──────────────────┘    └─────────────────┘
```

## Configuração do MCP Server

### URL do Servidor
```
http://egkccc8ow4ww4kw40gokgkw0.157.180.32.249.sslip.io/
```

### Endpoints Disponíveis
- `GET /` - Informações básicas do servidor
- `GET /health` - Verificação de saúde
- `GET /status` - Status detalhado
- `GET /test` - Teste de conectividade
- `POST /mcp` - Endpoint principal para comunicação MCP

## Implementação no Projeto

### 1. Módulo de Integração MCP

**Arquivo**: `scripts/agent_tools/mcp_supabase_integration.py`

#### Classe Principal: `MCPSupabaseClient`
```python
class MCPSupabaseClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or "http://egkccc8ow4ww4kw40gokgkw0.157.180.32.249.sslip.io"
        self.mcp_endpoint = f"{self.base_url}/mcp"
    
    def execute_sql(self, query: str) -> List[Dict[str, Any]]:
        """Executa query SQL via MCP Server"""
    
    def list_tables(self, schemas: List[str] = None) -> List[Dict[str, Any]]:
        """Lista tabelas do banco via MCP Server"""
```

#### Ferramentas Disponíveis

##### `consultar_dados_lead_mcp(phone_number: str)`
- **Função**: Consulta dados de lead via MCP
- **Parâmetros**: Número de telefone
- **Retorno**: Dados do lead em JSON
- **Fallback**: Busca em múltiplos formatos de telefone

##### `salvar_ou_atualizar_lead_mcp(dados_lead: str)`
- **Função**: Salva/atualiza lead via MCP
- **Parâmetros**: Dados do lead em JSON
- **Retorno**: Resultado da operação
- **Operação**: UPSERT com timestamp

##### `listar_tabelas_mcp()`
- **Função**: Lista tabelas do banco
- **Retorno**: Lista de tabelas em JSON
- **Uso**: Debugging e monitoramento

##### `verificar_status_mcp()`
- **Função**: Verifica status do MCP Server
- **Retorno**: Status online/offline
- **Uso**: Monitoramento de saúde

### 2. Integração no Agent Orchestrator

**Arquivo**: `scripts/agent_orchestrator.py`

#### Detecção Automática
```python
try:
    from scripts.agent_tools.mcp_supabase_integration import (
        consultar_dados_lead_mcp,
        salvar_ou_atualizar_lead_mcp,
        listar_tabelas_mcp,
        verificar_status_mcp
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
```

#### Seleção Dinâmica de Ferramentas
```python
if MCP_AVAILABLE:
    tools = [
        consultar_dados_lead_mcp,  # MCP version
        salvar_ou_atualizar_lead_mcp,  # MCP version
        listar_tabelas_mcp,  # Nova ferramenta MCP
        verificar_status_mcp  # Nova ferramenta MCP
    ]
else:
    tools = [
        consultar_dados_lead,  # Direct PostgreSQL
        salvar_ou_atualizar_lead_silvia  # Direct PostgreSQL
    ]
```

### 3. Workflow de Teste

**Arquivo**: `kestra/workflows/4_mcp_integration_test.yml`

#### Funcionalidades do Workflow
- **Verificação de Status**: Testa conectividade com MCP Server
- **Teste de Query**: Valida operações de banco via MCP
- **Fallback Testing**: Testa conexão direta PostgreSQL
- **Logging**: Registra sucessos e erros
- **Monitoramento**: Execução automática a cada 6 horas

## Vantagens da Integração MCP

### 1. **Padronização**
- Protocolo JSON-RPC padronizado
- Interface consistente para todas as operações
- Facilita integração com outros sistemas

### 2. **Robustez**
- Fallback automático para conexão direta
- Detecção de disponibilidade do servidor
- Tratamento de erros centralizado

### 3. **Monitoramento**
- Status em tempo real do servidor
- Logs detalhados de operações
- Métricas de performance

### 4. **Escalabilidade**
- Suporte a múltiplos ambientes
- Gestão de branches de desenvolvimento
- Deploy de Edge Functions

### 5. **Segurança**
- Autenticação centralizada
- Controle de acesso granular
- Auditoria de operações

## Comparação: MCP vs Conexão Direta

| Aspecto | MCP Server | Conexão Direta |
|---------|------------|----------------|
| **Padronização** | ✅ JSON-RPC | ❌ Custom |
| **Monitoramento** | ✅ Integrado | ❌ Manual |
| **Fallback** | ✅ Automático | ❌ Não aplicável |
| **Performance** | ⚠️ Overhead HTTP | ✅ Direto |
| **Segurança** | ✅ Centralizada | ⚠️ Distribuída |
| **Manutenção** | ✅ Simplificada | ❌ Complexa |

## Configuração de Ambiente

### Variáveis de Ambiente
```bash
# MCP Server (opcional - usa URL padrão se não definida)
MCP_SERVER_URL=http://egkccc8ow4ww4kw40gokgkw0.157.180.32.249.sslip.io

# Fallback PostgreSQL (mantida para compatibilidade)
SECRET_DB_CONNECTION_STRING=<base64_encoded_connection_string>
```

### Dependências Python
```python
# MCP Integration
requests>=2.31.0

# Fallback (já existente)
psycopg2-binary>=2.9.0
```

## Troubleshooting

### Problemas Comuns

#### 1. MCP Server Offline
**Sintoma**: `MCP_AVAILABLE = False`
**Solução**: 
- Verificar conectividade de rede
- Confirmar URL do servidor
- Verificar logs do MCP Server

#### 2. Erro de Query MCP
**Sintoma**: `mcp_query_success = False`
**Solução**:
- Verificar sintaxe SQL
- Confirmar permissões no Supabase
- Verificar logs do MCP Server

#### 3. Fallback para Conexão Direta
**Sintoma**: Uso de ferramentas PostgreSQL diretas
**Solução**:
- Verificar `SECRET_DB_CONNECTION_STRING`
- Confirmar conectividade com Supabase
- Verificar logs de erro

### Logs e Debugging

#### Logs do Agent
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Using MCP Supabase integration")
logger.error("MCP Server error: %s", error)
```

#### Logs do Workflow
- **Sucesso**: `log-mcp-success`
- **Erro**: `log-mcp-error`
- **Status Geral**: `log-overall-status`

## Roadmap de Melhorias

### Fase 1: Estabilização ✅
- [x] Implementação básica MCP
- [x] Fallback para conexão direta
- [x] Workflow de teste
- [x] Documentação

### Fase 2: Otimização 🔄
- [ ] Cache de consultas frequentes
- [ ] Pool de conexões MCP
- [ ] Métricas de performance
- [ ] Alertas automáticos

### Fase 3: Expansão 📋
- [ ] Suporte a Edge Functions
- [ ] Gestão de branches
- [ ] Migrações automáticas
- [ ] Backup e restore

## Conclusão

A integração MCP Supabase representa um avanço significativo na arquitetura do projeto Serena Qualifier, oferecendo:

1. **Maior robustez** com fallback automático
2. **Melhor monitoramento** com logs centralizados
3. **Padronização** via protocolo JSON-RPC
4. **Escalabilidade** para futuras expansões

A implementação mantém compatibilidade total com o sistema existente, permitindo uma migração gradual e segura.

---

**Última atualização**: 30/01/2025  
**Versão**: 1.0.0  
**Autor**: Serena-Coder AI Agent 