/**
 * Vercel MCP - Model, Controller, Provider pattern for Vercel deployment
 * This file helps configure the Vercel deployment settings
 */

// Model - Configuration data
const vercelConfig = {
  version: 2,
  framework: 'nextjs',
  buildCommand: 'npm install && npm run build',
  outputDirectory: '.next',
  rootDirectory: 'DevDocs',
  environmentVariables: [
    'NEXT_PUBLIC_SUPABASE_URL',
    'NEXT_PUBLIC_SUPABASE_ANON_KEY',
    'SUPABASE_SERVICE_ROLE_KEY',
    'OPENAI_API_KEY',
    'OPENROUTER_API_KEY',
    'GOOGLE_API_KEY'
  ]
};

// Controller - Functions to manage deployment
const vercelController = {
  getConfig() {
    return vercelConfig;
  },
  
  validateConfig() {
    // Check if all required fields are present
    const requiredFields = ['version', 'framework', 'buildCommand', 'outputDirectory'];
    const missingFields = requiredFields.filter(field => !vercelConfig[field]);
    
    if (missingFields.length > 0) {
      throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
    }
    
    return true;
  },
  
  generateVercelJson() {
    // Generate vercel.json content
    return {
      version: vercelConfig.version,
      framework: vercelConfig.framework,
      buildCommand: vercelConfig.buildCommand,
      outputDirectory: vercelConfig.outputDirectory,
      rewrites: [
        {
          source: '/api/:path*',
          destination: '/api/:path*'
        }
      ],
      functions: {
        'api/**/*.js': {
          memory: 1024,
          maxDuration: 10
        }
      },
      env: {
        NEXT_PUBLIC_API_URL: '/api'
      }
    };
  }
};

// Provider - Interface for external systems
const vercelProvider = {
  getDeploymentConfig() {
    vercelController.validateConfig();
    return vercelController.generateVercelJson();
  },
  
  getRequiredEnvironmentVariables() {
    return vercelConfig.environmentVariables;
  },
  
  getRootDirectory() {
    return vercelConfig.rootDirectory;
  }
};

module.exports = {
  vercelConfig,
  vercelController,
  vercelProvider
};
