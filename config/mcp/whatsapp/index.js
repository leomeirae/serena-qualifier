const axios = require('axios');
const express = require('express');

// Health check endpoint
const app = express();
const port = process.env.PORT || 3003;

app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'whatsapp-mcp' });
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
                name: "sendTextMessage",
                description: "Send text message via WhatsApp Business API",
                inputSchema: {
                  type: "object",
                  properties: {
                    to: { type: "string" },
                    message: { type: "string" }
                  },
                  required: ["to", "message"]
                }
              },
              {
                name: "sendTemplateMessage",
                description: "Send template message via WhatsApp Business API",
                inputSchema: {
                  type: "object",
                  properties: {
                    to: { type: "string" },
                    templateName: { type: "string" },
                    language: { type: "string" },
                    components: { type: "array" }
                  },
                  required: ["to", "templateName", "language"]
                }
              }
            ]
          }
        });
        break;
        
      case "tools/call":
        const { name, arguments: args } = params;
        
        const apiToken = process.env.WHATSAPP_API_TOKEN;
        const phoneNumberId = process.env.WHATSAPP_PHONE_NUMBER_ID;
        const apiUrl = `https://graph.facebook.com/v18.0/${phoneNumberId}/messages`;
        
        switch (name) {
          case "sendTextMessage":
            const textResponse = await axios.post(apiUrl, {
              messaging_product: "whatsapp",
              to: args.to,
              type: "text",
              text: {
                body: args.message
              }
            }, {
              headers: {
                'Authorization': `Bearer ${apiToken}`,
                'Content-Type': 'application/json'
              }
            });
            
            res.json({ 
              result: { 
                content: [{ type: "text", text: JSON.stringify(textResponse.data) }] 
              } 
            });
            break;
            
          case "sendTemplateMessage":
            const templateResponse = await axios.post(apiUrl, {
              messaging_product: "whatsapp",
              to: args.to,
              type: "template",
              template: {
                name: args.templateName,
                language: {
                  code: args.language
                },
                components: args.components || []
              }
            }, {
              headers: {
                'Authorization': `Bearer ${apiToken}`,
                'Content-Type': 'application/json'
              }
            });
            
            res.json({ 
              result: { 
                content: [{ type: "text", text: JSON.stringify(templateResponse.data) }] 
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
  console.log(`WhatsApp MCP Server running on port ${port}`);
});
