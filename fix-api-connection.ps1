# Script to diagnose and fix API connection issues

Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "API Connection Diagnostic and Fix Tool" -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan

# Define variables
$backendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\backend"
$frontendDir = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend"
$apiUrl = "http://localhost:24125"
$frontendUrl = "http://localhost:3002"

# Create a middleware.py file to fix CORS issues
Write-Host "`nStep 1: Creating CORS middleware..." -ForegroundColor Yellow

$middlewareContent = @"
"""Middleware functions for the Flask application"""
from flask import request, current_app

def setup_cors_headers(response):
    """Add CORS headers to every response"""
    # Allow requests from any origin
    response.headers['Access-Control-Allow-Origin'] = '*'
    
    # Allow specific HTTP methods
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    
    # Allow specific headers in requests
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    
    # Cache preflight response for 1 hour (3600 seconds)
    response.headers['Access-Control-Max-Age'] = '3600'
    
    return response

def handle_options_requests():
    """Handler for OPTIONS requests"""
    if request.method == 'OPTIONS':
        # Create response object
        response = current_app.make_default_options_response()
        
        # Add CORS headers
        setup_cors_headers(response)
        
        return response
    
    # Not an OPTIONS request, continue normal processing
    return None
"@

Set-Location -Path $backendDir
$middlewareContent | Out-File -FilePath "middleware.py" -Encoding utf8

# Step 2: Verify the API is running
Write-Host "`nStep 2: Checking if API is running..." -ForegroundColor Yellow

$apiRunning = $false
try {
    $response = Invoke-WebRequest -Uri "$apiUrl/api/health" -UseBasicParsing -TimeoutSec 2
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ API is running!" -ForegroundColor Green
        $apiRunning = $true
    } else {
        Write-Host "✗ API returned status code: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ API is not running or not responding: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 3: If API is not running, start it
if (-not $apiRunning) {
    Write-Host "`nStep 3: Starting the API..." -ForegroundColor Yellow
    
    # Kill any existing processes on the port
    $portCheck = netstat -ano | Select-String "24125" | Select-String "LISTENING"
    if ($portCheck) {
        $processId = $portCheck[0].ToString().Split(" ")[-1].Trim()
        try {
            Stop-Process -Id $processId -Force
            Write-Host "Killed process $processId using port 24125" -ForegroundColor Green
        } catch {
            Write-Host "Failed to kill process: $_" -ForegroundColor Red
        }
    }
    
    # Start the API
    Set-Location -Path $backendDir
    $apiProcess = Start-Process -FilePath "python" -ArgumentList "app.py" -PassThru -WindowStyle Normal
    
    # Wait for API to start
    Write-Host "Waiting for API to start..." -ForegroundColor Cyan
    $retries = 0
    $maxRetries = 10
    $apiStarted = $false
    
    while (-not $apiStarted -and $retries -lt $maxRetries) {
        $retries++
        Start-Sleep -Seconds 2
        
        try {
            $response = Invoke-WebRequest -Uri "$apiUrl/api/health" -UseBasicParsing -TimeoutSec 1
            if ($response.StatusCode -eq 200) {
                $apiStarted = $true
                Write-Host "✓ API started successfully!" -ForegroundColor Green
            }
        } catch {
            Write-Host "Waiting for API to start (attempt $retries/$maxRetries)..." -ForegroundColor Yellow
        }
    }
    
    if (-not $apiStarted) {
        Write-Host "✗ Failed to start the API" -ForegroundColor Red
    }
}

# Step 4: Test API endpoints
Write-Host "`nStep 4: Testing API endpoints..." -ForegroundColor Yellow

$endpoints = @(
    @{Path = "/api/health"; Name = "Health check"},
    @{Path = "/api/documents"; Name = "Documents list"},
    @{Path = "/api/tags"; Name = "Tags list"}
)

$endpointsWorking = $true

foreach ($endpoint in $endpoints) {
    Write-Host "Testing $($endpoint.Name) endpoint..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri "$apiUrl$($endpoint.Path)" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ $($endpoint.Name) endpoint is working" -ForegroundColor Green
        } else {
            Write-Host "✗ $($endpoint.Name) endpoint returned status code: $($response.StatusCode)" -ForegroundColor Red
            $endpointsWorking = $false
        }
    } catch {
        Write-Host "✗ $($endpoint.Name) endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
        $endpointsWorking = $false
    }
}

# Step 5: Fix Next.js version if needed
Write-Host "`nStep 5: Checking Next.js version..." -ForegroundColor Yellow

Set-Location -Path $frontendDir
$packageJson = Get-Content -Path "package.json" -Raw | ConvertFrom-Json
$currentNextVersion = $packageJson.dependencies.next

if ($currentNextVersion -like "*15.1.4*") {
    Write-Host "Next.js is outdated (version $currentNextVersion). Updating to v14.0.4..." -ForegroundColor Yellow
    
    # Update package.json
    $packageJson.dependencies.next = "^14.0.4"
    $packageJson | ConvertTo-Json -Depth 10 | Set-Content -Path "package.json"
    
    # Install updated dependencies
    Write-Host "Installing updated dependencies..." -ForegroundColor Cyan
    npm install
    
    Write-Host "✓ Next.js version has been updated" -ForegroundColor Green
} else {
    Write-Host "✓ Next.js version is already up to date ($currentNextVersion)" -ForegroundColor Green
}

# Final summary
Write-Host "`n===============================================================" -ForegroundColor Cyan
Write-Host "Fix Summary" -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan

Write-Host "API Status: $(if ($apiRunning -or $apiStarted) { "Running ✓" } else { "Not Running ✗" })" -ForegroundColor $(if ($apiRunning -or $apiStarted) { "Green" } else { "Red" })
Write-Host "API Endpoints: $(if ($endpointsWorking) { "Working ✓" } else { "Some Failed ✗" })" -ForegroundColor $(if ($endpointsWorking) { "Green" } else { "Yellow" })
Write-Host "Next.js: $(if ($currentNextVersion -notlike "*15.1.4*") { "Updated ✓" } else { "Outdated ✗" })" -ForegroundColor $(if ($currentNextVersion -notlike "*15.1.4*") { "Green" } else { "Yellow" })

Write-Host "`nNext steps:" -ForegroundColor White
Write-Host "1. Restart the frontend: cd $frontendDir; npm run dev" -ForegroundColor Cyan
Write-Host "2. Verify the app works at: $frontendUrl" -ForegroundColor Cyan
Write-Host "3. If issues persist, review the UI status document for more information" -ForegroundColor Cyan
