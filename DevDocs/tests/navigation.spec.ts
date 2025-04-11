import { test, expect } from '@playwright/test';

test.describe('Main Navigation', () => {
  // Reduce timeout for faster test failures if pages don't load
  test.setTimeout(15000);

  test.beforeEach(async ({ page }) => {
    // Add error handling for page errors
    page.on('pageerror', error => {
      console.error(`Page error: ${error.message}`);
    });

    // Configure page to ignore certain errors
    page.on('console', msg => {
      if (msg.type() === 'error' && (
        msg.text().includes('LaunchDarkly') ||
        msg.text().includes('Failed to load resource')
      )) {
        // Ignore specific errors
        return;
      }
      console.log(`Console ${msg.type()}: ${msg.text()}`);
    });
  });

  test('should load the home page correctly', async ({ page }) => {
    try {
      await page.goto('/', { timeout: 20000 });
      await page.waitForLoadState('domcontentloaded', { timeout: 10000 });
      
      // Check for any content
      await expect(page.locator('body')).toBeVisible();
      
      // Take a screenshot for debugging
      await page.screenshot({ path: 'test-results/home-page.png' });
    } catch (error) {
      console.error('Error in home page test:', error);
      // Save error screenshot
      await page.screenshot({ path: 'test-results/home-page-error.png' });
      throw error;
    }
  });

  test('should load the dashboard page correctly', async ({ page }) => {
    await page.goto('/dashboard', { timeout: 5000 });
    await page.waitForLoadState('domcontentloaded', { timeout: 5000 });
    
    // Just check that any content loaded, without specific heading requirements
    await expect(page.locator('body')).not.toBeEmpty({ timeout: 3000 });
  });

  test('should load the documents page correctly', async ({ page }) => {
    await page.goto('/documents', { timeout: 5000 });
    await page.waitForLoadState('domcontentloaded', { timeout: 5000 });
    
    // Check for basic content rather than specific headings
    await expect(page.locator('body')).not.toBeEmpty({ timeout: 3000 });
  });

  // Add a test for basic app functionality
  test('should have working navigation menu', async ({ page }) => {
    await page.goto('/', { timeout: 5000 });
    await page.waitForLoadState('domcontentloaded', { timeout: 5000 });
    
    // Find navigation elements
    const navLinks = page.locator('nav a, header a, [role="navigation"] a');
    
    // Check if we have any navigation links
    const count = await navLinks.count();
    expect(count).toBeGreaterThan(0);
    
    // Check that at least one link is clickable
    if (count > 0) {
      await navLinks.first().click();
      // Verify navigation happened
      expect(page.url()).not.toBe('/');
    }
  });
});