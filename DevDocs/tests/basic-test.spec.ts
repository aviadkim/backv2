import { test, expect } from '@playwright/test';

// A very basic test that doesn't require any server or complex setup
test('basic test - no server required', async ({ page }) => {
  console.log('Starting basic test...');
  
  // Create a simple HTML page directly in the browser
  await page.setContent('<html><body><h1>Basic Test Page</h1><p>This is a test</p></body></html>');
  
  // Check if content is visible
  await expect(page.locator('h1')).toContainText('Basic Test');
  
  console.log('Basic test completed successfully');
});

// Additional simple test
test('simple math test', () => {
  console.log('Running simple math test...');
  expect(1 + 1).toBe(2);
  console.log('Math test passed');
});
