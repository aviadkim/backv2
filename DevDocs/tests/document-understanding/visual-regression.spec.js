const { test, expect } = require('@playwright/test');

test.describe('Visual Regression', () => {
  test('document demo page should match snapshot', async ({ page }) => {
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Wait for the page to be fully loaded
    await page.waitForSelector('text=Upload Financial Document');
    
    // Take a screenshot of the page
    const screenshot = await page.screenshot();
    
    // Compare the screenshot with a baseline (first run will create the baseline)
    expect(screenshot).toMatchSnapshot('document-demo.png');
  });

  test('Messos demo page should match snapshot', async ({ page }) => {
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Wait for the page to be fully loaded
    await page.waitForSelector('text=Messos Financial Document');
    
    // Take a screenshot of the page
    const screenshot = await page.screenshot();
    
    // Compare the screenshot with a baseline (first run will create the baseline)
    expect(screenshot).toMatchSnapshot('messos-demo.png');
  });

  test('document upload interface should match snapshot', async ({ page }) => {
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Wait for the upload interface to be visible
    await page.waitForSelector('text=Upload Financial Document');
    
    // Take a screenshot of the upload interface
    const uploadInterface = await page.locator('div').filter({ hasText: 'Upload Financial Document' }).first().screenshot();
    
    // Compare the screenshot with a baseline (first run will create the baseline)
    expect(uploadInterface).toMatchSnapshot('document-upload-interface.png');
  });

  test('document analysis results should match snapshot', async ({ page }) => {
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
    
    // Wait for analysis results to be visible
    await page.waitForSelector('text=Analysis Results');
    
    // Take a screenshot of the analysis results
    const analysisResults = await page.locator('div').filter({ hasText: 'Analysis Results' }).first().screenshot();
    
    // Compare the screenshot with a baseline (first run will create the baseline)
    expect(analysisResults).toMatchSnapshot('document-analysis-results.png');
  });

  test('Messos analysis results should match snapshot', async ({ page }) => {
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Click the analyze button
    await page.click('button', { hasText: 'Analyze Document' });
    
    // Wait for analysis results to be visible
    await page.waitForSelector('text=Analysis Results');
    
    // Take a screenshot of the analysis results
    const analysisResults = await page.locator('div').filter({ hasText: 'Analysis Results' }).first().screenshot();
    
    // Compare the screenshot with a baseline (first run will create the baseline)
    expect(analysisResults).toMatchSnapshot('messos-analysis-results.png');
  });

  test('document demo page on mobile should match snapshot', async ({ page }) => {
    // Set viewport to mobile size
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Navigate to the document demo page
    await page.goto('/document-demo');
    
    // Wait for the page to be fully loaded
    await page.waitForSelector('text=Upload Financial Document');
    
    // Take a screenshot of the page
    const screenshot = await page.screenshot();
    
    // Compare the screenshot with a baseline (first run will create the baseline)
    expect(screenshot).toMatchSnapshot('document-demo-mobile.png');
  });

  test('Messos demo page on mobile should match snapshot', async ({ page }) => {
    // Set viewport to mobile size
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Navigate to the Messos demo page
    await page.goto('/messos-demo');
    
    // Wait for the page to be fully loaded
    await page.waitForSelector('text=Messos Financial Document');
    
    // Take a screenshot of the page
    const screenshot = await page.screenshot();
    
    // Compare the screenshot with a baseline (first run will create the baseline)
    expect(screenshot).toMatchSnapshot('messos-demo-mobile.png');
  });
});
