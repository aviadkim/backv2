#!/usr/bin/env node

/**
 * Test Google Cloud Connection
 * 
 * This script tests the connection to Google Cloud and verifies that
 * the API key is correctly configured.
 */

const fs = require('fs');
const path = require('path');
const chalk = require('chalk');
const axios = require('axios');

// Load environment variables
function loadEnv() {
  try {
    const envPath = path.join(__dirname, '../frontend/.env.local');
    if (fs.existsSync(envPath)) {
      const envContent = fs.readFileSync(envPath, 'utf8');
      const envVars = {};
      
      envContent.split('\n').forEach(line => {
        if (line && !line.startsWith('#')) {
          const [key, ...valueParts] = line.split('=');
          if (key && valueParts.length > 0) {
            envVars[key.trim()] = valueParts.join('=').trim();
          }
        }
      });
      
      return envVars;
    }
  } catch (error) {
    console.error(chalk.red('Error loading environment variables:'), error);
  }
  
  return {};
}

// Test Google Cloud connection
async function testGoogleCloudConnection() {
  console.log(chalk.blue('Testing Google Cloud Connection'));
  console.log(chalk.blue('==============================\n'));
  
  // Load environment variables
  const env = loadEnv();
  
  // Check if Google Cloud API key is set
  const apiKey = env.NEXT_PUBLIC_GOOGLE_CLOUD_API_KEY;
  
  if (!apiKey) {
    console.log(chalk.red('❌ Google Cloud API key is not set'));
    console.log(chalk.yellow('Please set NEXT_PUBLIC_GOOGLE_CLOUD_API_KEY in .env.local'));
    process.exit(1);
  }
  
  console.log(chalk.green('✓ Google Cloud API key is set'));
  
  // Test connection by making a simple API call
  try {
    // Use a simple API call to test the key (e.g., Cloud Translation API)
    const response = await axios.post(
      `https://translation.googleapis.com/language/translate/v2?key=${apiKey}`,
      {
        q: 'Hello, world!',
        target: 'es'
      }
    );
    
    if (response.data && response.data.data && response.data.data.translations) {
      console.log(chalk.green('✓ Successfully connected to Google Cloud'));
      console.log(chalk.green(`Translation: ${response.data.data.translations[0].translatedText}`));
      process.exit(0);
    } else {
      console.log(chalk.red('❌ Failed to connect to Google Cloud'));
      console.log(chalk.red('Invalid response from API'));
      process.exit(1);
    }
  } catch (error) {
    console.log(chalk.red('❌ Failed to connect to Google Cloud'));
    
    if (error.response && error.response.data && error.response.data.error) {
      console.log(chalk.red(`Error: ${error.response.data.error.message}`));
    } else {
      console.log(chalk.red(`Error: ${error.message}`));
    }
    
    process.exit(1);
  }
}

// Run the test
testGoogleCloudConnection();
