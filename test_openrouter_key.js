/**
 * Test script for OpenRouter API key
 */

const axios = require('axios');

// Use the OpenRouter API key from environment variable
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || 'sk-or-v1-64e1068c3a61a5e4be88c64c6992b39dbc15ad687201cb3fd05a98a9ba1e22dc8';

async function testOpenRouterAPI() {
  try {
    console.log('Testing OpenRouter API key...');
    
    const response = await axios.post(
      'https://openrouter.ai/api/v1/chat/completions',
      {
        model: 'anthropic/claude-3-opus-20240229',
        messages: [
          { role: 'user', content: 'Hello, can you confirm this API key is working?' }
        ],
        max_tokens: 100
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
          'HTTP-Referer': 'https://github.com/aviadkim/backv2',
          'X-Title': 'FinDoc API Key Test'
        }
      }
    );
    
    console.log('API Response Status:', response.status);
    console.log('API Response:', response.data.choices[0].message.content);
    console.log('✅ OpenRouter API key is working!');
    return true;
  } catch (error) {
    console.error('❌ Error testing OpenRouter API key:');
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Data:', error.response.data);
    } else {
      console.error(error.message);
    }
    return false;
  }
}

// Run the test
testOpenRouterAPI();
