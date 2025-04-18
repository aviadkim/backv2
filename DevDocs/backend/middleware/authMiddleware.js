/**
 * Authentication Middleware
 * 
 * Middleware for authenticating and authorizing requests.
 */

const authService = require('../services/auth/authService');
const logger = require('../utils/logger');

/**
 * Authenticate a request
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
function authenticate(req, res, next) {
  // Get token from header
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    logger.warn('Authentication failed: No token provided');
    return res.status(401).json({ error: 'Authentication required' });
  }
  
  const token = authHeader.split(' ')[1];
  
  // Verify token
  const result = authService.verifyToken(token);
  
  if (!result.success) {
    logger.warn(`Authentication failed: ${result.message}`);
    return res.status(401).json({ error: 'Invalid token' });
  }
  
  // Set user in request
  req.user = result.decoded;
  
  next();
}

/**
 * Authorize a request based on role
 * @param {string[]} roles - Allowed roles
 * @returns {Function} - Express middleware
 */
function authorizeRole(roles) {
  return (req, res, next) => {
    if (!req.user) {
      logger.warn('Authorization failed: No user in request');
      return res.status(401).json({ error: 'Authentication required' });
    }
    
    if (!roles.includes(req.user.role)) {
      logger.warn(`Authorization failed: User ${req.user.username} does not have required role`);
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    
    next();
  };
}

/**
 * Authorize a request based on permission
 * @param {string} permission - Required permission
 * @returns {Function} - Express middleware
 */
function authorizePermission(permission) {
  return (req, res, next) => {
    if (!req.user) {
      logger.warn('Authorization failed: No user in request');
      return res.status(401).json({ error: 'Authentication required' });
    }
    
    if (!req.user.permissions.includes(permission) && !req.user.permissions.includes('admin')) {
      logger.warn(`Authorization failed: User ${req.user.username} does not have required permission`);
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    
    next();
  };
}

module.exports = {
  authenticate,
  authorizeRole,
  authorizePermission
};
