@echo off
cd /d "%~dp0"
echo Running integration tests...

mkdir DevDocs\test-results 2>nul

start cmd /k "npm run dev:all"
timeout /t 20 /nobreak
cd DevDocs
npx playwright test tests/integration.spec.ts --headed
npx playwright show-report

pause
