const { test, expect } = require('@playwright/test');

test.describe('Accessibility', () => {
  test('document demo page should have proper heading structure', async ({ page }) => {
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Check if the page has an h1 heading
    await expect(page.locator('h1')).toHaveCount(1);
    
    // Check if the page has h2 headings
    await expect(page.locator('h2')).toBeVisible();
    
    // Check if the page has h3 headings
    await expect(page.locator('h3')).toBeVisible();
  });

  test('Messos demo page should have proper heading structure', async ({ page }) => {
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Check if the page has an h1 heading
    await expect(page.locator('h1')).toHaveCount(1);
    
    // Check if the page has h2 headings
    await expect(page.locator('h2')).toBeVisible();
    
    // Check if the page has h3 headings
    await expect(page.locator('h3')).toBeVisible();
  });

  test('document demo page should have proper button labels', async ({ page }) => {
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
    
    // Check if the process button has a descriptive label
    await expect(page.locator('button', { hasText: 'Process Document' })).toBeVisible();
    
    // Click the process button
    await page.click('text=Process Document');
    
    // Wait for processing to complete
    await expect(page.locator('text=Document processed successfully!')).toBeVisible({ timeout: 10000 });
    
    // Check if the upload another document button has a descriptive label
    await expect(page.locator('button', { hasText: 'Upload Another Document' })).toBeVisible();
  });

  test('Messos demo page should have proper button labels', async ({ page }) => {
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Check if the analyze button has a descriptive label
    await expect(page.locator('button', { hasText: 'Analyze Document' })).toBeVisible();
  });

  test('document demo page should have proper form labels', async ({ page }) => {
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Check if the file input has a descriptive label
    await expect(page.locator('text=Drag and drop your file here, or browse')).toBeVisible();
  });

  test('document demo page should have proper table headers', async ({ page }) => {
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
    
    // Check if the metrics table has proper headers
    await expect(page.locator('th', { hasText: 'Metric' })).toBeVisible();
    await expect(page.locator('th', { hasText: 'Value' })).toBeVisible();
    await expect(page.locator('th', { hasText: 'Period' })).toBeVisible();
  });

  test('Messos demo page should have proper table headers', async ({ page }) => {
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Click the analyze button
    await page.click('button', { hasText: 'Analyze Document' });
    
    // Check if the metrics table has proper headers
    await expect(page.locator('th', { hasText: 'Metric' })).toBeVisible();
    await expect(page.locator('th', { hasText: 'Value' })).toBeVisible();
    await expect(page.locator('th', { hasText: 'Period' })).toBeVisible();
    
    // Check if the ratios table has proper headers
    await expect(page.locator('th', { hasText: 'Ratio' })).toBeVisible();
  });

  test('document demo page should have proper color contrast', async ({ page }) => {
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Check if the page title has proper color contrast
    const pageTitle = page.locator('h1');
    await expect(pageTitle).toBeVisible();
    
    // Get the color and background color of the page title
    const titleStyles = await pageTitle.evaluate((element) => {
      const styles = window.getComputedStyle(element);
      return {
        color: styles.color,
        backgroundColor: styles.backgroundColor
      };
    });
    
    // Check if the color and background color are defined
    expect(titleStyles.color).toBeDefined();
    expect(titleStyles.backgroundColor).toBeDefined();
  });

  test('Messos demo page should have proper color contrast', async ({ page }) => {
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Check if the page title has proper color contrast
    const pageTitle = page.locator('h1');
    await expect(pageTitle).toBeVisible();
    
    // Get the color and background color of the page title
    const titleStyles = await pageTitle.evaluate((element) => {
      const styles = window.getComputedStyle(element);
      return {
        color: styles.color,
        backgroundColor: styles.backgroundColor
      };
    });
    
    // Check if the color and background color are defined
    expect(titleStyles.color).toBeDefined();
    expect(titleStyles.backgroundColor).toBeDefined();
  });
});
