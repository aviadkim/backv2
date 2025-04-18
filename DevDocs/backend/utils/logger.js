/**
 * Logger Utility
 *
 * Provides consistent logging throughout the application
 * Simple version that doesn't depend on external libraries
 */

// Create a simple logger
const logger = {
  info: (message, meta) => {
    console.log(`[INFO] ${message}`);
    if (meta) {
      console.log(meta);
    }
  },

  error: (message, error) => {
    console.error(`[ERROR] ${message}`);
    if (error) {
      console.error(error);
    }
  },

  warn: (message, meta) => {
    console.warn(`[WARN] ${message}`);
    if (meta) {
      console.warn(meta);
    }
  },

  debug: (message, meta) => {
    if (process.env.NODE_ENV === 'development') {
      console.debug(`[DEBUG] ${message}`);
      if (meta) {
        console.debug(meta);
      }
    }
  }
};

module.exports = logger;
