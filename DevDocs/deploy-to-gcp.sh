#!/bin/bash
# Bash script to deploy DevDocs to Google Cloud Run

# Check if gcloud CLI is installed
if ! command -v gcloud &> /dev/null; then
    echo "Google Cloud SDK is not installed or not in PATH. Please install it first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
else
    echo "Google Cloud SDK is installed."
fi

# Ask for project ID
read -p "Enter your Google Cloud Project ID: " projectId

# Set the project
echo "Setting Google Cloud project to: $projectId"
gcloud config set project $projectId

# Enable required APIs
echo "Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com secretmanager.googleapis.com containerregistry.googleapis.com

# Ask for API keys
read -p "Enter your OpenRouter API Key: " openRouterApiKey
read -p "Enter your Supabase URL (e.g., https://your-project-id.supabase.co): " supabaseUrl
read -p "Enter your Supabase Key: " supabaseKey

# Create secrets
echo "Creating secrets in Secret Manager..."

# Check if secrets already exist
openRouterExists=$(gcloud secrets list --filter="name:OPENROUTER_API_KEY" --format="value(name)" 2>/dev/null)
supabaseUrlExists=$(gcloud secrets list --filter="name:SUPABASE_URL" --format="value(name)" 2>/dev/null)
supabaseKeyExists=$(gcloud secrets list --filter="name:SUPABASE_KEY" --format="value(name)" 2>/dev/null)

if [ -z "$openRouterExists" ]; then
    echo -n "$openRouterApiKey" | gcloud secrets create OPENROUTER_API_KEY --data-file=-
else
    echo -n "$openRouterApiKey" | gcloud secrets versions add OPENROUTER_API_KEY --data-file=-
    echo "Updated existing OPENROUTER_API_KEY secret."
fi

if [ -z "$supabaseUrlExists" ]; then
    echo -n "$supabaseUrl" | gcloud secrets create SUPABASE_URL --data-file=-
else
    echo -n "$supabaseUrl" | gcloud secrets versions add SUPABASE_URL --data-file=-
    echo "Updated existing SUPABASE_URL secret."
fi

if [ -z "$supabaseKeyExists" ]; then
    echo -n "$supabaseKey" | gcloud secrets create SUPABASE_KEY --data-file=-
else
    echo -n "$supabaseKey" | gcloud secrets versions add SUPABASE_KEY --data-file=-
    echo "Updated existing SUPABASE_KEY secret."
fi

# Get the Cloud Run service account
serviceAccount=$(gcloud iam service-accounts list --filter="displayName:Cloud Run Service Agent" --format="value(email)")

# Grant access to secrets
echo "Granting Cloud Run service account access to secrets..."
gcloud secrets add-iam-policy-binding OPENROUTER_API_KEY --member="serviceAccount:$serviceAccount" --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding SUPABASE_URL --member="serviceAccount:$serviceAccount" --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding SUPABASE_KEY --member="serviceAccount:$serviceAccount" --role="roles/secretmanager.secretAccessor"

# Ask for region
read -p "Enter the region to deploy to (default: us-central1): " region
if [ -z "$region" ]; then
    region="us-central1"
fi

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy devdocs \
  --source . \
  --platform managed \
  --region $region \
  --allow-unauthenticated \
  --update-secrets=OPENROUTER_API_KEY=OPENROUTER_API_KEY:latest,SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_KEY=SUPABASE_KEY:latest

# Get the deployed URL
serviceUrl=$(gcloud run services describe devdocs --platform managed --region $region --format="value(status.url)")

echo "Deployment complete!"
echo "Your application is available at: $serviceUrl"
echo "Remember to set up your Supabase database as described in the GOOGLE_CLOUD_DEPLOYMENT.md guide."
