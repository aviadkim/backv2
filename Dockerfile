# Use a Node.js image with Chrome for web browsing capabilities
FROM node:18

# Install Chrome for web browsing capabilities
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    apt-transport-https \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all application files
COPY . .

# Install dependencies
RUN cd mcp-integration && npm install

# Install puppeteer for web browsing
RUN cd mcp-integration && npm install puppeteer axios cheerio cors

# Create enhanced MCP server with web capabilities
COPY mcp-integration/devdocs-mcp-server.js ./server.js

# Set environment variables
ENV PORT=8080
ENV GOOGLE_CLOUD_PROJECT_ID=github-456508
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV CHROME_BIN=/usr/bin/google-chrome

# Create public directory for static files
RUN mkdir -p public

# Copy web files to public directory
COPY devdocs-app.html ./public/index.html
COPY mcp-web-demo.html ./public/demo.html

# Expose port
EXPOSE $PORT

# Start the application
CMD ["node", "server.js"]
