/**
 * Helper functions for tests
 */

/**
 * Wait for page to be in ready state
 */
async function waitForPageReady(page) {
  await page.waitForFunction(() => {
    return document.readyState === 'complete';
  }, { timeout: 10000 }).catch(() => {
    console.log('Page readyState wait timed out, continuing anyway');
  });
}

/**
 * Try to navigate to a page with retries
 */
async function navigateTo(page, url, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      await page.goto(url, { timeout: 10000 });
      await waitForPageReady(page);
      return true;
    } catch (error) {
      console.log(`Navigation to ${url} failed (attempt ${i + 1}/${maxRetries}): ${error.message}`);
      if (i === maxRetries - 1) {
        throw error;
      }
      // Brief pause before retry
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
  return false;
}

/**
 * Setup error handling for a page
 */
function setupErrorHandling(page) {
  page.on('pageerror', error => {
    console.error(`Page error: ${error.message}`);
  });
  
  page.on('console', msg => {
    if (msg.type() === 'error' && (
      msg.text().includes('LaunchDarkly') ||
      msg.text().includes('Failed to load resource')
    )) {
      return;
    }
    console.log(`Console ${msg.type()}: ${msg.text()}`);
  });
  
  page.on('requestfailed', request => {
    console.log(`Request failed: ${request.url()}`);
  });
}

module.exports = {
  waitForPageReady,
  navigateTo,
  setupErrorHandling
};
