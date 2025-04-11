/**
 * ${name}Controller
 * 
 * This controller handles business logic for ${description}
 */

import { ${name} } from '../models/types';
import ${name}Repository from '../repositories/${name.toLowerCase()}Repository';

class ${name}Controller {
  /**
   * Get all ${name.toLowerCase()}s
   */
  async getAll${name}s(): Promise<${name}[]> {
    try {
      return await ${name}Repository.getAll${name}s();
    } catch (error) {
      console.error(`Error in ${name}Controller.getAll${name}s:`, error);
      throw error;
    }
  }

  /**
   * Get a ${name.toLowerCase()} by ID
   */
  async get${name}ById(id: string): Promise<${name} | null> {
    try {
      return await ${name}Repository.get${name}ById(id);
    } catch (error) {
      console.error(`Error in ${name}Controller.get${name}ById(${id}):`, error);
      throw error;
    }
  }

  /**
   * Create a new ${name.toLowerCase()}
   */
  async create${name}(data: Omit<${name}, 'id' | 'createdAt' | 'updatedAt'>): Promise<${name}> {
    try {
      // Validate data
      this.validate${name}Data(data);
      
      // Create ${name.toLowerCase()}
      return await ${name}Repository.create${name}(data);
    } catch (error) {
      console.error(`Error in ${name}Controller.create${name}:`, error);
      throw error;
    }
  }

  /**
   * Update a ${name.toLowerCase()}
   */
  async update${name}(id: string, data: Partial<${name}>): Promise<${name}> {
    try {
      // Validate data
      this.validate${name}Data(data, false);
      
      // Update ${name.toLowerCase()}
      return await ${name}Repository.update${name}(id, data);
    } catch (error) {
      console.error(`Error in ${name}Controller.update${name}:`, error);
      throw error;
    }
  }

  /**
   * Delete a ${name.toLowerCase()}
   */
  async delete${name}(id: string): Promise<boolean> {
    try {
      return await ${name}Repository.delete${name}(id);
    } catch (error) {
      console.error(`Error in ${name}Controller.delete${name}:`, error);
      throw error;
    }
  }

  /**
   * Validate ${name.toLowerCase()} data
   */
  private validate${name}Data(data: Partial<${name}>, isRequired = true): void {
    // Add validation logic here
    if (isRequired) {
      // Required fields validation
    }
    
    // Field-specific validation
  }
}

export default new ${name}Controller();
