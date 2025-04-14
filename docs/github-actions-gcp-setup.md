# Setting up GitHub Actions with Google Cloud

This guide explains how to set up GitHub Actions to deploy to Google Cloud using Workload Identity Federation.

## Prerequisites

1. A Google Cloud project with the following APIs enabled:
   - Cloud Run API
   - IAM API
   - Artifact Registry API
   - Cloud Build API

2. A GitHub repository with your application code

## Step 1: Create a Workload Identity Pool

1. Go to the Google Cloud Console
2. Navigate to "IAM & Admin" > "Workload Identity Federation"
3. Click "Create Pool"
4. Enter a name (e.g., "github-pool")
5. Enter a description (e.g., "Pool for GitHub Actions")
6. Click "Continue"
7. For "Provider", select "OpenID Connect (OIDC)"
8. Enter a provider name (e.g., "github-provider")
9. Enter a description (e.g., "GitHub Actions provider")
10. For "Issuer URL", enter `https://token.actions.githubusercontent.com`
11. Click "Continue"
12. In the "Configure provider attributes" section:
    - For "google.subject", enter `assertion.sub`
    - Click "Add Attribute Mapping"
    - For "Attribute name", enter `attribute.repository`
    - For "Attribute value", enter `assertion.repository`
13. Click "Save"

## Step 2: Create a Service Account

1. Go to the Google Cloud Console
2. Navigate to "IAM & Admin" > "Service Accounts"
3. Click "Create Service Account"
4. Enter a name (e.g., "github-actions")
5. Enter a description (e.g., "Service account for GitHub Actions")
6. Click "Create and Continue"
7. Add the following roles:
   - Cloud Run Admin
   - Storage Admin
   - Service Account User
   - Artifact Registry Admin
8. Click "Done"

## Step 3: Grant the Service Account Access to the Workload Identity Pool

1. Go to the Google Cloud Console
2. Navigate to "IAM & Admin" > "Workload Identity Federation"
3. Click on the pool you created (e.g., "github-pool")
4. Click on the "Grant Access" button
5. In the "Service account" field, select the service account you created
6. In the "Attribute conditions" field, enter:
   ```
   assertion.repository=='aviadkim/backv2'
   ```
7. Click "Save"

## Step 4: Update the GitHub Actions Workflow

The GitHub Actions workflow file should be updated to use Workload Identity Federation:

```yaml
- name: Authenticate to Google Cloud
  id: auth
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: 'projects/683496987674/locations/global/workloadIdentityPools/github-pool/providers/github-provider'
    service_account: 'github@github-456508.iam.gserviceaccount.com'
```

## Step 5: Push the Changes to GitHub

1. Commit the changes to your repository
2. Push the changes to GitHub
3. Go to the "Actions" tab in your GitHub repository to see the workflow run

## Troubleshooting

If you encounter any issues, check the following:

1. Make sure the Workload Identity Pool and Provider are correctly configured
2. Make sure the Service Account has the necessary permissions
3. Make sure the attribute conditions are correctly set
4. Check the GitHub Actions logs for any error messages
