import { test, expect } from '@playwright/test';

test.describe('Dashboard Page Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login and navigate to dashboard
    await page.goto('/login');
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Password').fill('TestPassword123!');
    await page.getByRole('button', { name: 'Login' }).click();
    await expect(page).toHaveURL(/dashboard/);
  });

  test('should display recent documents widget', async ({ page }) => {
    // Check for recent documents section
    await expect(page.getByRole('heading', { name: /Recent Documents/i })).toBeVisible();
    
    // Check if document cards are rendered
    const documentCards = page.locator('.document-card');
    
    // There should be at least one document or a "no documents" message
    if (await documentCards.count() > 0) {
      await expect(documentCards.first()).toBeVisible();
    } else {
      await expect(page.getByText(/No recent documents|Upload your first document/i)).toBeVisible();
    }
  });

  test('should display system status and statistics', async ({ page }) => {
    // Check for system stats section
    await expect(page.getByRole('heading', { name: /System Status|Statistics/i })).toBeVisible();
    
    // Check for key metrics
    const metrics = ['Documents', 'Processing', 'Storage Used'];
    for (const metric of metrics) {
      await expect(page.getByText(new RegExp(metric, 'i'))).toBeVisible();
    }
  });

  test('should navigate to document upload from dashboard', async ({ page }) => {
    // Find and click the "Upload" button or card on the dashboard
    await page.getByRole('link', { name: /Upload|Add Document/i }).click();
    
    // Verify navigation to upload page
    await expect(page).toHaveURL(/upload/);
    await expect(page.getByRole('heading', { name: /Upload Documents/i })).toBeVisible();
  });

  test('should show quick actions menu', async ({ page }) => {
    // Look for quick actions section
    const quickActions = page.getByRole('region', { name: /Quick Actions/i });
    await expect(quickActions).toBeVisible();
    
    // Check common quick action buttons
    const actionButtons = ['Upload', 'Search', 'Create Table'];
    for (const action of actionButtons) {
      const button = page.getByRole('link', { name: new RegExp(action, 'i') });
      if (await button.isVisible()) {
        // If button exists, it should be clickable
        await expect(button).toBeEnabled();
      }
    }
  });
});
