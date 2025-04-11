/**
 * Test MCP Integration
 * This script tests the MCP integration with Google Cloud
 */

const { gcp } = require('./mcp');

async function testMcpIntegration() {
  try {
    console.log('Testing MCP integration with Google Cloud...');
    
    // Test listBuckets
    console.log('\nListing buckets...');
    const buckets = await gcp.listBuckets();
    console.log('Buckets:', buckets);
    
    // Test webSearch
    console.log('\nSearching the web...');
    const searchResults = await gcp.webSearch('Google Cloud MCP integration');
    console.log('Search results:', searchResults);
    
    // Test webFetch
    console.log('\nFetching web content...');
    const webContent = await gcp.webFetch('https://cloud.google.com/');
    console.log('Web content title:', webContent.title);
    console.log('Web content URL:', webContent.url);
    
    console.log('\nMCP integration test completed successfully!');
  } catch (error) {
    console.error('Error testing MCP integration:', error);
  }
}

// Run the test
testMcpIntegration();
