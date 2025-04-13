# Setting Up GitHub Integration with Google Cloud Run

This guide will walk you through the process of setting up continuous deployment from your GitHub repository to Google Cloud Run.

## Prerequisites

- A Google Cloud project with billing enabled
- A GitHub repository containing your DevDocs application
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
   - Artifact Registry API

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
   - Name: `devdocs-github-trigger`
   - Description: `Trigger for DevDocs application`
   - Event: `Push to a branch`
   - Source: Select your GitHub repository (`aviadkim/backv2`)
   - Branch: `^main$` (to trigger on pushes to the main branch)
   - Build configuration: `Cloud Build configuration file (yaml or json)`
   - Cloud Build configuration file location: `cloudbuild.yaml`
3. Click "Create"

## Step 4: Verify Your Configuration Files

Make sure your repository has the following files properly configured:

### Dockerfile

The Dockerfile should build your DevDocs application with all necessary dependencies:

```dockerfile
# Use a Node.js image with Chrome for web browsing capabilities
FROM node:18

# Install Chrome for web browsing capabilities
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    apt-transport-https \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all application files
COPY . .

# Install dependencies
RUN cd mcp-integration && npm install

# Install puppeteer for web browsing
RUN cd mcp-integration && npm install puppeteer axios cheerio cors

# Create enhanced MCP server with web capabilities
COPY mcp-integration/devdocs-mcp-server.js ./server.js

# Set environment variables
ENV PORT=8080
ENV GOOGLE_CLOUD_PROJECT_ID=github-456508
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV CHROME_BIN=/usr/bin/google-chrome

# Create public directory for static files
RUN mkdir -p public

# Copy web files to public directory
COPY devdocs-app.html ./public/index.html
COPY mcp-web-demo.html ./public/demo.html

# Expose port
EXPOSE $PORT

# Start the application
CMD ["node", "server.js"]
```

### cloudbuild.yaml

The cloudbuild.yaml file should define the build and deployment steps:

```yaml
steps:
  # Print directory structure for debugging
  - name: 'gcr.io/cloud-builders/gcloud'
    entrypoint: 'bash'
    args: ['-c', 'ls -la && echo "Current directory: $(pwd)"']

  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/devdocs-app:latest', '.']

  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/devdocs-app:latest']

  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'devdocs-mcp-server'
      - '--image=gcr.io/$PROJECT_ID/devdocs-app:latest'
      - '--region=me-west1'
      - '--platform=managed'
      - '--allow-unauthenticated'

# Store images in Google Container Registry
images:
  - 'gcr.io/$PROJECT_ID/devdocs-app:latest'
```

## Step 5: Commit and Push Your Changes

1. Commit your changes to the repository:
   ```
   git add .
   git commit -m "Set up continuous deployment to Google Cloud Run"
   git push origin main
   ```

2. This should trigger a build in Cloud Build. You can monitor the build progress at:
   https://console.cloud.google.com/cloud-build/builds?project=github-456508

## Step 6: Verify the Deployment

1. Once the build is complete, go to the Cloud Run page:
   https://console.cloud.google.com/run?project=github-456508

2. Click on the `devdocs-mcp-server` service

3. You should see the URL of your deployed application. Click on it to verify that your DevDocs application is running correctly.

## Step 7: Set Up Automatic Updates

Now that you have continuous deployment set up, any changes you push to the main branch of your GitHub repository will automatically trigger a build and deployment to Google Cloud Run.

To test this:

1. Make a change to your DevDocs application code
2. Commit and push the change to GitHub
3. Monitor the build in Cloud Build
4. Verify that the changes are reflected in the deployed application

## Troubleshooting

If you encounter any issues during the setup process, check the following:

1. **Build Failures**: Check the Cloud Build logs for error messages
2. **Deployment Failures**: Check the Cloud Run logs for error messages
3. **Permission Issues**: Make sure your service account has the necessary permissions
4. **API Enablement**: Verify that all required APIs are enabled
5. **Configuration Files**: Double-check your Dockerfile and cloudbuild.yaml for errors

## Additional Resources

- [Cloud Build GitHub Integration](https://cloud.google.com/build/docs/automating-builds/github/connect-repo-github)
- [Cloud Run Continuous Deployment](https://cloud.google.com/run/docs/continuous-deployment)
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)
- [Cloud Build Configuration Reference](https://cloud.google.com/build/docs/build-config-file-schema)
