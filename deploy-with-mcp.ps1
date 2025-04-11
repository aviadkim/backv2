# MCP Deployment Script for FinDoc
# This script uses MCP to deploy the application to Vercel

Write-Host "Starting MCP Deployment Process..." -ForegroundColor Green

# Step 1: Start the MCP Server
Write-Host "Step 1: Starting MCP Server..." -ForegroundColor Cyan
Set-Location -Path "MCP/augment-mcp-server"

# Check if node_modules exists
if (-not (Test-Path -Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    npm install
}

# Start the server in the background
$serverProcess = Start-Process -FilePath "npm" -ArgumentList "start" -NoNewWindow -PassThru

# Wait for the server to start
Write-Host "Waiting for MCP Server to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Step 2: Generate Vercel configuration
Write-Host "Step 2: Generating Vercel configuration..." -ForegroundColor Cyan
Set-Location -Path "../../DevDocs"

# Create a temporary script to generate the Vercel configuration
$tempScriptPath = "temp-vercel-config.js"
@"
const { vercelProvider } = require('./mcp/vercel-mcp');
const fs = require('fs');

// Generate the Vercel configuration
const vercelConfig = vercelProvider.getDeploymentConfig();

// Add Supabase environment variables
vercelConfig.env.NEXT_PUBLIC_SUPABASE_URL = 'https://dnjnsotemnfrjlotgved.supabase.co';
vercelConfig.env.NEXT_PUBLIC_SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRuam5zb3RlbW5mcmpsb3RndmVkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2NDk2ODYsImV4cCI6MjA1NTIyNTY4Nn0.GqTKv9B2MDAkBxHf0FLGKa60e-yZUDpyxXEychKVDo8';

// Write the configuration to vercel.json
fs.writeFileSync('vercel.json', JSON.stringify(vercelConfig, null, 2));

console.log('Vercel configuration generated successfully!');
"@ | Out-File -FilePath $tempScriptPath -Encoding utf8

# Run the script to generate the Vercel configuration
node $tempScriptPath

# Remove the temporary script
Remove-Item -Path $tempScriptPath

# Step 3: Open browser to deploy to Vercel
Write-Host "Step 3: Opening browser to deploy to Vercel..." -ForegroundColor Cyan
Start-Process "https://vercel.com/new/import?repository-url=https://github.com/aviadkim/backv2"

# Step 4: Provide deployment instructions
Write-Host "Step 4: Deployment Instructions" -ForegroundColor Green
Write-Host "1. In the Vercel import page, select your GitHub repository (backv2)" -ForegroundColor Yellow
Write-Host "2. Configure the project with these settings:" -ForegroundColor Yellow
Write-Host "   - Framework Preset: Next.js" -ForegroundColor Yellow
Write-Host "   - Root Directory: DevDocs" -ForegroundColor Yellow
Write-Host "   - Build Command: npm install && npm run build" -ForegroundColor Yellow
Write-Host "   - Output Directory: .next" -ForegroundColor Yellow
Write-Host "3. Add the SUPABASE_SERVICE_ROLE_KEY environment variable (get this from your Supabase dashboard)" -ForegroundColor Yellow
Write-Host "4. Click 'Deploy'" -ForegroundColor Yellow

# Step 5: Clean up
Write-Host "Step 5: Cleaning up..." -ForegroundColor Cyan
Set-Location -Path "../.."

# Stop the MCP Server
if ($serverProcess -ne $null) {
    Stop-Process -Id $serverProcess.Id -Force
}

Write-Host "Deployment process completed!" -ForegroundColor Green
