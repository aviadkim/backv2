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

const server = http.createServer((req, res) => {
  console.log(`Request: ${req.method} ${req.url}`);

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
            res.writeHead(500);
            res.end(`Server Error: ${err.code}`);
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
      // Success
      res.writeHead(200, { "Content-Type": contentType });
      res.end(content, "utf-8");
    }
  });
});

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}/`);
});
