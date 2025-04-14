# Use a Node.js image with Chrome for web browsing capabilities
FROM node:18

# Install Chrome for web browsing capabilities
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    apt-transport-https \
    python3 \
    python3-pip \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-heb \
    libgl1-mesa-glx \
    poppler-utils \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all application files
COPY . .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Install Node.js dependencies
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
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create public directory for static files
RUN mkdir -p public

# Copy web files to public directory
COPY devdocs-app.html ./public/index.html
COPY mcp-web-demo.html ./public/demo.html

# Start the backend API server
RUN echo '#!/bin/bash\npython3 DevDocs/backend/main.py --host 0.0.0.0 --port 8000 &\nnode server.js' > start.sh
RUN chmod +x start.sh

# Expose ports
EXPOSE $PORT 8000

# Start the application
CMD ["/app/start.sh"]
