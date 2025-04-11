const { test, expect } = require('@playwright/test');

test.describe('Error Handling', () => {
  test('should handle invalid file types on document demo page', async ({ page }) => {
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Create an invalid mock file and set it as the selected file
    await page.evaluate(() => {
      const mockFile = new File(['test content'], 'invalid-document.txt', { type: 'text/plain' });
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(mockFile);
      
      const fileInput = document.querySelector('input[type="file"]');
      fileInput.files = dataTransfer.files;
      
      // Dispatch change event
      fileInput.dispatchEvent(new Event('change', { bubbles: true }));
    });
    
    // Check if validation error is displayed
    await expect(page.locator('text=Invalid file type. Please upload a PDF, Excel, or CSV file.')).toBeVisible();
    
    // Check if the process button is disabled
    const processButton = page.locator('text=Process Document');
    await expect(processButton).toHaveClass(/bg-gray-400/);
  });

  test('should handle empty file selection on document demo page', async ({ page }) => {
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Check if the process button is not visible when no file is selected
    await expect(page.locator('text=Process Document')).not.toBeVisible();
  });

  test('should handle processing errors on document demo page', async ({ page }) => {
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Create a mock file and set it as the selected file
    await page.evaluate(() => {
      const mockFile = new File(['test content'], 'error-document.pdf', { type: 'application/pdf' });
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(mockFile);
      
      const fileInput = document.querySelector('input[type="file"]');
      fileInput.files = dataTransfer.files;
      
      // Dispatch change event
      fileInput.dispatchEvent(new Event('change', { bubbles: true }));
    });
    
    // Mock an error response for the upload
    await page.route('**/api/documents/process-and-analyze', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Error processing document' })
      });
    });
    
    // Click the process button
    await page.click('text=Process Document');
    
    // Check if error message is displayed
    await expect(page.locator('text=Error processing document')).toBeVisible();
  });

  test('should handle network errors on document demo page', async ({ page }) => {
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Create a mock file and set it as the selected file
    await page.evaluate(() => {
      const mockFile = new File(['test content'], 'network-error-document.pdf', { type: 'application/pdf' });
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(mockFile);
      
      const fileInput = document.querySelector('input[type="file"]');
      fileInput.files = dataTransfer.files;
      
      // Dispatch change event
      fileInput.dispatchEvent(new Event('change', { bubbles: true }));
    });
    
    // Mock a network error for the upload
    await page.route('**/api/documents/process-and-analyze', async (route) => {
      await route.abort('failed');
    });
    
    // Click the process button
    await page.click('text=Process Document');
    
    // Check if error message is displayed
    await expect(page.locator('text=Error processing document')).toBeVisible();
  });

  test('should handle timeout errors on document demo page', async ({ page }) => {
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Create a mock file and set it as the selected file
    await page.evaluate(() => {
      const mockFile = new File(['test content'], 'timeout-document.pdf', { type: 'application/pdf' });
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(mockFile);
      
      const fileInput = document.querySelector('input[type="file"]');
      fileInput.files = dataTransfer.files;
      
      // Dispatch change event
      fileInput.dispatchEvent(new Event('change', { bubbles: true }));
    });
    
    // Mock a timeout error for the upload
    await page.route('**/api/documents/process-and-analyze', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 30000));
      await route.fulfill({
        status: 408,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Request timeout' })
      });
    });
    
    // Click the process button
    await page.click('text=Process Document');
    
    // Check if processing indicator is shown
    await expect(page.locator('text=Processing document...')).toBeVisible();
  });

  test('should handle server errors on document demo page', async ({ page }) => {
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Create a mock file and set it as the selected file
    await page.evaluate(() => {
      const mockFile = new File(['test content'], 'server-error-document.pdf', { type: 'application/pdf' });
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(mockFile);
      
      const fileInput = document.querySelector('input[type="file"]');
      fileInput.files = dataTransfer.files;
      
      // Dispatch change event
      fileInput.dispatchEvent(new Event('change', { bubbles: true }));
    });
    
    // Mock a server error for the upload
    await page.route('**/api/documents/process-and-analyze', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' })
      });
    });
    
    // Click the process button
    await page.click('text=Process Document');
    
    // Check if error message is displayed
    await expect(page.locator('text=Internal server error')).toBeVisible();
  });

  test('should handle client errors on document demo page', async ({ page }) => {
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Create a mock file and set it as the selected file
    await page.evaluate(() => {
      const mockFile = new File(['test content'], 'client-error-document.pdf', { type: 'application/pdf' });
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(mockFile);
      
      const fileInput = document.querySelector('input[type="file"]');
      fileInput.files = dataTransfer.files;
      
      // Dispatch change event
      fileInput.dispatchEvent(new Event('change', { bubbles: true }));
    });
    
    // Mock a client error for the upload
    await page.route('**/api/documents/process-and-analyze', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Bad request' })
      });
    });
    
    // Click the process button
    await page.click('text=Process Document');
    
    // Check if error message is displayed
    await expect(page.locator('text=Bad request')).toBeVisible();
  });
});
