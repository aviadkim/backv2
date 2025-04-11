# Setup Secrets in Google Cloud Secret Manager
# This script sets up API secrets in Google Cloud Secret Manager

# Configuration
$PROJECT_ID = "github-456508"
$REGION = "me-west1"
$SECRET_NAME = "mcp-api-key"

Write-Host "Setting up API secrets in Google Cloud Secret Manager..." -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "Region: $REGION" -ForegroundColor Yellow
Write-Host "Secret Name: $SECRET_NAME" -ForegroundColor Yellow

# Enable the Secret Manager API
Write-Host "`nEnabling the Secret Manager API..." -ForegroundColor Cyan
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID

# Prompt for the API key
Write-Host "`nEnter your MCP API key:" -ForegroundColor Yellow
$API_KEY = Read-Host -AsSecureString
$API_KEY_PLAIN = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($API_KEY))

# Create a temporary file for the API key
$TEMP_FILE = [System.IO.Path]::GetTempFileName()
$API_KEY_PLAIN | Out-File -FilePath $TEMP_FILE -NoNewline

# Create the secret
Write-Host "`nCreating the secret..." -ForegroundColor Cyan
gcloud secrets create $SECRET_NAME --data-file=$TEMP_FILE --replication-policy=user-managed --locations=$REGION --project=$PROJECT_ID

# Delete the temporary file
Remove-Item -Path $TEMP_FILE

# Grant access to the service account
Write-Host "`nGranting access to the service account..." -ForegroundColor Cyan
gcloud secrets add-iam-policy-binding $SECRET_NAME --member=serviceAccount:github@github-456508.iam.gserviceaccount.com --role=roles/secretmanager.secretAccessor --project=$PROJECT_ID

Write-Host "`nSecret setup complete!" -ForegroundColor Green
Write-Host "You can now access the secret in your application using the Secret Manager API or environment variables." -ForegroundColor Green

# Instructions for using the secret in Cloud Run
Write-Host "`nTo use the secret in Cloud Run:" -ForegroundColor Cyan
Write-Host "1. Add the following to your Cloud Run deployment command:" -ForegroundColor Yellow
Write-Host "   --set-secrets=MCP_API_KEY=$SECRET_NAME:latest" -ForegroundColor Yellow
Write-Host "2. Access the secret in your code using:" -ForegroundColor Yellow
Write-Host "   const apiKey = process.env.MCP_API_KEY;" -ForegroundColor Yellow
