@echo off
REM Script to start the backend API server

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b 1
)

REM Check if the OpenRouter API key is set
if "%OPENROUTER_API_KEY%"=="" (
    if exist .env (
        for /f "tokens=*" %%a in (.env) do (
            set %%a
        )
    )
    
    if "%OPENROUTER_API_KEY%"=="" (
        echo OpenRouter API key is not set. Please set the OPENROUTER_API_KEY environment variable or create a .env file.
        echo You can set up the API key using the setup_openrouter_key.py script:
        echo   python backend\scripts\setup_openrouter_key.py --api-key YOUR_API_KEY
        exit /b 1
    )
)

REM Start the backend API server
echo Starting backend API server...
cd backend
python main.py --reload
