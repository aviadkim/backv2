/**
 * Simplified Supabase Client for API routes
 */

/**
 * Get a Supabase client
 * @returns {Object|null} The Supabase client or null if not configured
 */
function getSupabaseClient() {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
  
  if (!supabaseUrl || !supabaseAnonKey) {
    console.error('Supabase URL or anon key not available');
    return null;
  }
  
  // In a real application, this would create a Supabase client
  // For this demo, we'll return a mock client
  return {
    from: (table) => ({
      select: (columns) => ({
        limit: (limit) => ({
          async then(resolve, reject) {
            resolve({ data: [], error: null });
          }
        })
      })
    })
  };
}

export default getSupabaseClient;
