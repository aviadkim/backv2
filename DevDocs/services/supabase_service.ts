import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { Database } from '../frontend/types/supabase';

/**
 * Supabase Service for server-side operations
 * This service should only be used in API routes and server components
 */
class SupabaseService {
  private client: SupabaseClient<Database> | null = null;
  private serviceClient: SupabaseClient<Database> | null = null;

  /**
   * Get the Supabase client with anonymous key
   * @returns Supabase client
   */
  getClient(): SupabaseClient<Database> | null {
    if (this.client) {
      return this.client;
    }

    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!supabaseUrl || !supabaseAnonKey) {
      console.error('Supabase URL or anon key not available');
      return null;
    }

    this.client = createClient<Database>(supabaseUrl, supabaseAnonKey);
    return this.client;
  }

  /**
   * Get the Supabase client with service role key
   * This should only be used in server-side code
   * @returns Supabase client with service role key
   */
  getServiceClient(): SupabaseClient<Database> | null {
    if (typeof window !== 'undefined') {
      console.error('Service client should not be used in client-side code');
      return null;
    }

    if (this.serviceClient) {
      return this.serviceClient;
    }

    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

    if (!supabaseUrl || !supabaseServiceKey) {
      console.error('Supabase URL or service key not available');
      return null;
    }

    this.serviceClient = createClient<Database>(supabaseUrl, supabaseServiceKey);
    return this.serviceClient;
  }

  /**
   * Get a Supabase client with a custom key
   * @param key Custom API key
   * @returns Supabase client with custom key
   */
  getClientWithKey(key: string): SupabaseClient<Database> | null {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;

    if (!supabaseUrl) {
      console.error('Supabase URL not available');
      return null;
    }

    return createClient<Database>(supabaseUrl, key);
  }
}

// Export a singleton instance
const supabaseService = new SupabaseService();
export default supabaseService;
