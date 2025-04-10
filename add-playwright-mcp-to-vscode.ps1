# Add Playwright MCP Server to VS Code
# This script adds the Playwright MCP server to your VS Code configuration

Write-Host "Adding Playwright MCP Server to VS Code..." -ForegroundColor Green

# Execute the VS Code CLI command to add the MCP server
Write-Host "Configuring VS Code to use Playwright MCP..." -ForegroundColor Cyan
code --add-mcp '{"name":"playwright","command":"npx","args":["@playwright/mcp@latest"]}'

Write-Host ""
Write-Host "Playwright MCP server has been added to VS Code!" -ForegroundColor Green
Write-Host "You can now use it with GitHub Copilot in VS Code." -ForegroundColor Green
Write-Host ""
Write-Host "To use with different configurations, you can modify your VS Code settings:" -ForegroundColor Yellow
Write-Host '{"mcpServers": {"playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]}}}' -ForegroundColor Yellow
Write-Host ""
Write-Host "Headless mode example:" -ForegroundColor Yellow
Write-Host '{"mcpServers": {"playwright": {"command": "npx", "args": ["@playwright/mcp@latest", "--headless"]}}}' -ForegroundColor Yellow