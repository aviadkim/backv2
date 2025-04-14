import configManager from './configManager';

/**
 * API handler for getting configuration values
 * @param {import('next').NextApiRequest} req - The request object
 * @param {import('next').NextApiResponse} res - The response object
 */
export default async function handler(req, res) {
  // Only allow GET requests
  if (req.method !== 'GET') {
    return res.status(405).json({
      success: false,
      error: 'Method not allowed'
    });
  }

  try {
    const { key } = req.query;

    if (!key) {
      return res.status(400).json({
        success: false,
        error: 'Missing required parameter: key'
      });
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
      return res.status(400).json({
        success: false,
        error: `Invalid configuration key: ${key}`
      });
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

    return res.status(200).json({
      success: true,
      key,
      value: maskedValue,
      isSet: !!value
    });
  } catch (error) {
    console.error('Error getting configuration:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Failed to get configuration'
    });
  }
}
