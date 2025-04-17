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
const loadingHtml = `
<!DOCTYPE html>
<html>
<head>
    <title>DevDocs - Financial Document Processing</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f5f5f5;
        }
        .container {
            text-align: center;
            padding: 2rem;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 600px;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        p {
            color: #7f8c8d;
            margin-bottom: 2rem;
        }
        .loader {
            border: 5px solid #f3f3f3;
            border-top: 5px solid #3498db;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 2s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .dashboard-link {
            display: inline-block;
            margin-top: 2rem;
            padding: 0.75rem 1.5rem;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
        }
        .dashboard-link:hover {
            background-color: #2980b9;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>DevDocs - Financial Document Processing</h1>
        <p>Welcome to the Financial Document Processing Platform</p>
        <div class="loader"></div>
        <p>Loading the application...</p>
        <a href="/dashboard" class="dashboard-link">Go to Dashboard</a>
    </div>
    <script>
        // Simple dashboard page
        if (window.location.pathname === '/dashboard') {
            document.querySelector('.container').innerHTML = `
                <h1>Financial Document Dashboard</h1>
                <p>Welcome to the Financial Document Dashboard</p>
                <div style="text-align: left; margin-top: 2rem;">
                    <h2>Available Tools</h2>
                    <ul style="list-style-type: none; padding: 0;">
                        <li style="margin-bottom: 1rem;">
                            <a href="/upload" style="color: #3498db; text-decoration: none; font-weight: bold;">Upload Document</a>
                            <p style="margin: 0.5rem 0;">Upload and process financial documents</p>
                        </li>
                        <li style="margin-bottom: 1rem;">
                            <a href="/analysis" style="color: #3498db; text-decoration: none; font-weight: bold;">Financial Analysis</a>
                            <p style="margin: 0.5rem 0;">Analyze financial data and generate reports</p>
                        </li>
                        <li style="margin-bottom: 1rem;">
                            <a href="/export" style="color: #3498db; text-decoration: none; font-weight: bold;">Data Export</a>
                            <p style="margin: 0.5rem 0;">Export financial data to various formats</p>
                        </li>
                    </ul>
                </div>
                <a href="/" class="dashboard-link" style="background-color: #2c3e50;">Back to Home</a>
            `;
        }

        // Simple upload page
        if (window.location.pathname === '/upload') {
            document.querySelector('.container').innerHTML = `
                <h1>Upload Financial Document</h1>
                <p>Upload a financial document for processing</p>
                <form style="text-align: left; margin-top: 2rem;">
                    <div style="margin-bottom: 1rem;">
                        <label for="file" style="display: block; margin-bottom: 0.5rem; font-weight: bold;">Select File</label>
                        <input type="file" id="file" name="file" accept=".pdf" style="width: 100%;">
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <label for="type" style="display: block; margin-bottom: 0.5rem; font-weight: bold;">Document Type</label>
                        <select id="type" name="type" style="width: 100%; padding: 0.5rem;">
                            <option value="bank_statement">Bank Statement</option>
                            <option value="portfolio_report">Portfolio Report</option>
                            <option value="financial_statement">Financial Statement</option>
                        </select>
                    </div>
                    <button type="submit" style="padding: 0.75rem 1.5rem; background-color: #3498db; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer;">Upload Document</button>
                </form>
                <a href="/dashboard" class="dashboard-link" style="background-color: #2c3e50; margin-top: 1rem;">Back to Dashboard</a>
            `;
        }

        // Simple analysis page
        if (window.location.pathname === '/analysis') {
            document.querySelector('.container').innerHTML = `
                <h1>Financial Analysis</h1>
                <p>Analyze financial data and generate reports</p>
                <div style="text-align: left; margin-top: 2rem;">
                    <h2>Available Reports</h2>
                    <ul style="list-style-type: none; padding: 0;">
                        <li style="margin-bottom: 1rem;">
                            <a href="#" style="color: #3498db; text-decoration: none; font-weight: bold;">Portfolio Summary</a>
                            <p style="margin: 0.5rem 0;">Summary of portfolio performance</p>
                        </li>
                        <li style="margin-bottom: 1rem;">
                            <a href="#" style="color: #3498db; text-decoration: none; font-weight: bold;">Asset Allocation</a>
                            <p style="margin: 0.5rem 0;">Breakdown of asset allocation</p>
                        </li>
                        <li style="margin-bottom: 1rem;">
                            <a href="#" style="color: #3498db; text-decoration: none; font-weight: bold;">Performance Analysis</a>
                            <p style="margin: 0.5rem 0;">Analysis of portfolio performance</p>
                        </li>
                    </ul>
                </div>
                <a href="/dashboard" class="dashboard-link" style="background-color: #2c3e50;">Back to Dashboard</a>
            `;
        }

        // Simple export page
        if (window.location.pathname === '/export') {
            document.querySelector('.container').innerHTML = `
                <h1>Data Export</h1>
                <p>Export financial data to various formats</p>
                <div style="text-align: left; margin-top: 2rem;">
                    <h2>Export Options</h2>
                    <form>
                        <div style="margin-bottom: 1rem;">
                            <label for="format" style="display: block; margin-bottom: 0.5rem; font-weight: bold;">Export Format</label>
                            <select id="format" name="format" style="width: 100%; padding: 0.5rem;">
                                <option value="csv">CSV</option>
                                <option value="json">JSON</option>
                                <option value="pdf">PDF</option>
                                <option value="excel">Excel</option>
                            </select>
                        </div>
                        <div style="margin-bottom: 1rem;">
                            <label for="data" style="display: block; margin-bottom: 0.5rem; font-weight: bold;">Data to Export</label>
                            <select id="data" name="data" style="width: 100%; padding: 0.5rem;">
                                <option value="portfolio">Portfolio Data</option>
                                <option value="transactions">Transaction History</option>
                                <option value="performance">Performance Metrics</option>
                            </select>
                        </div>
                        <button type="submit" style="padding: 0.75rem 1.5rem; background-color: #3498db; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer;">Export Data</button>
                    </form>
                </div>
                <a href="/dashboard" class="dashboard-link" style="background-color: #2c3e50; margin-top: 1rem;">Back to Dashboard</a>
            `;
        }
    </script>
</body>
</html>
`;

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

  // Check if the out directory exists
  if (!fs.existsSync('./out')) {
    // If out directory doesn't exist, serve the loading page
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(loadingHtml);
    return;
  }

  // Handle root path
  let filePath = req.url === "/" ? "./out/index.html" : `./out${req.url}`;

  // If URL doesn't have an extension, assume it's a route and serve index.html
  if (!path.extname(filePath) && !filePath.endsWith("/")) {
    filePath = `./out${req.url}.html`;
    if (!fs.existsSync(filePath)) {
      filePath = "./out/index.html";
    }
  }

  // If URL ends with /, serve index.html from that directory
  if (filePath.endsWith("/")) {
    filePath = `${filePath}index.html`;
  }

  const extname = path.extname(filePath);
  const contentType = MIME_TYPES[extname] || "application/octet-stream";

  fs.readFile(filePath, (error, content) => {
    if (error) {
      if (error.code === "ENOENT") {
        // File not found, serve index.html
        fs.readFile("./out/index.html", (err, content) => {
          if (err) {
            // If index.html is not found, serve the loading page
            res.writeHead(200, { "Content-Type": "text/html" });
            res.end(loadingHtml);
          } else {
            res.writeHead(200, { "Content-Type": "text/html" });
            res.end(content, "utf-8");
          }
        });
      } else {
        // Server error
        res.writeHead(500);
        res.end(`Server Error: ${error.code}`);
      }
    } else {
      // Success - add CORS headers
      res.writeHead(200, {
        "Content-Type": contentType,
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
      });
      res.end(content, "utf-8");
    }
  });
});

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}/`);
});
