const express = require('express');
const cors = require('cors');
const DevDocsGoogleCloudIntegration = require('./devdocs-integration');

// Initialize Express app
const app = express();
const port = 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

// Initialize DevDocs Google Cloud Integration
const integration = new DevDocsGoogleCloudIntegration();

// API endpoints
app.get('/api/status', (req, res) => {
  res.json({
    status: 'ok',
    message: 'Augment connector is running',
    mcpServer: 'http://localhost:8080/mcp'
  });
});

app.get('/api/buckets', async (req, res) => {
  try {
    const buckets = await integration.listBuckets();
    res.json({ success: true, buckets });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.get('/api/files/:bucketName', async (req, res) => {
  try {
    const { bucketName } = req.params;
    const files = await integration.listFiles(bucketName);
    res.json({ success: true, files });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/upload', async (req, res) => {
  try {
    const { bucketName, fileName, fileContent } = req.body;
    const result = await integration.uploadFile(bucketName, fileName, fileContent);
    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/process-document', async (req, res) => {
  try {
    const { bucketName, fileName } = req.body;
    const result = await integration.processDocument(bucketName, fileName);
    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.get('/api/search', async (req, res) => {
  try {
    const { query } = req.query;
    const results = await integration.webSearch(query);
    res.json({ success: true, results });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

app.get('/api/fetch', async (req, res) => {
  try {
    const { url } = req.query;
    const content = await integration.webFetch(url);
    res.json({ success: true, content });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Augment integration endpoint
app.post('/api/augment', async (req, res) => {
  try {
    const { action, parameters } = req.body;
    
    let result;
    
    switch (action) {
      case 'listBuckets':
        result = await integration.listBuckets();
        break;
      case 'listFiles':
        result = await integration.listFiles(parameters.bucketName);
        break;
      case 'uploadFile':
        result = await integration.uploadFile(parameters.bucketName, parameters.fileName, parameters.fileContent);
        break;
      case 'downloadFile':
        result = await integration.downloadFile(parameters.bucketName, parameters.fileName);
        break;
      case 'processDocument':
        result = await integration.processDocument(parameters.bucketName, parameters.fileName);
        break;
      case 'webSearch':
        result = await integration.webSearch(parameters.query);
        break;
      case 'webFetch':
        result = await integration.webFetch(parameters.url);
        break;
      default:
        throw new Error(`Unknown action: ${action}`);
    }
    
    res.json({ success: true, result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Augment connector listening at http://localhost:${port}`);
  console.log(`DevDocs web interface available at http://localhost:${port}/devdocs-web.html`);
});
