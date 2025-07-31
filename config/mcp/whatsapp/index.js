const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const axios = require('axios');
const express = require('express');

const server = new Server(
  {
    name: "whatsapp-mcp-server",
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
const port = process.env.PORT || 3003;

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'whatsapp-mcp' });
});

app.listen(port, () => {
  console.log(`WhatsApp MCP Server running on port ${port}`);
});

// MCP Server implementation
server.setRequestHandler("tools/list", async () => {
  return {
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
  };
});

server.setRequestHandler("tools/call", async (request) => {
  const { name, arguments: args } = request.params;
  
  const apiToken = process.env.WHATSAPP_API_TOKEN;
  const phoneNumberId = process.env.WHATSAPP_PHONE_NUMBER_ID;
  const apiUrl = `https://graph.facebook.com/v18.0/${phoneNumberId}/messages`;
  
  try {
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
        
        return { content: [{ type: "text", text: JSON.stringify(textResponse.data) }] };
        
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
        
        return { content: [{ type: "text", text: JSON.stringify(templateResponse.data) }] };
        
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
