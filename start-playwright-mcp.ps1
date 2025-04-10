# Start Playwright MCP Server
# This script starts the Playwright MCP server using the global installation

Write-Host "Starting Playwright MCP Server..." -ForegroundColor Green

# Default parameters
$headless = $false
$browser = "chrome"
$port = 8931

# Parse command line arguments
for ($i = 0; $i -lt $args.Count; $i++) {
    if ($args[$i] -eq "--headless") {
        $headless = $true
    }
    elseif ($args[$i] -eq "--browser" -and $i+1 -lt $args.Count) {
        $browser = $args[$i+1]
        $i++
    }
    elseif ($args[$i] -eq "--port" -and $i+1 -lt $args.Count) {
        $port = $args[$i+1]
        $i++
    }
}

# Build the command
$command = "npx @playwright/mcp@latest"
if ($headless) {
    $command += " --headless"
}
$command += " --browser $browser"
$command += " --port $port"

# Display configuration
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Browser: $browser" -ForegroundColor Cyan
Write-Host "  Headless: $headless" -ForegroundColor Cyan
Write-Host "  Port: $port" -ForegroundColor Cyan
Write-Host ""

# Execute the command
Write-Host "Executing: $command" -ForegroundColor Yellow
Write-Host ""
Invoke-Expression $command

# Note: The script will stay running as long as the MCP server is active
# Press Ctrl+C to stop the server