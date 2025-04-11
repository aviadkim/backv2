const { test, expect } = require('@playwright/test');

test('minimal test', async () => {
  expect(true).toBe(true);
  console.log('Minimal test passed');
});
