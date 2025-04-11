# Deploying from GitHub to Vercel

This guide will walk you through the process of deploying your application from GitHub to Vercel.

## Prerequisites

1. A GitHub account with your repository (backv2) pushed and up to date
2. A Vercel account (you can sign up at https://vercel.com)

## Step 1: Connect Vercel to GitHub

1. Go to the Vercel dashboard (https://vercel.com/dashboard)
2. Click on "Add New" > "Project"
3. Select the "Import Git Repository" option
4. Connect your GitHub account if you haven't already
5. Select your repository (backv2)

## Step 2: Configure Project Settings

When configuring your project, use these settings:

- **Framework Preset**: Next.js
- **Root Directory**: DevDocs
- **Build Command**: npm install && npm run build
- **Output Directory**: .next

## Step 3: Environment Variables

The basic environment variables are already set in your `vercel.json` file, but you may need to add the Supabase service role key:

- **SUPABASE_SERVICE_ROLE_KEY**: (Get this from your Supabase dashboard)

## Step 4: Deploy

Click the "Deploy" button to start the deployment process. Vercel will:

1. Clone your repository
2. Install dependencies
3. Build your application
4. Deploy it to their global CDN

## Step 5: Check Deployment

Once the deployment is complete, Vercel will provide you with a URL where your application is hosted. Click on it to verify that your application is working correctly.

## Troubleshooting

If you encounter any issues during deployment, check the build logs in the Vercel dashboard for error messages. Common issues include:

1. **Missing dependencies**: Make sure all dependencies are listed in your package.json file
2. **Build errors**: Check for any errors in your code that might prevent the build from completing
3. **Environment variables**: Ensure all required environment variables are set correctly

## Automatic Deployments

With the GitHub integration, Vercel will automatically deploy your application whenever you push changes to your repository. This ensures that your deployed application is always up to date with your latest code.

## Custom Domains

If you want to use a custom domain for your application:

1. Go to your project in the Vercel dashboard
2. Click on "Settings" > "Domains"
3. Add your domain and follow the instructions to configure DNS settings

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [Supabase Documentation](https://supabase.io/docs)
