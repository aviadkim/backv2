# Deploy DevDocs to Google Cloud Run

# Configuration
$PROJECT_ID = "github-456508"
$REGION = "me-west1"
$SERVICE_NAME = "devdocs-service"
$IMAGE_NAME = "devdocs-app"

Write-Host "Deploying DevDocs to Google Cloud Run..." -ForegroundColor Cyan

# Build the Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build -t "$REGION-docker.pkg.dev/$PROJECT_ID/devdocs/$IMAGE_NAME" -f Dockerfile .

# Push the image to Artifact Registry
Write-Host "Pushing image to Artifact Registry..." -ForegroundColor Yellow
docker push "$REGION-docker.pkg.dev/$PROJECT_ID/devdocs/$IMAGE_NAME"

# Deploy to Cloud Run
Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
  --image="$REGION-docker.pkg.dev/$PROJECT_ID/devdocs/$IMAGE_NAME" `
  --platform=managed `
  --region=$REGION `
  --allow-unauthenticated `
  --set-env-vars="MCP_SERVER_URL=https://mcp-server-$PROJECT_ID.$REGION.run.app/mcp" `
  --project=$PROJECT_ID

Write-Host "Deployment completed!" -ForegroundColor Green
Write-Host "Your DevDocs application is now available at: https://$SERVICE_NAME-$PROJECT_ID.$REGION.run.app" -ForegroundColor Cyan
