/**
 * ${name}Repository
 * 
 * This repository handles data access for ${description}
 */

import { ${name} } from '../models/types';
import getSupabaseClient from '../lib/supabase';

class ${name}Repository {
  /**
   * Get all ${name.toLowerCase()}s
   */
  async getAll${name}s(): Promise<${name}[]> {
    const supabase = getSupabaseClient();
    if (!supabase) {
      // Fall back to API if Supabase client is not available
      return this.getAll${name}sFromApi();
    }

    try {
      const { data, error } = await supabase
        .from('${name.toLowerCase()}s')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) {
        console.error(`Error fetching ${name.toLowerCase()}s from Supabase:`, error);
        return this.getAll${name}sFromApi();
      }

      return data as ${name}[];
    } catch (error) {
      console.error(`Exception fetching ${name.toLowerCase()}s from Supabase:`, error);
      return this.getAll${name}sFromApi();
    }
  }

  /**
   * Get a ${name.toLowerCase()} by ID
   */
  async get${name}ById(id: string): Promise<${name} | null> {
    const supabase = getSupabaseClient();
    if (!supabase) {
      // Fall back to API if Supabase client is not available
      return this.get${name}ByIdFromApi(id);
    }

    try {
      const { data, error } = await supabase
        .from('${name.toLowerCase()}s')
        .select('*')
        .eq('id', id)
        .single();

      if (error) {
        console.error(`Error fetching ${name.toLowerCase()} from Supabase:`, error);
        return this.get${name}ByIdFromApi(id);
      }

      return data as ${name};
    } catch (error) {
      console.error(`Exception fetching ${name.toLowerCase()} from Supabase:`, error);
      return this.get${name}ByIdFromApi(id);
    }
  }

  /**
   * Create a new ${name.toLowerCase()}
   */
  async create${name}(data: Omit<${name}, 'id' | 'createdAt' | 'updatedAt'>): Promise<${name}> {
    const supabase = getSupabaseClient();
    if (!supabase) {
      // Fall back to API if Supabase client is not available
      return this.create${name}ToApi(data);
    }

    try {
      const { data: result, error } = await supabase
        .from('${name.toLowerCase()}s')
        .insert(this.mapToDbFormat(data))
        .select()
        .single();

      if (error) {
        console.error(`Error creating ${name.toLowerCase()} in Supabase:`, error);
        return this.create${name}ToApi(data);
      }

      return this.mapFromDbFormat(result);
    } catch (error) {
      console.error(`Exception creating ${name.toLowerCase()} in Supabase:`, error);
      return this.create${name}ToApi(data);
    }
  }

  /**
   * Update a ${name.toLowerCase()}
   */
  async update${name}(id: string, data: Partial<${name}>): Promise<${name}> {
    const supabase = getSupabaseClient();
    if (!supabase) {
      // Fall back to API if Supabase client is not available
      return this.update${name}ToApi(id, data);
    }

    try {
      const { data: result, error } = await supabase
        .from('${name.toLowerCase()}s')
        .update(this.mapToDbFormat(data))
        .eq('id', id)
        .select()
        .single();

      if (error) {
        console.error(`Error updating ${name.toLowerCase()} in Supabase:`, error);
        return this.update${name}ToApi(id, data);
      }

      return this.mapFromDbFormat(result);
    } catch (error) {
      console.error(`Exception updating ${name.toLowerCase()} in Supabase:`, error);
      return this.update${name}ToApi(id, data);
    }
  }

  /**
   * Delete a ${name.toLowerCase()}
   */
  async delete${name}(id: string): Promise<boolean> {
    const supabase = getSupabaseClient();
    if (!supabase) {
      // Fall back to API if Supabase client is not available
      return this.delete${name}FromApi(id);
    }

    try {
      const { error } = await supabase
        .from('${name.toLowerCase()}s')
        .delete()
        .eq('id', id);

      if (error) {
        console.error(`Error deleting ${name.toLowerCase()} from Supabase:`, error);
        return this.delete${name}FromApi(id);
      }

      return true;
    } catch (error) {
      console.error(`Exception deleting ${name.toLowerCase()} from Supabase:`, error);
      return this.delete${name}FromApi(id);
    }
  }

  // Mapping methods
  private mapToDbFormat(data: Partial<${name}>): Record<string, any> {
    // Convert camelCase to snake_case for database
    const result: Record<string, any> = {};
    
    Object.entries(data).forEach(([key, value]) => {
      // Convert camelCase to snake_case
      const dbKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
      result[dbKey] = value;
    });
    
    return result;
  }
  
  private mapFromDbFormat(data: Record<string, any>): ${name} {
    // Convert snake_case to camelCase for application
    const result: Record<string, any> = {};
    
    Object.entries(data).forEach(([key, value]) => {
      // Convert snake_case to camelCase
      const appKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
      result[appKey] = value;
    });
    
    return result as ${name};
  }

  // API fallback methods
  private async getAll${name}sFromApi(): Promise<${name}[]> {
    try {
      const response = await fetch('http://localhost:24125/api/${name.toLowerCase()}s');
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data = await response.json();
      return data.${name.toLowerCase()}s || [];
    } catch (error) {
      console.error(`Error fetching ${name.toLowerCase()}s from API:`, error);
      return [];
    }
  }

  private async get${name}ByIdFromApi(id: string): Promise<${name} | null> {
    try {
      const response = await fetch(`http://localhost:24125/api/${name.toLowerCase()}s/${id}`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data = await response.json();
      return data.${name.toLowerCase()} || null;
    } catch (error) {
      console.error(`Error fetching ${name.toLowerCase()} from API:`, error);
      return null;
    }
  }

  private async create${name}ToApi(data: Omit<${name}, 'id' | 'createdAt' | 'updatedAt'>): Promise<${name}> {
    try {
      const response = await fetch(`http://localhost:24125/api/${name.toLowerCase()}s`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const result = await response.json();
      return result.${name.toLowerCase()};
    } catch (error) {
      console.error(`Error creating ${name.toLowerCase()} via API:`, error);
      throw error;
    }
  }

  private async update${name}ToApi(id: string, data: Partial<${name}>): Promise<${name}> {
    try {
      const response = await fetch(`http://localhost:24125/api/${name.toLowerCase()}s/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const result = await response.json();
      return result.${name.toLowerCase()};
    } catch (error) {
      console.error(`Error updating ${name.toLowerCase()} via API:`, error);
      throw error;
    }
  }

  private async delete${name}FromApi(id: string): Promise<boolean> {
    try {
      const response = await fetch(`http://localhost:24125/api/${name.toLowerCase()}s/${id}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      return true;
    } catch (error) {
      console.error(`Error deleting ${name.toLowerCase()} via API:`, error);
      return false;
    }
  }
}

export default new ${name}Repository();
