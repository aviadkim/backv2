# Simple script to check if the API is accessible

Write-Host "Checking API endpoints..." -ForegroundColor Cyan
$baseUrl = "http://localhost:24125"

# Function to test an endpoint
function Test-Endpoint {
    param (
        [string]$Url,
        [string]$Name
    )
    
    try {
        Write-Host "Testing $Name endpoint at $Url..." -ForegroundColor Cyan
        $response = Invoke-WebRequest -Uri $Url -Method GET -UseBasicParsing
        
        Write-Host "SUCCESS: $Name endpoint responded with status code $($response.StatusCode)" -ForegroundColor Green
        Write-Host "Response: $($response.Content)" -ForegroundColor Gray
        return $true
    } catch {
        Write-Host "ERROR: $Name endpoint failed with error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Test root endpoint
Test-Endpoint -Url "$baseUrl/" -Name "Root"

# Test health endpoint
Test-Endpoint -Url "$baseUrl/api/health" -Name "Health"

# Test documents endpoint
Test-Endpoint -Url "$baseUrl/api/documents" -Name "Documents"

# Test tags endpoint
Test-Endpoint -Url "$baseUrl/api/tags" -Name "Tags"

Write-Host "Endpoint tests complete" -ForegroundColor Cyan
