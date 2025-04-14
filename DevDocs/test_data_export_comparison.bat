@echo off
REM Script to test the data export and document comparison agents

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b 1
)

REM Check if the API key is provided
if "%1"=="" (
    echo Usage: %0 ^<openrouter-api-key^> [export-format]
    echo Example: %0 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 excel
    exit /b 1
)

REM Set default export format if not provided
set EXPORT_FORMAT=json
if not "%2"=="" set EXPORT_FORMAT=%2

REM Run the tests
python test_data_export_comparison.py --api-key %1 --export-format %EXPORT_FORMAT%
