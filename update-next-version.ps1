# Script to update Next.js version

Write-Host "Updating Next.js version..." -ForegroundColor Green

$packageJsonPath = "C:\Users\aviad\OneDrive\Desktop\backv2\DevDocs\frontend\package.json"

# Check if file exists
if (Test-Path $packageJsonPath) {
    # Read package.json
    $packageJson = Get-Content -Path $packageJsonPath -Raw | ConvertFrom-Json
    
    # Check current Next.js version
    $currentVersion = $packageJson.dependencies.next
    Write-Host "Current Next.js version: $currentVersion" -ForegroundColor Yellow
    
    # Update to appropriate version
    $packageJson.dependencies.next = "^14.0.4"
    Write-Host "Updating to Next.js version: ^14.0.4" -ForegroundColor Green
    
    # Save updated package.json
    $packageJson | ConvertTo-Json -Depth 10 | Set-Content -Path $packageJsonPath
    
    Write-Host "Package.json updated successfully!" -ForegroundColor Green
    Write-Host "Please run 'npm install' in the frontend directory to apply changes." -ForegroundColor Yellow
} else {
    Write-Host "Error: package.json not found at $packageJsonPath" -ForegroundColor Red
}
