import configManager from './configManager';
import { apiResponse, apiError, withErrorHandling } from '../lib/apiUtils';

/**
 * API handler for getting the OpenRouter API key status
 */
const handler = async (req, res) => {
  // Only allow GET requests
  if (req.method !== 'GET') {
    return apiError(res, 405, 'Method not allowed');
  }

  try {
    // Get the OpenRouter API key
    const key = await configManager.getConfig('OPENROUTER_API_KEY');

    // Return the status
    return apiResponse(res, 200, {
      isSet: !!key,
      // If the key exists, return a masked version for display
      maskedKey: key ? `${key.substring(0, 8)}...${key.substring(key.length - 4)}` : null
    });
  } catch (error) {
    console.error('Error getting OpenRouter API key status:', error);
    return apiError(res, 500, 'Failed to get OpenRouter API key status', error.message);
  }
};

export default withErrorHandling(handler);
