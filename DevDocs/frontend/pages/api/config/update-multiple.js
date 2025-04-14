import configManager from './configManager';

/**
 * API handler for updating multiple configuration values
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
    const { updates } = req.body;

    if (!updates || typeof updates !== 'object') {
      return res.status(400).json({
        success: false,
        error: 'Missing or invalid required parameter: updates'
      });
    }

    // Validate the keys to prevent security issues
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

    const invalidKeys = Object.keys(updates).filter(key => !allowedKeys.includes(key));
    if (invalidKeys.length > 0) {
      return res.status(400).json({
        success: false,
        error: `Invalid configuration keys: ${invalidKeys.join(', ')}`
      });
    }

    // Update the configurations
    await configManager.updateMultipleConfig(updates);

    return res.status(200).json({
      success: true,
      message: `Configurations updated successfully`
    });
  } catch (error) {
    console.error('Error updating configurations:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Failed to update configurations'
    });
  }
}
