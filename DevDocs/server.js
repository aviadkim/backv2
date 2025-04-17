const express = require('express');
const cors = require('cors');
// Try to load the real MCP client, fall back to mock if not available
let MCPClient;
try {
  MCPClient = require('gcp-mcp').MCPClient;
  console.log('Using real MCP client');
} catch (error) {
  console.log('Using mock MCP client');
  MCPClient = require('./mcp-mock').MCPClient;
}
const dotenv = require('dotenv');
const { createClient } = require('@supabase/supabase-js');
const path = require('path');
const fs = require('fs');
const axios = require('axios');
const cheerio = require('cheerio');

// Load environment variables
dotenv.config();

const app = express();
const port = process.env.PORT || 8080;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Initialize MCP client
const mcpClient = new MCPClient({
  projectId: process.env.GOOGLE_CLOUD_PROJECT_ID || 'github-456508',
  apiKey: process.env.MCP_API_KEY,
  webCapabilities: true
});

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL || 'https://dnjnsotemnfrjlotgved.supabase.co';
const supabaseKey = process.env.SUPABASE_KEY;
let supabase = null;

if (supabaseKey) {
  console.log('Supabase credentials provided');
  supabase = createClient(supabaseUrl, supabaseKey);
} else {
  console.log('Supabase credentials not provided');
}

// Import API routes
const apiRoutes = require('./api-routes');

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Create public directory if it doesn't exist
if (!fs.existsSync(path.join(__dirname, 'public'))) {
  fs.mkdirSync(path.join(__dirname, 'public'), { recursive: true });
}

// Create temp directory if it doesn't exist
if (!fs.existsSync(path.join(__dirname, 'temp'))) {
  fs.mkdirSync(path.join(__dirname, 'temp'), { recursive: true });
}

// Create results directory if it doesn't exist
if (!fs.existsSync(path.join(__dirname, 'results'))) {
  fs.mkdirSync(path.join(__dirname, 'results'), { recursive: true });
}

// Create a simple HTML page for the home page
const homePage = `
<!DOCTYPE html>
<html>
<head>
    <title>DevDocs MCP Server</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }
        h1, h2 {
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        ul {
            list-style-type: none;
            padding-left: 20px;
        }
        li {
            margin-bottom: 10px;
        }
        a {
            color: #0366d6;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>DevDocs MCP Server</h1>
    <h2>Server Status</h2>
    <p>The MCP server is running!</p>
    <h2>Available Actions</h2>
    <ul>
        <li><strong>listBuckets</strong> - List all storage buckets</li>
        <li><strong>listFiles</strong> - List files in a storage bucket</li>
        <li><strong>webSearch</strong> - Search the web</li>
        <li><strong>webFetch</strong> - Fetch content from a URL</li>
    </ul>
</body>
</html>
`;

// Write the home page to the public directory
fs.writeFileSync(path.join(__dirname, 'public', 'index.html'), homePage);

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// API routes
app.use('/api', apiRoutes);

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

// Web fetch endpoint (GET)
app.get('/webFetch', async (req, res) => {
  try {
    const url = req.query.url;
    if (!url) {
      return res.status(400).json({ error: 'URL parameter is required' });
    }

    console.log(`Fetching content from ${url}`);

    const response = await axios.get(url, {
      responseType: url.endsWith('.pdf') ? 'arraybuffer' : 'text'
    });

    if (url.endsWith('.pdf')) {
      // For PDFs, save to a temporary file and return the path
      const tempDir = path.join(__dirname, 'temp');
      if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir, { recursive: true });
      }

      const filename = `temp_${Date.now()}.pdf`;
      const filePath = path.join(tempDir, filename);

      fs.writeFileSync(filePath, response.data);

      res.json({
        success: true,
        message: 'PDF downloaded successfully',
        filePath: filePath,
        filename: filename
      });
    } else {
      // For HTML content, parse and return as text
      const $ = cheerio.load(response.data);
      const text = $('body').text().trim();

      res.json({
        success: true,
        content: text,
        url: url
      });
    }
  } catch (error) {
    console.error('Error fetching content:', error);
    res.status(500).json({ error: error.message });
  }
});

// Web search endpoint (GET)
app.get('/webSearch', async (req, res) => {
  try {
    const query = req.query.query;
    if (!query) {
      return res.status(400).json({ error: 'Query parameter is required' });
    }

    console.log(`Searching for ${query}`);

    // Use MCP client to search the web
    const response = await mcpClient.searchWeb({
      query,
      maxResults: 5
    });

    res.json(response);
  } catch (error) {
    console.error('Error searching:', error);
    res.status(500).json({ error: error.message });
  }
});

// Start server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
  console.log(`Access the application at http://localhost:${port}`);
});
