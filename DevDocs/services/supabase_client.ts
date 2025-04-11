import { createClient } from '@supabase/supabase-js';

// Initialize the Supabase client with environment variables
// These will be set from Google Cloud Secret Manager
const supabaseUrl = process.env.SUPABASE_URL || '';
const supabaseKey = process.env.SUPABASE_KEY || '';

if (!supabaseUrl || !supabaseKey) {
  console.warn('Supabase credentials not found in environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseKey);

// Helper functions for common database operations
export async function storeDocument(userId: string, documentData: any) {
  const { data, error } = await supabase
    .from('documents')
    .insert([{ user_id: userId, ...documentData }])
    .select();
  
  if (error) {
    console.error('Error storing document:', error);
    throw error;
  }
  
  return data;
}

export async function getUserDocuments(userId: string) {
  const { data, error } = await supabase
    .from('documents')
    .select('*')
    .eq('user_id', userId)
    .order('created_at', { ascending: false });
  
  if (error) {
    console.error('Error fetching user documents:', error);
    throw error;
  }
  
  return data;
}

export async function storeApiKey(userId: string, service: string, apiKey: string) {
  const { data, error } = await supabase
    .from('api_keys')
    .insert([{ user_id: userId, service, api_key: apiKey }])
    .select();
  
  if (error) {
    console.error('Error storing API key:', error);
    throw error;
  }
  
  return data;
}

export async function getUserApiKeys(userId: string) {
  const { data, error } = await supabase
    .from('api_keys')
    .select('service, created_at')
    .eq('user_id', userId);
  
  if (error) {
    console.error('Error fetching user API keys:', error);
    throw error;
  }
  
  // Return only the service names and creation dates, not the actual keys
  return data;
}

export async function getApiKey(userId: string, service: string) {
  const { data, error } = await supabase
    .from('api_keys')
    .select('api_key')
    .eq('user_id', userId)
    .eq('service', service)
    .single();
  
  if (error) {
    console.error(`Error fetching ${service} API key:`, error);
    return null;
  }
  
  return data?.api_key;
}
