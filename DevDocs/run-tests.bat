@echo off
echo Running DevDocs Tests...
echo.

IF "%1"=="playwright" (
  echo Running Playwright tests for Document Understanding...
  cd DevDocs
  npx playwright test tests/document-understanding/
) ELSE (
  echo Running DevDocs comprehensive tests...
  cd scripts
  node run-tests.js %*
)

echo.
echo Tests completed!
pause
