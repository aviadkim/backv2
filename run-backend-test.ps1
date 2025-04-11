# Simple script to test the backend API

# First, navigate to the backend directory
Set-Location -Path "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend"

# Start the Flask application
Write-Host "Starting Flask API..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-Command python app.py" -WindowStyle Normal

# Wait for server to start
Write-Host "Waiting for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test basic connectivity
Write-Host "Testing API connectivity..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:24125/" -Method GET
    Write-Host "API is responding!" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: API is not responding." -ForegroundColor Red
    Write-Host "Error details: $_" -ForegroundColor Red
}

Write-Host "Press Enter to exit..." -ForegroundColor Cyan
Read-Host
