#!/bin/bash
# Setup GitHub Integration with Google Cloud Build
# This script sets up a Cloud Build trigger that automatically builds and deploys
# your application when changes are pushed to your GitHub repository

# Configuration
PROJECT_ID="github-456508"
REGION="me-west1"
REPO_OWNER="aviadkim"
REPO_NAME="backv2"
BRANCH="main"
SERVICE_NAME="devdocs-mcp-server"

echo "Setting up GitHub integration with Google Cloud Build..."
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Repository: $REPO_OWNER/$REPO_NAME"
echo "Branch: $BRANCH"
echo "Service Name: $SERVICE_NAME"

# Connect GitHub repository to Cloud Build
echo -e "\nConnecting GitHub repository to Cloud Build..."
echo "This will open a browser window to authenticate with GitHub."
echo "Please follow the instructions in the browser."

gcloud source repos create $REPO_NAME --project=$PROJECT_ID

# Create Cloud Build trigger
echo -e "\nCreating Cloud Build trigger..."
gcloud builds triggers create github \
  --name="devdocs-mcp-trigger" \
  --repository="https://github.com/$REPO_OWNER/$REPO_NAME" \
  --branch="$BRANCH" \
  --build-config="cloudbuild.yaml" \
  --project=$PROJECT_ID \
  --region=$REGION

echo -e "\nGitHub integration setup complete!"
echo "Now, any changes pushed to the $BRANCH branch of $REPO_OWNER/$REPO_NAME will automatically trigger a build and deployment to Cloud Run."

# Instructions for testing the integration
echo -e "\nTo test the integration:"
echo "1. Make a change to your code"
echo "2. Commit and push the change to GitHub"
echo "3. Check the build status in the Google Cloud Console:"
echo "   https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
echo "4. Once the build is complete, check the deployed application at:"
echo "   https://$SERVICE_NAME-$PROJECT_ID.$REGION.run.app"
