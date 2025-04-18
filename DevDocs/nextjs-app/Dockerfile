# Stage 1: Build the Next.js application
FROM node:18-alpine AS builder

WORKDIR /app

# Copy frontend package.json and package-lock.json
COPY ../frontend/package*.json ./frontend/

# Install dependencies in the frontend directory
WORKDIR /app/frontend
RUN npm install

# Copy the rest of the frontend application
COPY ../frontend .

# Build the Next.js application
RUN npm run build

# Stage 2: Create a lightweight production image
FROM node:18-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install production dependencies only
RUN npm install --production

# Copy the server.js file
COPY server.js ./

# Copy the built application from the builder stage
COPY --from=builder /app/frontend/.next ./frontend/.next
COPY --from=builder /app/frontend/public ./frontend/public
COPY --from=builder /app/frontend/next.config.js ./frontend/next.config.js

# Expose the port the app will run on
EXPOSE 3002

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3002

# Start the application
CMD ["npm", "start"]
