const axios = require('axios');

// Configuration
const MCP_SERVER_URL = 'https://devdocs-mcp-server-678297464867.me-west1.run.app/mcp';

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

// Test functions
async function testListBuckets() {
  console.log('\n=== Testing listBuckets ===');
  try {
    const response = await mcpRequest('listBuckets');
    console.log('Response:', JSON.stringify(response, null, 2));
    return response.success;
  } catch (error) {
    console.error('Error:', error.message);
    return false;
  }
}

async function testListFiles() {
  console.log('\n=== Testing listFiles ===');
  try {
    const response = await mcpRequest('listFiles', { bucketName: 'devdocs-bucket' });
    console.log('Response:', JSON.stringify(response, null, 2));
    return response.success;
  } catch (error) {
    console.error('Error:', error.message);
    return false;
  }
}

async function testWebSearch() {
  console.log('\n=== Testing webSearch ===');
  try {
    const response = await mcpRequest('webSearch', { query: 'Google Cloud DevDocs' });
    console.log('Response:', JSON.stringify(response, null, 2));
    return response.success;
  } catch (error) {
    console.error('Error:', error.message);
    return false;
  }
}

async function testWebFetch() {
  console.log('\n=== Testing webFetch ===');
  try {
    const response = await mcpRequest('webFetch', { url: 'https://cloud.google.com/' });
    console.log('Response title:', response.result.title);
    console.log('Response content length:', response.result.content.length);
    return response.success;
  } catch (error) {
    console.error('Error:', error.message);
    return false;
  }
}

// Run all tests
async function runTests() {
  console.log('Starting MCP server tests...');
  console.log(`MCP Server URL: ${MCP_SERVER_URL}`);
  
  let success = true;
  
  // Test listBuckets
  if (!(await testListBuckets())) {
    success = false;
  }
  
  // Test listFiles
  if (!(await testListFiles())) {
    success = false;
  }
  
  // Test webSearch
  if (!(await testWebSearch())) {
    success = false;
  }
  
  // Test webFetch
  if (!(await testWebFetch())) {
    success = false;
  }
  
  console.log('\n=== Test Results ===');
  if (success) {
    console.log('All tests passed!');
  } else {
    console.error('Some tests failed!');
  }
}

// Run the tests
runTests();
