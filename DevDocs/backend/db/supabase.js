/**
 * Supabase Client
 * 
 * Provides a configured Supabase client with connection pooling.
 */

const { createClient } = require('@supabase/supabase-js');
const logger = require('../utils/logger');
const config = require('../config');

// Initialize Supabase client with connection pooling
const supabaseUrl = config.database.url;
const supabaseKey = config.database.key;

let supabase = null;

// Create Supabase client if credentials are provided
if (supabaseUrl && supabaseKey) {
  try {
    supabase = createClient(supabaseUrl, supabaseKey, {
      auth: {
        persistSession: false,
        autoRefreshToken: true,
      },
      db: {
        schema: 'public',
      },
      global: {
        headers: {
          'x-application-name': 'findoc-analyzer',
        },
      },
      realtime: {
        params: {
          eventsPerSecond: 10,
        },
      },
    });
    
    logger.info('Supabase client initialized successfully');
  } catch (error) {
    logger.error('Failed to initialize Supabase client', error);
  }
} else {
  logger.warn('Supabase credentials not provided, client not initialized');
}

/**
 * Get the Supabase client instance
 * @returns {Object} Supabase client
 * @throws {Error} If Supabase client is not initialized
 */
const getClient = () => {
  if (!supabase) {
    throw new Error('Supabase client not initialized');
  }
  
  return supabase;
};

/**
 * Execute a query with error handling
 * @param {Function} queryFn - Function that executes a Supabase query
 * @returns {Promise<Object>} Query result
 */
const executeQuery = async (queryFn) => {
  try {
    const client = getClient();
    const result = await queryFn(client);
    
    if (result.error) {
      throw result.error;
    }
    
    return { data: result.data, error: null };
  } catch (error) {
    logger.error('Supabase query error', error);
    return { data: null, error };
  }
};

/**
 * Check database connection
 * @returns {Promise<boolean>} True if connection is successful
 */
const checkConnection = async () => {
  try {
    const client = getClient();
    const { error } = await client.from('health_check').select('count').limit(1);
    
    if (error) {
      logger.error('Database connection check failed', error);
      return false;
    }
    
    return true;
  } catch (error) {
    logger.error('Database connection check failed', error);
    return false;
  }
};

module.exports = {
  getClient,
  executeQuery,
  checkConnection,
};
