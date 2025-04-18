/**
 * Test runner script
 * 
 * This script runs all the tests in the tests directory.
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// Get all test files
const testFiles = fs.readdirSync(__dirname)
  .filter(file => file.startsWith('test-') && file.endsWith('.js'));

// Results tracking
const results = {
  total: testFiles.length,
  passed: 0,
  failed: 0,
  skipped: 0
};

// Run each test
async function runTests() {
  console.log(`Found ${testFiles.length} test files\n`);
  
  for (const testFile of testFiles) {
    const testPath = path.join(__dirname, testFile);
    const testName = testFile.replace(/^test-/, '').replace(/\.js$/, '');
    
    console.log(`Running test: ${testName}`);
    
    try {
      // Run the test
      const result = await runTest(testPath);
      
      if (result.success) {
        console.log(`✅ Test passed: ${testName}\n`);
        results.passed++;
      } else {
        console.error(`❌ Test failed: ${testName}`);
        console.error(`Error: ${result.error}\n`);
        results.failed++;
      }
    } catch (error) {
      console.error(`❌ Error running test: ${testName}`);
      console.error(`Error: ${error.message}\n`);
      results.failed++;
    }
  }
  
  // Print results
  console.log('=== Test Results ===');
  console.log(`Total: ${results.total}`);
  console.log(`Passed: ${results.passed}`);
  console.log(`Failed: ${results.failed}`);
  console.log(`Skipped: ${results.skipped}`);
  
  // Exit with appropriate code
  process.exit(results.failed > 0 ? 1 : 0);
}

// Run a single test
function runTest(testPath) {
  return new Promise((resolve, reject) => {
    const test = spawn('node', [testPath]);
    
    let output = '';
    let error = '';
    
    test.stdout.on('data', (data) => {
      output += data.toString();
      process.stdout.write(data);
    });
    
    test.stderr.on('data', (data) => {
      error += data.toString();
      process.stderr.write(data);
    });
    
    test.on('close', (code) => {
      if (code === 0) {
        resolve({ success: true, output });
      } else {
        resolve({ success: false, error: error || 'Test exited with non-zero code' });
      }
    });
    
    test.on('error', (err) => {
      reject(err);
    });
  });
}

// Run the tests
runTests().catch(error => {
  console.error('Error running tests:', error);
  process.exit(1);
});
