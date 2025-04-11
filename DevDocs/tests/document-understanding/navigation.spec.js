const { test, expect } = require('@playwright/test');

test.describe('Navigation and Routing', () => {
  test('should navigate to document demo page', async ({ page }) => {
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Check if the page title is displayed
    await expect(page.locator('h1')).toContainText('Document Understanding Demo');
  });

  test('should navigate to Messos demo page', async ({ page }) => {
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Check if the page title is displayed
    await expect(page.locator('h1')).toContainText('Messos Financial Document Analysis');
  });

  test('should handle direct URL access to document demo page', async ({ page }) => {
    // Navigate directly to the document demo page
    await page.goto('/document-demo');
    
    // Check if the page loads correctly
    await expect(page.locator('text=Upload Financial Document')).toBeVisible();
  });

  test('should handle direct URL access to Messos demo page', async ({ page }) => {
    // Navigate directly to the Messos demo page
    await page.goto('/messos-demo');
    
    // Check if the page loads correctly
    await expect(page.locator('text=Messos Financial Document')).toBeVisible();
  });

  test('should handle page refresh on document demo page', async ({ page }) => {
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Refresh the page
    await page.reload();
    
    // Check if the page loads correctly after refresh
    await expect(page.locator('text=Upload Financial Document')).toBeVisible();
  });

  test('should handle page refresh on Messos demo page', async ({ page }) => {
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Refresh the page
    await page.reload();
    
    // Check if the page loads correctly after refresh
    await expect(page.locator('text=Messos Financial Document')).toBeVisible();
  });

  test('should handle browser back and forward navigation', async ({ page }) => {
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Go back to the document demo page
    await page.goBack();
    await expect(page.locator('h1')).toContainText('Document Understanding Demo');
    
    // Go forward to the Messos demo page
    await page.goForward();
    await expect(page.locator('h1')).toContainText('Messos Financial Document Analysis');
  });
});
