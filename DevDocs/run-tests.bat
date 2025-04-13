@echo off
echo Running DevDocs Tests...
echo.

IF "%1"=="playwright" (
  echo Running Playwright tests for Document Understanding...
  cd DevDocs
  npx playwright test tests/document-understanding/
) ELSE (
  echo Running DevDocs comprehensive tests...
  cd frontend
  npm run dev:test %*
)

echo.
echo Tests completed!
pause
