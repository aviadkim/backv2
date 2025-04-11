const { test, expect } = require('@playwright/test');

test.describe('Performance', () => {
  test('should load document demo page quickly', async ({ page }) => {
    // Measure the time it takes to load the document demo page
    const startTime = Date.now();
    
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Wait for the page to be fully loaded
    await page.waitForSelector('text=Upload Financial Document');
    
    const loadTime = Date.now() - startTime;
    
    // Check if the page loads within a reasonable time (5 seconds)
    expect(loadTime).toBeLessThan(5000);
  });

  test('should load Messos demo page quickly', async ({ page }) => {
    // Measure the time it takes to load the Messos demo page
    const startTime = Date.now();
    
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Wait for the page to be fully loaded
    await page.waitForSelector('text=Messos Financial Document');
    
    const loadTime = Date.now() - startTime;
    
    // Check if the page loads within a reasonable time (5 seconds)
    expect(loadTime).toBeLessThan(5000);
  });

  test('should process document quickly on document demo page', async ({ page }) => {
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
    
    // Measure the time it takes to process the document
    const startTime = Date.now();
    
    // Click the process button
    await page.click('text=Process Document');
    
    // Wait for processing to complete
    await expect(page.locator('text=Document processed successfully!')).toBeVisible({ timeout: 10000 });
    
    const processTime = Date.now() - startTime;
    
    // Check if the document is processed within a reasonable time (5 seconds)
    expect(processTime).toBeLessThan(5000);
  });

  test('should analyze document quickly on Messos demo page', async ({ page }) => {
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Measure the time it takes to analyze the document
    const startTime = Date.now();
    
    // Click the analyze button
    await page.click('button', { hasText: 'Analyze Document' });
    
    // Wait for analysis to complete
    await expect(page.locator('text=Analysis Results')).toBeVisible({ timeout: 10000 });
    
    const analyzeTime = Date.now() - startTime;
    
    // Check if the document is analyzed within a reasonable time (3 seconds)
    expect(analyzeTime).toBeLessThan(3000);
  });

  test('should render large tables efficiently on document demo page', async ({ page }) => {
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
    
    // Measure the time it takes to render the tables
    const startTime = Date.now();
    
    // Force a re-render of the tables
    await page.evaluate(() => {
      window.dispatchEvent(new Event('resize'));
    });
    
    // Wait for the tables to be rendered
    await page.waitForSelector('table');
    
    const renderTime = Date.now() - startTime;
    
    // Check if the tables are rendered within a reasonable time (1 second)
    expect(renderTime).toBeLessThan(1000);
  });

  test('should handle multiple document uploads efficiently', async ({ page }) => {
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Process 3 documents in sequence
    for (let i = 0; i < 3; i++) {
      // Create a mock file and set it as the selected file
      await page.evaluate((index) => {
        const mockFile = new File(['test content'], `financial-report-${index}.pdf`, { type: 'application/pdf' });
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(mockFile);
        
        const fileInput = document.querySelector('input[type="file"]');
        fileInput.files = dataTransfer.files;
        
        // Dispatch change event
        fileInput.dispatchEvent(new Event('change', { bubbles: true }));
      }, i);
      
      // Click the process button
      await page.click('text=Process Document');
      
      // Wait for processing to complete
      await expect(page.locator('text=Document processed successfully!')).toBeVisible({ timeout: 10000 });
      
      // Click the "Upload Another Document" button
      await page.click('text=Upload Another Document');
      
      // Check if the upload interface is reset
      await expect(page.locator('text=Drag and drop your file here, or browse')).toBeVisible();
    }
  });
});
