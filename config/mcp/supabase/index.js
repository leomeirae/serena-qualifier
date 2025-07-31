const { createClient } = require('@supabase/supabase-js');
const express = require('express');

// Health check endpoint
const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'supabase-mcp' });
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
          }
        });
        break;
        
      case "tools/call":
        const { name, arguments: args } = params;
        
        // Initialize Supabase client
        const supabaseUrl = process.env.SUPABASE_URL;
        const supabaseKey = process.env.SUPABASE_ANON_KEY;
        const supabase = createClient(supabaseUrl, supabaseKey);
        
        switch (name) {
          case "execute_sql":
            const { data, error } = await supabase.rpc('exec_sql', { 
              query: args.query,
              params: args.params || []
            });
            
            if (error) throw error;
            res.json({ 
              result: { 
                content: [{ type: "text", text: JSON.stringify(data) }] 
              } 
            });
            break;
            
          case "list_tables":
            const { data: tables, error: tablesError } = await supabase
              .from('information_schema.tables')
              .select('table_name')
              .eq('table_schema', 'public');
              
            if (tablesError) throw tablesError;
            res.json({ 
              result: { 
                content: [{ type: "text", text: JSON.stringify(tables) }] 
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
  console.log(`Supabase MCP Server running on port ${port}`);
});
