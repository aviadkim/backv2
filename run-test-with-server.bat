@echo off
echo Installing TypeScript and Playwright dependencies...
npm install @playwright/test --save-dev

echo Installing Python dependencies...
python -m pip install flask flask-cors pymongo bson python-dotenv

echo Starting application servers...
start cmd /k "cd %~dp0 && npm run dev:all"

echo Waiting for servers to start (15 seconds)...
timeout /t 15 /nobreak

echo Running tests...
cd DevDocs
npx playwright test

pause
