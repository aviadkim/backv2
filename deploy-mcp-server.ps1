# Deploy MCP Server to Google Cloud Run
# This script deploys the MCP server to Google Cloud Run

# Configuration
$PROJECT_ID = "github-456508"
$REGION = "me-west1"
$SERVICE_NAME = "devdocs-mcp-server"

Write-Host "Deploying MCP Server to Google Cloud Run..." -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "Region: $REGION" -ForegroundColor Yellow
Write-Host "Service Name: $SERVICE_NAME" -ForegroundColor Yellow

# Navigate to the MCP integration directory
Write-Host "`nNavigating to MCP integration directory..." -ForegroundColor Cyan
Set-Location -Path "mcp-integration"

# Deploy the MCP server to Google Cloud Run
Write-Host "`nDeploying to Google Cloud Run..." -ForegroundColor Cyan
gcloud run deploy $SERVICE_NAME --source . --region=$REGION --allow-unauthenticated --project=$PROJECT_ID

# Get the service URL
Write-Host "`nGetting service URL..." -ForegroundColor Cyan
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)"

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host "Service URL: $SERVICE_URL" -ForegroundColor Green
Write-Host "MCP Endpoint: $SERVICE_URL/mcp" -ForegroundColor Green

# Update the MCP URL in the web application
Write-Host "`nUpdating MCP URL in web application..." -ForegroundColor Cyan
$MCP_URL = "$SERVICE_URL/mcp"

# Return to the root directory
Set-Location -Path ".."

# Test the MCP server
Write-Host "`nTesting the MCP server..." -ForegroundColor Cyan
Write-Host "Run the following command to test the MCP server:" -ForegroundColor Yellow
Write-Host "node test-mcp-server.js" -ForegroundColor Yellow

# Open the web application
Write-Host "`nOpening the web application..." -ForegroundColor Cyan
Write-Host "Run the following command to open the web application:" -ForegroundColor Yellow
Write-Host "start devdocs-app.html" -ForegroundColor Yellow
