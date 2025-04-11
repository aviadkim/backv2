const { cleanupServer } = require('./setup');

/**
 * Global teardown for Playwright tests
 */
async function globalTeardown() {
  console.log('Running global teardown...');
  
  // Cleanup server if needed
  await cleanupServer();
}

module.exports = globalTeardown;
