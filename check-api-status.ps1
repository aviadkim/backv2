# Script to check API status and connectivity

Write-Host "=== API Status Checker ===" -ForegroundColor Cyan

$apiUrl = "http://localhost:24125"
$endpoints = @(
    @{Path = "/api/health"; Name = "Health Endpoint"},
    @{Path = "/api/documents"; Name = "Documents Endpoint"},
    @{Path = "/api/tags"; Name = "Tags Endpoint"}
)

Write-Host "`nBasic network connectivity check:" -ForegroundColor Yellow

# Check if localhost is resolvable
try {
    $ipAddress = [System.Net.Dns]::GetHostAddresses("localhost") | 
                 Where-Object { $_.AddressFamily -eq [System.Net.Sockets.AddressFamily]::InterNetwork } | 
                 Select-Object -First 1 -ExpandProperty IPAddressToString
    
    Write-Host "Localhost resolves to: $ipAddress" -ForegroundColor Green
} catch {
    Write-Host "Error resolving localhost: $_" -ForegroundColor Red
}

# Check if port 24125 is open
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $portOpen = $tcpClient.ConnectAsync("localhost", 24125).Wait(1000)
    $tcpClient.Close()
    
    if ($portOpen) {
        Write-Host "Port 24125 is open and accepting connections" -ForegroundColor Green
    } else {
        Write-Host "Port 24125 is not responding (connection timed out)" -ForegroundColor Red
    }
} catch {
    Write-Host "Error checking port 24125: $_" -ForegroundColor Red
}

# Check processes using port 24125
$portProcess = netstat -ano | Select-String "24125" | Select-String "LISTENING"
if ($portProcess) {
    $processId = $portProcess[0].ToString().Split(" ")[-1].Trim()
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "Process using port 24125: $($process.ProcessName) (ID: $processId)" -ForegroundColor Cyan
    } else {
        Write-Host "Process ID $processId is using port 24125 but details couldn't be retrieved" -ForegroundColor Yellow
    }
} else {
    Write-Host "No process found using port 24125" -ForegroundColor Red
}

Write-Host "`nAPI Endpoint Tests:" -ForegroundColor Yellow

# Test all endpoints
foreach ($endpoint in $endpoints) {
    $fullUrl = "$apiUrl$($endpoint.Path)"
    Write-Host "Testing $($endpoint.Name) ($fullUrl)..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri $fullUrl -UseBasicParsing -TimeoutSec 5
        
        Write-Host "  Status: $($response.StatusCode) $($response.StatusDescription)" -ForegroundColor Green
        Write-Host "  Response Size: $($response.Content.Length) bytes" -ForegroundColor Green
        
        # Try to parse response as JSON
        try {
            $json = $response.Content | ConvertFrom-Json
            $properties = $json | Get-Member -MemberType NoteProperty
            Write-Host "  Response Properties: $($properties.Name -join ', ')" -ForegroundColor Green
        } catch {
            Write-Host "  Response is not valid JSON or empty" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
        
        # Try with curl as a fallback
        Write-Host "  Trying with curl..." -ForegroundColor Yellow
        try {
            $curlResult = curl -s -m 5 $fullUrl
            Write-Host "  Curl result: $curlResult" -ForegroundColor Cyan
        } catch {
            Write-Host "  Curl also failed: $_" -ForegroundColor Red
        }
    }
    
    Write-Host ""
}

Write-Host "`nChecking Backend Process:" -ForegroundColor Yellow
$pythonProcesses = Get-Process -Name python* -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "Python processes running:" -ForegroundColor Cyan
    $pythonProcesses | Format-Table Id, ProcessName, Path, StartTime -AutoSize
} else {
    Write-Host "No Python processes found! Backend may not be running." -ForegroundColor Red
}

Write-Host "`nAPI Connection Recommendations:" -ForegroundColor Yellow
Write-Host "1. Ensure the backend is running: cd DevDocs\backend; python app.py" -ForegroundColor White
Write-Host "2. Try using a different port for the frontend: Update port in package.json" -ForegroundColor White
Write-Host "3. Make sure the NEXT_PUBLIC_API_URL environment variable is set correctly" -ForegroundColor White
Write-Host "4. Check for firewall or antivirus blocking connections" -ForegroundColor White
Write-Host "5. Try using curl to test API endpoints manually" -ForegroundColor White
