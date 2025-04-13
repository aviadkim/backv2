# Push changes to GitHub to trigger continuous deployment
# This script commits and pushes changes to GitHub

# Configuration
$BRANCH = "main"
$COMMIT_MESSAGE = "Set up continuous deployment to Google Cloud Run"

Write-Host "Pushing changes to GitHub..." -ForegroundColor Cyan
Write-Host "Branch: $BRANCH" -ForegroundColor Yellow
Write-Host "Commit Message: $COMMIT_MESSAGE" -ForegroundColor Yellow

# Add all changes
Write-Host "`nAdding changes..." -ForegroundColor Cyan
git add .

# Commit changes
Write-Host "`nCommitting changes..." -ForegroundColor Cyan
git commit -m "$COMMIT_MESSAGE"

# Push changes
Write-Host "`nPushing changes to GitHub..." -ForegroundColor Cyan
git push origin $BRANCH

Write-Host "`nChanges pushed to GitHub!" -ForegroundColor Green
Write-Host "This should trigger a build in Cloud Build." -ForegroundColor Green
Write-Host "You can monitor the build progress at:" -ForegroundColor Yellow
Write-Host "https://console.cloud.google.com/cloud-build/builds?project=github-456508" -ForegroundColor Yellow

# Instructions for verifying the deployment
Write-Host "`nTo verify the deployment:" -ForegroundColor Cyan
Write-Host "1. Wait for the build to complete" -ForegroundColor Yellow
Write-Host "2. Go to the Cloud Run page:" -ForegroundColor Yellow
Write-Host "   https://console.cloud.google.com/run?project=github-456508" -ForegroundColor Yellow
Write-Host "3. Click on the 'devdocs-mcp-server' service" -ForegroundColor Yellow
Write-Host "4. Click on the URL to open the deployed application" -ForegroundColor Yellow
