/**
 * API utility functions for handling requests and responses
 */

/**
 * Handles API responses and formats them consistently
 * @param {Object} res - The response object
 * @param {number} statusCode - HTTP status code
 * @param {Object|Array} data - The data to return
 * @param {string} message - Optional message
 */
export const apiResponse = (res, statusCode, data, message = '') => {
  return res.status(statusCode).json({
    success: statusCode >= 200 && statusCode < 300,
    message,
    data
  });
};

/**
 * Handles API errors consistently
 * @param {Object} res - The response object
 * @param {number} statusCode - HTTP status code
 * @param {string} message - Error message
 * @param {Object} error - Optional error object
 */
export const apiError = (res, statusCode, message, error = null) => {
  console.error(`API Error: ${message}`, error);
  
  return res.status(statusCode).json({
    success: false,
    message,
    error: process.env.NODE_ENV === 'development' ? error : null
  });
};

/**
 * Validates required fields in a request
 * @param {Object} req - The request object
 * @param {Array} requiredFields - Array of required field names
 * @returns {Object} - { valid: boolean, missing: array }
 */
export const validateRequiredFields = (req, requiredFields) => {
  const body = req.body || {};
  const missing = requiredFields.filter(field => !body[field]);
  
  return {
    valid: missing.length === 0,
    missing
  };
};

/**
 * Wraps an API handler with error handling
 * @param {Function} handler - The API handler function
 */
export const withErrorHandling = (handler) => {
  return async (req, res) => {
    try {
      return await handler(req, res);
    } catch (error) {
      console.error('Unhandled API error:', error);
      return apiError(
        res,
        500,
        'An unexpected error occurred',
        error.message
      );
    }
  };
};
