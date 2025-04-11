const { test, expect } = require('@playwright/test');

test.describe('Integration Tests', () => {
  test('should process document and display analysis results', async ({ page }) => {
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
    
    // Check if analysis results are displayed
    await expect(page.locator('text=Analysis Results')).toBeVisible();
    await expect(page.locator('text=Document Information')).toBeVisible();
    await expect(page.locator('text=Company Information')).toBeVisible();
    await expect(page.locator('text=Financial Metrics')).toBeVisible();
    await expect(page.locator('text=Financial Ratios')).toBeVisible();
  });

  test('should analyze Messos document and display results', async ({ page }) => {
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Click the analyze button
    await page.click('button', { hasText: 'Analyze Document' });
    
    // Check if analysis results are displayed
    await expect(page.locator('text=Analysis Results')).toBeVisible();
    await expect(page.locator('text=Document Information')).toBeVisible();
    await expect(page.locator('text=Company Information')).toBeVisible();
    await expect(page.locator('text=Financial Metrics')).toBeVisible();
    await expect(page.locator('text=Financial Ratios')).toBeVisible();
  });

  test('should handle the complete document processing workflow', async ({ page }) => {
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
    
    // Check if the file name is displayed
    await expect(page.locator('text=financial-report.pdf')).toBeVisible();
    
    // Click the process button
    await page.click('text=Process Document');
    
    // Check if processing indicator is shown
    await expect(page.locator('text=Processing document...')).toBeVisible();
    
    // Wait for processing to complete
    await expect(page.locator('text=Document processed successfully!')).toBeVisible({ timeout: 10000 });
    
    // Check if analysis results are displayed
    await expect(page.locator('text=Analysis Results')).toBeVisible();
    
    // Click the "Upload Another Document" button
    await page.click('text=Upload Another Document');
    
    // Check if the upload interface is reset
    await expect(page.locator('text=Drag and drop your file here, or browse')).toBeVisible();
  });

  test('should handle the complete Messos document analysis workflow', async ({ page }) => {
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Check if the PDF viewer is displayed
    await expect(page.locator('iframe[src="/messos.pdf"]')).toBeVisible();
    
    // Click the analyze button
    await page.click('button', { hasText: 'Analyze Document' });
    
    // Check if analysis results are displayed
    await expect(page.locator('text=Analysis Results')).toBeVisible();
    
    // Check if document information is displayed
    await expect(page.locator('text=Document Information')).toBeVisible();
    await expect(page.locator('text=Messos 28.02.2025.pdf')).toBeVisible();
    
    // Check if company information is displayed
    await expect(page.locator('text=Company Information')).toBeVisible();
    await expect(page.locator('text=Messos Group')).toBeVisible();
    
    // Check if financial metrics are displayed
    await expect(page.locator('text=Financial Metrics')).toBeVisible();
    await expect(page.locator('text=Revenue')).toBeVisible();
    await expect(page.locator('text=€1,234,567')).toBeVisible();
    
    // Check if financial ratios are displayed
    await expect(page.locator('text=Financial Ratios')).toBeVisible();
    await expect(page.locator('text=Gross Margin')).toBeVisible();
    await expect(page.locator('text=42.5%')).toBeVisible();
  });

  test('should navigate between document demo and Messos demo pages', async ({ page }) => {
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Check if the page title is displayed
    await expect(page.locator('h1')).toContainText('Document Understanding Demo');
    
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Check if the page title is displayed
    await expect(page.locator('h1')).toContainText('Messos Financial Document Analysis');
    
    // Go back to the document demo page
    await page.goBack();
    
    // Check if the page title is displayed
    await expect(page.locator('h1')).toContainText('Document Understanding Demo');
  });
});
