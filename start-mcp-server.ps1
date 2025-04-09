# MCP Server Launcher Script
# This script installs dependencies and starts the MCP Server

Write-Host "Starting MCP Server..." -ForegroundColor Green

# Navigate to the MCP Server directory
Set-Location -Path "MCP/augment-mcp-server"

# Check if node_modules exists
if (-not (Test-Path -Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    npm install
}

# Start the server
Write-Host "Launching MCP Server..." -ForegroundColor Cyan
npm start

# Return to the root directory
Set-Location -Path "../.."
