# Simple API Test
Write-Host "Testing API endpoints..."

# Test health endpoint
$response = Invoke-WebRequest -Uri "http://localhost:24125/api/health" -UseBasicParsing
Write-Host "Health endpoint: $($response.StatusCode)"
$content = $response.Content | ConvertFrom-Json
Write-Host "Status: $($content.status)"

# Test documents endpoint
$response = Invoke-WebRequest -Uri "http://localhost:24125/api/documents" -UseBasicParsing
Write-Host "Documents endpoint: $($response.StatusCode)"
$content = $response.Content | ConvertFrom-Json
Write-Host "Documents count: $($content.documents.Count)"

# Test portfolio endpoint
$response = Invoke-WebRequest -Uri "http://localhost:24125/api/portfolio" -UseBasicParsing
Write-Host "Portfolio endpoint: $($response.StatusCode)"
$content = $response.Content | ConvertFrom-Json
Write-Host "Portfolio items: $($content.portfolio.Count)"

# Test portfolio summary endpoint
$response = Invoke-WebRequest -Uri "http://localhost:24125/api/portfolio/summary" -UseBasicParsing
Write-Host "Portfolio summary endpoint: $($response.StatusCode)"
$content = $response.Content | ConvertFrom-Json
Write-Host "Status: $($content.status)"

Write-Host "Tests completed."
