@echo off
REM Script to test the document integration and query engine agents

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b 1
)

REM Check if the API key is provided
if "%1"=="" (
    echo Usage: %0 ^<openrouter-api-key^> [query]
    echo Example: %0 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 "What is the total value of the portfolio?"
    exit /b 1
)

REM Run the tests
if "%2"=="" (
    python test_document_integration.py --api-key %1
) else (
    python test_document_integration.py --api-key %1 --query "%~2"
)
