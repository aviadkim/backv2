#!/bin/bash
# Deploy MCP Server to Google Cloud Run
# This script builds and deploys the MCP server to Google Cloud Run

# Configuration
PROJECT_ID="github-456508"
REGION="me-west1"
SERVICE_NAME="devdocs-mcp-server"

echo "Deploying MCP Server to Google Cloud Run..."
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service Name: $SERVICE_NAME"

# Build and deploy using Cloud Build
echo -e "\nBuilding and deploying using Cloud Build..."
gcloud builds submit --config=cloudbuild.mcp.yaml --project=$PROJECT_ID

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
