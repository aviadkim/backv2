# Setting Up a Google Cloud Service Account for GitHub Actions

This guide will walk you through the process of setting up a Google Cloud service account and adding it to GitHub Actions secrets.

## Prerequisites

- A Google Cloud project with billing enabled
- Owner or IAM Admin permissions on the Google Cloud project
- Admin permissions on the GitHub repository

## Step 1: Create a Service Account

1. Go to the Google Cloud Console: https://console.cloud.google.com/
2. Select your project: `github-456508`
3. Navigate to "IAM & Admin" > "Service Accounts"
4. Click "Create Service Account"
5. Enter the following details:
   - Service account name: `github-actions`
   - Service account ID: `github-actions`
   - Description: `Service account for GitHub Actions`
6. Click "Create and Continue"
7. Add the following roles:
   - Cloud Run Admin
   - Storage Admin
   - Service Account User
   - Cloud Build Editor
   - Secret Manager Secret Accessor
8. Click "Continue"
9. Click "Done"

## Step 2: Create a Service Account Key

1. On the Service Accounts page, click on the service account you just created
2. Click on the "Keys" tab
3. Click "Add Key" > "Create new key"
4. Select "JSON" as the key type
5. Click "Create"
6. The key file will be downloaded to your computer. Keep this file secure!

## Step 3: Add the Service Account Key to GitHub Secrets

1. Go to your GitHub repository: https://github.com/aviadkim/backv2
2. Click on "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Enter the following details:
   - Name: `GCP_SA_KEY`
   - Value: The entire contents of the JSON key file you downloaded
5. Click "Add secret"

## Step 4: Add the MCP API Key to GitHub Secrets

1. Go to your GitHub repository: https://github.com/aviadkim/backv2
2. Click on "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Enter the following details:
   - Name: `MCP_API_KEY`
   - Value: Your MCP API key
5. Click "Add secret"

## Step 5: Verify the GitHub Actions Workflow

1. Go to your GitHub repository: https://github.com/aviadkim/backv2
2. Click on "Actions"
3. You should see the workflow running or completed
4. If the workflow failed, check the logs for errors

## Additional Resources

- [Google Cloud Service Accounts Documentation](https://cloud.google.com/iam/docs/service-accounts)
- [GitHub Actions Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Google Cloud Authentication for GitHub Actions](https://github.com/google-github-actions/auth)
