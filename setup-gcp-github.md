# Setting up Google Cloud Authentication for GitHub Actions

Follow these steps to set up authentication between GitHub Actions and Google Cloud:

## 1. Create a Service Account

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project: `github-456508`
3. Navigate to "IAM & Admin" > "Service Accounts"
4. Click "Create Service Account"
5. Enter a name (e.g., "github-actions")
6. Add the following roles:
   - Cloud Run Admin
   - Storage Admin
   - Service Account User
   - Artifact Registry Admin
7. Click "Done"

## 2. Create a Service Account Key

1. Find the service account you just created in the list
2. Click on the three dots menu and select "Manage keys"
3. Click "Add Key" > "Create new key"
4. Select "JSON" format
5. Click "Create"
6. The key file will be downloaded to your computer

## 3. Add the Key to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Name: `GCP_SA_KEY`
5. Value: Copy and paste the entire content of the JSON key file
6. Click "Add secret"

## 4. Enable Required APIs

Make sure the following APIs are enabled in your Google Cloud project:

1. Go to "APIs & Services" > "Library"
2. Search for and enable:
   - Cloud Run API
   - Artifact Registry API
   - Cloud Build API
   - IAM API

## 5. Push the GitHub Actions Workflow

The workflow file is already created at `.github/workflows/google-cloud-deploy.yml`. When you push changes to the `main` branch, the workflow will automatically deploy to Google Cloud Run.

## 6. Verify Deployment

After pushing changes to the `main` branch, go to the "Actions" tab in your GitHub repository to see the workflow run. If successful, you'll see a URL where your application is deployed.

You can also check the deployment in the Google Cloud Console under "Cloud Run".
