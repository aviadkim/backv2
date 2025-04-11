# FinDoc Deployment Guide

This document provides instructions for deploying the FinDoc application to Vercel using GitHub integration.

## Repository Structure

The repository is structured as follows:

- `DevDocs/`: Contains the Next.js application
- `vercel.json`: Configuration file for Vercel deployment
- Other files and directories for development and testing

## Deployment Steps

1. **Push your changes to GitHub**:
   ```bash
   git add .
   git commit -m "Update for deployment"
   git push origin main
   ```

2. **Connect to Vercel**:
   - Go to [Vercel](https://vercel.com/dashboard)
   - Click "Add New" > "Project"
   - Select your GitHub repository (backv2)

3. **Configure Project Settings**:
   - Framework Preset: Next.js
   - Root Directory: DevDocs
   - Build Command: npm install && npm run build
   - Output Directory: .next

4. **Environment Variables**:
   The basic environment variables are already set in your `vercel.json` file, but you may need to add:
   - SUPABASE_SERVICE_ROLE_KEY: (Get this from your Supabase dashboard)

5. **Deploy**:
   - Click "Deploy"
   - Wait for the deployment to complete
   - Vercel will provide a URL for your deployed application

## Supabase Integration

The application uses Supabase for database and authentication. The connection details are:

- Supabase URL: https://dnjnsotemnfrjlotgved.supabase.co
- Supabase Anon Key: Already configured in vercel.json

## Troubleshooting

If you encounter issues during deployment:

1. Check the build logs in the Vercel dashboard
2. Verify that all environment variables are set correctly
3. Ensure the DevDocs directory contains a valid Next.js application
4. Check that the package.json file includes all necessary dependencies

## Updating the Deployment

After making changes to your code:

1. Push the changes to GitHub
2. Vercel will automatically detect the changes and redeploy your application

## Additional Resources

For more detailed information, refer to:
- [GITHUB_TO_VERCEL_DEPLOYMENT.md](./GITHUB_TO_VERCEL_DEPLOYMENT.md)
- [VERCEL_SUPABASE_DEPLOYMENT.md](./VERCEL_SUPABASE_DEPLOYMENT.md)
