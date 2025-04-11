Write-Host "Running integration tests between frontend and backend..." -ForegroundColor Green

Write-Host "Creating test results directory..." -ForegroundColor Yellow
if (-not (Test-Path -Path ".\DevDocs\test-results")) {
    New-Item -ItemType Directory -Force -Path ".\DevDocs\test-results" | Out-Null
}

Write-Host "Starting application servers..." -ForegroundColor Yellow
Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd /d $($PWD.Path) && npm run dev:all"

Write-Host "Waiting for servers to start (20 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

Write-Host "Running integration tests..." -ForegroundColor Cyan
Set-Location -Path ".\DevDocs"
npx playwright test tests/integration.spec.ts --headed

Write-Host "Opening test report..." -ForegroundColor Green
npx playwright show-report

Write-Host "Press Enter to exit..." -ForegroundColor Yellow
Read-Host
