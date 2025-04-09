# PowerShell script to create an isolated virtual environment for MCP servers
# This avoids dependency conflicts with other Python packages

Write-Host "Creating virtual environment 'mcp-venv'..."
python -m venv mcp-venv

Write-Host "Activating virtual environment..."
& .\mcp-venv\Scripts\Activate.ps1

Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

Write-Host "Installing awslabs.cdk-mcp-server inside virtual environment..."
pip install awslabs.cdk-mcp-server

Write-Host "MCP virtual environment setup complete."
Write-Host "To activate later, run: `n` .\mcp-venv\Scripts\Activate.ps1"