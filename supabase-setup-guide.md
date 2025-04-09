# Supabase Setup Guide for FinDoc

This guide walks through setting up a Supabase project for the FinDoc application.

## 1. Create a New Supabase Project

1. Go to [Supabase Dashboard](https://app.supabase.io/)
2. Click "New Project"
3. Enter project details:
   - **Name**: FinDoc
   - **Database Password**: Create a strong password
   - **Region**: Choose the region closest to your users (e.g., eu-central-1)
   - **Pricing Plan**: Start with Free tier

## 2. Set Up Database Schema

After your project is created, you'll need to set up the database schema:

1. Go to the SQL Editor in your Supabase dashboard
2. Click "New Query"
3. Copy and paste the contents of `supabase/schema.sql` from this repository
4. Click "Run" to execute the SQL script

## 3. Configure Authentication

1. Go to Authentication → Settings
2. Configure Site URL: Set to your application URL (e.g., https://findoc.vercel.app)
3. Enable the following providers:
   - Email (enabled by default)
   - Set minimum password length to 8
   - Enable "Confirm email" option

## 4. Create Storage Buckets

1. Go to Storage in your Supabase dashboard
2. Create the following buckets:
   - `documents`: For storing uploaded documents
   - `avatars`: For user profile pictures
   - `exports`: For exported reports and data

3. Set up bucket policies:
   - For `documents`:
     ```sql
     CREATE POLICY "Documents are accessible by organization members"
     ON storage.objects FOR SELECT
     USING (
       bucket_id = 'documents' AND
       (storage.foldername(name))[1] IN (
         SELECT organization_id::text FROM auth.users
         JOIN public.profiles ON auth.users.id = profiles.id
         WHERE auth.uid() = profiles.id
       )
     );
     
     CREATE POLICY "Documents can be inserted by organization members"
     ON storage.objects FOR INSERT
     WITH CHECK (
       bucket_id = 'documents' AND
       (storage.foldername(name))[1] IN (
         SELECT organization_id::text FROM auth.users
         JOIN public.profiles ON auth.users.id = profiles.id
         WHERE auth.uid() = profiles.id
       )
     );
     
     CREATE POLICY "Documents can be updated by organization members"
     ON storage.objects FOR UPDATE
     USING (
       bucket_id = 'documents' AND
       (storage.foldername(name))[1] IN (
         SELECT organization_id::text FROM auth.users
         JOIN public.profiles ON auth.users.id = profiles.id
         WHERE auth.uid() = profiles.id
       )
     );
     
     CREATE POLICY "Documents can be deleted by organization members"
     ON storage.objects FOR DELETE
     USING (
       bucket_id = 'documents' AND
       (storage.foldername(name))[1] IN (
         SELECT organization_id::text FROM auth.users
         JOIN public.profiles ON auth.users.id = profiles.id
         WHERE auth.uid() = profiles.id
       )
     );
     ```

   - Similar policies for `avatars` and `exports` buckets

## 5. Get API Keys

1. Go to Project Settings → API
2. Note down the following:
   - **Project URL**: Your Supabase project URL
   - **anon public key**: For client-side access
   - **service_role key**: For server-side access (keep this secret)

## 6. Update Environment Variables

Add these values to your environment variables:

```
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

## 7. Test Connection

Test your Supabase connection using the following code:

```javascript
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Test query
const { data, error } = await supabase.from('profiles').select('*').limit(1);
console.log('Connection test:', data, error);
```

## 8. Next Steps

After setting up Supabase:
1. Implement authentication in your application
2. Set up storage functionality
3. Create data access repositories
