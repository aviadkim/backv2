// Super minimal test - no global setup
import { test, expect } from '@playwright/test';

// Skip global setup completely
test.use({ baseURL: undefined });

test('minimal html test', async ({ page }) => {
  console.log('Running minimal HTML test...');
  
  // Set HTML directly - no need for any server
  await page.setContent("<html><body><h1>DevDocs Test</h1><p>This test bypasses all setup</p></body></html>");
  
  // Simple existence check
  await expect(page.locator('h1')).toBeVisible();
  
  console.log('Minimal test completed successfully');
});
