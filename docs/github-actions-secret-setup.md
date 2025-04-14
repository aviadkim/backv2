# Setting up GitHub Actions Secret for Google Cloud Authentication

This guide explains how to set up the `GCP_SA_KEY` secret in GitHub for authenticating with Google Cloud.

## Step 1: Create a Service Account Key in Google Cloud

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project: `github-456508`
3. Navigate to "IAM & Admin" > "Service Accounts"
4. Find the service account you want to use (e.g., `github@github-456508.iam.gserviceaccount.com`)
5. Click on the three dots menu and select "Manage keys"
6. Click "Add Key" > "Create new key"
7. Select "JSON" format
8. Click "Create"
9. The key file will be downloaded to your computer

## Step 2: Add the Service Account Key as a GitHub Secret

1. Go to your GitHub repository
2. Navigate to "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Name: `GCP_SA_KEY`
5. Value: Copy and paste the entire content of the JSON key file
6. Click "Add secret"

## Step 3: Ensure the Service Account Has the Required Permissions

The service account needs the following roles:

- Cloud Run Admin
- Storage Admin
- Service Account User
- Artifact Registry Admin

To add these roles:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project: `github-456508`
3. Navigate to "IAM & Admin" > "IAM"
4. Find the service account
5. Click the pencil icon to edit
6. Click "Add another role" and add each of the required roles
7. Click "Save"

## Step 4: Enable Required APIs

Make sure the following APIs are enabled in your Google Cloud project:

1. Go to "APIs & Services" > "Library"
2. Search for and enable:
   - Cloud Run API
   - Artifact Registry API
   - Cloud Build API
   - IAM API

## Step 5: Verify the GitHub Actions Workflow

The GitHub Actions workflow should now be able to authenticate with Google Cloud using the `GCP_SA_KEY` secret:

```yaml
- name: Authenticate to Google Cloud
  id: auth
  uses: google-github-actions/auth@v2
  with:
    credentials_json: ${{ secrets.GCP_SA_KEY }}
```

## Troubleshooting

If you encounter any issues, check the following:

1. Make sure the service account key is correctly formatted in the GitHub secret
2. Make sure the service account has the necessary permissions
3. Make sure the required APIs are enabled
4. Check the GitHub Actions logs for any error messages
