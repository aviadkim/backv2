FROM node:18-alpine

WORKDIR /app

# Copy package.json and install dependencies
COPY package.json .
RUN npm install

# Copy application code
COPY devdocs-mcp-server.js .

# Create public directory
RUN mkdir -p public

# Expose port
EXPOSE 8080

# Start the application
CMD ["node", "devdocs-mcp-server.js"]
