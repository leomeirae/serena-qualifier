# Coolify MCP Server

Um servidor MCP (Model Context Protocol) para interagir com sua instância Coolify self-hosted.

## Visão Geral

Este servidor MCP permite que você gerencie sua instância Coolify diretamente através de ferramentas como Cursor, Claude Desktop ou qualquer outro cliente MCP. Você pode:

- Gerenciar aplicações (listar, iniciar, parar, reiniciar, fazer deploy)
- Gerenciar bancos de dados (listar, iniciar, parar, reiniciar)
- Gerenciar serviços (listar, iniciar, parar, reiniciar)
- Gerenciar servidores (listar, validar, obter recursos)
- Gerenciar projetos (listar, criar, obter detalhes)
- Visualizar deployments e logs
- Gerenciar teams e recursos

## Instalação

### 1. Pré-requisitos

```bash
# Instale as dependências
pip install -r mcp_coolify_requirements.txt
```

### 2. Configuração

#### Opção A: Variáveis de Ambiente

```bash
export COOLIFY_BASE_URL="https://coolify.darwinai.com.br"
export COOLIFY_TOKEN="your-coolify-api-token-here"
```

#### Opção B: Configuração MCP

Edite o arquivo `coolify_mcp_config.json`:

```json
{
  "mcpServers": {
    "coolify": {
      "command": "python",
      "args": ["mcp_coolify_server.py"],
      "env": {
        "COOLIFY_BASE_URL": "https://coolify.darwinai.com.br",
        "COOLIFY_TOKEN": "YOUR_COOLIFY_TOKEN_HERE"
      }
    }
  }
}
```

### 3. Obter Token da API

1. Acesse sua instância Coolify
2. Vá para `Security` > `API Tokens`
3. Clique em `Create New Token`
4. Dê um nome ao token
5. Selecione as permissões necessárias (recomendado: `*` para acesso completo)
6. Copie o token gerado

## Uso

### Teste Local

```bash
# Teste o servidor localmente
python mcp_coolify_server.py
```

### Integração com Cursor

1. Copie o arquivo `coolify_mcp_config.json` para o diretório de configuração do Cursor
2. Ou adicione a configuração ao seu arquivo MCP existente
3. Reinicie o Cursor
4. O servidor Coolify estará disponível como `@coolify`

### Integração com Claude Desktop

Adicione ao seu arquivo `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "coolify": {
      "command": "python",
      "args": ["/caminho/para/mcp_coolify_server.py"],
      "env": {
        "COOLIFY_BASE_URL": "https://coolify.darwinai.com.br",
        "COOLIFY_TOKEN": "YOUR_COOLIFY_TOKEN_HERE"
      }
    }
  }
}
```

## Ferramentas Disponíveis

### Geral
- `coolify_version` - Obter versão do Coolify
- `coolify_health` - Verificar status de saúde
- `set_coolify_config` - Configurar URL base e token

### Aplicações
- `list_applications` - Listar todas as aplicações
- `get_application` - Obter detalhes de uma aplicação
- `start_application` - Iniciar aplicação
- `stop_application` - Parar aplicação
- `restart_application` - Reiniciar aplicação
- `delete_application` - Deletar aplicação
- `get_application_logs` - Obter logs da aplicação
- `deploy_application` - Fazer deploy da aplicação

### Bancos de Dados
- `list_databases` - Listar todos os bancos de dados
- `get_database` - Obter detalhes de um banco de dados
- `start_database` - Iniciar banco de dados
- `stop_database` - Parar banco de dados
- `restart_database` - Reiniciar banco de dados

### Serviços
- `list_services` - Listar todos os serviços
- `get_service` - Obter detalhes de um serviço
- `start_service` - Iniciar serviço
- `stop_service` - Parar serviço
- `restart_service` - Reiniciar serviço

### Servidores
- `list_servers` - Listar todos os servidores
- `get_server` - Obter detalhes de um servidor
- `get_server_resources` - Obter recursos do servidor
- `validate_server` - Validar conexão com servidor

### Projetos
- `list_projects` - Listar todos os projetos
- `get_project` - Obter detalhes de um projeto
- `create_project` - Criar novo projeto

### Deployments
- `list_deployments` - Listar todos os deployments
- `get_deployment` - Obter detalhes de um deployment

### Teams
- `list_teams` - Listar todas as teams
- `get_team` - Obter detalhes de uma team

### Recursos
- `list_resources` - Listar todos os recursos

## Exemplos de Uso

### Listar todas as aplicações
```
Use @coolify list_applications
```

### Iniciar uma aplicação específica
```
Use @coolify start_application com uuid="app-uuid-here"
```

### Obter logs de uma aplicação
```
Use @coolify get_application_logs com uuid="app-uuid-here"
```

### Criar um novo projeto
```
Use @coolify create_project com name="Meu Projeto" description="Descrição do projeto"
```

### Verificar status de saúde
```
Use @coolify coolify_health
```

## Troubleshooting

### Token inválido
- Verifique se o token foi copiado corretamente
- Verifique se o token não expirou
- Verifique se o token tem as permissões necessárias

### Erro de conexão
- Verifique se a URL base está correta
- Verifique se a instância Coolify está rodando
- Verifique se há firewall bloqueando a conexão

### Erro de permissão
- Verifique se o token tem as permissões necessárias
- Para acesso completo, use permissão `*`

## Estrutura do Projeto

```
serena-qualifier/
├── mcp_coolify_server.py         # Servidor MCP principal
├── mcp_coolify_requirements.txt  # Dependências
├── coolify_mcp_config.json       # Configuração MCP
└── COOLIFY_MCP_SERVER_README.md  # Esta documentação
```

## Contribuindo

Para contribuir com melhorias:

1. Adicione novas ferramentas ao método `list_tools()`
2. Implemente a lógica no método `call_tool()`
3. Atualize a documentação
4. Teste localmente antes de enviar

## Licença

Este projeto segue a mesma licença do projeto principal serena-qualifier. 