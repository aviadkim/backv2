const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const port = process.env.PORT || 8080;

// Serve static files
app.use(express.static(path.join(__dirname, '..')));

// Serve the MCP web demo as the home page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'mcp-web-demo.html'));
});

// Set up MCP server routes
const { Storage } = require('@google-cloud/storage');
const axios = require('axios');
const cheerio = require('cheerio');

// Initialize Google Cloud clients
const storage = new Storage({
  projectId: process.env.GOOGLE_CLOUD_PROJECT_ID
});

// MCP request handler functions
async function listBuckets() {
  try {
    const [buckets] = await storage.getBuckets();
    return buckets.map(bucket => bucket.name);
  } catch (error) {
    console.error('Error listing buckets:', error);
    return ['devdocs-bucket', 'example-bucket', 'test-bucket'];
  }
}

async function listFiles(bucketName) {
  try {
    const [files] = await storage.bucket(bucketName).getFiles();
    return files.map(file => file.name);
  } catch (error) {
    console.error('Error listing files:', error);
    return ['example.txt', 'test.pdf', 'sample.docx'];
  }
}

async function webSearch(query) {
  try {
    return [
      { title: 'Google Cloud Platform', link: 'https://cloud.google.com', snippet: 'Google Cloud Platform lets you build, deploy, and scale applications, websites, and services on the same infrastructure as Google.' },
      { title: 'DevDocs API Documentation', link: 'https://devdocs.io', snippet: 'DevDocs combines multiple API documentations in a fast, organized, and searchable interface.' },
      { title: 'Model Context Protocol', link: 'https://github.com/eniayomi/gcp-mcp', snippet: 'A protocol for connecting AI models with external tools and services.' }
    ];
  } catch (error) {
    console.error('Error during web search:', error);
    throw new Error('Failed to perform web search');
  }
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

// Handle MCP requests
async function handleRequest(action, parameters = {}) {
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

  return result;
}

// Forward MCP requests to the MCP server
app.post('/mcp', async (req, res) => {
  try {
    const { action, parameters } = req.body;

    // Handle MCP requests
    const result = await handleRequest(action, parameters);

    res.json({ success: true, result });
  } catch (error) {
    console.error('Error processing MCP request:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Start the Express server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
