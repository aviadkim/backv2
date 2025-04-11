const { exec } = require('child_process');
const http = require('http');
const path = require('path');
const fs = require('fs');

/**
 * Check if server is already running
 */
async function isServerRunning(url) {
  return new Promise((resolve) => {
    http.get(url, (res) => {
      resolve(res.statusCode === 200);
    }).on('error', () => {
      resolve(false);
    });
  });
}

/**
 * Setup function to ensure server is running
 */
async function setupServer() {
  const isRunning = await isServerRunning('http://localhost:3000');
  
  if (!isRunning) {
    console.log('Server not running, starting development server...');
    
    // Create log directory if it doesn't exist
    const logDir = path.join(__dirname, '../logs');
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir);
    }
    
    // Start the development server
    const serverProcess = exec('npm run dev:all', {
      cwd: path.join(__dirname, '../')
    });
    
    // Log server output
    const logFile = fs.createWriteStream(path.join(logDir, 'server.log'));
    serverProcess.stdout.pipe(logFile);
    serverProcess.stderr.pipe(logFile);
    
    // Give the server some time to start
    await new Promise(resolve => setTimeout(resolve, 10000));
    
    // Check if server started successfully
    const serverStarted = await isServerRunning('http://localhost:3000');
    if (!serverStarted) {
      console.error('Failed to start server! Check logs for details.');
    } else {
      console.log('Server started successfully.');
      
      // Store process for cleanup
      global.__SERVER_PROCESS__ = serverProcess;
    }
  } else {
    console.log('Server is already running.');
  }
}

/**
 * Cleanup function to stop server if we started it
 */
async function cleanupServer() {
  if (global.__SERVER_PROCESS__) {
    console.log('Shutting down development server...');
    global.__SERVER_PROCESS__.kill();
  }
}

module.exports = { setupServer, cleanupServer };
