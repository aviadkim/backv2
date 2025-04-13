const express = require('express');
const path = require('path');
const axios = require('axios');
const cheerio = require('cheerio');

const app = express();
const port = process.env.PORT || 8080;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, '..')));

// Serve the MCP web demo as the home page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'mcp-web-demo.html'));
});

// MCP request handler functions
async function listBuckets() {
  return ['devdocs-bucket', 'example-bucket', 'test-bucket'];
}

async function listFiles(bucketName) {
  return ['example.txt', 'test.pdf', 'sample.docx'];
}

async function webSearch(query) {
  return [
    { title: 'Google Cloud Platform', link: 'https://cloud.google.com', snippet: 'Google Cloud Platform lets you build, deploy, and scale applications, websites, and services on the same infrastructure as Google.' },
    { title: 'DevDocs API Documentation', link: 'https://devdocs.io', snippet: 'DevDocs combines multiple API documentations in a fast, organized, and searchable interface.' },
    { title: 'Model Context Protocol', link: 'https://github.com/eniayomi/gcp-mcp', snippet: 'A protocol for connecting AI models with external tools and services.' }
  ];
}

async function webFetch(url) {
  try {
    const response = await axios.get(url);
    const $ = cheerio.load(response.data);

    // Extract the main content
    $('script').remove();
    $('style').remove();

    // Convert to markdown-like format
    const title = $('title').text();
    const content = $('body').text().replace(/\s+/g, ' ').trim();

    return {
      title,
      content,
      url
    };
  } catch (error) {
    console.error('Error fetching web content:', error);
    return {
      title: 'Sample Page',
      content: 'This is a sample page content.',
      url
    };
  }
}

// MCP endpoint
app.post('/mcp', async (req, res) => {
  try {
    const { action, parameters } = req.body;
    
    let result;
    
    switch (action) {
      case 'listBuckets':
        result = await listBuckets();
        break;
      case 'listFiles':
        result = await listFiles(parameters.bucketName);
        break;
      case 'webSearch':
        result = await webSearch(parameters.query);
        break;
      case 'webFetch':
        result = await webFetch(parameters.url);
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
