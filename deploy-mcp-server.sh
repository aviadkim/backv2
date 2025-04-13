#!/bin/bash
# Deploy MCP Server to Google Cloud Run
# This script deploys the MCP server to Google Cloud Run

# Configuration
PROJECT_ID="github-456508"
REGION="me-west1"
SERVICE_NAME="devdocs-mcp-server"

echo "Deploying MCP Server to Google Cloud Run..."
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service Name: $SERVICE_NAME"

# Navigate to the MCP integration directory
echo -e "\nNavigating to MCP integration directory..."
cd mcp-integration

# Deploy the MCP server to Google Cloud Run
echo -e "\nDeploying to Google Cloud Run..."
gcloud run deploy $SERVICE_NAME --source . --region=$REGION --allow-unauthenticated --project=$PROJECT_ID

# Get the service URL
echo -e "\nGetting service URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")

echo -e "\nDeployment complete!"
echo "Service URL: $SERVICE_URL"
echo "MCP Endpoint: $SERVICE_URL/mcp"

# Update the MCP URL in the web application
echo -e "\nUpdating MCP URL in web application..."
MCP_URL="$SERVICE_URL/mcp"

# Return to the root directory
cd ..

# Test the MCP server
echo -e "\nTesting the MCP server..."
echo "Run the following command to test the MCP server:"
echo "node test-mcp-server.js"

# Open the web application
echo -e "\nOpening the web application..."
echo "Run the following command to open the web application:"
echo "open devdocs-app.html"
