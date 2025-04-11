@echo off
echo Running emergency simple test (should complete quickly)...

cd /d "c:\Users\aviad\OneDrive\Desktop\backv2\DevDocs"
echo Current directory is now: %CD%

echo Terminating any existing Playwright processes...
taskkill /F /IM playwright.exe /T 2>nul
taskkill /F /IM node.exe /T 2>nul

echo Running simplified test with strict timeout...
npx playwright test tests\basic-test.spec.ts --headed --timeout=10000 --workers=1

echo Test completed.
pause
