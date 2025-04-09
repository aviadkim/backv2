@echo off
echo Running integration tests between frontend and backend...

echo Creating test results directory...
if not exist "DevDocs\test-results" mkdir DevDocs\test-results

echo Starting application servers...
start cmd /k "cd /d %~dp0 && npm run dev:all"

echo Waiting for servers to start (20 seconds)...
timeout /t 20 /nobreak

echo Running integration tests...
cd DevDocs
npx playwright test tests\integration.spec.ts --headed

echo Opening test report...
npx playwright show-report

pause
