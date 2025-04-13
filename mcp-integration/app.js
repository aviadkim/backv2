const express = require('express');
const app = express();
const port = process.env.PORT || 8080;

// Middleware
app.use(express.json());

// Simple home page
app.get('/', (req, res) => {
  res.send('DevDocs MCP Server is running!');
});

// MCP endpoint
app.post('/mcp', (req, res) => {
  res.json({
    success: true,
    result: {
      message: 'MCP endpoint is working!',
      action: req.body.action || 'unknown',
      parameters: req.body.parameters || {}
    }
  });
});

// Start the server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
