# Setting Up API Secrets in Google Cloud Secret Manager

This guide will walk you through the process of setting up API secrets in Google Cloud Secret Manager and using them in your DevDocs application.

## What is Google Cloud Secret Manager?

Google Cloud Secret Manager is a secure and convenient storage system for API keys, passwords, certificates, and other sensitive data. It provides a central place to manage your secrets with fine-grained access control and audit logging.

## Prerequisites

- A Google Cloud project with billing enabled
- Owner or Secret Manager Admin permissions on the Google Cloud project

## Step 1: Enable the Secret Manager API

1. Go to the Google Cloud Console: https://console.cloud.google.com/
2. Select your project: `github-456508`
3. Navigate to "APIs & Services" > "Library"
4. Search for "Secret Manager API"
5. Click "Enable"

## Step 2: Create a Secret

1. Go to the Secret Manager page: https://console.cloud.google.com/security/secret-manager?project=github-456508
2. Click "Create Secret"
3. Enter the following details:
   - Name: `mcp-api-key` (use lowercase letters, numbers, and hyphens only)
   - Secret value: Enter your API key
   - Regions: Select "me-west1" (Tel Aviv)
4. Click "Create Secret"

## Step 3: Grant Access to the Secret

1. On the Secret Manager page, click on the secret you just created
2. Click on the "Permissions" tab
3. Click "Add Principal"
4. Enter the service account email: `github@github-456508.iam.gserviceaccount.com`
5. Select the role: "Secret Manager Secret Accessor"
6. Click "Save"

## Step 4: Access the Secret in Your Application

### Option 1: Using Environment Variables (Recommended)

When deploying to Cloud Run, you can pass the secret as an environment variable:

```yaml
# In cloudbuild.yaml or GitHub Actions workflow
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  entrypoint: gcloud
  args:
    - 'run'
    - 'deploy'
    - 'devdocs-mcp-server'
    - '--image=gcr.io/$PROJECT_ID/devdocs-mcp-server:$COMMIT_SHA'
    - '--region=me-west1'
    - '--platform=managed'
    - '--allow-unauthenticated'
    - '--set-env-vars=GOOGLE_CLOUD_PROJECT_ID=$PROJECT_ID'
    - '--set-secrets=MCP_API_KEY=mcp-api-key:latest'
```

Then in your code, you can access the secret using:

```javascript
const apiKey = process.env.MCP_API_KEY;
```

### Option 2: Using the Secret Manager API

You can also access the secret programmatically using the Secret Manager API:

```javascript
const {SecretManagerServiceClient} = require('@google-cloud/secret-manager');
const client = new SecretManagerServiceClient();

async function accessSecret() {
  const name = 'projects/github-456508/secrets/mcp-api-key/versions/latest';
  const [version] = await client.accessSecretVersion({name});
  const payload = version.payload.data.toString();
  return payload;
}

// Usage
const apiKey = await accessSecret();
```

## Step 5: Setting Up GitHub Secrets for GitHub Actions

If you're using GitHub Actions for deployment, you'll need to set up the following secrets in your GitHub repository:

1. Go to your GitHub repository: https://github.com/aviadkim/backv2
2. Click on "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Add the following secrets:
   - Name: `GCP_PROJECT_ID`
   - Value: `github-456508`
5. Click "Add secret"
6. Add another secret:
   - Name: `GCP_SA_KEY`
   - Value: The JSON key of your Google Cloud service account (you can create a new key in the IAM & Admin > Service Accounts section)
7. Click "Add secret"
8. Add another secret:
   - Name: `MCP_API_KEY`
   - Value: Your MCP API key
9. Click "Add secret"

## Additional Resources

- [Google Cloud Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Using Secrets in Cloud Run](https://cloud.google.com/run/docs/configuring/secrets)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
