const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3002;

// Serve static files from the 'out' directory (Next.js static export)
app.use(express.static(path.join(__dirname, 'out')));

// Handle API requests
app.use('/api', (req, res) => {
  res.json({ message: 'API endpoint - will be implemented in the future' });
});

// For all other requests, serve the index.html file
app.get('*', (req, res) => {
  // Check if the specific path exists in the out directory
  const filePath = path.join(__dirname, 'out', req.path);
  
  if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    return res.sendFile(filePath);
  }
  
  // If the file doesn't exist, serve index.html
  res.sendFile(path.join(__dirname, 'out', 'index.html'));
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
