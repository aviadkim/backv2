# Script to start both backend and frontend with the FinDoc UI

Write-Host "=== Starting FinDoc Analyzer Application ===" -ForegroundColor Cyan

# Function to check if a port is in use
function Test-PortInUse {
    param (
        [int]$Port
    )
    
    $connections = netstat -ano | Select-String -Pattern "TCP.*:$Port\s+.*LISTENING"
    return ($connections -ne $null)
}

# Function to free up port if it's in use
function Clear-Port {
    param (
        [int]$Port
    )
    
    if (Test-PortInUse -Port $Port) {
        Write-Host "Port $Port is in use. Attempting to free it up..." -ForegroundColor Yellow
        
        $connections = netstat -ano | Select-String -Pattern "TCP.*:$Port\s+.*LISTENING"
        foreach ($conn in $connections) {
            $processId = ($conn -split "\s+")[-1]
            
            try {
                $process = Get-Process -Id $processId -ErrorAction Stop
                $procName = $process.ProcessName
                
                Write-Host "Stopping $procName (PID: $processId) using port $Port..." -ForegroundColor Yellow
                Stop-Process -Id $processId -Force
                Write-Host "Process stopped successfully" -ForegroundColor Green
            } catch {
                Write-Host "Failed to stop process: $_" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "Port $Port is available" -ForegroundColor Green
    }
}

# Step 1: Clear ports for both frontend and backend
Write-Host "`nStep 1: Clearing ports..." -ForegroundColor Yellow
Clear-Port -Port 3002  # Frontend port
Clear-Port -Port 24125 # Backend port

# Step 2: Start backend in a new window
Write-Host "`nStep 2: Starting backend..." -ForegroundColor Yellow
$backendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend"

if (Test-Path $backendDir) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; python app.py" -WindowStyle Normal
    Write-Host "Backend started in a new window" -ForegroundColor Green
    
    # Wait for backend to start
    Write-Host "Waiting for backend to initialize (10 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
} else {
    Write-Host "Backend directory not found: $backendDir" -ForegroundColor Red
    exit
}

# Step 3: Start frontend in this window
Write-Host "`nStep 3: Starting frontend with FinDoc UI..." -ForegroundColor Yellow
$frontendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend"

if (Test-Path $frontendDir) {
    Write-Host "`nFinDoc Analyzer is starting!" -ForegroundColor Cyan
    Write-Host "Backend API: http://localhost:24125" -ForegroundColor Cyan
    Write-Host "Frontend UI: http://localhost:3002" -ForegroundColor Cyan
    Write-Host "`nPress Ctrl+C to stop the frontend (close the other window to stop the backend)" -ForegroundColor Yellow
    
    Set-Location -Path $frontendDir
    npm run dev
} else {
    Write-Host "Frontend directory not found: $frontendDir" -ForegroundColor Red
}
