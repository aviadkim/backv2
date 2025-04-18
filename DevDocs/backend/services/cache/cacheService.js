/**
 * Cache Service
 *
 * Provides caching functionality for frequently accessed data.
 */

const NodeCache = require('node-cache');
const logger = require('../../utils/logger');

// Default cache settings
const DEFAULT_TTL = 60 * 60; // 1 hour in seconds
const CHECK_PERIOD = 60; // Check for expired keys every 60 seconds

// Create cache instance
const cache = new NodeCache({
  stdTTL: DEFAULT_TTL,
  checkperiod: CHECK_PERIOD,
  useClones: false // For better performance with large objects
});

/**
 * Get item from cache
 * @param {string} key - Cache key
 * @returns {*} - Cached value or undefined if not found
 */
function get(key) {
  try {
    return cache.get(key);
  } catch (error) {
    logger.error(`Error getting item from cache: ${error.message}`, error);
    return undefined;
  }
}

/**
 * Set item in cache
 * @param {string} key - Cache key
 * @param {*} value - Value to cache
 * @param {number} ttl - Time to live in seconds (optional)
 * @returns {boolean} - Whether the item was set successfully
 */
function set(key, value, ttl = DEFAULT_TTL) {
  try {
    return cache.set(key, value, ttl);
  } catch (error) {
    logger.error(`Error setting item in cache: ${error.message}`, error);
    return false;
  }
}

/**
 * Delete item from cache
 * @param {string} key - Cache key
 * @returns {number} - Number of items deleted (0 or 1)
 */
function del(key) {
  try {
    return cache.del(key);
  } catch (error) {
    logger.error(`Error deleting item from cache: ${error.message}`, error);
    return 0;
  }
}

/**
 * Check if key exists in cache
 * @param {string} key - Cache key
 * @returns {boolean} - Whether the key exists
 */
function has(key) {
  try {
    return cache.has(key);
  } catch (error) {
    logger.error(`Error checking if key exists in cache: ${error.message}`, error);
    return false;
  }
}

/**
 * Get multiple items from cache
 * @param {string[]} keys - Cache keys
 * @returns {Object} - Object with key-value pairs
 */
function mget(keys) {
  try {
    return cache.mget(keys);
  } catch (error) {
    logger.error(`Error getting multiple items from cache: ${error.message}`, error);
    return {};
  }
}

/**
 * Set multiple items in cache
 * @param {Object} keyValuePairs - Object with key-value pairs
 * @param {number} ttl - Time to live in seconds (optional)
 * @returns {boolean} - Whether all items were set successfully
 */
function mset(keyValuePairs, ttl = DEFAULT_TTL) {
  try {
    return cache.mset(Object.entries(keyValuePairs).map(([key, value]) => ({
      key,
      val: value,
      ttl
    })));
  } catch (error) {
    logger.error(`Error setting multiple items in cache: ${error.message}`, error);
    return false;
  }
}

/**
 * Delete multiple items from cache
 * @param {string[]} keys - Cache keys
 * @returns {number} - Number of items deleted
 */
function mdel(keys) {
  try {
    return cache.del(keys);
  } catch (error) {
    logger.error(`Error deleting multiple items from cache: ${error.message}`, error);
    return 0;
  }
}

/**
 * Flush cache (delete all items)
 * @returns {void}
 */
function flush() {
  try {
    cache.flushAll();
    logger.info('Cache flushed');
  } catch (error) {
    logger.error(`Error flushing cache: ${error.message}`, error);
  }
}

/**
 * Get cache statistics
 * @returns {Object} - Cache statistics
 */
function getStats() {
  try {
    return cache.getStats();
  } catch (error) {
    logger.error(`Error getting cache statistics: ${error.message}`, error);
    return {};
  }
}

/**
 * Get all keys in cache
 * @returns {string[]} - Array of keys
 */
function keys() {
  try {
    return cache.keys();
  } catch (error) {
    logger.error(`Error getting cache keys: ${error.message}`, error);
    return [];
  }
}

/**
 * Get cache size (number of items)
 * @returns {number} - Number of items in cache
 */
function size() {
  try {
    return cache.keys().length;
  } catch (error) {
    logger.error(`Error getting cache size: ${error.message}`, error);
    return 0;
  }
}

/**
 * Create a cached version of a function
 * @param {Function} fn - Function to cache
 * @param {Function} keyFn - Function to generate cache key from arguments
 * @param {number} ttl - Time to live in seconds (optional)
 * @returns {Function} - Cached function
 */
function memoize(fn, keyFn, ttl = DEFAULT_TTL) {
  return async function(...args) {
    const key = keyFn(...args);

    // Check if result is in cache
    if (has(key)) {
      logger.debug(`Cache hit for key: ${key}`);
      return get(key);
    }

    // Execute function and cache result
    logger.debug(`Cache miss for key: ${key}`);
    const result = await fn(...args);
    set(key, result, ttl);

    return result;
  };
}

/**
 * Cache middleware for Express routes
 * @param {number} ttl - Time to live in seconds (optional)
 * @returns {Function} Express middleware
 */
function cacheMiddleware(ttl = DEFAULT_TTL) {
  return (req, res, next) => {
    // Skip caching for non-GET requests
    if (req.method !== 'GET') {
      return next();
    }

    // Create cache key from URL and query parameters
    const key = `cache:${req.originalUrl || req.url}`;

    // Try to get from cache
    const cachedBody = get(key);

    if (cachedBody) {
      // Return cached response
      logger.debug(`Cache hit for route: ${req.originalUrl}`);
      return res.send(cachedBody);
    }

    // Cache the response
    const originalSend = res.send;

    res.send = function(body) {
      // Only cache successful responses
      if (res.statusCode >= 200 && res.statusCode < 300) {
        set(key, body, ttl);
        logger.debug(`Cached route: ${req.originalUrl}`);
      }

      originalSend.call(this, body);
    };

    next();
  };
}

/**
 * Initialize cache service
 * @returns {boolean} True if successful
 */
function initCacheService() {
  logger.info('Cache service initialized');

  // Set up cache events
  cache.on('expired', (key, value) => {
    logger.debug(`Cache key expired: ${key}`);
  });

  cache.on('flush', () => {
    logger.debug('Cache flushed');
  });

  return true;
}

module.exports = {
  get,
  set,
  del,
  has,
  mget,
  mset,
  mdel,
  flush,
  getStats,
  keys,
  size,
  memoize,
  cacheMiddleware,
  initCacheService
};
