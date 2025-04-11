# Script to run the FinDoc application
Write-Host "=== FinDoc Application Launcher ===" -ForegroundColor Cyan

# Function to properly kill processes using a port
function Kill-ProcessByPort {
    param(
        [int]$Port
    )
    
    $processInfo = netstat -ano | findstr ":$Port" | findstr "LISTENING"
    if ($processInfo) {
        try {
            # Extract PID
            $pid = ($processInfo -split '\s+')[-1]
            # Get process
            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($process) {
                # Kill process
                Write-Host "Killing process $($process.ProcessName) (PID: $pid)..." -ForegroundColor Yellow
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                # Wait to ensure process is killed
                Start-Sleep -Seconds 1
                
                # Check if process is still running
                $checkProcess = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($checkProcess) {
                    Write-Host "Process could not be killed. Try manually stopping PID: $pid" -ForegroundColor Red
                } else {
                    Write-Host "Process successfully terminated" -ForegroundColor Green
                }
            }
        } catch {
            Write-Host "Error processing port $Port" -ForegroundColor Red
        }
    } else {
        Write-Host "No process using port $Port" -ForegroundColor Green
    }
}

# More reliably kill processes on required ports
Write-Host "`nStopping any processes using required ports..." -ForegroundColor Yellow
Kill-ProcessByPort -Port 24125
Kill-ProcessByPort -Port 3003

# Ensure ports are free before continuing
Start-Sleep -Seconds 2

# Start backend in a new window
$backendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend"
if (Test-Path $backendDir) {
    Write-Host "Starting backend..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; python app.py"
    
    # Wait for backend to start
    Write-Host "Waiting for backend to start (5 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
} else {
    Write-Host "Backend directory not found at $backendDir" -ForegroundColor Red
    exit
}

# Open browser to the frontend URL
Start-Process "http://localhost:3003"

# Start frontend
$frontendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend"
if (Test-Path $frontendDir) {
    Write-Host "`nStarting frontend..." -ForegroundColor Cyan
    Write-Host "Frontend will be available at: http://localhost:3003" -ForegroundColor Green
    Write-Host "`nPress Ctrl+C to stop the frontend when done`n" -ForegroundColor Yellow
    
    Set-Location -Path $frontendDir
    npm run dev
} else {
    Write-Host "Frontend directory not found at $frontendDir" -ForegroundColor Red
}
