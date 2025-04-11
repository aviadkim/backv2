#!/bin/bash
# Setup Secrets in Google Cloud Secret Manager
# This script sets up API secrets in Google Cloud Secret Manager

# Configuration
PROJECT_ID="github-456508"
REGION="me-west1"
SECRET_NAME="mcp-api-key"

echo "Setting up API secrets in Google Cloud Secret Manager..."
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Secret Name: $SECRET_NAME"

# Enable the Secret Manager API
echo -e "\nEnabling the Secret Manager API..."
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID

# Prompt for the API key
echo -e "\nEnter your MCP API key:"
read -s API_KEY

# Create a temporary file for the API key
TEMP_FILE=$(mktemp)
echo -n "$API_KEY" > $TEMP_FILE

# Create the secret
echo -e "\nCreating the secret..."
gcloud secrets create $SECRET_NAME --data-file=$TEMP_FILE --replication-policy=user-managed --locations=$REGION --project=$PROJECT_ID

# Delete the temporary file
rm $TEMP_FILE

# Grant access to the service account
echo -e "\nGranting access to the service account..."
gcloud secrets add-iam-policy-binding $SECRET_NAME --member=serviceAccount:github@github-456508.iam.gserviceaccount.com --role=roles/secretmanager.secretAccessor --project=$PROJECT_ID

echo -e "\nSecret setup complete!"
echo "You can now access the secret in your application using the Secret Manager API or environment variables."

# Instructions for using the secret in Cloud Run
echo -e "\nTo use the secret in Cloud Run:"
echo "1. Add the following to your Cloud Run deployment command:"
echo "   --set-secrets=MCP_API_KEY=$SECRET_NAME:latest"
echo "2. Access the secret in your code using:"
echo "   const apiKey = process.env.MCP_API_KEY;"
