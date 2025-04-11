# MCP Deployment Script with Browser Integration for FinDoc
# This script uses MCP with browser integration to deploy the application to Vercel

Write-Host "Starting MCP Browser Deployment Process..." -ForegroundColor Green

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
const { supabaseProvider } = require('./mcp/supabase-mcp');
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

# Step 3: Create a browser automation script
Write-Host "Step 3: Creating browser automation script..." -ForegroundColor Cyan
$browserScriptPath = "browser-deploy.js"
@"
const puppeteer = require('puppeteer');

async function deployToVercel() {
  console.log('Starting browser automation for Vercel deployment...');
  
  // Launch the browser
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // Go to Vercel import page
    await page.goto('https://vercel.com/new/import?repository-url=https://github.com/aviadkim/backv2');
    console.log('Navigated to Vercel import page');
    
    // Wait for user to complete the authentication and repository selection
    console.log('Please complete the authentication and repository selection in the browser...');
    
    // Wait for the project configuration page
    await page.waitForSelector('input[name="root-directory"]', { timeout: 120000 });
    console.log('Project configuration page loaded');
    
    // Fill in the configuration
    await page.type('input[name="root-directory"]', 'DevDocs');
    console.log('Set root directory to DevDocs');
    
    // Wait for user to complete the configuration and deployment
    console.log('Please complete the configuration and click Deploy in the browser...');
    
    // Wait for deployment to start
    await page.waitForNavigation({ timeout: 300000 });
    console.log('Deployment started');
    
    // Get the deployment URL
    const deploymentUrl = page.url();
    console.log(`Deployment URL: \${deploymentUrl}`);
    
    // Keep the browser open for the user to monitor the deployment
    console.log('Browser will remain open for you to monitor the deployment');
    
  } catch (error) {
    console.error('Error during deployment:', error);
  }
}

deployToVercel();
"@ | Out-File -FilePath $browserScriptPath -Encoding utf8

# Check if puppeteer is installed
if (-not (Test-Path -Path "node_modules/puppeteer")) {
    Write-Host "Installing puppeteer for browser automation..." -ForegroundColor Cyan
    npm install puppeteer
}

# Step 4: Run the browser automation script
Write-Host "Step 4: Running browser automation script..." -ForegroundColor Cyan
Write-Host "A browser window will open to guide you through the deployment process." -ForegroundColor Yellow
node $browserScriptPath

# Step 5: Clean up
Write-Host "Step 5: Cleaning up..." -ForegroundColor Cyan
Set-Location -Path "../.."

# Stop the MCP Server
if ($serverProcess -ne $null) {
    Stop-Process -Id $serverProcess.Id -Force
}

Write-Host "Deployment process completed!" -ForegroundColor Green
Write-Host "Note: The browser window will remain open for you to monitor the deployment." -ForegroundColor Yellow
