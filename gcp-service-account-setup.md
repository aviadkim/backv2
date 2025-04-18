# Google Cloud Service Account Setup for GitHub Actions

Follow these steps to create a new service account key for GitHub Actions:

## 1. Create a Service Account

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project: `github-456508`
3. Navigate to "IAM & Admin" > "Service Accounts"
4. Click "Create Service Account"
5. Enter a name (e.g., `github-actions-deployer`) and description
6. Click "Create and Continue"

## 2. Assign Roles to the Service Account

Add the following roles to the service account:
- Cloud Run Admin
- Storage Admin
- Service Account User
- Cloud Build Editor

Click "Continue" and then "Done"

## 3. Create and Download the Key

1. Find your new service account in the list
2. Click on the three dots menu (⋮) at the end of the row
3. Select "Manage keys"
4. Click "Add Key" > "Create new key"
5. Select "JSON" format
6. Click "Create"

The key file will be automatically downloaded to your computer.

## 4. Add the Key to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Name: `GCP_SA_KEY`
5. Value: Copy and paste the entire contents of the downloaded JSON key file
6. Click "Add secret"

## 5. Verify the Secret Format

Make sure the secret contains a valid JSON object with all the necessary fields:
- `type`: Should be "service_account"
- `project_id`: Your Google Cloud project ID
- `private_key_id`: The ID of the private key
- `private_key`: The private key (starts with "-----BEGIN PRIVATE KEY-----")
- `client_email`: The service account email
- `client_id`: The client ID
- `auth_uri`: The authentication URI
- `token_uri`: The token URI
- `auth_provider_x509_cert_url`: The auth provider cert URL
- `client_x509_cert_url`: The client cert URL

## Important Security Notes

- Never commit the service account key file to your repository
- Rotate the key periodically for better security
- Consider using Workload Identity Federation for keyless authentication if possible
