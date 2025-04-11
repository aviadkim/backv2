import { test, expect } from '@playwright/test';

// Simple test that doesn't rely on any server or complex setup
test('basic browser test', async ({ page }) => {
  console.log('Running simple browser test...');
  
  // Create test page directly in browser (no server needed)
  await page.setContent(`
    <html>
      <body>
        <h1>Test Page</h1>
        <p>This test doesn't need any servers running</p>
        <button id="testButton">Click me</button>
        <div id="result">Not clicked yet</div>
        <script>
          document.getElementById('testButton').addEventListener('click', () => {
            document.getElementById('result').textContent = 'Button was clicked!';
          });
        </script>
      </body>
    </html>
  `);
  
  // Verify content loaded
  await expect(page.locator('h1')).toContainText('Test Page');
  
  // Test interaction
  await page.click('#testButton');
  await expect(page.locator('#result')).toContainText('Button was clicked!');
  
  console.log('✅ Browser test passed successfully');
});

// Fixed API mock test
test('API mock test', async ({ page }) => {
  console.log('Testing API mocking capabilities...');
  
  // Set base URL explicitly
  await page.goto('http://localhost:3000/');
  
  // Create test page with fixed fetch code
  await page.setContent(`
    <html>
      <body>
        <h1>API Test</h1>
        <button id="fetchButton">Fetch Data</button>
        <div id="apiResult">No data yet</div>
        <script>
          document.getElementById('fetchButton').addEventListener('click', async () => {
            try {
              // Use full absolute URL to avoid parsing issues
              const response = await fetch('http://example.com/api/data');
              const data = await response.json();
              document.getElementById('apiResult').textContent = data.message;
            } catch (error) {
              document.getElementById('apiResult').textContent = 'Error: ' + error.toString();
            }
          });
        </script>
      </body>
    </html>
  `);
  
  // Mock API response with specific domain
  await page.route('http://example.com/api/data', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ message: 'Mocked API response success!' }),
    });
  });
  
  // Trigger the API call
  await page.click('#fetchButton');
  
  // Verify the mocked response was received
  await expect(page.locator('#apiResult')).toContainText('Mocked API response success!');
  
  console.log('✅ API mock test passed successfully');
});

// Form submission test
test('form submission test', async ({ page }) => {
  console.log('Testing form submission...');
  
  await page.setContent(`
    <html>
      <body>
        <h1>Form Test</h1>
        <form id="testForm">
          <input type="text" id="nameInput" placeholder="Enter your name">
          <input type="email" id="emailInput" placeholder="Enter your email">
          <button type="submit">Submit</button>
        </form>
        <div id="formResult">No submission yet</div>
        <script>
          document.getElementById('testForm').addEventListener('submit', (event) => {
            event.preventDefault();
            const name = document.getElementById('nameInput').value;
            const email = document.getElementById('emailInput').value;
            document.getElementById('formResult').textContent = 
              'Form submitted with: ' + name + ' (' + email + ')';
          });
        </script>
      </body>
    </html>
  `);
  
  // Fill form fields
  await page.fill('#nameInput', 'Test User');
  await page.fill('#emailInput', 'test@example.com');
  
  // Submit form
  await page.click('button[type="submit"]');
  
  // Verify submission result
  await expect(page.locator('#formResult')).toContainText('Form submitted with: Test User (test@example.com)');
  
  console.log('✅ Form submission test passed successfully');
});
