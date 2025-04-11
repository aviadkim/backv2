# Validate critical files
# Get absolute path of script location
$scriptDir = $PSScriptRoot
$devDocsPath = Join-Path $scriptDir "DevDocs"

if (-not (Test-Path $devDocsPath)) {
    Write-Host "Error: DevDocs directory not found at $devDocsPath"
    exit 1
}

if (-not (Test-Path (Join-Path $devDocsPath "docker-compose.yml"))) {
    Write-Host "Error: docker-compose.yml not found in $devDocsPath"
    exit 1
}
# Define paths
$repoPath = Join-Path $scriptDir "repo"

# Validate repo directory
if (-not (Test-Path $repoPath)) {
    Write-Host "Error: repo directory not found at $repoPath"
    exit 1
}

if (-not (Test-Path (Join-Path $repoPath "docker-compose.yml"))) {
    Write-Host "Error: docker-compose.yml not found in $repoPath"
    exit 1
}

# Clean up existing containers
Write-Host "Stopping existing containers..."
docker-compose -f (Join-Path $devDocsPath "docker-compose.yml") down
docker-compose -f (Join-Path $repoPath "docker-compose.yml") down
docker-compose -f (Join-Path $devDocsPath "docker-compose.yml") down

# Validate all required files
$requiredFiles = @(
    "docker-compose.yml",
    "package.json"
)

foreach ($file in $requiredFiles) {
    $fullPath = Join-Path $devDocsPath $file
    if (-not (Test-Path $fullPath)) {
        Write-Host "Error: Required file $file not found at $fullPath"
        exit 1
    }
}

# Build and start Docker infrastructure with error handling
try {
    # Start DevDocs containers
    Set-Location $devDocsPath
    Write-Host "Starting DevDocs Docker containers..."
    docker-compose -f docker-compose.yml up -d --build
    
    # Start repo containers
    Set-Location $repoPath
    Write-Host "Starting repo Docker containers..."
    docker-compose -f docker-compose.yml up -d --build
    
    # Return to script directory
    Set-Location $scriptDir
}
catch {
    Write-Host "Docker startup failed: $($_.Exception.Message)"
    exit 1
}

# Verify container status with retries
$maxRetries = 3
$retryCount = 0
$containersReady = $false

while ($retryCount -lt $maxRetries -and -not $containersReady) {
    Start-Sleep -Seconds 10
    try {
        # Check for Redis container (could be named 'some-redis' or similar)
        $redisStatus = docker inspect --format='{{.State.Status}}' $(docker ps -q --filter "name=redis") 2>&1
        
        # Check for MongoDB container (named 'mongodb' in repo docker-compose)
        $mongoStatus = docker inspect --format='{{.State.Status}}' $(docker ps -q --filter "name=mongodb") 2>&1
        
        if ($redisStatus -eq "running" -and $mongoStatus -eq "running") {
            $containersReady = $true
            Write-Host "Docker containers operational"
        }
        else {
            $retryCount++
            Write-Host "Waiting for containers to start... (attempt $retryCount/$maxRetries)"
        }
    }
    catch {
        $retryCount++
        Write-Host "Container check failed: $($_.Exception.Message)"
    }
}

if (-not $containersReady) {
    Write-Host "Critical Error: Containers failed to start after $maxRetries attempts"
    exit 1
}

# Install dependencies and start application
try {
    Write-Host "Installing npm dependencies..."
    Set-Location $devDocsPath # Change to DevDocs directory first
    npm install # Install dependencies in the current directory (DevDocs)
    
    Write-Host "Starting application services..."
    Set-Location $devDocsPath
    npm run dev:all 2>&1 | Tee-Object -FilePath "startup.log"
    
    if (-not $?) {
        throw "npm run dev:all failed with exit code $LASTEXITCODE"
    }
}
catch {
    Write-Host "Application startup error: $($_.Exception.Message)"
    Get-Content "startup.log" | Write-Host
    exit 1
}

# Enhanced health checks with timeouts
$healthEndpoints = @(
    @{Url = "http://localhost:3000/api/health"; Timeout = 10},
    @{Url = "http://localhost:5173/healthcheck"; Timeout = 15}
)

foreach ($endpoint in $healthEndpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint.Url -UseBasicParsing -TimeoutSec $endpoint.Timeout
        Write-Host "$($endpoint.Url) : Healthy ($($response.StatusCode))"
    }
    catch {
        Write-Host "$($endpoint.Url) : Unhealthy - $($_.Exception.Message)"
        Write-Host "Checking running processes:"
        Get-Process node -ErrorAction SilentlyContinue | Format-Table Id, Path
        exit 1
    }
}

# Clean up any existing node processes
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Host "[SUCCESS] All systems operational - Application started successfully"