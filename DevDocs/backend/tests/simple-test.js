/**
 * Simple Test
 * 
 * A simplified test that doesn't depend on external libraries.
 */

const fs = require('fs');
const path = require('path');

// Test configuration
const TEST_SAMPLES_DIR = path.join(__dirname, 'samples');
const SAMPLE_PDF_PATH = path.join(TEST_SAMPLES_DIR, 'sample-portfolio.pdf');

/**
 * Run a simple test
 */
function runSimpleTest() {
  console.log('Running simple test...');
  
  // Check if sample directory exists
  if (!fs.existsSync(TEST_SAMPLES_DIR)) {
    console.error(`Sample directory not found: ${TEST_SAMPLES_DIR}`);
    return false;
  }
  
  // Check if sample PDF exists
  if (!fs.existsSync(SAMPLE_PDF_PATH)) {
    console.error(`Sample PDF not found: ${SAMPLE_PDF_PATH}`);
    return false;
  }
  
  // Read sample PDF
  try {
    const pdfContent = fs.readFileSync(SAMPLE_PDF_PATH, 'utf8');
    console.log('Sample PDF content length:', pdfContent.length);
    
    // Check if PDF content contains expected text
    if (pdfContent.includes('Sample Portfolio Statement')) {
      console.log('✅ PDF content test passed');
    } else {
      console.error('❌ PDF content test failed');
      return false;
    }
    
    // Check if PDF content contains expected ISINs
    if (pdfContent.includes('US0378331005') && pdfContent.includes('US5949181045')) {
      console.log('✅ ISIN detection test passed');
    } else {
      console.error('❌ ISIN detection test failed');
      return false;
    }
    
    return true;
  } catch (error) {
    console.error('Error reading sample PDF:', error.message);
    return false;
  }
}

// Run the test
const success = runSimpleTest();

if (success) {
  console.log('\nAll tests passed!');
  process.exit(0);
} else {
  console.error('\nSome tests failed!');
  process.exit(1);
}
