# Script to clear port and start the frontend

Write-Host "=== Port Management and App Startup Tool ===" -ForegroundColor Cyan

function Get-ProcessOnPort {
    param (
        [int]$PortNumber
    )
    
    $connections = netstat -ano | Select-String -Pattern "TCP.*:$PortNumber\s+.*LISTENING"
    return $connections
}

function Stop-ProcessOnPort {
    param (
        [int]$PortNumber
    )

    $connections = Get-ProcessOnPort -PortNumber $PortNumber
    
    if ($connections) {
        Write-Host "Found processes using port $PortNumber" -ForegroundColor Yellow
        $connections | ForEach-Object { Write-Host $_ -ForegroundColor Gray }
        
        $processIds = $connections | ForEach-Object {
            $parts = $_ -split " "
            $parts | Where-Object { $_ -match '^\d+$' } | Select-Object -Last 1
        } | Select-Object -Unique
        
        foreach ($processId in $processIds) {
            try {
                $process = Get-Process -Id $processId -ErrorAction Stop
                $processName = $process.ProcessName
                
                Write-Host "Stopping process $processName (ID: $processId) on port $PortNumber" -ForegroundColor Yellow
                Stop-Process -Id $processId -Force
                Write-Host "Successfully stopped process $processName (ID: $processId)" -ForegroundColor Green
            }
            catch {
                Write-Host "Failed to stop process ID $processId`: $_" -ForegroundColor Red
            }
        }
        
        # Verify port is now available
        Start-Sleep -Seconds 2
        $stillInUse = Get-ProcessOnPort -PortNumber $PortNumber
        if ($stillInUse) {
            Write-Host "Port $PortNumber is still in use after termination attempt" -ForegroundColor Red
            $stillInUse | ForEach-Object { Write-Host $_ -ForegroundColor Gray }
            return $false
        }
        
        return $true
    }
    else {
        Write-Host "No process found using port $PortNumber" -ForegroundColor Green
        return $true
    }
}

# Step 1: Check if port 3002 is in use and clear it
Write-Host "`nStep 1: Checking port 3002..." -ForegroundColor Yellow
$port3002Cleared = Stop-ProcessOnPort -PortNumber 3002

# Step 2: Check alternative ports if needed
$alternativePorts = @(3003, 3004, 3005, 3006)
$selectedPort = 3002
$portAvailable = $port3002Cleared

if (-not $portAvailable) {
    Write-Host "`nStep 2: Checking alternative ports..." -ForegroundColor Yellow
    
    foreach ($port in $alternativePorts) {
        Write-Host "Checking port $port..." -ForegroundColor Cyan
        $inUse = Get-ProcessOnPort -PortNumber $port
        
        if (-not $inUse) {
            $selectedPort = $port
            $portAvailable = $true
            Write-Host "Port $port is available and will be used instead" -ForegroundColor Green
            break
        }
        else {
            Write-Host "Port $port is also in use" -ForegroundColor Yellow
            $cleared = Stop-ProcessOnPort -PortNumber $port
            if ($cleared) {
                $selectedPort = $port
                $portAvailable = $true
                Write-Host "Port $port has been cleared and will be used" -ForegroundColor Green
                break
            }
        }
    }
}

# Step 3: Update next.config.js with the selected port
Write-Host "`nStep 3: Updating Next.js configuration..." -ForegroundColor Yellow
$nextConfigPath = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend\package.json"

if (Test-Path $nextConfigPath) {
    $packageJson = Get-Content -Path $nextConfigPath -Raw | ConvertFrom-Json
    
    # Update port in dev script
    $originalDevScript = $packageJson.scripts.dev
    $packageJson.scripts.dev = "next dev -p $selectedPort"
    
    # Save the updated config
    $packageJson | ConvertTo-Json -Depth 10 | Set-Content -Path $nextConfigPath
    
    Write-Host "Updated package.json to use port $selectedPort (was: $originalDevScript)" -ForegroundColor Green
} else {
    Write-Host "Warning: Could not find package.json" -ForegroundColor Red
}

# Step 4: Start the frontend server
Write-Host "`nStep 4: Starting the frontend server..." -ForegroundColor Yellow
Set-Location -Path "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend"

if ($portAvailable) {
    Write-Host "Starting frontend on port $selectedPort..." -ForegroundColor Green
    Write-Host "Access the app at: http://localhost:$selectedPort" -ForegroundColor Cyan
    Write-Host "`nPress Ctrl+C to stop the server when done" -ForegroundColor Yellow
    npm run dev
} else {
    Write-Host "Warning: Could not find an available port. Please manually free up a port and try again." -ForegroundColor Red
}
