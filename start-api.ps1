# Simple script to start the DevDocs API server

$ErrorActionPreference = "Stop"

# Print banner
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "        DevDocs API Server Startup            " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# Navigate to the backend directory
$backendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend"
Set-Location -Path $backendDir
Write-Host "Working directory: $backendDir" -ForegroundColor Yellow

# Check if port 24125 is already in use
$portCheck = netstat -ano | Select-String "24125"
if ($portCheck) {
    Write-Host "Port 24125 is already in use. Attempting to clear..." -ForegroundColor Yellow
    $process = ($portCheck | Select-String "LISTENING")
    if ($process) {
        $processId = $process[0].ToString().Split(" ")[-1].Trim()
        try {
            Stop-Process -Id $processId -Force
            Write-Host "Killed process $processId" -ForegroundColor Green
        } catch {
            Write-Host "Failed to kill process. Please stop it manually." -ForegroundColor Red
        }
    } else {
        Write-Host "Port is in use but no LISTENING process found." -ForegroundColor Yellow
    }
}

# Verify Python and Flask installation
try {
    $pythonVersion = python --version
    Write-Host "Python version: $pythonVersion" -ForegroundColor Green
    
    $flaskVersion = python -c "try: import flask; print(f'Flask version: {flask.__version__}'); except Exception as e: print(f'Error: {e}')"
    Write-Host $flaskVersion -ForegroundColor Green
} catch {
    Write-Host "Error checking Python/Flask versions: $_" -ForegroundColor Red
}

# Create a diagnostic report
Write-Host "Creating diagnostic report..." -ForegroundColor Yellow
$report = @"
===== DIAGNOSTIC REPORT =====
Date: $(Get-Date)
Working directory: $(Get-Location)
Python version: $pythonVersion
Flask check: $flaskVersion
Network info:
$(ipconfig | Select-String "IPv4")
Active connections:
$(netstat -ano | Select-String "LISTENING" | Select-String "24125")
============================
"@

$reportPath = "api-diagnostic-report.txt"
$report | Out-File $reportPath
Write-Host "Diagnostic report saved to $reportPath" -ForegroundColor Green

# Try to start Flask in verbose mode
Write-Host "Starting Flask application in verbose mode..." -ForegroundColor Green
Write-Host "Application will be available at: http://localhost:24125" -ForegroundColor Cyan
Write-Host "If app fails to start, check $reportPath for diagnostics" -ForegroundColor Yellow
python -v app.py
