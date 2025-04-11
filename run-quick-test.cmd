@echo off
echo Running the quick browser test to verify setup...

cd /d "c:\Users\aviad\OneDrive\Desktop\backv2\DevDocs"
echo Current directory is now: %CD%

echo Creating test results directory...
mkdir test-results 2>nul

echo Running quick browser test...
npx playwright test tests/integration.spec.ts:152 --headed

echo Test completed.
pause
