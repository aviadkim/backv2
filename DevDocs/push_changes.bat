@echo off
REM Script to push all changes to GitHub

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git is not installed. Please install Git and try again.
    exit /b 1
)

REM Check if the current directory is a git repository
if not exist ".git" (
    echo This directory is not a git repository. Please run this script from the root of the repository.
    exit /b 1
)

REM Add all changes
echo Adding all changes...
git add .

REM Commit the changes
echo Committing changes...
git commit -m "Add OpenRouter integration with Optimus Alpha model"

REM Push the changes
echo Pushing changes to GitHub...
git push origin main

echo Changes pushed to GitHub successfully!
