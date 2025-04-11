# Script to check status and open FinDoc application

Write-Host "=== FinDoc App Status Checker ===" -ForegroundColor Cyan

# Check if ports are in use (meaning services are running)
$frontendPort = 3002
$backendPort = 24125

$frontendRunning = $false
$backendRunning = $false

# Check backend
$backendConn = netstat -ano | Select-String "$backendPort" | Select-String "LISTENING"
if ($backendConn) {
    $processId = ($backendConn[0] -split "\s+")[-1]
    try {
        $process = Get-Process -Id $processId -ErrorAction Stop
        Write-Host "✓ Backend API is running (Process: $($process.ProcessName), PID: $processId)" -ForegroundColor Green
        $backendRunning = $true
    } catch {
        Write-Host "✓ Backend API appears to be running but process details unavailable" -ForegroundColor Green
        $backendRunning = $true
    }
} else {
    Write-Host "✗ Backend API is NOT running" -ForegroundColor Red
}

# Check frontend
$frontendConn = netstat -ano | Select-String "$frontendPort" | Select-String "LISTENING"
if ($frontendConn) {
    $processId = ($frontendConn[0] -split "\s+")[-1]
    try {
        $process = Get-Process -Id $processId -ErrorAction Stop
        Write-Host "✓ Frontend UI is running (Process: $($process.ProcessName), PID: $processId)" -ForegroundColor Green
        $frontendRunning = $true
    } catch {
        Write-Host "✓ Frontend UI appears to be running but process details unavailable" -ForegroundColor Green
        $frontendRunning = $true
    }
} else {
    Write-Host "✗ Frontend UI is NOT running" -ForegroundColor Red
}

# Check application status
Write-Host "`nApplication Status:" -ForegroundColor Yellow
if ($backendRunning -and $frontendRunning) {
    Write-Host "✓ FinDoc Application is fully operational!" -ForegroundColor Green
    
    # Offer to open in browser
    Write-Host "`nWould you like to open the FinDoc UI in your browser? (Y/N)" -ForegroundColor Cyan
    $openBrowser = Read-Host
    
    if ($openBrowser.ToLower() -eq "y") {
        Start-Process "http://localhost:$frontendPort"
        Write-Host "Opening FinDoc UI in your default browser..." -ForegroundColor Green
    }
} elseif ($backendRunning) {
    Write-Host "⚠ Partial: Backend is running, but frontend is not available" -ForegroundColor Yellow
    Write-Host "`nTo start the frontend:" -ForegroundColor Cyan
    Write-Host "cd C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend" -ForegroundColor White
    Write-Host "npm run dev" -ForegroundColor White
} elseif ($frontendRunning) {
    Write-Host "⚠ Partial: Frontend is running, but backend API is not available" -ForegroundColor Yellow
    Write-Host "Frontend may not function correctly without the backend API" -ForegroundColor Yellow
    Write-Host "`nTo start the backend:" -ForegroundColor Cyan
    Write-Host "cd C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend" -ForegroundColor White
    Write-Host "python app.py" -ForegroundColor White
} else {
    Write-Host "✗ FinDoc Application is not running" -ForegroundColor Red
    
    # Offer to start the application
    Write-Host "`nWould you like to start the FinDoc application now? (Y/N)" -ForegroundColor Cyan
    $startApp = Read-Host
    
    if ($startApp.ToLower() -eq "y") {
        Write-Host "Starting FinDoc application..." -ForegroundColor Green
        & "C:\Users\aviad\OneDrive\Desktop\backv2\start-findoc-app.ps1"
    } else {
        Write-Host "`nTo start the application manually, run:" -ForegroundColor Cyan
        Write-Host "C:\Users\aviad\OneDrive\Desktop\backv2\start-findoc-app.ps1" -ForegroundColor White
    }
}
