/**
 * Example of how to use the API in a JavaScript script.
 */

// Import required modules
const fetch = require('node-fetch');
const readline = require('readline');

// Create readline interface for user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// API configuration
const API_HOST = 'localhost';
const API_PORT = 8000;
const API_URL = `http://${API_HOST}:${API_PORT}`;

// Get OpenRouter API key from environment variable or prompt user
const getApiKey = () => {
  return new Promise((resolve) => {
    const apiKey = process.env.OPENROUTER_API_KEY;
    if (apiKey) {
      resolve(apiKey);
    } else {
      rl.question('Enter your OpenRouter API key: ', (answer) => {
        resolve(answer);
      });
    }
  });
};

// Check API health
const checkApiHealth = async () => {
  try {
    console.log('Checking API health...');
    const response = await fetch(`${API_URL}/api/health`);
    if (!response.ok) {
      throw new Error(`API health check failed with status ${response.status}`);
    }
    const data = await response.json();
    console.log(`API health: ${JSON.stringify(data)}`);
    return true;
  } catch (error) {
    console.error(`Error checking API health: ${error.message}`);
    console.error('Make sure the API server is running.');
    return false;
  }
};

// Check OpenRouter API status
const checkOpenRouterStatus = async () => {
  try {
    console.log('\nChecking OpenRouter API status...');
    const response = await fetch(`${API_URL}/api/openrouter/status`);
    if (!response.ok) {
      throw new Error(`OpenRouter API status check failed with status ${response.status}`);
    }
    const data = await response.json();
    console.log(`OpenRouter API status: ${JSON.stringify(data)}`);
    return true;
  } catch (error) {
    console.error(`Error checking OpenRouter API status: ${error.message}`);
    return false;
  }
};

// Example of using the chat completion endpoint
const useChatCompletionEndpoint = async () => {
  try {
    console.log('\nExample of using the chat completion endpoint:');
    const data = {
      messages: [
        { role: 'system', content: 'You are a helpful assistant.' },
        { role: 'user', content: 'Tell me about financial document analysis.' }
      ],
      temperature: 0.7,
      max_tokens: 100
    };
    
    const response = await fetch(`${API_URL}/api/openrouter/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error(`Chat completion request failed with status ${response.status}`);
    }
    
    const result = await response.json();
    console.log('Response from Optimus Alpha:');
    console.log('-'.repeat(40));
    console.log(result.choices[0].message.content);
    console.log('-'.repeat(40));
    return true;
  } catch (error) {
    console.error(`Error using chat completion endpoint: ${error.message}`);
    return false;
  }
};

// Example of using the text completion endpoint
const useTextCompletionEndpoint = async () => {
  try {
    console.log('\nExample of using the text completion endpoint:');
    const data = {
      prompt: 'Explain how financial document analysis works in 3 sentences.',
      temperature: 0.7,
      max_tokens: 100
    };
    
    const response = await fetch(`${API_URL}/api/openrouter/completion`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error(`Text completion request failed with status ${response.status}`);
    }
    
    const result = await response.json();
    console.log('Response from Optimus Alpha:');
    console.log('-'.repeat(40));
    console.log(result.completion);
    console.log('-'.repeat(40));
    return true;
  } catch (error) {
    console.error(`Error using text completion endpoint: ${error.message}`);
    return false;
  }
};

// Main function
const main = async () => {
  try {
    // Get API key
    const apiKey = await getApiKey();
    process.env.OPENROUTER_API_KEY = apiKey;
    
    // Check API health
    const healthOk = await checkApiHealth();
    if (!healthOk) {
      return 1;
    }
    
    // Check OpenRouter API status
    const openRouterOk = await checkOpenRouterStatus();
    if (!openRouterOk) {
      return 1;
    }
    
    // Use chat completion endpoint
    const chatOk = await useChatCompletionEndpoint();
    if (!chatOk) {
      return 1;
    }
    
    // Use text completion endpoint
    const textOk = await useTextCompletionEndpoint();
    if (!textOk) {
      return 1;
    }
    
    console.log('\nAPI usage examples completed successfully!');
    rl.close();
    return 0;
  } catch (error) {
    console.error(`Error in main function: ${error.message}`);
    rl.close();
    return 1;
  }
};

// Run the main function
main().then((exitCode) => {
  process.exit(exitCode);
});
