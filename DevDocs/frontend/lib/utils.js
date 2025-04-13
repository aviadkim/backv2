import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Combines multiple class names and resolves Tailwind CSS conflicts
 * @param {...string} inputs - Class names to combine
 * @returns {string} - Combined class names with resolved conflicts
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
