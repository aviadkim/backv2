# Use the official Node.js image as the base image
FROM node:18-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Install specific dependencies
RUN npm install react-dropzone formidable @tailwindcss/postcss --save

# Copy the rest of the application
COPY . .

# Set environment variables for build
ENV NEXT_PUBLIC_SUPABASE_URL=https://dnjnsotemnfrjlotgved.supabase.co
ENV NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRuam5zb3RlbW5mcmpsb3RndmVkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTI4NTI0MDAsImV4cCI6MjAyODQyODQwMH0.placeholder-key

# Build the application
RUN npm run build

# Use a smaller base image for the production build
FROM node:18-alpine AS runner

WORKDIR /app

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3002
ENV NEXT_PUBLIC_SUPABASE_URL=https://dnjnsotemnfrjlotgved.supabase.co
ENV NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRuam5zb3RlbW5mcmpsb3RndmVkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTI4NTI0MDAsImV4cCI6MjAyODQyODQwMH0.placeholder-key

# Install a more reliable static file server
RUN npm install -g http-server

# Copy necessary files from the builder stage
COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/out ./out

# Create a simple index.js file to handle redirects
RUN echo 'const http = require("http");\
const fs = require("fs");\
const path = require("path");\
const PORT = process.env.PORT || 3002;\
\
const MIME_TYPES = {\
  ".html": "text/html",\
  ".js": "text/javascript",\
  ".css": "text/css",\
  ".json": "application/json",\
  ".png": "image/png",\
  ".jpg": "image/jpg",\
  ".gif": "image/gif",\
  ".svg": "image/svg+xml",\
  ".ico": "image/x-icon"\
};\
\
const server = http.createServer((req, res) => {\
  console.log(`Request: ${req.method} ${req.url}`);\
\
  // Handle root path\
  let filePath = req.url === "/" ? "./out/index.html" : `./out${req.url}`;\
\
  // If URL doesn\'t have an extension, assume it\'s a route and serve index.html\
  if (!path.extname(filePath) && !filePath.endsWith("/")) {\
    filePath = `./out${req.url}.html`;\
    if (!fs.existsSync(filePath)) {\
      filePath = "./out/index.html";\
    }\
  }\
\
  // If URL ends with /, serve index.html from that directory\
  if (filePath.endsWith("/")) {\
    filePath = `${filePath}index.html`;\
  }\
\
  const extname = path.extname(filePath);\
  const contentType = MIME_TYPES[extname] || "application/octet-stream";\
\
  fs.readFile(filePath, (error, content) => {\
    if (error) {\
      if (error.code === "ENOENT") {\
        // File not found, serve index.html\
        fs.readFile("./out/index.html", (err, content) => {\
          if (err) {\
            res.writeHead(500);\
            res.end(`Server Error: ${err.code}`);\
          } else {\
            res.writeHead(200, { "Content-Type": "text/html" });\
            res.end(content, "utf-8");\
          }\
        });\
      } else {\
        // Server error\
        res.writeHead(500);\
        res.end(`Server Error: ${error.code}`);\
      }\
    } else {\
      // Success\
      res.writeHead(200, { "Content-Type": contentType });\
      res.end(content, "utf-8");\
    }\
  });\
});\
\
server.listen(PORT, () => {\
  console.log(`Server running at http://localhost:${PORT}/`);\
});' > server.js

# Expose the port the app will run on
EXPOSE 3002

# Set the command to run the app
CMD ["node", "server.js"]
