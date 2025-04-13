// Script to test Supabase connection
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '../frontend/.env.local' });

async function testSupabaseConnection() {
  console.log('Testing Supabase connection...');
  
  // Get Supabase credentials from environment variables
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  
  if (!supabaseUrl || !supabaseKey) {
    console.error('Error: Supabase credentials not found in environment variables');
    console.log('Make sure you have set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY');
    process.exit(1);
  }
  
  console.log(`Supabase URL: ${supabaseUrl}`);
  console.log(`Supabase Key: ${supabaseKey.substring(0, 10)}...`);
  
  try {
    // Initialize Supabase client
    const supabase = createClient(supabaseUrl, supabaseKey);
    
    // Test a simple query
    console.log('Executing test query...');
    const { data, error } = await supabase
      .from('documents')
      .select('count')
      .limit(1);
    
    if (error) {
      console.error('Error executing query:', error.message);
      process.exit(1);
    }
    
    console.log('Query successful!');
    console.log('Connection test passed!');
    
  } catch (err) {
    console.error('Exception occurred:', err.message);
    process.exit(1);
  }
}

// Run the test
testSupabaseConnection();
