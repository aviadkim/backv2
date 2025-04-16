/**
 * Utility functions for working with OpenRouter API
 */
import configManager from '../config/configManager';

/**
 * Get the OpenRouter API key
 * @returns {Promise<string>} The API key
 */
export async function getOpenRouterApiKey() {
  return await configManager.getConfig('OPENROUTER_API_KEY');
}

/**
 * Make a request to the OpenRouter API
 * @param {Object} options - Request options
 * @param {string} options.model - The model to use (e.g., 'openrouter/optimus-alpha')
 * @param {Array} options.messages - The messages to send
 * @param {Object} options.params - Additional parameters for the request
 * @returns {Promise<Object>} The response from the API
 */
export async function callOpenRouter({ model, messages, params = {} }) {
  const apiKey = await getOpenRouterApiKey();
  
  if (!apiKey) {
    throw new Error('OpenRouter API key is not configured');
  }
  
  const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
      'HTTP-Referer': typeof window !== 'undefined' ? window.location.origin : 'https://backv2.com',
      'X-Title': 'FinDoc Analyzer'
    },
    body: JSON.stringify({
      model,
      messages,
      ...params
    })
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || `OpenRouter API request failed with status ${response.status}`);
  }
  
  return await response.json();
}

/**
 * Call the Optimus Alpha model
 * @param {Array} messages - The messages to send
 * @param {Object} params - Additional parameters for the request
 * @returns {Promise<Object>} The response from the API
 */
export async function callOptimusAlpha(messages, params = {}) {
  return callOpenRouter({
    model: 'openrouter/optimus-alpha',
    messages,
    params
  });
}

/**
 * Check if the OpenRouter API key is configured
 * @returns {Promise<boolean>} Whether the API key is configured
 */
export async function isOpenRouterConfigured() {
  const apiKey = await getOpenRouterApiKey();
  return !!apiKey;
}
