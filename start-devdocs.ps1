# DevDocs Startup Script
# This script starts the DevDocs application components

Write-Host "Starting DevDocs Application..." -ForegroundColor Green

# Navigate to the DevDocs directory
Set-Location -Path "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs"
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Cyan

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

    Write-Host "Checking for processes using port $Port..." -ForegroundColor Yellow
    $connections = netstat -ano | Select-String -Pattern "TCP.*:$Port\s+.*LISTENING"
    
    if ($connections.Count -gt 0) {
        foreach ($connection in $connections) {
            $processId = $connection.ToString().Split(" ")[-1].Trim()
            Write-Host "Stopping process ID $processId" -ForegroundColor Yellow
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        }
    } else {
        Write-Host "No process found using port $Port" -ForegroundColor Green
    }
}

# Kill any processes using our ports
Stop-ProcessOnPort -Port 24125
Stop-ProcessOnPort -Port 3002

# Start the backend server directly (not in a new window for debugging)
Write-Host "Starting Flask backend server..." -ForegroundColor Cyan
$backendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend"
Set-Location -Path $backendDir
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Cyan

# Check if app.py exists in the backend directory
if (-not (Test-Path -Path "$backendDir\app.py")) {
    Write-Host "ERROR: app.py not found in $backendDir" -ForegroundColor Red
    exit 1
}

# Start backend in a new window but with detailed output
$pythonCommand = "cd '$backendDir'; Write-Host 'Starting Python App...'; python app.py"
Write-Host "Command: $pythonCommand" -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", $pythonCommand

# Wait for backend to start
Write-Host "Waiting for backend server to start..." -ForegroundColor Cyan
$maxRetries = 15
$retryCount = 0
$backendRunning = $false

while (-not $backendRunning -and $retryCount -lt $maxRetries) {
    Start-Sleep -Seconds 2
    $retryCount++
    
    try {
        Write-Host "Attempt $retryCount: Testing connection to http://localhost:24125/api/health" -ForegroundColor Yellow
        $response = Invoke-WebRequest -Uri "http://localhost:24125/api/health" -Method GET -UseBasicParsing -TimeoutSec 1
        if ($response.StatusCode -eq 200) {
            $backendRunning = $true
            Write-Host "Backend server is running! Response: $($response.Content)" -ForegroundColor Green
        }
    } catch {
        Write-Host "Waiting for backend to start (attempt $retryCount/$maxRetries): $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

if (-not $backendRunning) {
    Write-Host "Failed to start backend server after $maxRetries attempts" -ForegroundColor Red
    Write-Host "Please check for errors in the backend terminal window" -ForegroundColor Yellow
    
    # Try to test the root endpoint as fallback
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:24125/" -Method GET -UseBasicParsing -TimeoutSec 1
        Write-Host "Root endpoint responded with: $($response.Content)" -ForegroundColor Cyan
    } catch {
        Write-Host "Root endpoint also failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    $continueAnyway = Read-Host "Do you want to continue with frontend setup anyway? (y/n)"
    if ($continueAnyway -ne "y" -and $continueAnyway -ne "Y") {
        exit 1
    }
}

# Return to the DevDocs directory
Set-Location -Path "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs"

# Start the frontend server
Write-Host "Starting Next.js frontend server..." -ForegroundColor Cyan
$frontendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend"

# Check if package.json exists in the frontend directory
if (-not (Test-Path -Path "$frontendDir\package.json")) {
    Write-Host "ERROR: package.json not found in $frontendDir" -ForegroundColor Red
    exit 1
}

$npmCommand = "cd '$frontendDir'; Write-Host 'Starting Next.js App...'; npm run dev"
Write-Host "Command: $npmCommand" -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", $npmCommand

# Wait for frontend to start
Write-Host "Waiting for frontend server to start..." -ForegroundColor Cyan
$maxRetries = 20
$retryCount = 0
$frontendRunning = $false

while (-not $frontendRunning -and $retryCount -lt $maxRetries) {
    Start-Sleep -Seconds 2
    $retryCount++
    
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $portOpen = $tcpClient.ConnectAsync("localhost", 3002).Wait(1000)
        $tcpClient.Close()
        
        if ($portOpen) {
            $frontendRunning = $true
            Write-Host "Frontend server is running!" -ForegroundColor Green
        }
    } catch {
        Write-Host "Waiting for frontend to start (attempt $retryCount/$maxRetries): $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

if (-not $frontendRunning) {
    Write-Host "Failed to start frontend server after $maxRetries attempts" -ForegroundColor Red
    Write-Host "Please check for errors in the frontend terminal window" -ForegroundColor Yellow
    exit 1
}

Write-Host "DevDocs application is now running!" -ForegroundColor Green
Write-Host "Frontend URL: http://localhost:3002" -ForegroundColor Cyan
Write-Host "Backend API URL: http://localhost:24125" -ForegroundColor Cyan
Write-Host "Press Ctrl+C in each terminal window to stop the servers when done" -ForegroundColor Yellow

# Run tests if requested
$runTests = Read-Host "Would you like to run tests now? (y/n)"
if ($runTests -eq "y" -or $runTests -eq "Y") {
    Write-Host "Running tests..." -ForegroundColor Green
    & "C:\Users\aviad\OneDrive\Desktop\backv2\test-devdocs.ps1"
}
