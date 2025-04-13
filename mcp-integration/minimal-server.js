const express = require('express');
const app = express();
const port = process.env.PORT || 8080;

// Middleware
app.use(express.json());
app.use(express.static(__dirname));

// Simple home page
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>DevDocs MCP Server</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
        }
        h1 {
          color: #2c3e50;
        }
        .card {
          background-color: #f9f9f9;
          border: 1px solid #ddd;
          border-radius: 5px;
          padding: 20px;
          margin-bottom: 20px;
        }
      </style>
    </head>
    <body>
      <h1>DevDocs MCP Server</h1>
      <div class="card">
        <h2>Server Status</h2>
        <p>The MCP server is running!</p>
        <p>You can use this server to interact with Google Cloud services and browse the web.</p>
      </div>
      <div class="card">
        <h2>Available Actions</h2>
        <ul>
          <li><strong>listBuckets</strong> - List all storage buckets</li>
          <li><strong>listFiles</strong> - List files in a storage bucket</li>
          <li><strong>webSearch</strong> - Search the web</li>
          <li><strong>webFetch</strong> - Fetch content from a URL</li>
        </ul>
      </div>
    </body>
    </html>
  `);
});

// MCP endpoint
app.post('/mcp', (req, res) => {
  try {
    const { action, parameters } = req.body;
    
    let result;
    
    switch (action) {
      case 'listBuckets':
        result = ['devdocs-bucket', 'example-bucket', 'test-bucket'];
        break;
      case 'listFiles':
        result = ['example.txt', 'test.pdf', 'sample.docx'];
        break;
      case 'webSearch':
        result = [
          { title: 'Google Cloud Platform', link: 'https://cloud.google.com', snippet: 'Google Cloud Platform lets you build, deploy, and scale applications, websites, and services on the same infrastructure as Google.' },
          { title: 'DevDocs API Documentation', link: 'https://devdocs.io', snippet: 'DevDocs combines multiple API documentations in a fast, organized, and searchable interface.' },
          { title: 'Model Context Protocol', link: 'https://github.com/eniayomi/gcp-mcp', snippet: 'A protocol for connecting AI models with external tools and services.' }
        ];
        break;
      case 'webFetch':
        result = {
          title: 'Sample Page',
          content: 'This is a sample page content.',
          url: parameters.url
        };
        break;
      default:
        throw new Error(`Unknown action: ${action}`);
    }
    
    res.json({ success: true, result });
  } catch (error) {
    console.error('Error processing MCP request:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
