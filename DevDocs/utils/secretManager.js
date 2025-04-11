// This file is for server-side use only
// It demonstrates how to access secrets from Google Cloud Secret Manager
// In a Cloud Run environment, secrets will be automatically injected as environment variables

/**
 * Gets a secret from environment variables
 * In Cloud Run, secrets from Secret Manager are automatically injected as environment variables
 * when configured in the deployment
 * 
 * @param {string} secretName - The name of the secret
 * @returns {string|null} - The secret value or null if not found
 */
export function getSecret(secretName) {
  const secretValue = process.env[secretName];
  
  if (!secretValue) {
    console.warn(`Secret ${secretName} not found in environment variables`);
    return null;
  }
  
  return secretValue;
}

/**
 * Example of how to use the getSecret function
 * This would be called from your API routes or server-side code
 */
export function getOpenRouterApiKey() {
  return getSecret('OPENROUTER_API_KEY');
}

export function getSupabaseCredentials() {
  return {
    url: getSecret('SUPABASE_URL'),
    key: getSecret('SUPABASE_KEY')
  };
}

// For local development, you can load secrets from a .env file
// But for production in Cloud Run, they will come from Secret Manager
if (process.env.NODE_ENV !== 'production') {
  console.log('Running in development mode - secrets should be in .env file');
} else {
  console.log('Running in production mode - secrets should be injected from Secret Manager');
}
