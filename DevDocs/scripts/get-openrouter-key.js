#!/usr/bin/env node

/**
 * Script to get the OpenRouter API key from Supabase
 * 
 * Usage:
 * node get-openrouter-key.js
 */

const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '../frontend/.env.local' });

// Get Supabase credentials from environment variables
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseServiceKey) {
  console.error('Error: Supabase credentials not found in environment variables');
  console.log('Make sure NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set in .env.local');
  process.exit(1);
}

// Initialize Supabase client
const supabase = createClient(supabaseUrl, supabaseServiceKey, {
  auth: {
    persistSession: false,
  }
});

async function getOpenRouterApiKey() {
  try {
    console.log('Connecting to Supabase...');
    
    // Get the API key
    const { data, error } = await supabase
      .from('api_keys')
      .select('value, updated_at')
      .eq('name', 'OPENROUTER_API_KEY')
      .single();
    
    if (error) {
      if (error.code === 'PGRST116') { // No rows returned
        console.log('OpenRouter API key is not set');
        return;
      }
      throw error;
    }
    
    if (data) {
      // Mask the key for display
      const apiKey = data.value;
      const maskedKey = `${apiKey.substring(0, 8)}...${apiKey.substring(apiKey.length - 4)}`;
      const updatedAt = new Date(data.updated_at).toLocaleString();
      
      console.log('OpenRouter API key is set');
      console.log(`Key: ${maskedKey}`);
      console.log(`Last updated: ${updatedAt}`);
    } else {
      console.log('OpenRouter API key is not set');
    }
    
  } catch (error) {
    console.error('Error getting OpenRouter API key:', error);
    process.exit(1);
  }
}

// Run the function
getOpenRouterApiKey();
