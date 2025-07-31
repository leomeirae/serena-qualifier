const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const { createClient } = require('@supabase/supabase-js');
const express = require('express');

const server = new Server(
  {
    name: "supabase-mcp-server",
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
const port = process.env.PORT || 3001;

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'supabase-mcp' });
});

app.listen(port, () => {
  console.log(`Supabase MCP Server running on port ${port}`);
});

// MCP Server implementation
server.setRequestHandler("tools/list", async () => {
  return {
    tools: [
      {
        name: "execute_sql",
        description: "Execute SQL query on Supabase",
        inputSchema: {
          type: "object",
          properties: {
            query: { type: "string" },
            params: { type: "array" }
          },
          required: ["query"]
        }
      },
      {
        name: "list_tables",
        description: "List all tables in the database",
        inputSchema: {
          type: "object",
          properties: {}
        }
      }
    ]
  };
});

server.setRequestHandler("tools/call", async (request) => {
  const { name, arguments: args } = request.params;
  
  // Initialize Supabase client
  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_ANON_KEY;
  const supabase = createClient(supabaseUrl, supabaseKey);
  
  try {
    switch (name) {
      case "execute_sql":
        const { data, error } = await supabase.rpc('exec_sql', { 
          query: args.query,
          params: args.params || []
        });
        
        if (error) throw error;
        return { content: [{ type: "text", text: JSON.stringify(data) }] };
        
      case "list_tables":
        const { data: tables, error: tablesError } = await supabase
          .from('information_schema.tables')
          .select('table_name')
          .eq('table_schema', 'public');
          
        if (tablesError) throw tablesError;
        return { content: [{ type: "text", text: JSON.stringify(tables) }] };
        
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
