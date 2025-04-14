@echo off
REM Script to test the financial advisor agent

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b 1
)

REM Check if the API key is provided
if "%1"=="" (
    echo Usage: %0 ^<openrouter-api-key^> [analysis-type] [risk-profile] [investment-amount]
    echo Example: %0 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 portfolio medium 100000
    exit /b 1
)

REM Set default parameters if not provided
set ANALYSIS_TYPE=portfolio
if not "%2"=="" set ANALYSIS_TYPE=%2

set RISK_PROFILE=medium
if not "%3"=="" set RISK_PROFILE=%3

set INVESTMENT_AMOUNT=100000
if not "%4"=="" set INVESTMENT_AMOUNT=%4

REM Run the tests
python test_financial_advisor.py --api-key %1 --analysis-type %ANALYSIS_TYPE% --risk-profile %RISK_PROFILE% --investment-amount %INVESTMENT_AMOUNT%
