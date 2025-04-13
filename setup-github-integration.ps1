# Setup GitHub Integration with Google Cloud Build
# This script sets up a Cloud Build trigger that automatically builds and deploys
# your application when changes are pushed to your GitHub repository

# Configuration
$PROJECT_ID = "github-456508"
$REGION = "me-west1"
$REPO_OWNER = "aviadkim"
$REPO_NAME = "backv2"
$BRANCH = "main"
$SERVICE_NAME = "devdocs-mcp-server"

Write-Host "Setting up GitHub integration with Google Cloud Build..." -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "Region: $REGION" -ForegroundColor Yellow
Write-Host "Repository: $REPO_OWNER/$REPO_NAME" -ForegroundColor Yellow
Write-Host "Branch: $BRANCH" -ForegroundColor Yellow
Write-Host "Service Name: $SERVICE_NAME" -ForegroundColor Yellow

# Connect GitHub repository to Cloud Build
Write-Host "`nConnecting GitHub repository to Cloud Build..." -ForegroundColor Cyan
Write-Host "This will open a browser window to authenticate with GitHub." -ForegroundColor Yellow
Write-Host "Please follow the instructions in the browser." -ForegroundColor Yellow

gcloud source repos create $REPO_NAME --project=$PROJECT_ID

# Create Cloud Build trigger
Write-Host "`nCreating Cloud Build trigger..." -ForegroundColor Cyan
gcloud builds triggers create github `
  --name="devdocs-mcp-trigger" `
  --repository="https://github.com/$REPO_OWNER/$REPO_NAME" `
  --branch="$BRANCH" `
  --build-config="cloudbuild.yaml" `
  --project=$PROJECT_ID `
  --region=$REGION

Write-Host "`nGitHub integration setup complete!" -ForegroundColor Green
Write-Host "Now, any changes pushed to the $BRANCH branch of $REPO_OWNER/$REPO_NAME will automatically trigger a build and deployment to Cloud Run." -ForegroundColor Green

# Instructions for testing the integration
Write-Host "`nTo test the integration:" -ForegroundColor Cyan
Write-Host "1. Make a change to your code" -ForegroundColor Yellow
Write-Host "2. Commit and push the change to GitHub" -ForegroundColor Yellow
Write-Host "3. Check the build status in the Google Cloud Console:" -ForegroundColor Yellow
Write-Host "   https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID" -ForegroundColor Yellow
Write-Host "4. Once the build is complete, check the deployed application at:" -ForegroundColor Yellow
Write-Host "   https://$SERVICE_NAME-$PROJECT_ID.$REGION.run.app" -ForegroundColor Yellow
