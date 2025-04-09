# DevDocs Full Application Startup Script
# This script installs dependencies, starts both backend and frontend, and verifies they're working

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "DevDocs Full Application Startup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"
$backendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend"
$frontendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend"

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

# Step 1: Install backend dependencies
Write-Host "`nStep 1: Installing backend dependencies..." -ForegroundColor Yellow
Set-Location -Path $backendDir
python -m pip install flask flask_cors

# Step 2: Install frontend dependencies
Write-Host "`nStep 2: Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location -Path $frontendDir
npm install

# Step 3: Clear ports if they're in use
Write-Host "`nStep 3: Clearing ports..." -ForegroundColor Yellow
Stop-ProcessOnPort -Port 24125  # Backend API
Stop-ProcessOnPort -Port 3002   # Frontend

# Step 4: Start the backend
Write-Host "`nStep 4: Starting backend server..." -ForegroundColor Yellow
Set-Location -Path $backendDir
$backendProcess = Start-Process -FilePath "python" -ArgumentList "app.py" -PassThru -NoNewWindow

# Step 5: Start the frontend in a new window
Write-Host "`nStep 5: Starting frontend server..." -ForegroundColor Yellow
Set-Location -Path $frontendDir
$frontendProcess = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -PassThru -NoNewWindow

# Step 6: Wait for servers to start and verify they're running
Write-Host "`nStep 6: Verifying servers are running..." -ForegroundColor Yellow
$apiUrl = "http://localhost:24125/api/health"
$frontendUrl = "http://localhost:3002"

# Wait for backend
Write-Host "Waiting for backend to start..." -ForegroundColor Cyan
$backendReady = $false
$retries = 0
$maxRetries = 10

while (!$backendReady -and $retries -lt $maxRetries) {
    $retries++
    try {
        $response = Invoke-WebRequest -Uri $apiUrl -UseBasicParsing -TimeoutSec 1
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            Write-Host "✓ Backend is running!" -ForegroundColor Green
        }
    } catch {
        Start-Sleep -Seconds 2
        Write-Host "Waiting for backend ($retries/$maxRetries)..." -ForegroundColor Yellow
    }
}

if (!$backendReady) {
    Write-Host "✗ Backend failed to start properly" -ForegroundColor Red
}

# Wait for frontend
Write-Host "Waiting for frontend to start..." -ForegroundColor Cyan
$frontendReady = $false
$retries = 0
$maxRetries = 15

while (!$frontendReady -and $retries -lt $maxRetries) {
    $retries++
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $portOpen = $tcpClient.ConnectAsync("localhost", 3002).Wait(1000)
        $tcpClient.Close()
        
        if ($portOpen) {
            $frontendReady = $true
            Write-Host "✓ Frontend is running!" -ForegroundColor Green
        }
    } catch {
        Start-Sleep -Seconds 2
        Write-Host "Waiting for frontend ($retries/$maxRetries)..." -ForegroundColor Yellow
    }
}

if (!$frontendReady) {
    Write-Host "✗ Frontend failed to start properly" -ForegroundColor Red
}

# Step 7: Open browser
if ($backendReady -and $frontendReady) {
    Write-Host "`nStep 7: Opening application in browser..." -ForegroundColor Yellow
    Start-Process $frontendUrl
}

# Display status and instructions
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "DevDocs Application Status" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "Backend: $(if ($backendReady) { "Running ✓" } else { "Not Running ✗" })" -ForegroundColor $(if ($backendReady) { "Green" } else { "Red" })
Write-Host "Frontend: $(if ($frontendReady) { "Running ✓" } else { "Not Running ✗" })" -ForegroundColor $(if ($frontendReady) { "Green" } else { "Red" })

Write-Host "`nApplication URLs:" -ForegroundColor White
Write-Host "- Backend API: $apiUrl" -ForegroundColor Cyan
Write-Host "- Frontend: $frontendUrl" -ForegroundColor Cyan

Write-Host "`nTo stop the servers, close the windows or press Ctrl+C in each window" -ForegroundColor Yellow
