#!/bin/bash
# Push changes to GitHub to trigger continuous deployment
# This script commits and pushes changes to GitHub

# Configuration
BRANCH="main"
COMMIT_MESSAGE="Set up continuous deployment to Google Cloud Run"

echo "Pushing changes to GitHub..."
echo "Branch: $BRANCH"
echo "Commit Message: $COMMIT_MESSAGE"

# Add all changes
echo -e "\nAdding changes..."
git add .

# Commit changes
echo -e "\nCommitting changes..."
git commit -m "$COMMIT_MESSAGE"

# Push changes
echo -e "\nPushing changes to GitHub..."
git push origin $BRANCH

echo -e "\nChanges pushed to GitHub!"
echo "This should trigger a build in Cloud Build."
echo "You can monitor the build progress at:"
echo "https://console.cloud.google.com/cloud-build/builds?project=github-456508"

# Instructions for verifying the deployment
echo -e "\nTo verify the deployment:"
echo "1. Wait for the build to complete"
echo "2. Go to the Cloud Run page:"
echo "   https://console.cloud.google.com/run?project=github-456508"
echo "3. Click on the 'devdocs-mcp-server' service"
echo "4. Click on the URL to open the deployed application"
