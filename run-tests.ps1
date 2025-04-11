# Quick script to run the DevDocs tests
Write-Host "Starting DevDocs application and running tests..." -ForegroundColor Green

# Start the backend server (in a new window)
Start-Process powershell -ArgumentList "-Command cd C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend; python app.py"
Write-Host "Started backend server, waiting for it to initialize..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Start the frontend server (in a new window)
Start-Process powershell -ArgumentList "-Command cd C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend; npm run dev"
Write-Host "Started frontend server, waiting for it to initialize..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Run the tests
Write-Host "Running tests..." -ForegroundColor Green
& "C:\Users\aviad\OneDrive\Desktop\backv2\test-devdocs.ps1"
