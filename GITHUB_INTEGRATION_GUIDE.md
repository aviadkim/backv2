# Setting Up GitHub Integration with Google Cloud Build

This guide will walk you through the process of setting up GitHub integration with Google Cloud Build, so that changes pushed to your GitHub repository will automatically trigger a build and deployment to Google Cloud Run.

## Prerequisites

- A Google Cloud project with billing enabled
- A GitHub repository containing your application code
- Owner or Editor permissions on the Google Cloud project
- Admin permissions on the GitHub repository

## Step 1: Enable Required APIs

1. Go to the Google Cloud Console: https://console.cloud.google.com/
2. Select your project: `github-456508`
3. Navigate to "APIs & Services" > "Library"
4. Search for and enable the following APIs:
   - Cloud Build API
   - Cloud Run API
   - Container Registry API
   - Source Repository API

## Step 2: Connect GitHub Repository to Cloud Build

1. Go to the Cloud Build Triggers page: https://console.cloud.google.com/cloud-build/triggers?project=github-456508
2. Click "Connect Repository"
3. Select "GitHub (Cloud Build GitHub App)" as the source
4. Click "Continue"
5. Authenticate with GitHub and select your repository: `aviadkim/backv2`
6. Click "Connect"

## Step 3: Create a Cloud Build Trigger

1. On the Cloud Build Triggers page, click "Create Trigger"
2. Enter the following details:
   - Name: `devdocs-mcp-trigger`
   - Event: `Push to a branch`
   - Source: Select your GitHub repository (`aviadkim/backv2`)
   - Branch: `^main$` (to trigger on pushes to the main branch)
   - Build configuration: `Cloud Build configuration file (yaml or json)`
   - Cloud Build configuration file location: `cloudbuild.yaml`
3. Click "Create"

## Step 4: Test the Integration

1. Make a change to your code in the GitHub repository
2. Commit and push the change to the main branch
3. Go to the Cloud Build History page to see the build in progress: https://console.cloud.google.com/cloud-build/builds?project=github-456508
4. Once the build is complete, check the deployed application at: https://devdocs-mcp-server-github-456508.me-west1.run.app

## Troubleshooting

If you encounter any issues during the setup process, check the following:

1. Make sure you have the necessary permissions on both GitHub and Google Cloud
2. Verify that all required APIs are enabled
3. Check the Cloud Build logs for any error messages
4. Ensure that your `cloudbuild.yaml` file is correctly formatted and contains valid steps

## Additional Resources

- [Cloud Build GitHub Integration Documentation](https://cloud.google.com/build/docs/automating-builds/github/connect-repo-github)
- [Cloud Build Configuration File Reference](https://cloud.google.com/build/docs/build-config-file-schema)
- [Cloud Run Deployment Guide](https://cloud.google.com/run/docs/deploying)

## Next Steps

After setting up the GitHub integration, any changes you make to your code in the GitHub repository will automatically trigger a build and deployment to Google Cloud Run. This enables a continuous deployment workflow where your changes are automatically deployed to production.
