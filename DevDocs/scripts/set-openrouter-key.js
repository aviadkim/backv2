#!/usr/bin/env node

/**
 * Script to set the OpenRouter API key in Supabase
 * 
 * Usage:
 * node set-openrouter-key.js <api-key>
 */

const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '../frontend/.env.local' });

// Get the API key from command line arguments
const apiKey = process.argv[2];

if (!apiKey) {
  console.error('Error: API key is required');
  console.log('Usage: node set-openrouter-key.js <api-key>');
  process.exit(1);
}

// Validate the API key format
if (!apiKey.startsWith('sk-or-')) {
  console.error('Error: Invalid OpenRouter API key format. Keys should start with "sk-or-"');
  process.exit(1);
}

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

async function setOpenRouterApiKey() {
  try {
    console.log('Connecting to Supabase...');
    
    // Check if the key already exists
    const { data: existingKey, error: fetchError } = await supabase
      .from('api_keys')
      .select('id')
      .eq('name', 'OPENROUTER_API_KEY')
      .single();
    
    if (fetchError && fetchError.code !== 'PGRST116') { // PGRST116 is the error code for no rows returned
      throw fetchError;
    }
    
    if (existingKey) {
      // Update existing key
      console.log('Updating existing OpenRouter API key...');
      const { error } = await supabase
        .from('api_keys')
        .update({ 
          value: apiKey, 
          updated_at: new Date().toISOString() 
        })
        .eq('id', existingKey.id);
      
      if (error) throw error;
      console.log('OpenRouter API key updated successfully');
    } else {
      // Insert new key
      console.log('Creating new OpenRouter API key entry...');
      const { error } = await supabase
        .from('api_keys')
        .insert({
          name: 'OPENROUTER_API_KEY',
          value: apiKey,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        });
      
      if (error) throw error;
      console.log('OpenRouter API key created successfully');
    }
    
    // Mask the key for display
    const maskedKey = `${apiKey.substring(0, 8)}...${apiKey.substring(apiKey.length - 4)}`;
    console.log(`API key ${maskedKey} has been set in Supabase`);
    
  } catch (error) {
    console.error('Error setting OpenRouter API key:', error);
    process.exit(1);
  }
}

// Run the function
setOpenRouterApiKey();
