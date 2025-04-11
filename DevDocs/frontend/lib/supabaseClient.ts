import { createClient } from '@supabase/supabase-js';

// Get Supabase URL and anon key from environment variables
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://dnjnsotemnfrjlotgved.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRuam5zb3RlbW5mcmpsb3RndmVkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTI4NTI0MDAsImV4cCI6MjAyODQyODQwMH0.placeholder-key';
const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY || '';

// Create Supabase client
let supabase;
try {
  supabase = createClient(supabaseUrl, supabaseAnonKey);
} catch (error) {
  console.error('Failed to create Supabase client:', error);
  // Create a mock client for SSR/build
  supabase = {
    auth: { onAuthStateChange: () => ({ data: { subscription: { unsubscribe: () => {} } } }) },
    from: () => ({
      select: () => ({ eq: () => ({ single: () => ({ data: null, error: null }) }) })
    })
  };
}

export { supabase };

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
