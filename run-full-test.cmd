@echo off
echo Running tests with proper report generation...

cd /d "c:\Users\aviad\OneDrive\Desktop\backv2\DevDocs"
echo Current directory is now: %CD%

echo Creating test results directory...
mkdir test-results 2>nul

echo Running full integration tests...
npx playwright test tests/integration.spec.ts --headed

echo Opening test report from the correct location...
npx playwright show-report

pause
