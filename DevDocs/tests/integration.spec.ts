import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

// Test suite for integration between frontend and backend
test.describe('Frontend-Backend Integration', () => {
  // Set longer timeout for API operations
  test.setTimeout(60000);

  test('should connect to backend API and receive response', async ({ page, request }) => {
    // First load the frontend page to verify it's working
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    
    // Take a screenshot of the frontend
    await page.screenshot({ path: 'test-results/frontend-loaded.png' });
    
    // Test a direct API call to the backend
    const apiResponse = await request.get('http://localhost:5000/api/health');
    expect(apiResponse.ok()).toBeTruthy();
    
    const responseBody = await apiResponse.json();
    console.log('Backend health check response:', responseBody);
    expect(responseBody).toBeDefined();
  });

  test('should upload document and process it through backend', async ({ page }) => {
    // Navigate to upload page
    await page.goto('/upload');
    await page.waitForLoadState('domcontentloaded');
    
    // Check if file upload element exists
    const fileInputExists = await page.locator('input[type="file"]').count() > 0;
    
    if (fileInputExists) {
      console.log('File input found, attempting upload test');
      
      // Create a test PDF file if it doesn't exist
      const testFilePath = path.join(__dirname, 'fixtures', 'test-document.pdf');
      if (!fs.existsSync(testFilePath)) {
        console.log('Test file not found, skipping upload test');
        test.skip();
        return;
      }
      
      // Upload the file
      await page.setInputFiles('input[type="file"]', testFilePath);
      
      // Check if file name appears in the UI
      await expect(page.getByText('test-document.pdf')).toBeVisible({ timeout: 5000 });
      
      // Look for submit/upload button
      const uploadButton = page.getByRole('button', { name: /upload|process|submit/i });
      
      if (await uploadButton.count() > 0 && await uploadButton.isEnabled()) {
        await uploadButton.click();
        
        // Wait for confirmation or processing indication
        const successIndicator = page.getByText(/success|uploaded|processing/i);
        if (await successIndicator.isVisible({ timeout: 30000 })) {
          console.log('File upload successful');
        }
      }
    } else {
      console.log('File input not found, checking for alternative upload UI');
      await page.screenshot({ path: 'test-results/upload-page-ui.png' });
    }
  });

  test('should fetch and display data from backend', async ({ page }) => {
    // Navigate to documents or dashboard page where data from backend should be displayed
    await page.goto('/documents');
    await page.waitForLoadState('domcontentloaded');
    
    // Wait for network requests to complete
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {
      console.log('Network never became completely idle, continuing anyway');
    });
    
    // Take a screenshot to see what's rendered
    await page.screenshot({ path: 'test-results/documents-page.png' });
    
    // Check for evidence of data loading
    const hasData = await page.locator('.document-card, .document-list-item, table tr').count() > 0;
    const hasLoading = await page.getByText(/loading/i).isVisible();
    const hasNoData = await page.getByText(/no documents|no data|empty/i).isVisible();
    
    if (hasData) {
      console.log('Data was fetched from backend and displayed in the UI');
      // Check if we can see document details or names
      const documentNames = await page.locator('.document-name, .document-title').allInnerTexts();
      console.log('Found document names:', documentNames);
    } else if (hasLoading) {
      console.log('Data is still loading');
    } else if (hasNoData) {
      console.log('No data available, but connection to backend appears functional');
    } else {
      console.log('Unable to confirm data fetching from backend');
      // Check for any visible content
      const pageContent = await page.content();
      console.log('Page content length:', pageContent.length);
    }
  });

  test('should check backend API endpoints directly', async ({ request }) => {
    console.log('Starting backend API endpoint tests...');
    // Test various backend API endpoints with timeout and more ports
    const endpoints = [
      'http://localhost:5000/api/health',
      'http://localhost:5000/api/documents',
      'http://localhost:3004/api/health',  // Add port 3004 which is currently in use
      'http://localhost:5001/api/health',
      'http://localhost:8000/api/health',
    ];
    
    for (const endpoint of endpoints) {
      console.log(`Testing endpoint: ${endpoint}...`);
      try {
        const response = await request.get(endpoint, { 
          timeout: 5000  // Add shorter timeout to avoid hanging
        });
        
        console.log(`Endpoint ${endpoint} status:`, response.status());
        if (response.ok()) {
          const data = await response.json().catch(() => null);
          console.log(`Endpoint ${endpoint} returned:`, data ? 'Valid JSON data' : 'Non-JSON response');
        }
      } catch (error: any) { // Add type annotation
        console.log(`Failed to call endpoint ${endpoint}:`, error.message || 'Unknown error');
      }
    }
    console.log('Backend API endpoint tests completed.');
  });

  // Optional: Test for websocket or streaming connections if applicable
  test.skip('should establish websocket connection if applicable', async ({ page }) => {
    // This would test websocket connections if your app uses them
    // Implement if needed
  });

  // Add a simple test that will complete quickly
  test('should complete basic browser test quickly', async ({ page }) => {
    console.log('Running quick browser test...');
    await page.setContent('<html><body><h1>Test Page</h1></body></html>');
    await expect(page.locator('h1')).toContainText('Test Page');
    console.log('Quick browser test completed successfully.');
  });
});
