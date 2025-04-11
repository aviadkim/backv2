/**
 * Prepare Vercel Deployment
 * This script helps prepare the project for Vercel deployment
 */

const fs = require('fs');
const path = require('path');
const { vercelProvider } = require('../mcp/vercel-mcp');

// Get the root directory of the project
const rootDir = path.resolve(__dirname, '../../');
const devDocsDir = path.resolve(rootDir, 'DevDocs');

// Generate vercel.json
const vercelConfig = vercelProvider.getDeploymentConfig();
fs.writeFileSync(
  path.resolve(rootDir, 'vercel.json'),
  JSON.stringify(vercelConfig, null, 2),
  'utf8'
);
console.log('✅ Generated vercel.json');

// Create a next.config.js file if it doesn't exist
const nextConfigPath = path.resolve(devDocsDir, 'next.config.js');
if (!fs.existsSync(nextConfigPath)) {
  const nextConfig = `
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  },
}

module.exports = nextConfig
`;
  fs.writeFileSync(nextConfigPath, nextConfig, 'utf8');
  console.log('✅ Created next.config.js');
}

// Create a .env.example file
const envExamplePath = path.resolve(rootDir, '.env.example');
const envExample = `# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# API Configuration
NEXT_PUBLIC_API_URL=/api

# OpenRouter API (for AI agents)
OPENROUTER_API_KEY=your-openrouter-api-key

# OpenAI API (for document processing)
OPENAI_API_KEY=your-openai-api-key

# Google ADK Configuration (optional)
GOOGLE_API_KEY=your-google-api-key
`;
fs.writeFileSync(envExamplePath, envExample, 'utf8');
console.log('✅ Created .env.example');

// Print required environment variables
console.log('\n🔑 Required Environment Variables for Vercel:');
vercelProvider.getRequiredEnvironmentVariables().forEach(variable => {
  console.log(`- ${variable}`);
});

console.log('\n📂 Root Directory for Vercel: ', vercelProvider.getRootDirectory());
console.log('\n🚀 Project is ready for Vercel deployment!');
