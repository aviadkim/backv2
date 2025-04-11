# Script to diagnose issues with the FinDoc app

Write-Host "=== FinDoc Application Diagnostic Tool ===" -ForegroundColor Cyan
Write-Host "Running comprehensive diagnostics..." -ForegroundColor Yellow

# Check directory structure
Write-Host "`n1. Checking directory structure:" -ForegroundColor Cyan
$requiredDirs = @(
    "C:\Users\aviad\OneDrive\Desktop\backv2",
    "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs",
    "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend",
    "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend"
)

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "✓ Directory exists: $dir" -ForegroundColor Green
    } else {
        Write-Host "✗ Directory missing: $dir" -ForegroundColor Red
    }
}

# Check backend files
Write-Host "`n2. Checking backend files:" -ForegroundColor Cyan
$backendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend"
$backendFiles = @(
    "app.py"
)

if (Test-Path $backendDir) {
    foreach ($file in $backendFiles) {
        $filePath = Join-Path $backendDir $file
        if (Test-Path $filePath) {
            $fileSize = (Get-Item $filePath).Length
            Write-Host "✓ File exists: $file ($fileSize bytes)" -ForegroundColor Green
        } else {
            Write-Host "✗ File missing: $file" -ForegroundColor Red
        }
    }
} else {
    Write-Host "✗ Cannot check backend files - directory missing" -ForegroundColor Red
}

# Check frontend files
Write-Host "`n3. Checking frontend files:" -ForegroundColor Cyan
$frontendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend"
$frontendFiles = @(
    "package.json",
    "pages\index.js",
    "pages\_app.js",
    "components\FinDocLayout.js",
    "styles\globals.css"
)

if (Test-Path $frontendDir) {
    foreach ($file in $frontendFiles) {
        $filePath = Join-Path $frontendDir $file
        if (Test-Path $filePath) {
            $fileSize = (Get-Item $filePath).Length
            Write-Host "✓ File exists: $file ($fileSize bytes)" -ForegroundColor Green
        } else {
            Write-Host "✗ File missing: $file" -ForegroundColor Red
        }
    }
} else {
    Write-Host "✗ Cannot check frontend files - directory missing" -ForegroundColor Red
}

# Check software prerequisites
Write-Host "`n4. Checking software prerequisites:" -ForegroundColor Cyan

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python installed: $pythonVersion" -ForegroundColor Green
    
    # Check Python packages
    try {
        $flaskInstalled = python -c "import flask; print(f'Flask {flask.__version__}')" 2>&1
        Write-Host "✓ Flask installed: $flaskInstalled" -ForegroundColor Green
    } catch {
        Write-Host "✗ Flask not installed or error importing" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Python not found or not in PATH" -ForegroundColor Red
}

# Check Node.js and npm
try {
    $nodeVersion = node --version 2>&1
    $npmVersion = npm --version 2>&1
    Write-Host "✓ Node.js installed: $nodeVersion" -ForegroundColor Green
    Write-Host "✓ npm installed: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js or npm not found or not in PATH" -ForegroundColor Red
}

# Check network ports
Write-Host "`n5. Checking network ports:" -ForegroundColor Cyan
$requiredPorts = @(
    @{Port = 3002; Service = "Frontend"},
    @{Port = 24125; Service = "Backend API"}
)

