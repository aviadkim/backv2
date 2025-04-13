const express = require('express');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 8080;

// Middleware
app.use(cors());
app.use(express.json());

// Simple home page
app.get('/', (req, res) => {
  res.send('DevDocs MCP Server is running!');
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
          { title: 'Google Cloud Platform', link: 'https://cloud.google.com', snippet: 'Google Cloud Platform' },
          { title: 'DevDocs API Documentation', link: 'https://devdocs.io', snippet: 'DevDocs API' }
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
