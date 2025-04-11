# Enhanced script to run the FinDoc application with financial analysis features
Write-Host "=== FinDoc Financial Analyzer Launcher ===" -ForegroundColor Cyan

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

# Wait a moment for processes to terminate
Start-Sleep -Seconds 2

# Check if ports are in use
$backendPort = 24125
$frontendPort = 3002

$backendInUse = $false
$frontendInUse = $false

$connections = netstat -ano | Select-String -Pattern "TCP.*:$backendPort.*LISTENING"
if ($connections) {
    $backendInUse = $true
    Write-Host "Warning: Port $backendPort is still in use!" -ForegroundColor Red
}

$connections = netstat -ano | Select-String -Pattern "TCP.*:$frontendPort.*LISTENING"
if ($connections) {
    $frontendInUse = $true
    Write-Host "Warning: Port $frontendPort is still in use!" -ForegroundColor Red
}

if ($backendInUse -or $frontendInUse) {
    Write-Host "Some ports are still in use. Please close the applications using these ports and try again." -ForegroundColor Red
    exit
}

# Step 1: Start backend in a new window
Write-Host "`nStep 1: Starting backend API..." -ForegroundColor Yellow
$backendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend"

if (Test-Path $backendDir) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; python app.py"
    Write-Host "Backend API started in a new window." -ForegroundColor Green
} else {
    Write-Host "Backend directory not found: $backendDir" -ForegroundColor Red
    exit
}

# Wait for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Step 2: Test backend connection
Write-Host "`nStep 2: Testing backend connection..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:24125/api/health" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "Backend API is running and healthy!" -ForegroundColor Green
    } else {
        Write-Host "Backend API returned unexpected status: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "Failed to connect to backend API. Please check if it's running correctly." -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}

# Step 3: Start frontend in this window
Write-Host "`nStep 3: Starting frontend with FinDoc UI..." -ForegroundColor Yellow
$frontendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend"

if (Test-Path $frontendDir) {
    Write-Host "`nFinDoc Financial Analyzer is starting!" -ForegroundColor Cyan
    Write-Host "Backend API: http://localhost:24125" -ForegroundColor Cyan
    Write-Host "Frontend UI: http://localhost:3002" -ForegroundColor Cyan
    Write-Host "`nPress Ctrl+C to stop the frontend (close the other window to stop the backend)" -ForegroundColor Yellow
    
    Set-Location -Path $frontendDir
    npm run dev
} else {
    Write-Host "Frontend directory not found: $frontendDir" -ForegroundColor Red
}
