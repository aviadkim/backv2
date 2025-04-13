const express = require('express');
const cors = require('cors');
const { MCPClient } = require('gcp-mcp');
const dotenv = require('dotenv');
const { createClient } = require('@supabase/supabase-js');

// Load environment variables
dotenv.config();

const app = express();
const port = process.env.PORT || 8080;

// Middleware
app.use(cors());
app.use(express.json());

// Initialize MCP client
const mcpClient = new MCPClient({
  projectId: process.env.GOOGLE_CLOUD_PROJECT_ID || 'github-456508',
  apiKey: process.env.MCP_API_KEY,
  webCapabilities: true
});

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL || 'https://dnjnsotemnfrjlotgved.supabase.co';
const supabaseKey = process.env.SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

// Routes
app.get('/', (req, res) => {
  res.send('DevDocs MCP Server is running');
});

// Get context from MCP
app.post('/context', async (req, res) => {
  try {
    const { query, webSearch = false, maxResults = 5 } = req.body;
    
    const response = await mcpClient.getContext({
      query,
      webSearch,
      maxResults
    });
    
    res.json(response);
  } catch (error) {
    console.error('Error getting context:', error);
    res.status(500).json({ error: error.message });
  }
});

// Generate response with MCP
app.post('/generate', async (req, res) => {
  try {
    const { query, context = [], webSearch = false, maxTokens = 1000 } = req.body;
    
    const response = await mcpClient.generateResponse({
      query,
      context,
      webSearch,
      maxTokens
    });
    
    res.json(response);
  } catch (error) {
    console.error('Error generating response:', error);
    res.status(500).json({ error: error.message });
  }
});

// Search web with MCP
app.post('/search', async (req, res) => {
  try {
    const { query, maxResults = 5 } = req.body;
    
    const response = await mcpClient.searchWeb({
      query,
      maxResults
    });
    
    res.json(response);
  } catch (error) {
    console.error('Error searching web:', error);
    res.status(500).json({ error: error.message });
  }
});

// Start server
app.listen(port, () => {
  console.log(`DevDocs MCP Server listening on port ${port}`);
});
