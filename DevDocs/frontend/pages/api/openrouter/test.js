import { apiResponse, apiError, withErrorHandling } from '../lib/apiUtils';
import { callOptimusAlpha, isOpenRouterConfigured } from '../lib/openRouterUtils';

/**
 * API handler for testing the OpenRouter API
 */
const handler = async (req, res) => {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return apiError(res, 405, 'Method not allowed');
  }

  try {
    const { prompt } = req.body;

    if (!prompt) {
      return apiError(res, 400, 'Missing required parameter: prompt');
    }

    // Check if OpenRouter is configured
    const configured = await isOpenRouterConfigured();
    if (!configured) {
      return apiError(res, 400, 'OpenRouter API key is not configured');
    }

    // Call the Optimus Alpha model
    const result = await callOptimusAlpha([
      {
        role: 'user',
        content: prompt
      }
    ]);

    // Extract the response
    const response = result.choices[0]?.message?.content || '';

    return apiResponse(res, 200, {
      response,
      model: result.model
    });
  } catch (error) {
    console.error('Error testing OpenRouter:', error);
    return apiError(res, 500, 'Failed to test OpenRouter', error.message);
  }
};

export default withErrorHandling(handler);
