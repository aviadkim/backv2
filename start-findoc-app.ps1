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
    # Check if app.py exists
    if (-not (Test-Path "$backendDir\app.py")) {
        Write-Host "ERROR: app.py not found in backend directory!" -ForegroundColor Red
        Write-Host "Expected location: $backendDir\app.py" -ForegroundColor Red
        exit
    }
    
    # Check if Python is installed
    try {
        $pythonVersion = python --version
        Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Python not found or not in PATH!" -ForegroundColor Red
        Write-Host "Please install Python and make sure it's in your PATH" -ForegroundColor Red
        exit
    }
    
    # Try to start the backend with more verbose error handling
    try {
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; python app.py" -WindowStyle Normal
        Write-Host "Backend started in a new window" -ForegroundColor Green
        
        # Wait for backend to start and verify it's running
        Write-Host "Waiting for backend to initialize (15 seconds)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        
        # Check if backend is actually running after a few seconds
        $attempt = 1
        $maxAttempts = 3
        $backendRunning = $false
        
        while ($attempt -le $maxAttempts -and -not $backendRunning) {
            if (Test-PortInUse -Port 24125) {
                $backendRunning = $true
                Write-Host "Backend is now running on port 24125 ✓" -ForegroundColor Green
            } else {
                Write-Host "Backend not detected yet (attempt $attempt/$maxAttempts)..." -ForegroundColor Yellow
                Start-Sleep -Seconds 5
                $attempt++
            }
        }
        
        if (-not $backendRunning) {
            Write-Host "WARNING: Backend might not have started properly!" -ForegroundColor Red
            Write-Host "Check the backend window for error messages." -ForegroundColor Yellow
            Write-Host "Do you want to continue starting the frontend anyway? (Y/N)" -ForegroundColor Cyan
            $response = Read-Host
            if ($response.ToLower() -ne "y") {
                exit
            }
        }
    } catch {
        Write-Host "ERROR: Failed to start backend: $_" -ForegroundColor Red
        exit
    }
} else {
    Write-Host "ERROR: Backend directory not found: $backendDir" -ForegroundColor Red
    exit
}

# Step 3: Start frontend in this window
Write-Host "`nStep 3: Starting frontend with FinDoc UI..." -ForegroundColor Yellow
$frontendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend"

if (Test-Path $frontendDir) {
    # Verify package.json and required components
    if (-not (Test-Path "$frontendDir\package.json")) {
        Write-Host "ERROR: package.json not found in frontend directory!" -ForegroundColor Red
        exit
    }
    
    # Check if components directory exists
    if (-not (Test-Path "$frontendDir\components")) {
        Write-Host "ERROR: components directory not found! FinDoc UI won't work properly." -ForegroundColor Red
        Write-Host "Run setup script first: .\setup-findoc-ui.ps1" -ForegroundColor Yellow
        exit
    }
    
    # Check if FinDocLayout.js exists
    if (-not (Test-Path "$frontendDir\components\FinDocLayout.js")) {
        Write-Host "ERROR: FinDocLayout.js not found! FinDoc UI won't work properly." -ForegroundColor Red
        Write-Host "Run setup script first: .\setup-findoc-ui.ps1" -ForegroundColor Yellow
        exit
    }
    
    # Start npm
    try {
        Write-Host "`nFinDoc Analyzer is starting!" -ForegroundColor Cyan
        Write-Host "Backend API: http://localhost:24125" -ForegroundColor Cyan
        Write-Host "Frontend UI: http://localhost:3002" -ForegroundColor Cyan
        Write-Host "`nPress Ctrl+C to stop the frontend (close the other window to stop the backend)" -ForegroundColor Yellow
        
        Set-Location -Path $frontendDir
        npm run dev
    } catch {
        Write-Host "ERROR: Failed to start frontend: $_" -ForegroundColor Red
        Write-Host "Check if npm is installed and working properly" -ForegroundColor Yellow
    }
} else {
    Write-Host "ERROR: Frontend directory not found: $frontendDir" -ForegroundColor Red
}
