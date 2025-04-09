# Simple script to test API connectivity with DevDocs backend

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "DevDocs API Test" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Define test endpoints
$baseUrl = "http://localhost:24125"
$endpoints = @(
    @{Path = ""; Description = "Root endpoint"},
    @{Path = "/test"; Description = "Test endpoint"},
    @{Path = "/api/health"; Description = "Health endpoint"},
    @{Path = "/api/documents"; Description = "Documents endpoint"},
    @{Path = "/api/tags"; Description = "Tags endpoint"},
    @{Path = "/api/documents/1"; Description = "Specific document endpoint"}
)

# Track success count
$successCount = 0

# Test each endpoint
foreach ($endpoint in $endpoints) {
    $url = "$baseUrl$($endpoint.Path)"
    Write-Host "Testing $($endpoint.Description) at $url..." -ForegroundColor Yellow
    
    try {
        $start = Get-Date
        $response = Invoke-WebRequest -Uri $url -Method GET -UseBasicParsing -TimeoutSec 5
        $duration = (Get-Date) - $start
        
        Write-Host "Status Code: $($response.StatusCode) (in $($duration.TotalSeconds.ToString("0.00"))s)" -ForegroundColor Cyan
        
        if ($response.StatusCode -eq 200) {
            Write-Host "Response: $($response.Content)" -ForegroundColor Green
            Write-Host "✓ SUCCESS" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "Error: Unexpected status code $($response.StatusCode)" -ForegroundColor Red
            Write-Host "✗ FAILED" -ForegroundColor Red
        }
    } catch {
        $duration = if ($start) { (Get-Date) - $start } else { [TimeSpan]::Zero }
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "✗ FAILED" -ForegroundColor Red
    }
    
    Write-Host ("-" * 60) -ForegroundColor Gray
}

# Print summary
Write-Host "`nTest Summary:" -ForegroundColor Cyan
$summaryColor = if ($successCount -eq $endpoints.Count) { "Green" } else { "Yellow" }
Write-Host "✓ $successCount/$($endpoints.Count) endpoints passed" -ForegroundColor $summaryColor
