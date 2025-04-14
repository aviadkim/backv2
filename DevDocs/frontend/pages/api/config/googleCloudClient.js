/**
 * Simplified Google Cloud Client for API routes
 */

/**
 * Create a Google Cloud client
 * @returns {Object} The Google Cloud client
 */
function createGoogleCloudClient() {
  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_CLOUD_API_KEY || '';
  
  if (!apiKey) {
    console.error('Google Cloud API key not available');
    return null;
  }
  
  return {
    apiKey,
    isVisionApiEnabled: process.env.NEXT_PUBLIC_VISION_API_ENABLED === 'true',
    isChatbotEnabled: process.env.NEXT_PUBLIC_CHATBOT_ENABLED === 'true'
  };
}

export default createGoogleCloudClient;
