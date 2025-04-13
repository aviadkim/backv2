const axios = require('axios');
const readline = require('readline');

// Configuration
const MCP_SERVER_URL = 'https://devdocs-mcp-server-678297464867.me-west1.run.app/mcp';

// Create readline interface for user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Function to make MCP requests
async function mcpRequest(action, parameters = {}) {
  try {
    console.log(`Making MCP request: ${action}`);
    const response = await axios.post(MCP_SERVER_URL, {
      action,
      parameters
    });
    
    return response.data;
  } catch (error) {
    console.error(`Error making MCP request for action ${action}:`, error.message);
    throw new Error(`MCP request failed: ${error.message}`);
  }
}

// Function to list buckets
async function listBuckets() {
  try {
    console.log('Fetching buckets...');
    const response = await mcpRequest('listBuckets');
    
    if (response.success) {
      console.log('\nBuckets:');
      response.result.forEach(bucket => console.log(`- ${bucket}`));
    } else {
      console.error(`Error: ${response.error || 'Unknown error'}`);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
}

// Function to list files in a bucket
async function listFiles(bucketName) {
  try {
    console.log(`Fetching files in bucket: ${bucketName}...`);
    const response = await mcpRequest('listFiles', { bucketName });
    
    if (response.success) {
      console.log(`\nFiles in ${bucketName}:`);
      response.result.forEach(file => console.log(`- ${file}`));
    } else {
      console.error(`Error: ${response.error || 'Unknown error'}`);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
}

// Function to search the web
async function webSearch(query) {
  try {
    console.log(`Searching for: ${query}...`);
    const response = await mcpRequest('webSearch', { query });
    
    if (response.success) {
      console.log(`\nSearch Results for "${query}":`);
      response.result.forEach(result => {
        console.log(`\n${result.title}`);
        console.log(`URL: ${result.link}`);
        console.log(`${result.snippet}`);
      });
    } else {
      console.error(`Error: ${response.error || 'Unknown error'}`);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
}

// Function to fetch web content
async function webFetch(url) {
  try {
    console.log(`Fetching content from: ${url}...`);
    const response = await mcpRequest('webFetch', { url });
    
    if (response.success) {
      console.log(`\nContent from ${url}:`);
      console.log(`Title: ${response.result.title}`);
      console.log(`\nContent (first 500 chars):`);
      console.log(response.result.content.substring(0, 500) + '...');
    } else {
      console.error(`Error: ${response.error || 'Unknown error'}`);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
}

// Main menu
function showMenu() {
  console.log('\n=== DevDocs MCP Client ===');
  console.log('1. List Buckets');
  console.log('2. List Files in Bucket');
  console.log('3. Web Search');
  console.log('4. Web Fetch');
  console.log('0. Exit');
  
  rl.question('\nEnter your choice: ', async (choice) => {
    switch (choice) {
      case '1':
        await listBuckets();
        showMenu();
        break;
      case '2':
        rl.question('Enter bucket name: ', async (bucketName) => {
          await listFiles(bucketName);
          showMenu();
        });
        break;
      case '3':
        rl.question('Enter search query: ', async (query) => {
          await webSearch(query);
          showMenu();
        });
        break;
      case '4':
        rl.question('Enter URL to fetch: ', async (url) => {
          await webFetch(url);
          showMenu();
        });
        break;
      case '0':
        console.log('Exiting...');
        rl.close();
        break;
      default:
        console.log('Invalid choice. Please try again.');
        showMenu();
        break;
    }
  });
}

// Start the application
console.log('Starting DevDocs MCP Client...');
console.log(`MCP Server URL: ${MCP_SERVER_URL}`);
showMenu();
