/**
 * Start the backend server
 * 
 * This script starts the backend server and sets up the necessary environment variables.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Check if .env file exists
const envPath = path.join(__dirname, '.env');
if (!fs.existsSync(envPath)) {
  console.log('Creating default .env file...');
  
  // Create default .env file
  const defaultEnv = `
# Server configuration
PORT=8000
NODE_ENV=development

# Supabase configuration
SUPABASE_URL=https://dnjnsotemnfrjlotgved.supabase.co
SUPABASE_KEY=

# OpenRouter configuration
OPENROUTER_API_KEY=sk-or-v1-64e1068c3a61a5e4be88c64c6992b39dbc15ad687201cb3fd05a98a9ba1e22dc8

# Logging configuration
LOG_LEVEL=info
  `.trim();
  
  fs.writeFileSync(envPath, defaultEnv);
  console.log('Default .env file created. Please update it with your API keys.');
}

// Load environment variables from .env file
require('dotenv').config({ path: envPath });

// Create necessary directories
const dirs = ['logs', 'temp', 'uploads'];
dirs.forEach(dir => {
  const dirPath = path.join(__dirname, dir);
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    console.log(`Created directory: ${dir}`);
  }
});

// Start the server
console.log('Starting backend server...');
const server = spawn('node', ['server.js'], {
  stdio: 'inherit',
  env: process.env
});

// Handle server exit
server.on('close', (code) => {
  console.log(`Server exited with code ${code}`);
  process.exit(code);
});

// Handle process signals
process.on('SIGINT', () => {
  console.log('Stopping server...');
  server.kill('SIGINT');
});

process.on('SIGTERM', () => {
  console.log('Stopping server...');
  server.kill('SIGTERM');
});
