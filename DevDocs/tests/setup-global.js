const { setupServer } = require('./setup');

/**
 * Global setup for Playwright tests
 */
async function globalSetup() {
  console.log('Running global setup...');
  
  // Ensure server is running
  await setupServer();
  
  return async () => {
    // This runs after all tests
    console.log('All tests completed.');
  };
}

module.exports = globalSetup;
