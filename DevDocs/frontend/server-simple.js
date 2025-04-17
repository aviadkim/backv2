const http = require("http");
const fs = require("fs");
const path = require("path");
const PORT = process.env.PORT || 3002;

const MIME_TYPES = {
  ".html": "text/html",
  ".js": "text/javascript",
  ".css": "text/css",
  ".json": "application/json",
  ".png": "image/png",
  ".jpg": "image/jpg",
  ".gif": "image/gif",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon"
};

// Create a simple HTML page for the loading state
const loadingHtml = '<!DOCTYPE html><html><head><title>DevDocs - Financial Document Processing</title><style>body{font-family:Arial,sans-serif;margin:0;padding:0;display:flex;justify-content:center;align-items:center;height:100vh;background-color:#f5f5f5}.container{text-align:center;padding:2rem;background-color:white;border-radius:8px;box-shadow:0 4px 6px rgba(0,0,0,0.1);max-width:800px}h1{color:#2c3e50;margin-bottom:1rem}p{color:#7f8c8d;margin-bottom:2rem}.dashboard{display:grid;grid-template-columns:repeat(2,1fr);gap:1.5rem;margin-top:2rem}.card{background-color:#f9f9f9;border-radius:8px;padding:1.5rem;text-align:left;transition:transform 0.3s ease}.card:hover{transform:translateY(-5px);box-shadow:0 10px 20px rgba(0,0,0,0.1)}.card h2{color:#3498db;margin-top:0}.card p{margin-bottom:1rem}.button{display:inline-block;padding:0.75rem 1.5rem;background-color:#3498db;color:white;text-decoration:none;border-radius:4px;font-weight:bold;transition:background-color 0.3s ease}.button:hover{background-color:#2980b9}</style></head><body><div class="container"><h1>DevDocs - Financial Document Processing</h1><p>Welcome to the Financial Document Processing Platform</p><div class="dashboard"><div class="card"><h2>Document Upload</h2><p>Upload and process financial documents</p><a href="/upload" class="button">Upload Document</a></div><div class="card"><h2>Financial Analysis</h2><p>Analyze financial data and generate reports</p><a href="/analysis" class="button">View Analysis</a></div><div class="card"><h2>Data Export</h2><p>Export financial data to various formats</p><a href="/export" class="button">Export Data</a></div><div class="card"><h2>Document Comparison</h2><p>Compare multiple financial documents</p><a href="/comparison" class="button">Compare Documents</a></div></div></div></body></html>';

const server = http.createServer((req, res) => {
  console.log(`Request: ${req.method} ${req.url}`);

  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400' // 24 hours
    });
    res.end();
    return;
  }

  // Serve the loading page for all requests
  res.writeHead(200, { 'Content-Type': 'text/html' });
  res.end(loadingHtml);
});

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}/`);
});
