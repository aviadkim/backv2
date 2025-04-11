# Deploy Simple MCP Server to Google Cloud Run
# This script builds and deploys the simplified MCP server to Google Cloud Run

# Configuration
$PROJECT_ID = "github-456508"
$REGION = "me-west1"
$SERVICE_NAME = "devdocs-mcp-server"

Write-Host "Deploying Simple MCP Server to Google Cloud Run..." -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "Region: $REGION" -ForegroundColor Yellow
Write-Host "Service Name: $SERVICE_NAME" -ForegroundColor Yellow

# Build the Docker image
Write-Host "`nBuilding Docker image..." -ForegroundColor Cyan
docker build -t gcr.io/$PROJECT_ID/devdocs-mcp-server:latest -f Dockerfile.simple .

# Push the Docker image to Google Container Registry
Write-Host "`nPushing Docker image to Google Container Registry..." -ForegroundColor Cyan
docker push gcr.io/$PROJECT_ID/devdocs-mcp-server:latest

# Deploy the image to Google Cloud Run
Write-Host "`nDeploying to Google Cloud Run..." -ForegroundColor Cyan
gcloud run deploy $SERVICE_NAME --image=gcr.io/$PROJECT_ID/devdocs-mcp-server:latest --region=$REGION --allow-unauthenticated --project=$PROJECT_ID

# Get the service URL
Write-Host "`nGetting service URL..." -ForegroundColor Cyan
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)"

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host "Service URL: $SERVICE_URL" -ForegroundColor Green
Write-Host "MCP Endpoint: $SERVICE_URL/mcp" -ForegroundColor Green

# Open the service URL in the default browser
Write-Host "`nOpening service URL in browser..." -ForegroundColor Cyan
Start-Process $SERVICE_URL
