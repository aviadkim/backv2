/**
 * ${name} Model
 * 
 * This model represents ${description}
 */

export interface ${name} {
  id: string;
  // Add your properties here
  createdAt: string;
  updatedAt: string;
}

// Add any type guards or utility functions related to this model
export function is${name}(obj: any): obj is ${name} {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.createdAt === 'string' &&
    typeof obj.updatedAt === 'string'
  );
}
