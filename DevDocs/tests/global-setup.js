/**
 * Global setup for Playwright tests
 */
async function globalSetup() {
  console.log('Setting up global test configuration...');
  
  // You can add any global setup here
  // For example, preparing test data, setting up mocks, etc.
  
  return async () => {
    // Teardown function
    console.log('Test run complete, cleaning up...');
  };
}

module.exports = globalSetup;
