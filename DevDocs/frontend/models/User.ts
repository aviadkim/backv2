/**
 * User Model
 * 
 * This model represents User model for authentication
 */

export interface User {
  id: string;
  // Add your properties here
  createdAt: string;
  updatedAt: string;
}

// Add any type guards or utility functions related to this model
export function isUser(obj: any): obj is User {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.createdAt === 'string' &&
    typeof obj.updatedAt === 'string'
  );
}
