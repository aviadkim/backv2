@echo off
echo Starting tests from DevDocs directory...

cd DevDocs
npx playwright test

echo Tests completed.
pause
