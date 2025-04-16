import configManager from './configManager';
import { apiResponse, apiError, withErrorHandling } from '../lib/apiUtils';

/**
 * API handler for setting the OpenRouter API key
 */
const handler = async (req, res) => {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return apiError(res, 405, 'Method not allowed');
  }

  try {
    const { key } = req.body;

    if (!key) {
      return apiError(res, 400, 'Missing required parameter: key');
    }

    // Validate the key format (OpenRouter keys start with sk-or-)
    if (!key.startsWith('sk-or-')) {
      return apiError(res, 400, 'Invalid OpenRouter API key format');
    }

    // Update the key in the database
    const success = await configManager.updateConfig('OPENROUTER_API_KEY', key);

    if (!success) {
      return apiError(res, 500, 'Failed to update OpenRouter API key');
    }

    return apiResponse(res, 200, {
      message: 'OpenRouter API key updated successfully'
    });
  } catch (error) {
    console.error('Error setting OpenRouter API key:', error);
    return apiError(res, 500, 'Failed to set OpenRouter API key', error.message);
  }
};

export default withErrorHandling(handler);
