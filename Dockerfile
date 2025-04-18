# Use Node.js as base image
FROM node:18-slim

# Install Python and required system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-heb \
    ghostscript \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY backend/package*.json ./backend/
COPY frontend/package*.json ./frontend/

# Install Node.js dependencies
RUN cd backend && npm install
RUN cd frontend && npm install

# Copy Python requirements
COPY backend/requirements.txt ./backend/

# Install Python dependencies
RUN pip3 install --no-cache-dir -r backend/requirements.txt

# Copy application code
COPY . .

# Build React frontend
RUN cd frontend && npm run build

# Expose port
EXPOSE 3000

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3000

# Start the application
CMD ["node", "backend/server.js"]
