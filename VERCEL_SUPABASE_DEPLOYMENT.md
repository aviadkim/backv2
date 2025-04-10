# Vercel and Supabase Deployment Guide

This guide provides step-by-step instructions for deploying the FinDoc application to Vercel with Supabase as the database and storage solution.

## Prerequisites

- A GitHub account with your repository pushed
- A Vercel account (https://vercel.com)
- A Supabase account (https://supabase.com)

## 1. Set Up Supabase Project

### Create a New Supabase Project

1. Go to [Supabase Dashboard](https://app.supabase.io/)
2. Click "New Project"
3. Enter project details:
   - **Name**: FinDoc
   - **Database Password**: Create a strong password
   - **Region**: Choose the region closest to your users (e.g., eu-central-1)
   - **Pricing Plan**: Start with Free tier

### Set Up Database Schema

1. Go to the SQL Editor in your Supabase dashboard
2. Click "New Query"
3. Copy and paste the contents of `supabase/schema.sql` from this repository
4. Click "Run" to execute the SQL script

### Configure Authentication

1. Go to Authentication → Settings
2. Configure Site URL: Set to your application URL (e.g., https://findoc.vercel.app)
3. Enable the following providers:
   - Email (enabled by default)
   - Set minimum password length to 8
   - Enable "Confirm email" option

### Create Storage Buckets

1. Go to Storage in your Supabase dashboard
2. Create a new bucket named "documents"
3. Set the bucket to public (for this example) or private (for more security)
4. Configure CORS if needed

### Get API Keys

1. Go to Project Settings → API
2. Copy the following values:
   - **Project URL**: Your Supabase project URL
   - **anon public key**: Your anonymous API key
   - **service_role key**: Your service role key (keep this secure)

## 2. Deploy to Vercel

### Connect Your Repository

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Next.js
   - **Root Directory**: Leave empty (uses the vercel.json configuration)
   - **Build Command**: This will be taken from vercel.json
   - **Output Directory**: This will be taken from vercel.json

### Set Environment Variables

Add the following environment variables in the Vercel project settings:

1. `NEXT_PUBLIC_SUPABASE_URL`: Your Supabase project URL
   - Value: `https://your-project-id.supabase.co`

2. `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Your Supabase anonymous key
   - Value: Your anon key from Supabase project settings

3. `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key
   - Value: Your service role key from Supabase project settings

4. `OPENAI_API_KEY`: Your OpenAI API key (if using OpenAI for document processing)
   - Value: Your OpenAI API key

### Deploy the Project

1. Click "Deploy"
2. Wait for the build and deployment to complete
3. Once deployed, Vercel will provide a URL for your application

## 3. Test the Deployment

1. Visit your deployed application URL
2. Test the following functionality:
   - User registration and login
   - Document upload
   - Document querying
   - API key management

## 4. Custom Domain (Optional)

1. Go to your Vercel project settings
2. Click on "Domains"
3. Add your custom domain
4. Follow the instructions to configure DNS settings

## 5. Monitoring and Logs

### Vercel Logs

1. Go to your Vercel project
2. Click on "Deployments"
3. Select the latest deployment
4. Click on "Functions" to see serverless function logs

### Supabase Logs

1. Go to your Supabase project
2. Click on "Database" → "Logs"
3. View SQL query logs and performance metrics

## 6. Scaling Considerations

### Supabase

- Monitor your database usage in the Supabase dashboard
- Upgrade to a paid plan when you exceed free tier limits
- Consider adding indexes for frequently queried columns

### Vercel

- Monitor function execution times and memory usage
- Adjust function configuration in vercel.json as needed
- Consider using Edge Functions for performance-critical routes

## Troubleshooting

### CORS Issues

If you encounter CORS issues:

1. Go to Supabase → Storage → CORS
2. Add your Vercel deployment URL to the allowed origins
3. Add `*` for development purposes (restrict this in production)

### Authentication Issues

If users cannot log in:

1. Check that Site URL in Supabase Auth settings matches your deployment URL
2. Verify that environment variables are correctly set in Vercel
3. Check browser console for any JavaScript errors

### Storage Issues

If file uploads fail:

1. Verify that the "documents" bucket exists in Supabase Storage
2. Check bucket permissions (public vs. private)
3. Verify that RLS policies are correctly configured

## Security Best Practices

1. **Never expose your service role key** in client-side code
2. Use Row Level Security (RLS) policies to restrict data access
3. Implement proper authentication checks in API routes
4. Consider encrypting sensitive data (like API keys) before storing
5. Regularly rotate API keys and monitor for suspicious activity

## Next Steps

1. Set up CI/CD with GitHub Actions
2. Implement automated testing
3. Configure monitoring and alerting
4. Set up backup and disaster recovery procedures
