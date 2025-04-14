@echo off
REM Test script for OpenRouter integration

REM Check if API key is provided
if "%1"=="" (
  echo Usage: %0 ^<openrouter-api-key^>
  echo Example: %0 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
  exit /b 1
)

set API_KEY=%1

REM Set up the API key
echo Setting up OpenRouter API key...
python backend\scripts\setup_openrouter_key.py --api-key %API_KEY% --env-file .env

REM Test the API key
echo Testing OpenRouter API key...
python backend\scripts\test_openrouter.py

REM Run a simple agent example
echo Running simple agent example...
python backend\examples\simple_agent_example.py --prompt "Explain how financial document analysis works in 3 sentences."

echo Tests completed successfully!
