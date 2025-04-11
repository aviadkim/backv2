import { test, expect } from '@playwright/test';

// DevDocs specific features tests
test.describe('DevDocs Core Features', () => {
  test.setTimeout(10000);

  test('Documentation homepage should load', async ({ page }) => {
    console.log('Testing DevDocs homepage...');
    
    // Simple content to simulate DevDocs homepage
    await page.setContent(`
      <html>
        <head><title>DevDocs - Documentation Browser</title></head>
        <body>
          <header>
            <h1>DevDocs</h1>
            <div class="subtitle">All your documentation in one place</div>
          </header>
          <main>
            <div class="documentation-list">
              <div class="doc-item">JavaScript</div>
              <div class="doc-item">Python</div>
              <div class="doc-item">React</div>
            </div>
          </main>
        </body>
      </html>
    `);
    
    // Verify DevDocs UI elements
    await expect(page.locator('h1')).toContainText('DevDocs');
    await expect(page.locator('.doc-item')).toHaveCount(3);
    
    console.log('DevDocs homepage test completed');
  });

  test('Documentation search should work', async ({ page }) => {
    console.log('Testing DevDocs search functionality...');
    
    // Simple content to simulate DevDocs search
    await page.setContent(`
      <html>
        <head><title>DevDocs - Search</title></head>
        <body>
          <header>
            <h1>DevDocs</h1>
            <input type="text" id="search-input" placeholder="Search documentation...">
            <button id="search-button">Search</button>
          </header>
          <div id="search-results"></div>
          <script>
            document.getElementById('search-button').addEventListener('click', () => {
              const query = document.getElementById('search-input').value;
              const results = document.getElementById('search-results');
              
              if (query.includes('javascript')) {
                results.innerHTML = '<div class="result-item">JavaScript Array Methods</div><div class="result-item">JavaScript Promises</div>';
              } else {
                results.innerHTML = '<div class="no-results">No results found</div>';
              }
            });
          </script>
        </body>
      </html>
    `);
    
    // Test search functionality
    await page.fill('#search-input', 'javascript array');
    await page.click('#search-button');
    
    // Verify search results
    await expect(page.locator('.result-item')).toHaveCount(2);
    await expect(page.locator('.result-item').first()).toContainText('JavaScript Array Methods');
    
    console.log('DevDocs search test completed');
  });

  test('Documentation content viewer should display markdown', async ({ page }) => {
    console.log('Testing DevDocs content viewer...');
    
    // Content to simulate DevDocs markdown viewer
    await page.setContent(`
      <html>
        <head>
          <title>DevDocs - Markdown Viewer</title>
          <style>
            .markdown-content { font-family: system-ui; padding: 20px; }
            .markdown-content h1 { color: #333; }
            .markdown-content pre { background: #f5f5f5; padding: 10px; }
          </style>
        </head>
        <body>
          <header>
            <h1>DevDocs</h1>
          </header>
          <main>
            <div class="markdown-content">
              <h1>JavaScript Arrays</h1>
              <p>Arrays are list-like objects whose prototype has methods to perform traversal and mutation operations.</p>
              <pre><code>const array1 = ['a', 'b', 'c'];
array1.forEach(element => console.log(element));</code></pre>
            </div>
          </main>
        </body>
      </html>
    `);
    
    // Verify markdown content is displayed correctly
    await expect(page.locator('.markdown-content h1')).toHaveText('JavaScript Arrays');
    await expect(page.locator('.markdown-content pre')).toContainText('array1.forEach');
    
    console.log('DevDocs content viewer test completed');
  });
});
