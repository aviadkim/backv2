@echo off
REM Script to install dependencies for the OpenRouter integration

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip is not installed. Please install pip and try again.
    exit /b 1
)

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r backend\requirements.txt

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js is not installed. Please install Node.js and try again.
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo npm is not installed. Please install npm and try again.
    exit /b 1
)

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install

echo Dependencies installed successfully!
