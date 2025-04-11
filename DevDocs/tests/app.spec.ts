import { test, expect } from '@playwright/test';

test.describe('DevDocs Full Application Test', () => {
  test.beforeEach(async ({ page }) => {
    // Start from home page for each test
    await page.goto('/');
  });

  test('should navigate through all major pages', async ({ page }) => {
    // Check home page loads
    await expect(page).toHaveTitle(/Document Understanding Demo/);

    // Check navigation to document demo page
    await page.getByRole('link', { name: /Try Document Upload Demo/i }).click();
    await expect(page.getByRole('heading', { name: /Document Understanding Demo/i })).toBeVisible();

    // Go back to home page
    await page.goto('/');

    // Check navigation to messos demo page
    await page.getByRole('link', { name: /View Messos Demo/i }).click();
    await expect(page.getByRole('heading', { name: /Messos Financial Document Analysis/i })).toBeVisible();
  });

  test('should allow document upload and processing workflow', async ({ page }) => {
    // Navigate to document demo page
    await page.goto('/document-demo');

    // Check that the upload area is visible
    await expect(page.getByText('Drag and drop your file here, or browse')).toBeVisible();

    // Check that the supported document types section is visible
    await expect(page.getByText('Supported Document Types:')).toBeVisible();

    // Check that the how it works section is visible
    await expect(page.getByText('How It Works')).toBeVisible();
  });

  test('should display Messos document analysis correctly', async ({ page }) => {
    // Navigate to Messos demo page
    await page.goto('/messos-demo');

    // Verify the page loads correctly
    await expect(page.getByRole('heading', { name: /Messos Financial Document Analysis/i })).toBeVisible();

    // Check that document preview is displayed
    await expect(page.getByText('Document Preview')).toBeVisible();

    // Check that about this demo section is visible
    await expect(page.getByText('About This Demo')).toBeVisible();

    // Check that sample analysis results are displayed
    await expect(page.getByText('Sample Analysis Results')).toBeVisible();

    // Check that document information is displayed
    await expect(page.getByText('Document Information')).toBeVisible();

    // Check that company information is displayed
    await expect(page.getByText('Company Information')).toBeVisible();
  });

  test('should have proper navigation between pages', async ({ page }) => {
    // Start at home page
    await page.goto('/');

    // Navigate to document demo
    await page.getByRole('link', { name: /Try Document Upload Demo/i }).click();
    await expect(page.getByRole('heading', { name: /Document Understanding Demo/i })).toBeVisible();

    // Navigate back to home
    await page.goto('/');

    // Navigate to Messos demo
    await page.getByRole('link', { name: /View Messos Demo/i }).click();
    await expect(page.getByRole('heading', { name: /Messos Financial Document Analysis/i })).toBeVisible();

    // Navigate back to home
    await page.goto('/');

    // Verify home page content
    await expect(page.getByText('About Document Understanding')).toBeVisible();
  });

  test('should validate application performance', async ({ page }) => {
    // Check initial page load time
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;

    // Log performance metrics
    console.log(`Initial page load time: ${loadTime}ms`);

    // Acceptable threshold check (adjust based on application requirements)
    expect(loadTime).toBeLessThan(5000);

    // Check responsiveness of key interactive elements
    await page.getByRole('link', { name: /Try Document Upload Demo/i }).click();
    await expect(page.getByRole('heading', { name: /Document Understanding Demo/i })).toBeVisible({ timeout: 2000 });
  });
});
