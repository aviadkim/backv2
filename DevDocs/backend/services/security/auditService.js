/**
 * Audit Service
 * 
 * Provides audit logging functionality for security and compliance.
 */

const logger = require('../../utils/logger');
const fs = require('fs').promises;
const path = require('path');

// Audit log settings
const AUDIT_LOG_DIR = process.env.AUDIT_LOG_DIR || path.join(process.cwd(), 'logs', 'audit');
const AUDIT_LOG_FILE = process.env.AUDIT_LOG_FILE || 'audit.log';
const AUDIT_LOG_PATH = path.join(AUDIT_LOG_DIR, AUDIT_LOG_FILE);

// Audit event types
const EVENT_TYPES = {
  AUTH: 'authentication',
  ACCESS: 'access',
  DATA: 'data',
  ADMIN: 'admin',
  SECURITY: 'security',
  SYSTEM: 'system'
};

/**
 * Initialize audit logging
 * @returns {Promise<void>}
 */
async function initAuditLogging() {
  try {
    // Create audit log directory if it doesn't exist
    await fs.mkdir(AUDIT_LOG_DIR, { recursive: true });
    
    logger.info(`Audit logging initialized. Log path: ${AUDIT_LOG_PATH}`);
  } catch (error) {
    logger.error(`Error initializing audit logging: ${error.message}`, error);
    throw error;
  }
}

/**
 * Log an audit event
 * @param {string} eventType - Event type
 * @param {string} action - Action performed
 * @param {Object} details - Event details
 * @param {Object} user - User who performed the action
 * @returns {Promise<void>}
 */
async function logEvent(eventType, action, details, user = null) {
  try {
    // Validate event type
    if (!Object.values(EVENT_TYPES).includes(eventType)) {
      throw new Error(`Invalid event type: ${eventType}`);
    }
    
    // Create audit event
    const auditEvent = {
      timestamp: new Date().toISOString(),
      eventType,
      action,
      details,
      user: user ? {
        id: user.id,
        username: user.username,
        role: user.role
      } : null,
      ip: details.ip || null,
      userAgent: details.userAgent || null
    };
    
    // Log to file
    await logToFile(auditEvent);
    
    // Log to application logger
    logger.info(`Audit event: ${eventType} - ${action}`, { auditEvent });
    
    return auditEvent;
  } catch (error) {
    logger.error(`Error logging audit event: ${error.message}`, error);
    throw error;
  }
}

/**
 * Log an authentication event
 * @param {string} action - Authentication action
 * @param {Object} details - Event details
 * @param {Object} user - User who performed the action
 * @returns {Promise<Object>} - Audit event
 */
async function logAuthEvent(action, details, user = null) {
  return logEvent(EVENT_TYPES.AUTH, action, details, user);
}

/**
 * Log an access event
 * @param {string} action - Access action
 * @param {Object} details - Event details
 * @param {Object} user - User who performed the action
 * @returns {Promise<Object>} - Audit event
 */
async function logAccessEvent(action, details, user = null) {
  return logEvent(EVENT_TYPES.ACCESS, action, details, user);
}

/**
 * Log a data event
 * @param {string} action - Data action
 * @param {Object} details - Event details
 * @param {Object} user - User who performed the action
 * @returns {Promise<Object>} - Audit event
 */
async function logDataEvent(action, details, user = null) {
  return logEvent(EVENT_TYPES.DATA, action, details, user);
}

/**
 * Log an admin event
 * @param {string} action - Admin action
 * @param {Object} details - Event details
 * @param {Object} user - User who performed the action
 * @returns {Promise<Object>} - Audit event
 */
async function logAdminEvent(action, details, user = null) {
  return logEvent(EVENT_TYPES.ADMIN, action, details, user);
}

/**
 * Log a security event
 * @param {string} action - Security action
 * @param {Object} details - Event details
 * @param {Object} user - User who performed the action
 * @returns {Promise<Object>} - Audit event
 */
async function logSecurityEvent(action, details, user = null) {
  return logEvent(EVENT_TYPES.SECURITY, action, details, user);
}

/**
 * Log a system event
 * @param {string} action - System action
 * @param {Object} details - Event details
 * @param {Object} user - User who performed the action
 * @returns {Promise<Object>} - Audit event
 */
async function logSystemEvent(action, details, user = null) {
  return logEvent(EVENT_TYPES.SYSTEM, action, details, user);
}

/**
 * Log an audit event to file
 * @param {Object} auditEvent - Audit event
 * @returns {Promise<void>}
 * @private
 */
async function logToFile(auditEvent) {
  try {
    // Convert audit event to string
    const eventString = JSON.stringify(auditEvent) + '\n';
    
    // Append to audit log file
    await fs.appendFile(AUDIT_LOG_PATH, eventString, 'utf8');
  } catch (error) {
    logger.error(`Error writing to audit log file: ${error.message}`, error);
    throw error;
  }
}

/**
 * Get audit logs
 * @param {Object} options - Query options
 * @returns {Promise<Array>} - Audit events
 */
async function getAuditLogs(options = {}) {
  try {
    // Read audit log file
    const logContent = await fs.readFile(AUDIT_LOG_PATH, 'utf8');
    
    // Parse audit events
    const auditEvents = logContent
      .split('\n')
      .filter(line => line.trim())
      .map(line => JSON.parse(line));
    
    // Apply filters
    let filteredEvents = auditEvents;
    
    if (options.eventType) {
      filteredEvents = filteredEvents.filter(event => event.eventType === options.eventType);
    }
    
    if (options.action) {
      filteredEvents = filteredEvents.filter(event => event.action === options.action);
    }
    
    if (options.userId) {
      filteredEvents = filteredEvents.filter(event => event.user && event.user.id === options.userId);
    }
    
    if (options.startDate) {
      const startDate = new Date(options.startDate);
      filteredEvents = filteredEvents.filter(event => new Date(event.timestamp) >= startDate);
    }
    
    if (options.endDate) {
      const endDate = new Date(options.endDate);
      filteredEvents = filteredEvents.filter(event => new Date(event.timestamp) <= endDate);
    }
    
    // Apply pagination
    if (options.limit) {
      const limit = parseInt(options.limit);
      const offset = options.offset ? parseInt(options.offset) : 0;
      
      filteredEvents = filteredEvents.slice(offset, offset + limit);
    }
    
    return filteredEvents;
  } catch (error) {
    // If file doesn't exist, return empty array
    if (error.code === 'ENOENT') {
      return [];
    }
    
    logger.error(`Error getting audit logs: ${error.message}`, error);
    throw error;
  }
}

/**
 * Create an audit middleware
 * @param {string} eventType - Event type
 * @param {string} action - Action
 * @returns {Function} - Express middleware
 */
function auditMiddleware(eventType, action) {
  return async (req, res, next) => {
    try {
      // Get request details
      const details = {
        method: req.method,
        url: req.originalUrl,
        ip: req.ip,
        userAgent: req.get('User-Agent'),
        params: req.params,
        query: req.query,
        body: req.method === 'GET' ? undefined : req.body
      };
      
      // Log audit event
      await logEvent(eventType, action, details, req.user);
      
      next();
    } catch (error) {
      logger.error(`Audit middleware error: ${error.message}`, error);
      next();
    }
  };
}

module.exports = {
  EVENT_TYPES,
  initAuditLogging,
  logEvent,
  logAuthEvent,
  logAccessEvent,
  logDataEvent,
  logAdminEvent,
  logSecurityEvent,
  logSystemEvent,
  getAuditLogs,
  auditMiddleware
};
