const { test, expect } = require('@playwright/test');

test.describe('Responsive Design', () => {
  test('should display correctly on mobile viewport', async ({ page }) => {
    // Set viewport to mobile size
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Check if the page title is displayed
    await expect(page.locator('h1')).toContainText('Document Understanding Demo');
    
    // Check if the upload interface is visible
    await expect(page.locator('text=Upload Financial Document')).toBeVisible();
  });

  test('should display correctly on tablet viewport', async ({ page }) => {
    // Set viewport to tablet size
    await page.setViewportSize({ width: 768, height: 1024 });
    
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Check if the page title is displayed
    await expect(page.locator('h1')).toContainText('Document Understanding Demo');
    
    // Check if the upload interface is visible
    await expect(page.locator('text=Upload Financial Document')).toBeVisible();
  });

  test('should display correctly on desktop viewport', async ({ page }) => {
    // Set viewport to desktop size
    await page.setViewportSize({ width: 1280, height: 800 });
    
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Check if the page title is displayed
    await expect(page.locator('h1')).toContainText('Document Understanding Demo');
    
    // Check if the upload interface is visible
    await expect(page.locator('text=Upload Financial Document')).toBeVisible();
  });

  test('should display Messos demo correctly on mobile viewport', async ({ page }) => {
    // Set viewport to mobile size
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Check if the page title is displayed
    await expect(page.locator('h1')).toContainText('Messos Financial Document Analysis');
    
    // Check if the PDF viewer is visible
    await expect(page.locator('text=Messos Financial Document')).toBeVisible();
  });

  test('should display Messos demo correctly on tablet viewport', async ({ page }) => {
    // Set viewport to tablet size
    await page.setViewportSize({ width: 768, height: 1024 });
    
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Check if the page title is displayed
    await expect(page.locator('h1')).toContainText('Messos Financial Document Analysis');
    
    // Check if the PDF viewer is visible
    await expect(page.locator('text=Messos Financial Document')).toBeVisible();
  });

  test('should display Messos demo correctly on desktop viewport', async ({ page }) => {
    // Set viewport to desktop size
    await page.setViewportSize({ width: 1280, height: 800 });
    
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Check if the page title is displayed
    await expect(page.locator('h1')).toContainText('Messos Financial Document Analysis');
    
    // Check if the PDF viewer is visible
    await expect(page.locator('text=Messos Financial Document')).toBeVisible();
  });

  test('should have responsive layout on document demo page', async ({ page }) => {
    // Set viewport to mobile size
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Create a mock file and set it as the selected file
    await page.evaluate(() => {
      const mockFile = new File(['test content'], 'financial-report.pdf', { type: 'application/pdf' });
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(mockFile);
      
      const fileInput = document.querySelector('input[type="file"]');
      fileInput.files = dataTransfer.files;
      
      // Dispatch change event
      fileInput.dispatchEvent(new Event('change', { bubbles: true }));
    });
    
    // Click the process button
    await page.click('text=Process Document');
    
    // Wait for processing to complete
    await expect(page.locator('text=Document processed successfully!')).toBeVisible({ timeout: 10000 });
    
    // Check if analysis results are displayed in a single column
    const analysisResults = page.locator('text=Analysis Results').first();
    await expect(analysisResults).toBeVisible();
    
    // Set viewport to desktop size
    await page.setViewportSize({ width: 1280, height: 800 });
    
    // Check if analysis results are still visible
    await expect(analysisResults).toBeVisible();
  });

  test('should have responsive layout on Messos demo page', async ({ page }) => {
    // Set viewport to mobile size
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Click the analyze button
    await page.click('button', { hasText: 'Analyze Document' });
    
    // Check if analysis results are displayed
    await expect(page.locator('text=Analysis Results')).toBeVisible();
    
    // Set viewport to desktop size
    await page.setViewportSize({ width: 1280, height: 800 });
    
    // Check if analysis results are still visible
    await expect(page.locator('text=Analysis Results')).toBeVisible();
  });
});
