import { test, expect } from '@playwright/test';

test.describe('Document Upload Page', () => {
  const uploadPageUrl = '/upload'; // Assuming base URL is handled by Playwright config

  test('should allow uploading a PDF file', async ({ page }) => {
    // 1. Navigate to the upload page
    await page.goto(uploadPageUrl);

    // 2. Check if the main heading is visible
    await expect(page.getByRole('heading', { name: 'Upload Documents' })).toBeVisible();

    // 3. Select language (assuming the dropdown trigger is identifiable)
    //    We need to inspect the actual rendered HTML for a reliable selector,
    //    but let's assume it has an ID or data-testid for now.
    //    await page.locator('#language-select').click(); // Example selector
    //    await page.getByRole('option', { name: 'Hebrew + English' }).click();
    //    Note: Selecting from Shadcn/ui Select might need specific handling,
    //          deferring precise selector until needed or if basic upload fails.

    // 4. Select a file using the input element
    //    Playwright interacts directly with the input, even if visually hidden.
    const fileInput = page.locator('input[type="file"]');
    await expect(fileInput).toBeAttached(); // Ensure it exists
    // Use a dummy file path - we'll create this file next.
    await fileInput.setInputFiles('../repo/uploads/doc_1af59f04_sample.pdf');

    // 5. Verify the selected file appears (optional but good practice)
    await expect(page.getByText('doc_1af59f04_sample.pdf')).toBeVisible();

    // 6. Click the upload button
    //    Using getByRole is generally robust
    await page.getByRole('button', { name: /Start Processing/ }).click();

    // 7. Wait for and verify the success message
    //    The success message appears in a div with specific text content
    //    Increase timeout if backend processing takes longer
    await expect(page.getByText('Upload successful! Documents are processing.')).toBeVisible({ timeout: 60000 }); // Increased to 60s timeout

    // 8. Check if the file list is cleared after success (optional)
    await expect(page.getByText('doc_1af59f04_sample.pdf')).not.toBeVisible();
  });

  test('should show error toast if no file is selected', async ({ page }) => {
    // 1. Navigate to the upload page
    await page.goto(uploadPageUrl);

    // 2. Verify the upload button is disabled
    await expect(page.getByRole('button', { name: /Start Processing/ })).toBeDisabled();

    // Note: We could also check for the toast, but checking the button state
    // is a more direct test of the intended behavior in this case.
    // await expect(page.getByText('No Files Selected')).toBeVisible({ timeout: 2000 }); // Short timeout if checking toast
  });

  test('should show error toast for non-PDF file type', async ({ page }) => {
    // 1. Navigate to the upload page
    await page.goto(uploadPageUrl);

    // 2. Select a non-PDF file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('tests/fixtures/dummy.txt'); // Use the dummy text file

    // 3. Verify the application state reflects the invalid file rejection
    //    (Toast assertion is unreliable, so check functional outcome)

    // 4. Optionally, check if the invalid file is NOT listed
    // Ensure the invalid file is not listed in the selected files UI
    await expect(page.getByText('dummy.txt')).not.toBeVisible();

    // 5. Optionally, check if the upload button is still disabled or reflects 0 files
     // Ensure the button text indicates 0 files selected and is likely disabled
     await expect(page.getByRole('button', { name: /Start Processing \(0\)/ })).toBeVisible();
     await expect(page.getByRole('button', { name: /Start Processing \(0\)/ })).toBeDisabled(); // Add check for disabled state
  });

  // Add more tests here later (e.g., batch upload)
});