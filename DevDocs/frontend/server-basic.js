const http = require("http");
const PORT = process.env.PORT || 3002;

const server = http.createServer((req, res) => {
  res.writeHead(200, { "Content-Type": "text/html" });
  res.end("<html><body><h1>DevDocs - Financial Document Processing</h1><p>Welcome to the Financial Document Processing Platform</p></body></html>");
});

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}/`);
});
