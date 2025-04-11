# Google Cloud Deployment Guide for DevDocs

This guide provides step-by-step instructions for deploying the DevDocs application to Google Cloud Platform (GCP) using Cloud Run and integrating with Supabase.

## Prerequisites

1. A Google Cloud Platform account
2. A Supabase account and project
3. Google Cloud CLI installed locally
4. Git installed locally

## Step 1: Set Up Google Cloud Project

1. Create a new Google Cloud project (or use an existing one):
   ```bash
   gcloud projects create [PROJECT_ID] --name="DevDocs Project"
   ```

2. Set the current project:
   ```bash
   gcloud config set project [PROJECT_ID]
   ```

3. Enable required APIs:
   ```bash
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com secretmanager.googleapis.com containerregistry.googleapis.com
   ```

## Step 2: Set Up Secret Manager for API Keys

1. Create secrets for your API keys:
   ```bash
   # Create a secret for OpenRouter API key
   echo -n "your-openrouter-api-key" | gcloud secrets create OPENROUTER_API_KEY --data-file=-
   
   # Create a secret for Supabase URL
   echo -n "https://your-project-id.supabase.co" | gcloud secrets create SUPABASE_URL --data-file=-
   
   # Create a secret for Supabase key
   echo -n "your-supabase-key" | gcloud secrets create SUPABASE_KEY --data-file=-
   ```

2. Grant access to the Cloud Run service account:
   ```bash
   # Get the service account email
   SERVICE_ACCOUNT=$(gcloud iam service-accounts list --filter="displayName:Cloud Run Service Agent" --format="value(email)")
   
   # Grant access to secrets
   gcloud secrets add-iam-policy-binding OPENROUTER_API_KEY --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/secretmanager.secretAccessor"
   gcloud secrets add-iam-policy-binding SUPABASE_URL --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/secretmanager.secretAccessor"
   gcloud secrets add-iam-policy-binding SUPABASE_KEY --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/secretmanager.secretAccessor"
   ```

## Step 3: Set Up Continuous Deployment from GitHub

1. Connect your GitHub repository to Cloud Build:
   - Go to Cloud Build in the Google Cloud Console
   - Click "Triggers"
   - Click "Connect Repository"
   - Select GitHub as the source
   - Follow the prompts to authenticate and select your repository

2. Create a build trigger:
   - Name: "DevDocs Deployment"
   - Event: "Push to a branch"
   - Source: Your repository and branch (e.g., main)
   - Configuration: "Cloud Build configuration file (yaml or json)"
   - Location: "Repository"
   - Cloud Build configuration file location: "cloudbuild.yaml"

## Step 4: Manual Deployment (Alternative to GitHub Integration)

If you prefer to deploy manually or for the first deployment:

1. Clone your repository locally:
   ```bash
   git clone https://github.com/yourusername/backv2.git
   cd backv2/DevDocs
   ```

2. Build and deploy to Cloud Run:
   ```bash
   gcloud run deploy devdocs \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --update-secrets=OPENROUTER_API_KEY=OPENROUTER_API_KEY:latest,SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_KEY=SUPABASE_KEY:latest
   ```

## Step 5: Set Up Supabase Database

1. Create the necessary tables in your Supabase project:

   - Documents Table:
     ```sql
     CREATE TABLE documents (
       id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
       user_id TEXT NOT NULL,
       title TEXT NOT NULL,
       content TEXT,
       metadata JSONB,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
     );
     ```

   - API Keys Table:
     ```sql
     CREATE TABLE api_keys (
       id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
       user_id TEXT NOT NULL,
       service TEXT NOT NULL,
       api_key TEXT NOT NULL,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       UNIQUE(user_id, service)
     );
     ```

2. Set up Row Level Security (RLS) policies:
   ```sql
   -- Enable RLS on the tables
   ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
   ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
   
   -- Create policies for documents
   CREATE POLICY "Users can view their own documents" 
     ON documents FOR SELECT 
     USING (user_id = auth.uid());
   
   CREATE POLICY "Users can insert their own documents" 
     ON documents FOR INSERT 
     WITH CHECK (user_id = auth.uid());
   
   CREATE POLICY "Users can update their own documents" 
     ON documents FOR UPDATE 
     USING (user_id = auth.uid());
   
   -- Create policies for api_keys
   CREATE POLICY "Users can view their own API keys" 
     ON api_keys FOR SELECT 
     USING (user_id = auth.uid());
   
   CREATE POLICY "Users can insert their own API keys" 
     ON api_keys FOR INSERT 
     WITH CHECK (user_id = auth.uid());
   
   CREATE POLICY "Users can update their own API keys" 
     ON api_keys FOR UPDATE 
     USING (user_id = auth.uid());
   ```

## Step 6: Verify Deployment

1. After deployment, Cloud Run will provide a URL for your application (e.g., https://devdocs-abcdef123-uc.a.run.app)

2. Visit the URL to verify that your application is running correctly

3. Check the logs for any errors:
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=devdocs" --limit=10
   ```

## Troubleshooting

### Common Issues:

1. **Secret Access Issues**: Ensure the Cloud Run service account has access to the secrets.

2. **Build Failures**: Check the Cloud Build logs for details on why the build failed.

3. **Runtime Errors**: Check the Cloud Run logs for runtime errors.

4. **Database Connection Issues**: Verify that the Supabase URL and key are correct and that the service has network access to Supabase.

### Useful Commands:

- View logs:
  ```bash
  gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=devdocs" --limit=10
  ```

- Update secrets:
  ```bash
  gcloud run services update devdocs --update-secrets=OPENROUTER_API_KEY=OPENROUTER_API_KEY:latest
  ```

- Redeploy:
  ```bash
  gcloud run deploy devdocs --source .
  ```

## Best Practices

1. **Never commit API keys or secrets to your repository**. Always use Secret Manager.

2. **Use separate environments** (development, staging, production) with different secrets.

3. **Implement proper authentication** for your application.

4. **Set up monitoring and alerts** for your Cloud Run service.

5. **Regularly update dependencies** to keep your application secure.

## Additional Resources

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Google Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Supabase Documentation](https://supabase.io/docs)
- [Next.js on Cloud Run](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-nodejs-service)
