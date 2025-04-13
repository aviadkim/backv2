const axios = require('axios');

// Configuration
const MCP_SERVER_URL = 'https://mcp-server-678297464867.me-west1.run.app';

// Function to make MCP requests
async function mcpRequest(action, parameters = {}) {
  try {
    const response = await axios.post(`${MCP_SERVER_URL}/mcp`, {
      action,
      parameters
    });
    
    return response.data;
  } catch (error) {
    console.error(`Error making MCP request for action ${action}:`, error.message);
    throw new Error(`MCP request failed: ${error.message}`);
  }
}

// Example usage
async function testMCP() {
  try {
    // Test listBuckets
    console.log('Testing listBuckets...');
    const bucketsResult = await mcpRequest('listBuckets');
    console.log('Buckets:', bucketsResult);
    
    // Test webSearch
    console.log('\nTesting webSearch...');
    const searchResult = await mcpRequest('webSearch', { query: 'Google Cloud DevDocs' });
    console.log('Search results:', searchResult);
    
    // Test webFetch
    console.log('\nTesting webFetch...');
    const fetchResult = await mcpRequest('webFetch', { url: 'https://cloud.google.com/' });
    console.log('Fetch result:', fetchResult);
  } catch (error) {
    console.error('Error testing MCP:', error.message);
  }
}

// Run the test
testMCP();
