# Simple script to run just the backend server

Write-Host "Starting backend server..." -ForegroundColor Cyan
Set-Location -Path "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend"
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Cyan
Write-Host "Starting Python app.py..." -ForegroundColor Cyan

# Run the Python script
python app.py
