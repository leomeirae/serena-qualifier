# Kestra MCP Server Installation Guide

## ✅ Installation Complete!

The Kestra MCP Server has been successfully installed and configured for your serena-qualifier project.

## 📁 Installation Location

```
/Users/user/Desktop/serena-qualifier/mcp-server-python/
```

## 🔧 Configuration

### Environment Variables (.env)
```
KESTRA_TENANT_ID=main
KESTRA_BASE_URL=https://kestra.darwinai.com.br/api/v1
KESTRA_USERNAME=admin
KESTRA_PASSWORD=admin
KESTRA_MCP_DISABLED_TOOLS=ee
```

### Virtual Environment
- Python 3.13 virtual environment created at `.venv`
- All dependencies installed via `uv`

## 🚀 Usage in Cursor

### Step 1: Add MCP Configuration
1. Open Cursor
2. Go to Settings → MCP
3. Add the following configuration:

```json
{
  "mcpServers": {
    "kestra": {
      "command": "/Users/user/.local/bin/uv",
      "args": [
        "--directory",
        "/Users/user/Desktop/serena-qualifier/mcp-server-python/src",
        "run",
        "server.py"
      ]
    }
  }
}
```

### Step 2: Start Using MCP Tools
Once configured, you can use the MCP tools in Cursor:

- **@flow** - Manage Kestra flows
- **@execution** - Control flow executions
- **@files** - Handle namespace files
- **@kv** - Key-value store operations
- **@namespace** - Namespace management
- **@backfill** - Backfill executions
- **@replay** - Replay executions
- **@restart** - Restart executions
- **@resume** - Resume executions

## 🛠️ Available Tools

### Flow Management
- List flows in namespaces
- Create, update, delete flows
- Validate flow syntax
- Export/import flows

### Execution Control
- Trigger flow executions
- Monitor execution status
- View execution logs
- Cancel running executions

### Data Operations
- Upload/download files
- Manage key-value pairs
- Access execution outputs
- Handle flow inputs

## 🔍 Testing the Installation

You can test the MCP server by running:

```bash
cd /Users/user/Desktop/serena-qualifier/mcp-server-python
source $HOME/.local/bin/env
uv --directory src run server.py
```

This will start the server and you should see it waiting for MCP messages.

## 📚 Example Usage

Once configured in Cursor, you can use prompts like:

- "List all flows in the serena.production namespace"
- "Show me the execution logs for the latest lead activation flow"
- "Create a new flow based on the existing template"
- "Trigger the lead activation flow with test data"

## 🔒 Security Notes

- The server connects to your remote Kestra instance at https://kestra.darwinai.com.br/
- Enterprise Edition tools are disabled for OSS installations
- Basic authentication is used (admin/admin)
- Secure HTTPS connection to your self-hosted Kestra instance

## 🐛 Troubleshooting

### If MCP server doesn't start:
1. Check that Kestra is accessible at https://kestra.darwinai.com.br/
2. Verify the .env file configuration and credentials
3. Ensure all dependencies are installed
4. Check that uv is in your PATH
5. Verify network connectivity to the remote Kestra instance

### If tools don't appear in Cursor:
1. Restart Cursor after adding MCP configuration
2. Check the MCP server logs for errors
3. Verify the file paths in the configuration

## 📈 Next Steps

1. **Add to Cursor MCP settings** - Copy the configuration above
2. **Test basic functionality** - Try listing flows
3. **Explore available tools** - Use different MCP commands
4. **Integrate with workflows** - Use for debugging and monitoring your Kestra flows

## 🔗 Related Documentation

- [Kestra MCP Server GitHub](https://github.com/kestra-io/mcp-server-python)
- [Kestra Documentation](https://kestra.io/docs)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/docs) 