foreach ($portInfo in $requiredPorts) {
    $port = $portInfo.Port
    $service = $portInfo.Service
    
    $connections = netstat -ano | Select-String -Pattern "TCP.*:$port\s+.*LISTENING"
    if ($connections) {
        $processId = ($connections[0] -split "\s+")[-1]
        try {
            $process = Get-Process -Id $processId -ErrorAction Stop
            Write-Host "! Port $port ($service) is in use by: $($process.ProcessName) (PID: $processId)" -ForegroundColor Yellow
        } catch {
            Write-Host "! Port $port ($service) is in use by unknown process (PID: $processId)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "✓ Port $port ($service) is available" -ForegroundColor Green
    }
}

# Test FinDoc UI setup
Write-Host "`n6. Testing FinDoc UI setup:" -ForegroundColor Cyan
$checkIndexJs = Join-Path $frontendDir "pages\index.js"
$finDocLayoutImport = $false

if (Test-Path $checkIndexJs) {
    $content = Get-Content $checkIndexJs -Raw
    if ($content -match "import\s+FinDocLayout\s+from\s+['\"]") {
        Write-Host "✓ FinDocLayout is properly imported in index.js" -ForegroundColor Green
        $finDocLayoutImport = $true
    } else {
        Write-Host "✗ FinDocLayout import not found in index.js" -ForegroundColor Red
    }
    
    if ($content -match "<FinDocLayout>") {
        Write-Host "✓ FinDocLayout component is used in index.js" -ForegroundColor Green
    } else {
        Write-Host "✗ FinDocLayout component not used in index.js" -ForegroundColor Red
    }
} else {
    Write-Host "✗ Cannot check UI setup - index.js missing" -ForegroundColor Red
}

# Add more detailed checks and solutions for common issues

# Check for missing Flask CORS
Write-Host "`n7. Checking for Flask-CORS:" -ForegroundColor Cyan
try {
    $corsInstalled = python -c "import flask_cors; print('Flask-CORS installed')" 2>&1
    Write-Host "✓ Flask-CORS is installed" -ForegroundColor Green
} catch {
    Write-Host "✗ Flask-CORS is not installed - this may cause API connection issues" -ForegroundColor Red
    Write-Host "  Run: pip install flask-cors" -ForegroundColor Yellow
}

# Check Next.js version compatibility
Write-Host "`n8. Checking Next.js version:" -ForegroundColor Cyan
if (Test-Path (Join-Path $frontendDir "package.json")) {
    try {
        $packageJson = Get-Content -Path (Join-Path $frontendDir "package.json") -Raw | ConvertFrom-Json
        $nextVersion = $packageJson.dependencies.next
        if ($nextVersion -like "*15.1.4*") {
            Write-Host "✗ Incompatible Next.js version detected: $nextVersion" -ForegroundColor Red
            Write-Host "  This version has known issues with our application" -ForegroundColor Red
        } else {
            Write-Host "✓ Next.js version appears compatible: $nextVersion" -ForegroundColor Green
        }
    } catch {
        Write-Host "! Could not parse package.json to check Next.js version" -ForegroundColor Yellow
    }
}

# Check API connectivity
Write-Host "`n9. Testing API connectivity:" -ForegroundColor Cyan

# First check if backend is already running
$backendRunning = $false
$backendPort = netstat -ano | Select-String -Pattern "TCP.*:24125\s+.*LISTENING"
if ($backendPort) {
    $backendRunning = $true
    Write-Host "Found backend already running on port 24125" -ForegroundColor Yellow
    
    # Try accessing the API endpoints
    $endpoints = @("/api/health", "/api/documents", "/api/tags")
    foreach ($endpoint in $endpoints) {
        $url = "http://localhost:24125$endpoint"
        Write-Host "Testing endpoint: $url" -ForegroundColor Yellow
        try {
            $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
            Write-Host "✓ Endpoint accessible: $endpoint (Status: $($response.StatusCode))" -ForegroundColor Green
        } catch {
            Write-Host "✗ Failed to access endpoint: $endpoint (Error: $($_.Exception.Message))" -ForegroundColor Red
        }
    }
} else {
    Write-Host "Backend is not currently running - can't test API connectivity" -ForegroundColor Yellow
}

# Check for common errors in app.py
Write-Host "`n10. Scanning backend code for common issues:" -ForegroundColor Cyan
$appPyPath = Join-Path $backendDir "app.py"
if (Test-Path $appPyPath) {
    $appPyContent = Get-Content -Path $appPyPath -Raw
    
    # Check for common errors
    $issues = @()
    
    if (-not ($appPyContent -match "FLASK_SKIP_DOTENV")) {
        $issues += "Missing FLASK_SKIP_DOTENV environment variable (may cause Unicode decode errors)"
    }
    
    if (-not ($appPyContent -match "CORS\(app\)")) {
        $issues += "CORS middleware may not be properly configured"
    }
    
    if (-not ($appPyContent -match "host=.*0\.0\.0\.0")) {
        $issues += "Flask may not be configured to listen on all interfaces (0.0.0.0)"
    }
    
    if (-not ($appPyContent -match "port=.*24125")) {
        $issues += "Flask may be using wrong port (should be 24125)"
    }
    
    # Display issues or success
    if ($issues.Count -gt 0) {
        Write-Host "Found potential issues in app.py:" -ForegroundColor Yellow
        foreach ($issue in $issues) {
            Write-Host "- $issue" -ForegroundColor Yellow
        }
    } else {
        Write-Host "✓ No common issues detected in app.py" -ForegroundColor Green
    }
} else {
    Write-Host "✗ Cannot scan app.py - file not found" -ForegroundColor Red
}

# Provide diagnosis and recommendations
Write-Host "`n=== Diagnosis and Recommendations ===" -ForegroundColor Cyan

# Check if setup-findoc-ui.ps1 has been run
$setupScript = "C:\Users\aviad\OneDrive\Desktop\backv2\setup-findoc-ui.ps1"
if ((Test-Path $setupScript) -and -not $finDocLayoutImport) {
    Write-Host "→ Run the setup script to install the FinDoc UI:" -ForegroundColor Yellow
    Write-Host "   .\setup-findoc-ui.ps1" -ForegroundColor White
}

# Check backend issues
if (-not (Test-Path (Join-Path $backendDir "app.py"))) {
    Write-Host "→ Backend app.py is missing. Make sure to restore the backend code." -ForegroundColor Yellow
}

# Check frontend issues 
if (-not (Test-Path (Join-Path $frontendDir "package.json"))) {
    Write-Host "→ Frontend package.json is missing. Make sure to restore the frontend code." -ForegroundColor Yellow
} elseif (-not (Test-Path (Join-Path $frontendDir "components"))) {
    Write-Host "→ Components directory is missing. Run the setup script." -ForegroundColor Yellow
}

# Enhance the recommendations section
Write-Host "`n=== Diagnosis and Recommendations ===" -ForegroundColor Cyan

# More specific recommendations based on problems found
$problemsFound = 0

# Check if Backend is missing Flask-CORS
try {
    python -c "import flask_cors" 2>&1 | Out-Null
} catch {
    $problemsFound++
    Write-Host "$problemsFound. Install Flask-CORS:" -ForegroundColor Yellow
    Write-Host "   cd C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend" -ForegroundColor White
    Write-Host "   pip install flask-cors" -ForegroundColor White
}

# Check if FinDocLayout is missing
if (-not (Test-Path (Join-Path $frontendDir "components\FinDocLayout.js"))) {
    $problemsFound++
    Write-Host "$problemsFound. Create FinDoc UI components:" -ForegroundColor Yellow
    Write-Host "   .\setup-findoc-ui.ps1" -ForegroundColor White
}

# Check for port conflicts
$portConflicts = $false
foreach ($portInfo in $requiredPorts) {
    $connections = netstat -ano | Select-String -Pattern "TCP.*:$($portInfo.Port)\s+.*LISTENING"
    if ($connections) {
        $portConflicts = $true
        break
    }
}

if ($portConflicts) {
    $problemsFound++
    Write-Host "$problemsFound. Free up required ports:" -ForegroundColor Yellow
    Write-Host "   .\free-ports.ps1" -ForegroundColor White
}

# Check for Next.js version issues
if (Test-Path (Join-Path $frontendDir "package.json")) {
    try {
        $packageJson = Get-Content -Path (Join-Path $frontendDir "package.json") -Raw | ConvertFrom-Json
        $nextVersion = $packageJson.dependencies.next
        if ($nextVersion -like "*15.1.4*") {
            $problemsFound++
            Write-Host "$problemsFound. Fix Next.js version:" -ForegroundColor Yellow
            Write-Host "   cd C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend" -ForegroundColor White
            Write-Host "   npm uninstall next" -ForegroundColor White
            Write-Host "   npm install next@14.0.4" -ForegroundColor White
        }
    } catch {}
}

# Check if app.py has correct port
$appPyPath = Join-Path $backendDir "app.py"
if (Test-Path $appPyPath) {
    $appPyContent = Get-Content -Path $appPyPath -Raw
    if (-not ($appPyContent -match "port=.*24125")) {
        $problemsFound++
        Write-Host "$problemsFound. Update Flask port in app.py:" -ForegroundColor Yellow
        Write-Host "   Edit app.py to use port 24125" -ForegroundColor White
        Write-Host "   app.run(host='0.0.0.0', port=24125)" -ForegroundColor White
    }
}

if ($problemsFound -eq 0) {
    Write-Host "No specific issues detected! If the app still won't start, try the general fixes below." -ForegroundColor Green
}

# Final recommendation
Write-Host "`nTo fix all issues, try these steps:" -ForegroundColor Yellow
Write-Host "1. Run the setup script: .\setup-findoc-ui.ps1" -ForegroundColor White
Write-Host "2. Make sure backend is properly installed: cd DevDocs\backend; pip install flask flask_cors" -ForegroundColor White
Write-Host "3. Install frontend dependencies: cd DevDocs\frontend; npm install" -ForegroundColor White
Write-Host "4. Start the application: .\start-findoc-app.ps1" -ForegroundColor White

Write-Host "`nWould you like to run automatic fixes? (Y/N)" -ForegroundColor Cyan
$response = Read-Host

if ($response.ToLower() -eq "y") {
    Write-Host "`nRunning automatic fixes..." -ForegroundColor Yellow
    
    # Create components directory if missing
    if (-not (Test-Path (Join-Path $frontendDir "components"))) {
        New-Item -ItemType Directory -Path (Join-Path $frontendDir "components") -Force
        Write-Host "✓ Created components directory" -ForegroundColor Green
    }
    
    # Create styles directory if missing
    if (-not (Test-Path (Join-Path $frontendDir "styles"))) {
        New-Item -ItemType Directory -Path (Join-Path $frontendDir "styles") -Force
        Write-Host "✓ Created styles directory" -ForegroundColor Green
    }
    
    # Try to run setup script if it exists
    if (Test-Path $setupScript) {
        Write-Host "Running setup script..." -ForegroundColor Yellow
        & $setupScript
    } else {
        Write-Host "✗ Setup script not found" -ForegroundColor Red
    }
}

Write-Host "`nWould you like to run the Quick-Fix Tool to solve these issues? (Y/N)" -ForegroundColor Cyan
$response = Read-Host

if ($response.ToLower() -eq "y") {
    Write-Host "`nRunning Quick-Fix Tool..." -ForegroundColor Yellow
    & "C:\Users\aviad\OneDrive\Desktop\backv2\fix-all-issues.ps1"
}
