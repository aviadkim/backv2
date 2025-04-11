const { test, expect } = require('@playwright/test');

test.describe('Localization', () => {
  test('should display currency values in the correct format', async ({ page }) => {
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
    
    // Check if currency values are formatted correctly
    const revenueValue = page.locator('tr').filter({ hasText: 'Revenue' }).locator('td').nth(1);
    await expect(revenueValue).toContainText('$');
    await expect(revenueValue).toContainText(',');
  });

  test('should display percentage values in the correct format', async ({ page }) => {
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
    
    // Check if percentage values are formatted correctly
    const grossMarginValue = page.locator('tr').filter({ hasText: 'Gross Margin' }).locator('td').nth(1);
    await expect(grossMarginValue).toContainText('%');
  });

  test('should display date values in the correct format', async ({ page }) => {
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Click the analyze button
    await page.click('button', { hasText: 'Analyze Document' });
    
    // Check if date values are formatted correctly
    await expect(page.locator('text=2025')).toBeVisible();
  });

  test('should display Euro currency values in the correct format on Messos demo page', async ({ page }) => {
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Click the analyze button
    await page.click('button', { hasText: 'Analyze Document' });
    
    // Check if Euro currency values are formatted correctly
    await expect(page.locator('text=€1,234,567')).toBeVisible();
  });

  test('should handle different number formats correctly', async ({ page }) => {
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
    
    // Check if large numbers are formatted with commas
    const revenueValue = page.locator('tr').filter({ hasText: 'Revenue' }).locator('td').nth(1);
    await expect(revenueValue).toContainText(',');
  });
});
