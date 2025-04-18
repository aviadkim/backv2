/**
 * Test script for API endpoints
 * 
 * This script tests the API endpoints by making requests to them
 * and verifying the responses.
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');
const FormData = require('form-data');

// API base URL
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

// Sample document path
const sampleDocPath = path.join(__dirname, 'samples', 'sample-portfolio.pdf');

// Check if sample document exists
if (!fs.existsSync(sampleDocPath)) {
  console.error(`Sample document not found: ${sampleDocPath}`);
  console.error('Please make sure the sample document exists before running the test.');
  process.exit(1);
}

// Test API endpoints
async function testApiEndpoints() {
  console.log('Testing API endpoints...');
  
  try {
    // Test process-document endpoint
    console.log('\n=== Testing /api/financial/process-document endpoint ===\n');
    
    // Create form data
    const formData = new FormData();
    formData.append('file', fs.createReadStream(sampleDocPath));
    formData.append('document_type', 'portfolio');
    
    // Make request
    const response = await axios.post(`${API_BASE_URL}/api/financial/process-document`, formData, {
      headers: {
        ...formData.getHeaders()
      }
    });
    
    // Verify response
    console.log(`Status: ${response.status}`);
    
    if (response.status !== 200) {
      console.error(`❌ Expected status 200, got ${response.status}`);
      return false;
    }
    
    console.log('✅ Status is 200');
    
    // Check if response has expected properties
    const expectedProperties = ['jobId', 'documentType', 'extractedText', 'tables', 'isins', 'financialData'];
    
    for (const prop of expectedProperties) {
      if (!(prop in response.data)) {
        console.error(`❌ Response is missing property: ${prop}`);
        return false;
      }
    }
    
    console.log(`✅ Response has all expected properties: ${expectedProperties.join(', ')}`);
    
    // Check if tables were extracted
    console.log(`\nTables: ${response.data.tables.length}`);
    if (response.data.tables.length === 0) {
      console.error('❌ No tables were extracted');
    } else {
      console.log('✅ Tables were extracted');
    }
    
    // Check if ISINs were extracted
    console.log(`\nISINs: ${response.data.isins.length}`);
    if (response.data.isins.length === 0) {
      console.error('❌ No ISINs were extracted');
    } else {
      console.log('✅ ISINs were extracted');
    }
    
    // Check if portfolio value was extracted
    console.log(`\nPortfolio Value: ${response.data.financialData.portfolio_value}`);
    if (!response.data.financialData.portfolio_value) {
      console.error('❌ Portfolio value was not extracted');
    } else {
      console.log('✅ Portfolio value was extracted');
    }
    
    console.log('\n=== Test Completed ===\n');
    
    // Return success
    return true;
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
    
    return false;
  }
}

// Run the test
testApiEndpoints()
  .then(success => {
    if (success) {
      console.log('✅ API endpoints test completed successfully');
      process.exit(0);
    } else {
      console.error('❌ API endpoints test failed');
      process.exit(1);
    }
  })
  .catch(error => {
    console.error('❌ Unexpected error:', error);
    process.exit(1);
  });
