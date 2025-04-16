#!/bin/bash
# Setup script for Google Cloud environment

# Set variables
PROJECT_ID="github-456508"
SERVICE_ACCOUNT="github"
REGION="me-west1"
API_KEY="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"

# Create project if it doesn't exist
gcloud projects describe $PROJECT_ID > /dev/null 2>&1 || gcloud projects create $PROJECT_ID --name="GitHub"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Create service account
gcloud iam service-accounts create $SERVICE_ACCOUNT \
  --description="GitHub Actions service account" \
  --display-name="GitHub Actions"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/owner"

# Create service account key
gcloud iam service-accounts keys create key.json \
  --iam-account=$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com

# Store API key in Secret Manager
gcloud secrets create openrouter-api-key --replication-policy="automatic"
echo -n "$API_KEY" | gcloud secrets versions add openrouter-api-key --data-file=-

# Grant service account access to the secret
gcloud secrets add-iam-policy-binding openrouter-api-key \
  --member="serviceAccount:$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

echo "Google Cloud environment setup completed!"
echo "Please add the contents of key.json to your GitHub repository secrets as GCP_SA_KEY"
