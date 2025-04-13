# Setting Up GitHub Integration with Google Cloud Run for DevDocs

This guide will walk you through the process of setting up continuous deployment from your GitHub repository to Google Cloud Run for the DevDocs application.

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

## Step 3: Create a Cloud Build Trigger for the MCP Server

1. On the Cloud Build Triggers page, click "Create Trigger"
2. Enter the following details:
   - Name: `devdocs-mcp-trigger`
   - Description: `Trigger for DevDocs MCP server`
   - Event: `Push to a branch`
   - Source: Select your GitHub repository (`aviadkim/backv2`)
   - Branch: `^main$` (to trigger on pushes to the main branch)
   - Included files filter: `DevDocs/mcp/**` (to trigger only when MCP-related files change)
   - Build configuration: `Cloud Build configuration file (yaml or json)`
   - Cloud Build configuration file location: `DevDocs/cloudbuild.mcp.yaml`
3. Click "Create"

## Step 4: Create a Cloud Build Trigger for the DevDocs Application

1. On the Cloud Build Triggers page, click "Create Trigger"
2. Enter the following details:
   - Name: `devdocs-app-trigger`
   - Description: `Trigger for DevDocs application`
   - Event: `Push to a branch`
   - Source: Select your GitHub repository (`aviadkim/backv2`)
   - Branch: `^main$` (to trigger on pushes to the main branch)
   - Included files filter: `DevDocs/**` (to trigger when any DevDocs files change)
   - Excluded files filter: `DevDocs/mcp/**` (to avoid duplicate builds when MCP files change)
   - Build configuration: `Cloud Build configuration file (yaml or json)`
   - Cloud Build configuration file location: `DevDocs/cloudbuild.yaml`
3. Click "Create"

## Step 5: Verify Your Configuration Files

Make sure your repository has the following files properly configured:

### DevDocs/cloudbuild.yaml

This file should build and deploy the main DevDocs application:

```yaml
steps:
  # Print directory structure for debugging
  - name: 'gcr.io/cloud-builders/gcloud'
    entrypoint: 'bash'
    args: ['-c', 'ls -la && echo "Current directory: $(pwd)"']

  # Navigate to DevDocs directory
  - name: 'gcr.io/cloud-builders/gcloud'
    entrypoint: 'bash'
    args: ['-c', 'cd DevDocs && ls -la && echo "DevDocs directory: $(pwd)"']

  # Install dependencies
  - name: 'node:18'
    entrypoint: npm
    args: ['install']
    dir: 'DevDocs'

  # Build the application
  - name: 'node:18'
    entrypoint: npm
    args: ['run', 'build']
    dir: 'DevDocs'

  # Deploy to App Engine
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'app'
      - 'deploy'
      - 'DevDocs/app.yaml'
      - '--quiet'
      - '--version=v1'
      - '--project=$PROJECT_ID'
```

### DevDocs/cloudbuild.mcp.yaml

This file should build and deploy the MCP server:

```yaml
steps:
  # Print directory structure for debugging
  - name: 'gcr.io/cloud-builders/gcloud'
    entrypoint: 'bash'
    args: ['-c', 'ls -la && echo "Current directory: $(pwd)"']

  # Build the MCP server container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/devdocs-mcp-server:latest', '-f', 'DevDocs/docker/dockerfiles/Dockerfile.mcp.web', '.']

  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/devdocs-mcp-server:latest']

  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'devdocs-mcp-server'
      - '--image=gcr.io/$PROJECT_ID/devdocs-mcp-server:latest'
      - '--region=me-west1'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--set-env-vars=GOOGLE_CLOUD_PROJECT_ID=$PROJECT_ID'

# Store images in Google Container Registry
images:
  - 'gcr.io/$PROJECT_ID/devdocs-mcp-server:latest'
```

### DevDocs/docker/dockerfiles/Dockerfile.mcp.web

This file should define the MCP server with web browsing capabilities:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Chrome for web browsing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    gnupg \
    ca-certificates \
    apt-transport-https \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CHROME_BIN=/usr/bin/google-chrome

# Copy MCP server code
COPY DevDocs/fast-markdown-mcp/ /app/
COPY DevDocs/mcp/ /app/mcp/
COPY DevDocs/mcp-integration/ /app/mcp-integration/

# Install Python dependencies
RUN pip install --no-cache-dir -e .
RUN pip install --no-cache-dir google-cloud-storage google-cloud-documentai requests beautifulsoup4 selenium webdriver-manager

# Install Node.js for web capabilities
RUN apt-get update && apt-get install -y nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js dependencies
WORKDIR /app/mcp-integration
RUN npm install axios cheerio puppeteer cors express

# Create necessary directories
WORKDIR /app
RUN mkdir -p /app/storage/markdown
RUN mkdir -p /app/public

# Copy web files to public directory
COPY DevDocs/app/page.tsx /app/public/index.html
COPY DevDocs/components/ /app/public/components/

# Expose the port that the MCP server uses for communication
EXPOSE 8080

# Command to run the enhanced MCP server with web capabilities
CMD ["python", "-m", "fast_markdown_mcp.server", "/app/storage/markdown", "--web-enabled"]
```

## Step 6: Commit and Push Your Changes

1. Commit your changes to the repository:
   ```
   git add DevDocs/cloudbuild.mcp.yaml DevDocs/docker/dockerfiles/Dockerfile.mcp.web DevDocs/GITHUB_CLOUD_RUN_SETUP.md
   git commit -m "Set up continuous deployment for DevDocs MCP server"
   git push origin main
   ```

2. This should trigger a build in Cloud Build. You can monitor the build progress at:
   https://console.cloud.google.com/cloud-build/builds?project=github-456508

## Step 7: Verify the Deployment

1. Once the build is complete, go to the Cloud Run page:
   https://console.cloud.google.com/run?project=github-456508

2. Click on the `devdocs-mcp-server` service

3. You should see the URL of your deployed MCP server. Click on it to verify that it's running correctly.

## Step 8: Update the DevDocs Application to Use the Deployed MCP Server

1. Update the MCP server URL in your DevDocs application:
   - Open `DevDocs/mcp/gcp-mcp-config.json`
   - Update the MCP server URL to point to your deployed MCP server

2. Commit and push your changes:
   ```
   git add DevDocs/mcp/gcp-mcp-config.json
   git commit -m "Update MCP server URL"
   git push origin main
   ```

3. This should trigger a build of the DevDocs application.

## Step 9: Test the Integration

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
