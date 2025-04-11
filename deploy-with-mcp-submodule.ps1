# MCP Deployment Script for FinDoc with Submodule Support
# This script handles the DevDocs submodule and opens the browser for manual deployment

Write-Host "Starting MCP Deployment Process with Submodule Support..." -ForegroundColor Green

# Step 1: Update the submodule
Write-Host "Step 1: Updating the DevDocs submodule..." -ForegroundColor Cyan
git submodule update --init --recursive
cd DevDocs

# Step 2: Generate Vercel configuration
Write-Host "Step 2: Generating Vercel configuration..." -ForegroundColor Cyan

# Create a temporary script to generate the Vercel configuration
$tempScriptPath = "temp-vercel-config.js"
@"
// Simple script to generate Vercel configuration
const fs = require('fs');

// Generate the Vercel configuration
const vercelConfig = {
  version: 2,
  framework: 'nextjs',
  buildCommand: 'npm install && npm run build',
  outputDirectory: '.next',
  rewrites: [
    {
      source: '/api/:path*',
      destination: '/api/:path*'
    }
  ],
  functions: {
    'api/**/*.js': {
      memory: 1024,
      maxDuration: 10
    }
  },
  env: {
    NEXT_PUBLIC_API_URL: '/api',
    NEXT_PUBLIC_SUPABASE_URL: 'https://dnjnsotemnfrjlotgved.supabase.co',
    NEXT_PUBLIC_SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRuam5zb3RlbW5mcmpsb3RndmVkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2NDk2ODYsImV4cCI6MjA1NTIyNTY4Nn0.GqTKv9B2MDAkBxHf0FLGKa60e-yZUDpyxXEychKVDo8'
  }
};

// Write the configuration to vercel.json
fs.writeFileSync('vercel.json', JSON.stringify(vercelConfig, null, 2));

console.log('Vercel configuration generated successfully!');
"@ | Out-File -FilePath $tempScriptPath -Encoding utf8

# Run the script to generate the Vercel configuration
node $tempScriptPath

# Remove the temporary script
Remove-Item -Path $tempScriptPath

# Step 3: Commit and push changes to the submodule
Write-Host "Step 3: Committing and pushing changes to the DevDocs submodule..." -ForegroundColor Cyan
git add vercel.json
git commit -m "Update Vercel configuration for deployment"
git push origin HEAD:main

# Step 4: Update the main repository to point to the new submodule commit
Write-Host "Step 4: Updating the main repository..." -ForegroundColor Cyan
cd ..
git add DevDocs
git commit -m "Update DevDocs submodule for Vercel deployment"
git push origin main

# Step 5: Open browser to deploy to Vercel
Write-Host "Step 5: Opening browser to deploy to Vercel..." -ForegroundColor Cyan
Start-Process "https://vercel.com/new/import?repository-url=https://github.com/aviadkim/backv2"

# Step 6: Provide deployment instructions
Write-Host "Step 6: Deployment Instructions" -ForegroundColor Green
Write-Host "1. In the Vercel import page, select your GitHub repository (backv2)" -ForegroundColor Yellow
Write-Host "2. Configure the project with these settings:" -ForegroundColor Yellow
Write-Host "   - Framework Preset: Next.js" -ForegroundColor Yellow
Write-Host "   - Root Directory: DevDocs" -ForegroundColor Yellow
Write-Host "   - Build Command: npm install && npm run build" -ForegroundColor Yellow
Write-Host "   - Output Directory: .next" -ForegroundColor Yellow
Write-Host "3. Add the SUPABASE_SERVICE_ROLE_KEY environment variable (get this from your Supabase dashboard)" -ForegroundColor Yellow
Write-Host "4. Click 'Deploy'" -ForegroundColor Yellow

Write-Host "Deployment preparation completed!" -ForegroundColor Green
