# Simple script to test minimal Flask app

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "DevDocs Minimal Flask Test" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "Starting minimal Flask app for testing..." -ForegroundColor Green
Set-Location -Path "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend"

# Kill any process on port 24125
$portCheck = netstat -ano | Select-String "24125" | Select-String "LISTENING"
if ($portCheck) {
    $processId = $portCheck[0].ToString().Split(" ")[-1].Trim()
    try {
        Stop-Process -Id $processId -Force
        Write-Host "Killed process $processId" -ForegroundColor Green
    } catch {
        Write-Host "Failed to kill process." -ForegroundColor Red
    }
}

# Make sure test_minimal.py exists
if (-not (Test-Path ".\test_minimal.py")) {
    Write-Host "Creating minimal Flask test script..." -ForegroundColor Yellow
    $minimalAppContent = @"
import os
from flask import Flask

# Disable .env file loading which can cause UnicodeDecodeError
os.environ["FLASK_SKIP_DOTENV"] = "1"

app = Flask(__name__)

@app.route('/')
def home():
    return "Minimal Flask App is working!"

@app.route('/test')
def test():
    return "Test endpoint is working!"

if __name__ == '__main__':
    print("Starting minimal Flask app on port 24125...")
    print("Try accessing http://localhost:24125/")
    app.run(host='0.0.0.0', port=24125, debug=True)
"@
    $minimalAppContent | Out-File -FilePath ".\test_minimal.py" -Encoding utf8
}

Write-Host "Running minimal Flask test..." -ForegroundColor Cyan
Write-Host "Access http://localhost:24125/ in browser to test" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server when done" -ForegroundColor Yellow

python test_minimal.py
