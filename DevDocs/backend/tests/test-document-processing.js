/**
 * Test script for document processing
 * 
 * This script tests the document processing pipeline by processing a sample document
 * and verifying the results.
 */

const fs = require('fs');
const path = require('path');
const { processDocument } = require('../services/document-processing');

// Sample document path
const sampleDocPath = path.join(__dirname, 'samples', 'sample-portfolio.pdf');

// Check if sample document exists
if (!fs.existsSync(sampleDocPath)) {
  console.error(`Sample document not found: ${sampleDocPath}`);
  console.error('Please make sure the sample document exists before running the test.');
  process.exit(1);
}

// Test document processing
async function testDocumentProcessing() {
  console.log('Testing document processing...');
  
  try {
    // Process the document
    const result = await processDocument({
      filePath: sampleDocPath,
      documentType: 'portfolio',
      language: 'en',
      useAI: true,
      metadata: {
        originalFilename: 'sample-portfolio.pdf',
        mimeType: 'application/pdf',
        size: fs.statSync(sampleDocPath).size
      }
    });
    
    // Verify the results
    console.log('\n=== Document Processing Results ===\n');
    
    // Check if job ID is present
    console.log(`Job ID: ${result.jobId}`);
    if (!result.jobId) {
      console.error('❌ Job ID is missing');
    } else {
      console.log('✅ Job ID is present');
    }
    
    // Check if tables were extracted
    console.log(`\nTables: ${result.tables.length}`);
    if (result.tables.length === 0) {
      console.error('❌ No tables were extracted');
    } else {
      console.log('✅ Tables were extracted');
      
      // Print table headers
      result.tables.forEach((table, index) => {
        console.log(`\nTable ${index + 1} Headers: ${table.headers.join(', ')}`);
        console.log(`Table ${index + 1} Rows: ${table.rows.length}`);
      });
    }
    
    // Check if ISINs were extracted
    console.log(`\nISINs: ${result.isins.length}`);
    if (result.isins.length === 0) {
      console.error('❌ No ISINs were extracted');
    } else {
      console.log('✅ ISINs were extracted');
      
      // Print ISINs
      result.isins.forEach((isin, index) => {
        console.log(`\nISIN ${index + 1}: ${isin.code}`);
        console.log(`Name: ${isin.name}`);
        console.log(`Value: ${isin.value}`);
      });
    }
    
    // Check if portfolio value was extracted
    console.log(`\nPortfolio Value: ${result.financialData.portfolio_value}`);
    if (!result.financialData.portfolio_value) {
      console.error('❌ Portfolio value was not extracted');
    } else {
      console.log('✅ Portfolio value was extracted');
    }
    
    // Check if asset allocation was extracted
    console.log(`\nAsset Allocation: ${Object.keys(result.financialData.asset_allocation).length} categories`);
    if (Object.keys(result.financialData.asset_allocation).length === 0) {
      console.error('❌ Asset allocation was not extracted');
    } else {
      console.log('✅ Asset allocation was extracted');
      
      // Print asset allocation
      for (const [assetClass, percentage] of Object.entries(result.financialData.asset_allocation)) {
        console.log(`${assetClass}: ${(percentage * 100).toFixed(2)}%`);
      }
    }
    
    // Check if securities were extracted
    console.log(`\nSecurities: ${result.financialData.securities.length}`);
    if (result.financialData.securities.length === 0) {
      console.error('❌ No securities were extracted');
    } else {
      console.log('✅ Securities were extracted');
      
      // Print securities
      result.financialData.securities.slice(0, 5).forEach((security, index) => {
        console.log(`\nSecurity ${index + 1}: ${security.name}`);
        console.log(`ISIN: ${security.isin}`);
        console.log(`Quantity: ${security.quantity}`);
        console.log(`Price: ${security.price}`);
        console.log(`Value: ${security.value}`);
      });
      
      if (result.financialData.securities.length > 5) {
        console.log(`\n... and ${result.financialData.securities.length - 5} more securities`);
      }
    }
    
    // Check if validation was performed
    console.log(`\nValidation: ${result.validationResult.validationStatus}`);
    console.log(`Errors: ${result.validationResult.totalErrors}`);
    console.log(`Warnings: ${result.validationResult.totalWarnings}`);
    
    console.log('\n=== Test Completed ===\n');
    
    // Return success
    return true;
  } catch (error) {
    console.error('❌ Test failed:', error);
    return false;
  }
}

// Run the test
testDocumentProcessing()
  .then(success => {
    if (success) {
      console.log('✅ Document processing test completed successfully');
      process.exit(0);
    } else {
      console.error('❌ Document processing test failed');
      process.exit(1);
    }
  })
  .catch(error => {
    console.error('❌ Unexpected error:', error);
    process.exit(1);
  });
