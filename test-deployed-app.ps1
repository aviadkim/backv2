# Test the deployed DevDocs application

$deployedUrl = "https://devdocs-service-github-456508.me-west1.run.app"

Write-Host "Testing the deployed DevDocs application at $deployedUrl" -ForegroundColor Cyan

# Test the home page
Write-Host "Testing the home page..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $deployedUrl -UseBasicParsing
    Write-Host "Home page status code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Home page content length: $($response.Content.Length) bytes" -ForegroundColor Green
} catch {
    Write-Host "Error accessing home page: $_" -ForegroundColor Red
}

# Test the MCP endpoint
Write-Host "`nTesting the MCP endpoint..." -ForegroundColor Yellow
try {
    $body = @{
        action = "listBuckets"
        parameters = @{}
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$deployedUrl/mcp" -Method Post -Body $body -ContentType "application/json" -UseBasicParsing
    Write-Host "MCP endpoint status code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "MCP endpoint response: $($response.Content)" -ForegroundColor Green
} catch {
    Write-Host "Error accessing MCP endpoint: $_" -ForegroundColor Red
}

# Open the deployed application in the default browser
Write-Host "`nOpening the deployed application in the default browser..." -ForegroundColor Yellow
Start-Process $deployedUrl
