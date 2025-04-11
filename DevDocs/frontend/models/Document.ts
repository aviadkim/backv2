/**
 * Document Model
 * 
 * This model represents Document management
 */

export interface Document {
  id: string;
  // Add your properties here
  createdAt: string;
  updatedAt: string;
}

// Add any type guards or utility functions related to this model
export function isDocument(obj: any): obj is Document {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.createdAt === 'string' &&
    typeof obj.updatedAt === 'string'
  );
}
