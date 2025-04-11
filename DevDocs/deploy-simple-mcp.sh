#!/bin/bash
# Deploy Simple MCP Server to Google Cloud Run
# This script builds and deploys the simplified MCP server to Google Cloud Run

# Configuration
PROJECT_ID="github-456508"
REGION="me-west1"
SERVICE_NAME="devdocs-mcp-server"

echo "Deploying Simple MCP Server to Google Cloud Run..."
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service Name: $SERVICE_NAME"

# Build the Docker image
echo -e "\nBuilding Docker image..."
docker build -t gcr.io/$PROJECT_ID/devdocs-mcp-server:latest -f Dockerfile.simple .

# Push the Docker image to Google Container Registry
echo -e "\nPushing Docker image to Google Container Registry..."
docker push gcr.io/$PROJECT_ID/devdocs-mcp-server:latest

# Deploy the image to Google Cloud Run
echo -e "\nDeploying to Google Cloud Run..."
gcloud run deploy $SERVICE_NAME --image=gcr.io/$PROJECT_ID/devdocs-mcp-server:latest --region=$REGION --allow-unauthenticated --project=$PROJECT_ID

# Get the service URL
echo -e "\nGetting service URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")

echo -e "\nDeployment complete!"
echo "Service URL: $SERVICE_URL"
echo "MCP Endpoint: $SERVICE_URL/mcp"

# Open the service URL in the default browser
echo -e "\nOpening service URL in browser..."
if [[ "$OSTYPE" == "darwin"* ]]; then
  open $SERVICE_URL
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  xdg-open $SERVICE_URL
fi
