const axios = require('axios');

// Configuration
const MCP_SERVER_URL = 'https://devdocs-service-github-456508.me-west1.run.app/mcp';

// Test functions
async function testListBuckets() {
  console.log('Testing listBuckets...');
  try {
    const response = await axios.post(MCP_SERVER_URL, {
      action: 'listBuckets',
      parameters: {}
    });
    console.log('Success:', response.data);
    return true;
  } catch (error) {
    console.error('Error:', error.message);
    return false;
  }
}

async function testWebSearch() {
  console.log('Testing webSearch...');
  try {
    const response = await axios.post(MCP_SERVER_URL, {
      action: 'webSearch',
      parameters: {
        query: 'Google Cloud DevDocs'
      }
    });
    console.log('Success:', response.data);
    return true;
  } catch (error) {
    console.error('Error:', error.message);
    return false;
  }
}

async function testWebFetch() {
  console.log('Testing webFetch...');
  try {
    const response = await axios.post(MCP_SERVER_URL, {
      action: 'webFetch',
      parameters: {
        url: 'https://cloud.google.com/'
      }
    });
    console.log('Success:', response.data.result.title);
    return true;
  } catch (error) {
    console.error('Error:', error.message);
    return false;
  }
}

// Run all tests
async function runTests() {
  console.log('Running MCP integration tests...');
  console.log('MCP server URL:', MCP_SERVER_URL);
  
  let success = true;
  
  // Test listBuckets
  if (!(await testListBuckets())) {
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
  
  if (success) {
    console.log('All tests passed!');
  } else {
    console.error('Some tests failed!');
  }
}

// Run the tests
runTests();
