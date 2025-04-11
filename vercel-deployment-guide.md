# Vercel Deployment Guide for FinDoc

This guide walks through the process of deploying the FinDoc application to Vercel.

## Prerequisites

1. A GitHub account with the FinDoc repository
2. A Vercel account (can sign up with GitHub)
3. A Supabase project already set up

## Step 1: Connect to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New" > "Project"
3. Import your GitHub repository (authorize Vercel if needed)
4. Find and select the `aviadkim/backv2` repository

## Step 2: Configure Project

1. **Framework Preset**: Select "Next.js"
2. **Root Directory**: Leave empty (uses the vercel.json configuration)
3. **Build Command**: This will be taken from vercel.json
4. **Output Directory**: This will be taken from vercel.json

## Step 3: Environment Variables

Add the following environment variables:

1. `NEXT_PUBLIC_SUPABASE_URL`: Your Supabase project URL
   - Value: `https://your-project-id.supabase.co`

2. `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Your Supabase anonymous key
   - Value: Your anon key from Supabase project settings

3. `NEXT_PUBLIC_API_URL`: Your API URL
   - For production: `https://findoc-api.vercel.app/api`
   - For preview deployments: `https://findoc-api-git-${VERCEL_GIT_COMMIT_REF}.vercel.app/api`

## Step 4: Deploy

1. Click "Deploy"
2. Wait for the build and deployment to complete
3. Once deployed, Vercel will provide a URL to access your application

## Step 5: Custom Domain (Optional)

1. Go to the project settings in Vercel
2. Navigate to "Domains"
3. Add your custom domain (e.g., findoc.com)
4. Follow the instructions to configure DNS settings

## Step 6: Continuous Deployment

Vercel automatically sets up continuous deployment:

1. Every push to the main branch will trigger a production deployment
2. Every pull request will create a preview deployment
3. Preview deployments allow you to test changes before merging

## Troubleshooting

### Build Failures

If your build fails, check:

1. The build logs in Vercel for specific errors
2. Ensure all environment variables are correctly set
3. Verify that your code builds locally with `npm run build`

### API Connection Issues

If the frontend can't connect to the backend:

1. Check that the `NEXT_PUBLIC_API_URL` is correct
2. Ensure the backend is deployed and accessible
3. Verify CORS settings on the backend allow requests from your Vercel domain

### Supabase Connection Issues

If you can't connect to Supabase:

1. Verify the `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` are correct
2. Check Supabase dashboard for any service disruptions
3. Ensure your Supabase project has the correct security settings
