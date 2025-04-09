# MCP Tools Installation Script
# This script installs both the MCP Server and Client

Write-Host "Installing MCP Tools..." -ForegroundColor Green

# Install MCP Server
Write-Host "Installing MCP Server..." -ForegroundColor Cyan
Set-Location -Path "MCP/augment-mcp-server"
npm install
Set-Location -Path "../.."

# Install MCP Client
Write-Host "Installing MCP Client..." -ForegroundColor Cyan
Set-Location -Path "MCP/augment-mcp-client"
npm install
npm link
Set-Location -Path "../.."

Write-Host "MCP Tools installation completed!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the MCP Server:" -ForegroundColor Yellow
Write-Host "  .\\start-mcp-server.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "To use the MCP CLI:" -ForegroundColor Yellow
Write-Host "  mcp generate -p findoc -t model -n User -d 'User model for authentication'" -ForegroundColor Yellow
Write-Host "  mcp generate-all -p findoc -n Document -d 'Document management'" -ForegroundColor Yellow
Write-Host "  mcp list-projects" -ForegroundColor Yellow
Write-Host "  mcp add-project -i myproject -r ./path/to/project" -ForegroundColor Yellow
