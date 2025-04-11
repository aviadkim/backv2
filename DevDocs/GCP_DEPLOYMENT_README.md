# DevDocs Google Cloud Deployment

This README provides a quick overview of deploying the DevDocs application to Google Cloud Platform (GCP) using Cloud Run and Supabase.

## Why Google Cloud and Supabase?

- **Google Cloud Run**: Serverless container platform that automatically scales based on traffic. You only pay for what you use, making it cost-effective for SaaS applications.
- **Google Secret Manager**: Securely store and manage API keys and other sensitive information.
- **Supabase**: Provides a PostgreSQL database with built-in authentication, storage, and real-time capabilities. Perfect for SaaS applications.

## Quick Start

We've provided scripts to make deployment as simple as possible:

### Windows (PowerShell)

```powershell
# Set up local development environment
./setup-local-env.ps1

# Deploy to Google Cloud
./deploy-to-gcp.ps1
```

### macOS/Linux (Bash)

```bash
# Make scripts executable
chmod +x setup-local-env.sh deploy-to-gcp.sh

# Set up local development environment
./setup-local-env.sh

# Deploy to Google Cloud
./deploy-to-gcp.sh
```

## Detailed Documentation

For detailed step-by-step instructions, see the [Google Cloud Deployment Guide](./GOOGLE_CLOUD_DEPLOYMENT.md).

## Key Features of This Deployment Solution

1. **Simple Deployment**: One-command deployment to Google Cloud Run.
2. **Secure API Key Management**: All API keys are stored in Google Secret Manager, not in your code.
3. **Automatic Scaling**: Cloud Run automatically scales based on traffic, from zero to many instances.
4. **Cost-Effective**: You only pay for what you use. When there's no traffic, you pay nothing.
5. **Database Integration**: Easy integration with Supabase for database, authentication, and storage.
6. **CI/CD Ready**: Includes configuration for continuous deployment from GitHub.

## Folder Structure

```
DevDocs/
├── Dockerfile                # Container configuration for Cloud Run
├── cloudbuild.yaml           # CI/CD configuration for Cloud Build
├── .gcloudignore             # Files to exclude from deployment
├── deploy-to-gcp.ps1         # PowerShell deployment script
├── deploy-to-gcp.sh          # Bash deployment script
├── setup-local-env.ps1       # PowerShell local environment setup
├── setup-local-env.sh        # Bash local environment setup
├── GOOGLE_CLOUD_DEPLOYMENT.md # Detailed deployment guide
└── GCP_DEPLOYMENT_README.md  # This file
```

## Next Steps After Deployment

1. **Set Up Supabase Database**: Follow the instructions in the deployment guide to set up your database tables and security policies.
2. **Configure Authentication**: Set up authentication in Supabase if your application requires user accounts.
3. **Set Up Monitoring**: Configure monitoring and alerts in Google Cloud Console.
4. **Set Up Custom Domain**: Configure a custom domain for your Cloud Run service if needed.

## Troubleshooting

If you encounter issues during deployment, check the following:

1. **Check Logs**: View the Cloud Run logs in the Google Cloud Console.
2. **Secret Access**: Ensure the Cloud Run service account has access to the secrets.
3. **Database Connection**: Verify that the Supabase URL and key are correct.
4. **Network Issues**: Ensure that Cloud Run can access Supabase and any other external services.

For more detailed troubleshooting, see the [Google Cloud Deployment Guide](./GOOGLE_CLOUD_DEPLOYMENT.md).
