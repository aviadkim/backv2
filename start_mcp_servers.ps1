# Start missing MCP servers (CDK, AWS Docs, etc.)

Write-Host "Activating MCP virtual environment..."
& .\mcp-venv\Scripts\Activate.ps1

Write-Host "Starting awslabs.cdk-mcp-server..."
Start-Process -NoNewWindow -FilePath "C:\Users\aviad\AppData\Roaming\Python\Python313\Scripts\uvx.exe" -ArgumentList '--from', 'awslabs.cdk-mcp-server@latest', 'awslabs.cdk-mcp-server.exe'

Write-Host "Starting awslabs.aws-documentation-mcp-server..."
Start-Process -NoNewWindow -FilePath "C:\Users\aviad\AppData\Roaming\Python\Python313\Scripts\uvx.exe" -ArgumentList '--from', 'awslabs.aws-documentation-mcp-server@latest', 'awslabs.aws-documentation-mcp-server.exe'

Write-Host "All additional MCP servers started."
