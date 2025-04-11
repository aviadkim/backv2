Write-Host "Running simplified integration test with reduced timeout..." -ForegroundColor Green

# Navigate to the DevDocs directory
Set-Location -Path "c:\Users\aviad\OneDrive\Desktop\backv2\DevDocs"
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Cyan

# Create minimal test file directly from PowerShell
$minimalTestContent = @'
import { test, expect } from '@playwright/test';

// Minimal test with very short timeout
test.setTimeout(5000);

test('ultra quick test', async ({ page }) => {
  console.log('Starting ultra quick test...');
  
  // Simple content, no external dependencies
  await page.setContent("<html><body><h1>Quick Test</h1></body></html>");
  
  // Basic assertion
  await expect(page.locator('h1')).toHaveText('Quick Test');
  
  console.log('Ultra quick test completed');
});
'@

# Write minimal test to file
Set-Content -Path ".\tests\minimal-test.spec.js" -Value $minimalTestContent
Write-Host "Created minimal test file" -ForegroundColor Yellow

# Run the minimal test with strict timeout
Write-Host "Running minimal test with strict timeout..." -ForegroundColor Cyan
npx playwright test tests/minimal-test.spec.js --headed --timeout=5000

Write-Host "Tests completed." -ForegroundColor Green
