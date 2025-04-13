# Build and Deploy MCP Server to Google Cloud Run
# This script builds a Docker image and deploys it to Google Cloud Run

# Configuration
$PROJECT_ID = "github-456508"
$REGION = "me-west1"
$SERVICE_NAME = "devdocs-mcp-server"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/devdocs-mcp-server:latest"

Write-Host "Building and deploying MCP Server to Google Cloud Run..." -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "Region: $REGION" -ForegroundColor Yellow
Write-Host "Service Name: $SERVICE_NAME" -ForegroundColor Yellow
Write-Host "Image Name: $IMAGE_NAME" -ForegroundColor Yellow

# Build the Docker image
Write-Host "`nBuilding Docker image..." -ForegroundColor Cyan
docker build -t $IMAGE_NAME .

# Push the Docker image to Google Container Registry
Write-Host "`nPushing Docker image to Google Container Registry..." -ForegroundColor Cyan
docker push $IMAGE_NAME

# Deploy the image to Google Cloud Run
Write-Host "`nDeploying to Google Cloud Run..." -ForegroundColor Cyan
gcloud run deploy $SERVICE_NAME --image=$IMAGE_NAME --region=$REGION --allow-unauthenticated --project=$PROJECT_ID

# Get the service URL
Write-Host "`nGetting service URL..." -ForegroundColor Cyan
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)"

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host "Service URL: $SERVICE_URL" -ForegroundColor Green
Write-Host "MCP Endpoint: $SERVICE_URL/mcp" -ForegroundColor Green

# Open the service URL in the default browser
Write-Host "`nOpening service URL in browser..." -ForegroundColor Cyan
Start-Process $SERVICE_URL
