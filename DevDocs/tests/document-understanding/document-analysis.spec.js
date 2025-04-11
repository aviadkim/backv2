const { test, expect } = require('@playwright/test');

test.describe('Document Analysis Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the document demo page and simulate a processed document
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
  });

  test('should display document information section', async ({ page }) => {
    // Check if document information section is displayed
    await expect(page.locator('text=Document Information')).toBeVisible();
    
    // Check if file name is displayed
    await expect(page.locator('text=File Name')).toBeVisible();
    await expect(page.locator('text=financial-report.pdf')).toBeVisible();
    
    // Check if title is displayed
    await expect(page.locator('text=Title')).toBeVisible();
    await expect(page.locator('text=Financial Report')).toBeVisible();
  });

  test('should display company information section', async ({ page }) => {
    // Check if company information section is displayed
    await expect(page.locator('text=Company Information')).toBeVisible();
    
    // Check if company name is displayed
    await expect(page.locator('text=Company Name')).toBeVisible();
    await expect(page.locator('text=Demo Company Inc.')).toBeVisible();
    
    // Check if ticker symbol is displayed
    await expect(page.locator('text=Ticker Symbol')).toBeVisible();
    await expect(page.locator('text=DEMO')).toBeVisible();
    
    // Check if industry is displayed
    await expect(page.locator('text=Industry')).toBeVisible();
    await expect(page.locator('text=Technology')).toBeVisible();
    
    // Check if sector is displayed
    await expect(page.locator('text=Sector')).toBeVisible();
    await expect(page.locator('text=Software')).toBeVisible();
  });

  test('should display financial metrics section', async ({ page }) => {
    // Check if financial metrics section is displayed
    await expect(page.locator('text=Financial Metrics')).toBeVisible();
    
    // Check if metrics table is displayed
    const metricsTable = page.locator('table').filter({ hasText: 'MetricValuePeriod' }).first();
    await expect(metricsTable).toBeVisible();
    
    // Check if revenue is displayed
    await expect(page.locator('text=Revenue')).toBeVisible();
    
    // Check if net income is displayed
    await expect(page.locator('text=Net Income')).toBeVisible();
  });

  test('should display financial ratios section', async ({ page }) => {
    // Check if financial ratios section is displayed
    await expect(page.locator('text=Financial Ratios')).toBeVisible();
    
    // Check if ratios table is displayed
    const ratiosTable = page.locator('table').filter({ hasText: 'RatioValuePeriod' }).first();
    await expect(ratiosTable).toBeVisible();
    
    // Check if gross margin is displayed
    await expect(page.locator('text=Gross Margin')).toBeVisible();
    
    // Check if net margin is displayed
    await expect(page.locator('text=Net Margin')).toBeVisible();
  });

  test('should format currency values correctly', async ({ page }) => {
    // Check if currency values are formatted correctly
    const revenueValue = page.locator('tr').filter({ hasText: 'Revenue' }).locator('td').nth(1);
    await expect(revenueValue).toContainText('$1,000,000');
  });

  test('should format percentage values correctly', async ({ page }) => {
    // Check if percentage values are formatted correctly
    const grossMarginValue = page.locator('tr').filter({ hasText: 'Gross Margin' }).locator('td').nth(1);
    await expect(grossMarginValue).toContainText('%');
  });
});
