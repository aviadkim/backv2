# Supabase Setup Guide

This guide will help you set up and troubleshoot your Supabase connection for the DevDocs application.

## Common Issues

If you're seeing errors like:

```
Error fetching documents from Supabase: {message: 'Invalid API key', hint: 'Double check your Supabase `anon` or `service_role` API key.'}
```

Or:

```
GET https://dnjnsotemnfrjlotgved.supabase.co/rest/v1/documents?select=*&order=created_at.desc 401 (Unauthorized)
```

Follow the steps below to fix them.

## Setup Steps

### 1. Create or Update Environment Variables

Create a `.env.local` file in the `DevDocs/frontend` directory with the following content:

```
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://dnjnsotemnfrjlotgved.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:24125
```

Replace `your_anon_key_here` with your actual Supabase anon key.

### 2. Get Your Supabase API Keys

1. Log in to your Supabase dashboard at [https://app.supabase.io](https://app.supabase.io)
2. Select your project
3. Go to Project Settings > API
4. Copy the `anon` public key (not the service_role key)
5. Paste it in your `.env.local` file

### 3. Test Your Connection

Run the test script to verify your connection:

```bash
cd DevDocs/scripts
node test-supabase-connection.js
```

Or visit the test page in your browser:

```
http://localhost:3002/test-supabase
```

### 4. Restart Your Development Server

After updating your environment variables, restart your development server:

```bash
cd DevDocs/frontend
npm run dev
```

## Troubleshooting

### Tables Don't Exist

If you're getting errors about tables not existing, you may need to create the required tables in your Supabase database:

1. Go to your Supabase dashboard
2. Select your project
3. Go to the SQL Editor
4. Run the following SQL to create the documents table:

```sql
CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  file_path TEXT,
  file_name TEXT,
  file_type TEXT,
  file_size BIGINT,
  content TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  tags TEXT[] DEFAULT '{}'::text[],
  organization_id UUID,
  created_by UUID,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create storage bucket for documents if it doesn't exist
INSERT INTO storage.buckets (id, name, public)
VALUES ('documents', 'documents', true)
ON CONFLICT (id) DO NOTHING;

-- Set up Row Level Security (RLS) policies
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all users to view documents
CREATE POLICY "Allow all users to view documents"
  ON documents
  FOR SELECT
  USING (true);

-- Create policy to allow authenticated users to insert documents
CREATE POLICY "Allow authenticated users to insert documents"
  ON documents
  FOR INSERT
  WITH CHECK (auth.role() = 'authenticated');

-- Create policy to allow users to update their own documents
CREATE POLICY "Allow users to update their own documents"
  ON documents
  FOR UPDATE
  USING (auth.uid() = created_by);

-- Create policy to allow users to delete their own documents
CREATE POLICY "Allow users to delete their own documents"
  ON documents
  FOR DELETE
  USING (auth.uid() = created_by);
```

### CORS Issues

If you're experiencing CORS issues, make sure your Supabase project has the correct CORS configuration:

1. Go to your Supabase dashboard
2. Select your project
3. Go to Project Settings > API
4. Under "CORS (Cross-Origin Resource Sharing)", add your application URL (e.g., `http://localhost:3002`)

### API Key Issues

If your API key is not working:

1. Make sure you're using the `anon` key, not the `service_role` key
2. Check if the key has expired (Supabase keys can expire)
3. Generate a new API key if necessary

## Need More Help?

If you're still experiencing issues, please contact the DevDocs team or refer to the [Supabase documentation](https://supabase.io/docs).
