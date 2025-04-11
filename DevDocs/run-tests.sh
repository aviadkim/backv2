#!/bin/bash
echo "Running Playwright tests for Document Understanding..."

cd DevDocs
npx playwright test tests/document-understanding/

echo "Tests completed!"
