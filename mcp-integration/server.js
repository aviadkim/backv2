require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { Storage } = require('@google-cloud/storage');
const { DocumentProcessorServiceClient } = require('@google-cloud/documentai');
const axios = require('axios');
const cheerio = require('cheerio');

const app = express();
const port = process.env.MCP_PORT || 8080;

// Middleware
app.use(cors());
app.use(express.json());

// Initialize Google Cloud clients
const path = require('path');
const keyFilename = path.join(__dirname, 'github-service-account-key.json');
console.log(`Using key file: ${keyFilename}`);

const storage = new Storage({
  projectId: process.env.GOOGLE_CLOUD_PROJECT_ID,
  keyFilename: keyFilename
});

const documentAiClient = new DocumentProcessorServiceClient({
  projectId: process.env.GOOGLE_CLOUD_PROJECT_ID,
  keyFilename: keyFilename
});

// MCP request handler
async function handleRequest(action, parameters = {}) {
  let result;

  switch (action) {
    case 'listBuckets':
      result = await listBuckets();
      break;
    case 'listFiles':
      result = await listFiles(parameters.bucketName);
      break;
    case 'uploadFile':
      result = await uploadFile(parameters.bucketName, parameters.fileName, parameters.fileContent);
      break;
    case 'downloadFile':
      result = await downloadFile(parameters.bucketName, parameters.fileName);
      break;
    case 'processDocument':
      result = await processDocument(parameters.bucketName, parameters.fileName);
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

// MCP endpoint
app.post('/mcp', async (req, res) => {
  try {
    const { action, parameters } = req.body;
    const result = await handleRequest(action, parameters);
    res.json({ success: true, result });
  } catch (error) {
    console.error('Error processing MCP request:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Google Cloud Storage functions
async function listBuckets() {
  const [buckets] = await storage.getBuckets();
  return buckets.map(bucket => bucket.name);
}

async function listFiles(bucketName) {
  const [files] = await storage.bucket(bucketName).getFiles();
  return files.map(file => file.name);
}

async function uploadFile(bucketName, fileName, fileContent) {
  const file = storage.bucket(bucketName).file(fileName);
  await file.save(Buffer.from(fileContent, 'base64'));
  return { message: `File ${fileName} uploaded to ${bucketName}` };
}

async function downloadFile(bucketName, fileName) {
  const file = storage.bucket(bucketName).file(fileName);
  const [fileContent] = await file.download();
  return { content: fileContent.toString('base64') };
}

// Document AI functions
async function processDocument(bucketName, fileName) {
  const processorName = `projects/${process.env.GOOGLE_CLOUD_PROJECT_ID}/locations/${process.env.GOOGLE_CLOUD_DOCUMENT_AI_LOCATION}/processors/${process.env.GOOGLE_CLOUD_DOCUMENT_AI_PROCESSOR_ID}`;

  const file = storage.bucket(bucketName).file(fileName);
  const [fileContent] = await file.download();

  const request = {
    name: processorName,
    rawDocument: {
      content: fileContent.toString('base64'),
      mimeType: 'application/pdf',
    },
  };

  const [result] = await documentAiClient.processDocument(request);
  return result.document;
}

// Web functions
async function webSearch(query) {
  try {
    // This is a simple implementation. In a production environment, you would use a proper search API
    const response = await axios.get(`https://www.google.com/search?q=${encodeURIComponent(query)}`);
    const $ = cheerio.load(response.data);

    const results = [];
    $('div.g').each((i, element) => {
      const titleElement = $(element).find('h3');
      const linkElement = $(element).find('a');
      const snippetElement = $(element).find('div.VwiC3b');

      if (titleElement.length && linkElement.length) {
        results.push({
          title: titleElement.text(),
          link: linkElement.attr('href'),
          snippet: snippetElement.text()
        });
      }
    });

    return results;
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
    const content = $('body').text().replace(/\\s+/g, ' ').trim();

    return {
      title,
      content,
      url
    };
  } catch (error) {
    console.error('Error fetching web content:', error);
    throw new Error('Failed to fetch web content');
  }
}

// Start the server
app.listen(port, () => {
  console.log(`MCP server listening at http://localhost:${port}`);
});

// Export the handleRequest function
module.exports = {
  handleRequest
};
