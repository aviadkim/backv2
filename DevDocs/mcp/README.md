# MCP for Vercel and Supabase

This directory contains the Model-Controller-Provider (MCP) pattern implementation for Vercel deployment and Supabase integration.

## What is MCP?

MCP is a design pattern that separates concerns:

- **Model**: Data structures and configuration
- **Controller**: Business logic and operations
- **Provider**: Interface for external systems

## Files

- `vercel-mcp.js`: Configuration and utilities for Vercel deployment
- `supabase-mcp.js`: Configuration and utilities for Supabase integration
- `index.js`: Entry point that exports all providers

## Usage

```javascript
// Import the MCP system
const mcp = require('./mcp');

// Get Vercel deployment configuration
const vercelConfig = mcp.vercel.getDeploymentConfig();

// Get Supabase client configuration
const supabaseConfig = mcp.supabase.getClientConfig();
```

## Vercel Deployment

For Vercel deployment, make sure to:

1. Set the root directory to `DevDocs`
2. Use the build command: `npm install && npm run build`
3. Set the output directory to `.next`
4. Add all required environment variables

## Environment Variables

Required environment variables:

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `OPENAI_API_KEY` (if using OpenAI)
- `OPENROUTER_API_KEY` (if using OpenRouter)
- `GOOGLE_API_KEY` (if using Google services)
