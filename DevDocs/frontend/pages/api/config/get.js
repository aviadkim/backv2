import configManager from './configManager';
import { apiResponse, apiError, withErrorHandling } from '../lib/apiUtils';

/**
 * API handler for getting configuration values
 */
const handler = async (req, res) => {
  if (req.method !== 'GET') {
    return apiError(res, 405, 'Method not allowed');
  }

  try {
    const { key } = req.query;

    if (!key) {
      return apiError(res, 400, 'Missing required parameter: key');
    }

    // Validate the key to prevent security issues
    const allowedKeys = [
      'NEXT_PUBLIC_SUPABASE_URL',
      'NEXT_PUBLIC_SUPABASE_ANON_KEY',
      'NEXT_PUBLIC_API_URL',
      'NEXT_PUBLIC_GOOGLE_CLOUD_API_KEY',
      'NEXT_PUBLIC_VISION_API_ENABLED',
      'NEXT_PUBLIC_CHATBOT_ENABLED',
      'NEXT_PUBLIC_DIALOGFLOW_AGENT_ID'
    ];

    if (!allowedKeys.includes(key)) {
      return apiError(res, 400, `Invalid configuration key: ${key}`);
    }

    // Get the configuration value
    const value = await configManager.getConfig(key);

    // For security reasons, mask sensitive values
    const sensitiveKeys = [
      'NEXT_PUBLIC_SUPABASE_ANON_KEY',
      'NEXT_PUBLIC_GOOGLE_CLOUD_API_KEY'
    ];

    const maskedValue = sensitiveKeys.includes(key) && value
      ? `${value.substring(0, 5)}...${value.substring(value.length - 5)}`
      : value;

    return apiResponse(res, 200, {
      key,
      value: maskedValue,
      isSet: !!value
    });
  } catch (error) {
    console.error('Error getting configuration:', error);
    return apiError(res, 500, 'Failed to get configuration', error.message);
  }
};

export default withErrorHandling(handler);
