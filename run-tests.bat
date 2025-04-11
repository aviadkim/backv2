@echo off
echo Starting tests with server...

:: Kill any existing processes on ports 3000, 3002, and 8000
echo Killing existing processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3002') do (
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /F /PID %%a 2>nul
)

:: Navigate to the repo directory
cd repo

:: Start the backend server in the background
echo Starting backend server...
start /b python app.py

:: Wait for the backend server to start
echo Waiting for backend server to start...
timeout /t 10

:: Navigate to the DevDocs directory
cd ..
cd DevDocs

:: Start the frontend server in the background
echo Starting frontend server...
start /b npx next dev -p 3002

:: Wait for the frontend server to start
echo Waiting for frontend server to start...
timeout /t 10

:: Run all tests
echo Running all tests...
npx playwright test --config=playwright.config.ts

echo Tests completed.
pause
