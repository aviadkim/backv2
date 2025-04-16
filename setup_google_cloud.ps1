# Setup script for Google Cloud environment

# Set variables
$PROJECT_ID = "github-456508"
$SERVICE_ACCOUNT = "github"
$REGION = "me-west1"
$API_KEY = "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"

# Check if gcloud is installed
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Error "gcloud command not found. Please install Google Cloud SDK."
    exit 1
}

# Create project if it doesn't exist
try {
    gcloud projects describe $PROJECT_ID | Out-Null
    Write-Host "Project $PROJECT_ID already exists."
} catch {
    Write-Host "Creating project $PROJECT_ID..."
    gcloud projects create $PROJECT_ID --name="GitHub"
}

# Set project
Write-Host "Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
Write-Host "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Create service account
Write-Host "Creating service account $SERVICE_ACCOUNT..."
gcloud iam service-accounts create $SERVICE_ACCOUNT `
  --description="GitHub Actions service account" `
  --display-name="GitHub Actions"

# Grant permissions
Write-Host "Granting permissions to service account..."
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" `
  --role="roles/owner"

# Create service account key
Write-Host "Creating service account key..."
gcloud iam service-accounts keys create key.json `
  --iam-account=$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com

# Store API key in Secret Manager
Write-Host "Storing API key in Secret Manager..."
gcloud secrets create openrouter-api-key --replication-policy="automatic"
$API_KEY | gcloud secrets versions add openrouter-api-key --data-file=-

# Grant service account access to the secret
Write-Host "Granting service account access to the secret..."
gcloud secrets add-iam-policy-binding openrouter-api-key `
  --member="serviceAccount:$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor"

Write-Host "Google Cloud environment setup completed!"
Write-Host "Please add the contents of key.json to your GitHub repository secrets as GCP_SA_KEY"
