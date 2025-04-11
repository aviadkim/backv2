# PowerShell script to deploy DevDocs to Google Cloud Run

# Check if gcloud CLI is installed
try {
    $gcloudVersion = gcloud --version
    Write-Host "Google Cloud SDK is installed." -ForegroundColor Green
} catch {
    Write-Host "Google Cloud SDK is not installed or not in PATH. Please install it first." -ForegroundColor Red
    Write-Host "Visit: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Ask for project ID
$projectId = Read-Host -Prompt "Enter your Google Cloud Project ID"

# Set the project
Write-Host "Setting Google Cloud project to: $projectId" -ForegroundColor Cyan
gcloud config set project $projectId

# Enable required APIs
Write-Host "Enabling required Google Cloud APIs..." -ForegroundColor Cyan
gcloud services enable cloudbuild.googleapis.com run.googleapis.com secretmanager.googleapis.com containerregistry.googleapis.com

# Ask for API keys
$openRouterApiKey = Read-Host -Prompt "Enter your OpenRouter API Key"
$supabaseUrl = Read-Host -Prompt "Enter your Supabase URL (e.g., https://your-project-id.supabase.co)"
$supabaseKey = Read-Host -Prompt "Enter your Supabase Key"

# Create secrets
Write-Host "Creating secrets in Secret Manager..." -ForegroundColor Cyan

# Check if secrets already exist
$openRouterExists = gcloud secrets list --filter="name:OPENROUTER_API_KEY" --format="value(name)" 2>$null
$supabaseUrlExists = gcloud secrets list --filter="name:SUPABASE_URL" --format="value(name)" 2>$null
$supabaseKeyExists = gcloud secrets list --filter="name:SUPABASE_KEY" --format="value(name)" 2>$null

if (-not $openRouterExists) {
    $openRouterApiKey | gcloud secrets create OPENROUTER_API_KEY --data-file=-
} else {
    $openRouterApiKey | gcloud secrets versions add OPENROUTER_API_KEY --data-file=-
    Write-Host "Updated existing OPENROUTER_API_KEY secret." -ForegroundColor Yellow
}

if (-not $supabaseUrlExists) {
    $supabaseUrl | gcloud secrets create SUPABASE_URL --data-file=-
} else {
    $supabaseUrl | gcloud secrets versions add SUPABASE_URL --data-file=-
    Write-Host "Updated existing SUPABASE_URL secret." -ForegroundColor Yellow
}

if (-not $supabaseKeyExists) {
    $supabaseKey | gcloud secrets create SUPABASE_KEY --data-file=-
} else {
    $supabaseKey | gcloud secrets versions add SUPABASE_KEY --data-file=-
    Write-Host "Updated existing SUPABASE_KEY secret." -ForegroundColor Yellow
}

# Get the Cloud Run service account
$serviceAccount = gcloud iam service-accounts list --filter="displayName:Cloud Run Service Agent" --format="value(email)"

# Grant access to secrets
Write-Host "Granting Cloud Run service account access to secrets..." -ForegroundColor Cyan
gcloud secrets add-iam-policy-binding OPENROUTER_API_KEY --member="serviceAccount:$serviceAccount" --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding SUPABASE_URL --member="serviceAccount:$serviceAccount" --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding SUPABASE_KEY --member="serviceAccount:$serviceAccount" --role="roles/secretmanager.secretAccessor"

# Ask for region
$region = Read-Host -Prompt "Enter the region to deploy to (default: us-central1)"
if (-not $region) {
    $region = "us-central1"
}

# Deploy to Cloud Run
Write-Host "Deploying to Cloud Run..." -ForegroundColor Cyan
gcloud run deploy devdocs `
  --source . `
  --platform managed `
  --region $region `
  --allow-unauthenticated `
  --update-secrets=OPENROUTER_API_KEY=OPENROUTER_API_KEY:latest,SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_KEY=SUPABASE_KEY:latest

# Get the deployed URL
$serviceUrl = gcloud run services describe devdocs --platform managed --region $region --format="value(status.url)"

Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Your application is available at: $serviceUrl" -ForegroundColor Cyan
Write-Host "Remember to set up your Supabase database as described in the GOOGLE_CLOUD_DEPLOYMENT.md guide." -ForegroundColor Yellow
