# GitHub Secrets Setup for FinDoc Analyzer

This document explains how to set up the required GitHub secrets for the FinDoc Analyzer deployment workflow.

## Required Secrets

The following secrets need to be added to your GitHub repository:

1. `GCP_SA_KEY`: Google Cloud service account key (JSON format)
2. `OPENROUTER_API_KEY`: API key for OpenRouter AI services
3. `JWT_SECRET`: Secret key for JWT authentication
4. `ENCRYPTION_KEY`: Key for data encryption
5. `SUPABASE_URL`: URL for your Supabase instance
6. `SUPABASE_KEY`: API key for Supabase

## Adding Secrets to GitHub

1. Go to your GitHub repository
2. Navigate to "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Add each secret with its name and value
5. Click "Add secret"

## Secret Values

### GCP_SA_KEY

This should be the entire JSON content of your Google Cloud service account key file. Follow the instructions in `gcp-service-account-setup.md` to create this key.

### OPENROUTER_API_KEY

Your OpenRouter API key: `sk-or-v1-64e1068c3a61a5e4be88c64c6992b39dbc15ad687201cb3fd05a98a9ba1e22dc8`

### JWT_SECRET

Generate a random string to use as your JWT secret. You can use a command like:

```bash
openssl rand -base64 32
```

### ENCRYPTION_KEY

Generate a random string to use as your encryption key. You can use a command like:

```bash
openssl rand -base64 32
```

### SUPABASE_URL

Your Supabase URL: `https://dnjnsotemnfrjlotgved.supabase.co`

### SUPABASE_KEY

Your Supabase API key. This can be found in your Supabase project settings under "API".

## Verifying Secrets

After adding all secrets, they should appear in the list on the "Secrets and variables" page. The actual values will be hidden for security reasons.

## Updating Workflow

If you need to add or remove secrets from the workflow, update the `.github/workflows/google-cloud-deploy.yml` file accordingly.
