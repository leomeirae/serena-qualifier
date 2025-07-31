const axios = require('axios');
const express = require('express');

// Health check endpoint
const app = express();
const port = process.env.PORT || 3002;

app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'serena-mcp' });
});

// MCP Server implementation via HTTP endpoints
app.post('/mcp', async (req, res) => {
  const { method, params } = req.body;
  
  try {
    switch (method) {
      case "tools/list":
        res.json({
          result: {
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
          }
        });
        break;
        
      case "tools/call":
        const { name, arguments: args } = params;
        
        const apiToken = process.env.SERENA_API_TOKEN;
        const apiBaseUrl = process.env.SERENA_API_BASE_URL;
        
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
            
            res.json({ 
              result: { 
                content: [{ type: "text", text: JSON.stringify(response.data) }] 
              } 
            });
            break;
            
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
            
            res.json({ 
              result: { 
                content: [{ type: "text", text: JSON.stringify(plansResponse.data) }] 
              } 
            });
            break;
            
          default:
            res.status(400).json({ 
              error: { 
                message: `Unknown tool: ${name}` 
              } 
            });
        }
        break;
        
      default:
        res.status(400).json({ 
          error: { 
            message: `Unknown method: ${method}` 
          } 
        });
    }
  } catch (error) {
    res.status(500).json({ 
      error: { 
        message: `Error: ${error.message}` 
      } 
    });
  }
});

app.listen(port, () => {
  console.log(`Serena MCP Server running on port ${port}`);
});
