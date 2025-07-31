const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const axios = require('axios');
const express = require('express');

const server = new Server(
  {
    name: "serena-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Health check endpoint
const app = express();
const port = process.env.PORT || 3002;

app.get('/', (req, res) => {
  res.json({ status: 'ok', service: 'serena-mcp' });
});

app.listen(port, () => {
  console.log(`Serena MCP Server running on port ${port}`);
});

// MCP Server implementation
server.setRequestHandler("tools/list", async () => {
  return {
    tools: [
      {
        name: "validar_qualificacao_lead",
        description: "Validar qualificação de lead na Serena",
        inputSchema: {
          type: "object",
          properties: {
            cidade: { type: "string" },
            estado: { type: "string" },
            tipo_pessoa: { type: "string" },
            valor_conta: { type: "number" }
          },
          required: ["cidade", "estado", "tipo_pessoa", "valor_conta"]
        }
      },
      {
        name: "obter_planos_gd",
        description: "Obter planos de geração distribuída",
        inputSchema: {
          type: "object",
          properties: {
            cidade: { type: "string" },
            estado: { type: "string" }
          },
          required: ["cidade", "estado"]
        }
      }
    ]
  };
});

server.setRequestHandler("tools/call", async (request) => {
  const { name, arguments: args } = request.params;
  
  const apiToken = process.env.SERENA_API_TOKEN;
  const apiBaseUrl = process.env.SERENA_API_BASE_URL;
  
  try {
    switch (name) {
      case "validar_qualificacao_lead":
        const response = await axios.post(`${apiBaseUrl}/leads/qualificar`, {
          cidade: args.cidade,
          estado: args.estado,
          tipo_pessoa: args.tipo_pessoa,
          valor_conta: args.valor_conta
        }, {
          headers: {
            'Authorization': `Bearer ${apiToken}`,
            'Content-Type': 'application/json'
          }
        });
        
        return { content: [{ type: "text", text: JSON.stringify(response.data) }] };
        
      case "obter_planos_gd":
        const plansResponse = await axios.get(`${apiBaseUrl}/planos/gd`, {
          params: {
            cidade: args.cidade,
            estado: args.estado
          },
          headers: {
            'Authorization': `Bearer ${apiToken}`
          }
        });
        
        return { content: [{ type: "text", text: JSON.stringify(plansResponse.data) }] };
        
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return { 
      content: [{ type: "text", text: `Error: ${error.message}` }],
      isError: true
    };
  }
});

const transport = new StdioServerTransport();
server.connect(transport);
