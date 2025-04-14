import configManager from './configManager';
import getSupabaseClient from './supabaseClient';
import createGoogleCloudClient from './googleCloudClient';

/**
 * API handler for checking the status of all configurations
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
    // Get all configurations
    const config = await configManager.readConfig();

    // Check Supabase connection
    let supabaseStatus = 'missing';
    if (config.NEXT_PUBLIC_SUPABASE_URL && config.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
      try {
        const supabase = getSupabaseClient();
        if (supabase) {
          const { data, error } = await supabase.from('documents').select('count').limit(1);
          supabaseStatus = error ? 'invalid' : 'valid';
        } else {
          supabaseStatus = 'invalid';
        }
      } catch (error) {
        console.error('Error checking Supabase connection:', error);
        supabaseStatus = 'invalid';
      }
    }

    // Check Google Cloud connection
    let googleCloudStatus = 'missing';
    if (config.NEXT_PUBLIC_GOOGLE_CLOUD_API_KEY) {
      try {
        const googleCloudClient = createGoogleCloudClient();
        googleCloudStatus = googleCloudClient ? 'valid' : 'invalid';
      } catch (error) {
        console.error('Error checking Google Cloud connection:', error);
        googleCloudStatus = 'invalid';
      }
    }

    // Check OCR API status
    let ocrStatus = 'missing';
    if (config.NEXT_PUBLIC_VISION_API_ENABLED === 'true' && config.NEXT_PUBLIC_GOOGLE_CLOUD_API_KEY) {
      ocrStatus = 'valid';
    }

    // Check Chatbot API status
    let chatbotStatus = 'missing';
    if (config.NEXT_PUBLIC_CHATBOT_ENABLED === 'true' && config.NEXT_PUBLIC_GOOGLE_CLOUD_API_KEY) {
      chatbotStatus = 'valid';
    }

    return res.status(200).json({
      success: true,
      supabase: supabaseStatus,
      googleCloud: googleCloudStatus,
      ocr: ocrStatus,
      chatbot: chatbotStatus
    });
  } catch (error) {
    console.error('Error checking configuration status:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Failed to check configuration status'
    });
  }
}
