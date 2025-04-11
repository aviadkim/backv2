# Improved script to run the FinDoc application
Write-Host "=== FinDoc Application Launcher ===" -ForegroundColor Cyan

# First, kill all Node.js processes (this will terminate any Next.js server)
Get-Process -Name "node" -ErrorAction SilentlyContinue | ForEach-Object { 
    Write-Host "Stopping Node.js process (PID: $($_.Id))..." -ForegroundColor Yellow
    Stop-Process -Id $_.Id -Force 
}

# Then kill all Python processes (this will terminate any Flask server)
Get-Process -Name "python" -ErrorAction SilentlyContinue | ForEach-Object { 
    Write-Host "Stopping Python process (PID: $($_.Id))..." -ForegroundColor Yellow
    Stop-Process -Id $_.Id -Force 
}

# Wait for processes to fully terminate
Start-Sleep -Seconds 3

# Start backend in a new window
$backendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend"
if (Test-Path $backendDir) {
    Write-Host "`nStarting backend..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; python app.py" -WindowStyle Normal
    
    # Wait for backend to start
    Write-Host "Waiting for backend to initialize (5 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
} else {
    Write-Host "Backend directory not found at $backendDir" -ForegroundColor Red
    exit
}

# Start frontend with better error handling
$frontendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend"
if (Test-Path $frontendDir) {
    Write-Host "`nStarting frontend..." -ForegroundColor Cyan
    Write-Host "Frontend will be available at: http://localhost:3003" -ForegroundColor Green
    
    # Open browser to the frontend URL after a brief delay
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:3003"
    
    Write-Host "`nPress Ctrl+C to stop the frontend when done`n" -ForegroundColor Yellow
    
    # Start the frontend with error handling
    Set-Location -Path $frontendDir
    try {
        # Make sure dependencies are installed
        if (!(Test-Path (Join-Path $frontendDir "node_modules"))) {
            Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
            npm install --legacy-peer-deps
        }
        
        # Start the development server
        npm run dev
    } catch {
        Write-Host "Error starting frontend: $_" -ForegroundColor Red
        Write-Host "Try running 'npm install' and 'npm run dev' manually in the frontend directory" -ForegroundColor Yellow
    }
} else {
    Write-Host "Frontend directory not found at $frontendDir" -ForegroundColor Red
}
