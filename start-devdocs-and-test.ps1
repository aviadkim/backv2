# DevDocs Startup and Test Script
# This script starts both the backend and frontend, then runs tests

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "DevDocs Startup and Test Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Function to check if a port is in use
function Test-PortInUse {
    param (
        [int]$Port
    )
    
    $connections = netstat -ano | Select-String -Pattern "TCP.*:$Port\s+.*LISTENING"
    return $connections.Count -gt 0
}

# Function to stop process using a specific port
function Stop-ProcessOnPort {
    param (
        [int]$Port
    )

    $connections = netstat -ano | Select-String -Pattern "TCP.*:$Port\s+.*LISTENING"
    
    if ($connections.Count -gt 0) {
        foreach ($connection in $connections) {
            $processId = $connection.ToString().Split(" ")[-1].Trim()
            Write-Host "Stopping process ID $processId on port $Port" -ForegroundColor Yellow
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        }
        return $true
    } else {
        Write-Host "No process found using port $Port" -ForegroundColor Green
        return $false
    }
}

# Kill any processes on relevant ports
Stop-ProcessOnPort -Port 24125  # Backend API
Stop-ProcessOnPort -Port 3002   # Frontend server

# Start the backend server
Write-Host "`nStarting Flask backend..." -ForegroundColor Green
$backendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend"
$backendProcess = Start-Process -FilePath "powershell" -ArgumentList "-Command cd '$backendDir'; python app.py" -PassThru -WindowStyle Normal

# Wait for backend to start
Write-Host "Waiting for backend to initialize..." -ForegroundColor Yellow
$maxRetries = 10
$retries = 0
$backendReady = $false

while (-not $backendReady -and $retries -lt $maxRetries) {
    $retries++
    Start-Sleep -Seconds 2
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:24125/api/health" -UseBasicParsing -TimeoutSec 1
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            Write-Host "Backend is running!" -ForegroundColor Green
        }
    } catch {
        Write-Host "Waiting for backend to start (attempt $retries of $maxRetries)..." -ForegroundColor Yellow
    }
}

if (-not $backendReady) {
    Write-Host "Backend failed to start within the expected time" -ForegroundColor Red
    Write-Host "You can check the backend window for errors" -ForegroundColor Yellow
    
    $continue = Read-Host "Do you want to continue starting the frontend? (y/n)"
    if ($continue.ToLower() -ne "y") {
        exit
    }
}

# Start the frontend server
Write-Host "`nStarting Next.js frontend..." -ForegroundColor Green
$frontendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend"
$frontendProcess = Start-Process -FilePath "powershell" -ArgumentList "-Command cd '$frontendDir'; npm run dev" -PassThru -WindowStyle Normal

# Wait for frontend to start
Write-Host "Waiting for frontend to initialize..." -ForegroundColor Yellow
$maxRetries = 15
$retries = 0
$frontendReady = $false

while (-not $frontendReady -and $retries -lt $maxRetries) {
    $retries++
    Start-Sleep -Seconds 2
    
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $portOpen = $tcpClient.ConnectAsync("localhost", 3002).Wait(1000)
        $tcpClient.Close()
        
        if ($portOpen) {
            $frontendReady = $true
            Write-Host "Frontend is running!" -ForegroundColor Green
        }
    } catch {
        Write-Host "Waiting for frontend to start (attempt $retries of $maxRetries)..." -ForegroundColor Yellow
    }
}

if (-not $frontendReady) {
    Write-Host "Frontend failed to start within the expected time" -ForegroundColor Red
    Write-Host "You can check the frontend window for errors" -ForegroundColor Yellow
}

# Display status
Write-Host "`nDevDocs Application Status:" -ForegroundColor Cyan
Write-Host "- Backend: $(if ($backendReady) { "Running ✓" } else { "Not Running ✗" })" -ForegroundColor $(if ($backendReady) { "Green" } else { "Red" })
Write-Host "- Frontend: $(if ($frontendReady) { "Running ✓" } else { "Not Running ✗" })" -ForegroundColor $(if ($frontendReady) { "Green" } else { "Red" })

# Run tests if both components are running
if ($backendReady) {
    $runTests = Read-Host "`nDo you want to run API tests? (y/n)"
    if ($runTests.ToLower() -eq "y") {
        Write-Host "`nRunning API tests..." -ForegroundColor Green
        & "C:\Users\aviad\OneDrive\Desktop\backv2\test-api.ps1"
    }
}

Write-Host "`nDevDocs is now running!" -ForegroundColor Green
Write-Host "- Backend URL: http://localhost:24125" -ForegroundColor Cyan
Write-Host "- Frontend URL: http://localhost:3002" -ForegroundColor Cyan
Write-Host "`nTo stop the servers, close their PowerShell windows or press Ctrl+C in each window" -ForegroundColor Yellow
