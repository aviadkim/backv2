# Direct Deployment Script for FinDoc
# This script opens the browser for manual deployment without modifying the repository

Write-Host "Starting Direct Deployment Process..." -ForegroundColor Green

# Step 1: Open browser to deploy to Vercel
Write-Host "Step 1: Opening browser to deploy to Vercel..." -ForegroundColor Cyan
Start-Process "https://vercel.com/new/import?repository-url=https://github.com/aviadkim/backv2"

# Step 2: Provide deployment instructions
Write-Host "Step 2: Deployment Instructions" -ForegroundColor Green
Write-Host "1. In the Vercel import page, select your GitHub repository (backv2)" -ForegroundColor Yellow
Write-Host "2. Configure the project with these settings:" -ForegroundColor Yellow
Write-Host "   - Framework Preset: Next.js" -ForegroundColor Yellow
Write-Host "   - Root Directory: DevDocs" -ForegroundColor Yellow
Write-Host "   - Build Command: npm install && npm run build" -ForegroundColor Yellow
Write-Host "   - Output Directory: .next" -ForegroundColor Yellow
Write-Host "3. Add these environment variables:" -ForegroundColor Yellow
Write-Host "   - NEXT_PUBLIC_SUPABASE_URL: https://dnjnsotemnfrjlotgved.supabase.co" -ForegroundColor Yellow
Write-Host "   - NEXT_PUBLIC_SUPABASE_ANON_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRuam5zb3RlbW5mcmpsb3RndmVkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2NDk2ODYsImV4cCI6MjA1NTIyNTY4Nn0.GqTKv9B2MDAkBxHf0FLGKa60e-yZUDpyxXEychKVDo8" -ForegroundColor Yellow
Write-Host "   - SUPABASE_SERVICE_ROLE_KEY: (Get this from your Supabase dashboard)" -ForegroundColor Yellow
Write-Host "4. Click 'Deploy'" -ForegroundColor Yellow

Write-Host "Deployment preparation completed!" -ForegroundColor Green
