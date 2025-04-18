/**
 * Logger Utility
 *
 * Provides consistent logging throughout the application
 * Uses Winston for advanced logging capabilities
 */

const winston = require('winston');
const path = require('path');
const fs = require('fs');

// Create logs directory if it doesn't exist
const logsDir = path.join(__dirname, '..', 'logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
}

// Define log format
const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.splat(),
  winston.format.json()
);

// Define console format (more readable for development)
const consoleFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.printf(({ level, message, timestamp, ...meta }) => {
    return `${timestamp} ${level}: ${message} ${Object.keys(meta).length ? JSON.stringify(meta, null, 2) : ''}`;
  })
);

// Get log level from environment variable or default to 'info'
const logLevel = process.env.LOG_LEVEL || 'info';

// Create logger
const logger = winston.createLogger({
  level: logLevel,
  format: logFormat,
  defaultMeta: { service: 'findoc-analyzer' },
  transports: [
    // Write all logs to console
    new winston.transports.Console({
      format: consoleFormat
    })
  ]
});

// Add file transports in production environment
if (process.env.NODE_ENV === 'production') {
  logger.add(
    // Write all logs with level 'info' and below to combined.log
    new winston.transports.File({
      filename: path.join(logsDir, 'combined.log'),
      maxsize: 10485760, // 10MB
      maxFiles: 5,
      tailable: true
    })
  );

  logger.add(
    // Write all logs with level 'error' and below to error.log
    new winston.transports.File({
      filename: path.join(logsDir, 'error.log'),
      level: 'error',
      maxsize: 10485760, // 10MB
      maxFiles: 5,
      tailable: true
    })
  );
}

// Fallback to console if Winston is not available
if (!winston) {
  const simpleLogger = {
    info: (message, meta) => {
      console.log(`[INFO] ${message}`);
      if (meta) console.log(meta);
    },
    error: (message, error) => {
      console.error(`[ERROR] ${message}`);
      if (error) console.error(error);
    },
    warn: (message, meta) => {
      console.warn(`[WARN] ${message}`);
      if (meta) console.warn(meta);
    },
    debug: (message, meta) => {
      if (process.env.NODE_ENV === 'development') {
        console.debug(`[DEBUG] ${message}`);
        if (meta) console.debug(meta);
      }
    }
  };

  module.exports = simpleLogger;
} else {
  module.exports = logger;
}
