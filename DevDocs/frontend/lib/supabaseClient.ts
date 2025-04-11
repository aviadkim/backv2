import { createClient } from '@supabase/supabase-js';

// Get Supabase URL and anon key from environment variables
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY || '';

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Function to get Supabase client
const getSupabaseClient = () => {
  return supabase;
};

// Function to get service Supabase client with admin privileges
export const getServiceSupabaseClient = () => {
  if (!supabaseServiceKey) {
    console.warn('SUPABASE_SERVICE_KEY is not defined');
    return null;
  }
  return createClient(supabaseUrl, supabaseServiceKey);
};

export default getSupabaseClient;
