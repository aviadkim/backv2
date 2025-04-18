/**
 * Error Handling Middleware
 * 
 * Provides centralized error handling for the application:
 * - Custom error classes
 * - Error logging
 * - Standardized error responses
 */

const logger = require('../utils/logger');
const config = require('../config');

// Custom error classes
class AppError extends Error {
  constructor(message, statusCode, errorCode = null) {
    super(message);
    this.statusCode = statusCode;
    this.errorCode = errorCode;
    this.isOperational = true;
    
    Error.captureStackTrace(this, this.constructor);
  }
}

class BadRequestError extends AppError {
  constructor(message, errorCode = 'BAD_REQUEST') {
    super(message, 400, errorCode);
  }
}

class UnauthorizedError extends AppError {
  constructor(message, errorCode = 'UNAUTHORIZED') {
    super(message, 401, errorCode);
  }
}

class ForbiddenError extends AppError {
  constructor(message, errorCode = 'FORBIDDEN') {
    super(message, 403, errorCode);
  }
}

class NotFoundError extends AppError {
  constructor(message, errorCode = 'NOT_FOUND') {
    super(message, 404, errorCode);
  }
}

class ValidationError extends AppError {
  constructor(message, errorCode = 'VALIDATION_ERROR', validationErrors = []) {
    super(message, 422, errorCode);
    this.validationErrors = validationErrors;
  }
}

class ConflictError extends AppError {
  constructor(message, errorCode = 'CONFLICT') {
    super(message, 409, errorCode);
  }
}

class InternalServerError extends AppError {
  constructor(message, errorCode = 'INTERNAL_SERVER_ERROR') {
    super(message, 500, errorCode);
  }
}

// Error handler middleware
const errorHandler = (err, req, res, next) => {
  // Default error values
  let statusCode = err.statusCode || 500;
  let errorCode = err.errorCode || 'INTERNAL_SERVER_ERROR';
  let message = err.message || 'Something went wrong';
  let validationErrors = err.validationErrors || [];
  let stack = err.stack;
  
  // Log the error
  if (statusCode >= 500) {
    logger.error(`[${errorCode}] ${message}`, {
      error: err.message,
      stack: err.stack,
      url: req.originalUrl,
      method: req.method,
      ip: req.ip,
      userId: req.user?.id,
    });
  } else {
    logger.warn(`[${errorCode}] ${message}`, {
      error: err.message,
      url: req.originalUrl,
      method: req.method,
      ip: req.ip,
      userId: req.user?.id,
    });
  }
  
  // Prepare response
  const errorResponse = {
    status: 'error',
    code: errorCode,
    message,
  };
  
  // Add validation errors if present
  if (validationErrors.length > 0) {
    errorResponse.validationErrors = validationErrors;
  }
  
  // Add stack trace in development
  if (config.server.isDev) {
    errorResponse.stack = stack;
  }
  
  // Send response
  res.status(statusCode).json(errorResponse);
};

// Not found middleware
const notFoundHandler = (req, res, next) => {
  const error = new NotFoundError(`Route not found: ${req.originalUrl}`);
  next(error);
};

// Async handler to catch errors in async routes
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

// Export error handling utilities
module.exports = {
  // Error classes
  AppError,
  BadRequestError,
  UnauthorizedError,
  ForbiddenError,
  NotFoundError,
  ValidationError,
  ConflictError,
  InternalServerError,
  
  // Middleware
  errorHandler,
  notFoundHandler,
  asyncHandler,
};
