import configManager from './configManager';

/**
 * API handler for updating configuration values
 * @param {import('next').NextApiRequest} req - The request object
 * @param {import('next').NextApiResponse} res - The response object
 */
export default async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({
      success: false,
      error: 'Method not allowed'
    });
  }

  try {
    const { key, value } = req.body;

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
      'GOOGLE_APPLICATION_CREDENTIALS',
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

    // Update the configuration
    await configManager.updateConfig(key, value);

    return res.status(200).json({
      success: true,
      message: `Configuration ${key} updated successfully`
    });
  } catch (error) {
    console.error('Error updating configuration:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Failed to update configuration'
    });
  }
}
