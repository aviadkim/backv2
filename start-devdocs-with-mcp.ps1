# Start DevDocs with MCP Integration

Write-Host "Starting DevDocs with MCP Integration..." -ForegroundColor Cyan

# Start the MCP server in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\mcp-integration'; node server.js" -WindowStyle Normal

# Wait for the server to start
Write-Host "Waiting for MCP server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start the DevDocs backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\DevDocs\backend'; python app.py" -WindowStyle Normal

# Wait for the backend to start
Write-Host "Waiting for DevDocs backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start the DevDocs frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\DevDocs\frontend'; npm run dev" -WindowStyle Normal

Write-Host "`nDevDocs with MCP Integration started successfully!" -ForegroundColor Green
Write-Host "MCP server is running at http://localhost:8080" -ForegroundColor Cyan
Write-Host "DevDocs backend is running at http://localhost:24125" -ForegroundColor Cyan
Write-Host "DevDocs frontend is running at http://localhost:3000" -ForegroundColor Cyan
Write-Host "`nYou can access the MCP integration at http://localhost:3000/mcp-integration" -ForegroundColor Green

# Open the MCP integration page in the default browser
Start-Process "http://localhost:3000/mcp-integration"
