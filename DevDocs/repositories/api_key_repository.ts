import supabaseService from '../services/supabase_service';
import { ApiKey } from '../frontend/models/types';

/**
 * Repository for API key operations
 */
class ApiKeyRepository {
  /**
   * Get all API keys for the current user's organization
   * @returns Array of API keys
   */
  async getAllApiKeys(): Promise<ApiKey[]> {
    const supabase = supabaseService.getClient();
    if (!supabase) {
      console.error('Supabase client not available');
      return [];
    }

    try {
      const { data, error } = await supabase
        .from('api_keys')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Error fetching API keys from Supabase:', error);
        return [];
      }

      return data as ApiKey[];
    } catch (error) {
      console.error('Exception fetching API keys from Supabase:', error);
      return [];
    }
  }

  /**
   * Get an API key by ID
   * @param id API key ID
   * @returns API key or null if not found
   */
  async getApiKeyById(id: string): Promise<ApiKey | null> {
    const supabase = supabaseService.getClient();
    if (!supabase) {
      console.error('Supabase client not available');
      return null;
    }

    try {
      const { data, error } = await supabase
        .from('api_keys')
        .select('*')
        .eq('id', id)
        .single();

      if (error) {
        console.error('Error fetching API key from Supabase:', error);
        return null;
      }

      return data as ApiKey;
    } catch (error) {
      console.error('Exception fetching API key from Supabase:', error);
      return null;
    }
  }

  /**
   * Create a new API key
   * @param data API key data
   * @returns Created API key
   */
  async createApiKey(data: Omit<ApiKey, 'id' | 'created_at' | 'updated_at'>): Promise<ApiKey | null> {
    const supabase = supabaseService.getClient();
    if (!supabase) {
      console.error('Supabase client not available');
      return null;
    }

    try {
      const { data: createdData, error } = await supabase
        .from('api_keys')
        .insert(data)
        .select()
        .single();

      if (error) {
        console.error('Error creating API key in Supabase:', error);
        return null;
      }

      return createdData as ApiKey;
    } catch (error) {
      console.error('Exception creating API key in Supabase:', error);
      return null;
    }
  }

  /**
   * Update an API key
   * @param id API key ID
   * @param data Updated API key data
   * @returns Updated API key
   */
  async updateApiKey(id: string, data: Partial<ApiKey>): Promise<ApiKey | null> {
    const supabase = supabaseService.getClient();
    if (!supabase) {
      console.error('Supabase client not available');
      return null;
    }

    try {
      const { data: updatedData, error } = await supabase
        .from('api_keys')
        .update(data)
        .eq('id', id)
        .select()
        .single();

      if (error) {
        console.error('Error updating API key in Supabase:', error);
        return null;
      }

      return updatedData as ApiKey;
    } catch (error) {
      console.error('Exception updating API key in Supabase:', error);
      return null;
    }
  }

  /**
   * Delete an API key
   * @param id API key ID
   * @returns True if successful, false otherwise
   */
  async deleteApiKey(id: string): Promise<boolean> {
    const supabase = supabaseService.getClient();
    if (!supabase) {
      console.error('Supabase client not available');
      return false;
    }

    try {
      const { error } = await supabase
        .from('api_keys')
        .delete()
        .eq('id', id);

      if (error) {
        console.error('Error deleting API key from Supabase:', error);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Exception deleting API key from Supabase:', error);
      return false;
    }
  }
}

// Export a singleton instance
const apiKeyRepository = new ApiKeyRepository();
export default apiKeyRepository;
