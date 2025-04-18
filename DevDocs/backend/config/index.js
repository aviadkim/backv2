/**
 * Configuration Module
 * 
 * Centralizes all configuration settings for the application.
 * Loads environment-specific configurations based on NODE_ENV.
 */

const path = require('path');
const dotenv = require('dotenv');
const logger = require('../utils/logger');

// Load environment variables from .env file
dotenv.config({ path: path.join(__dirname, '../../.env') });

// Environment
const NODE_ENV = process.env.NODE_ENV || 'development';
const isProd = NODE_ENV === 'production';
const isDev = NODE_ENV === 'development';
const isTest = NODE_ENV === 'test';

// Server configuration
const server = {
  port: parseInt(process.env.PORT || '3001', 10),
  host: process.env.HOST || '0.0.0.0',
  env: NODE_ENV,
  isProd,
  isDev,
  isTest,
};

// Database configuration
const database = {
  url: process.env.SUPABASE_URL || 'https://dnjnsotemnfrjlotgved.supabase.co',
  key: process.env.SUPABASE_KEY || '',
  poolConfig: {
    min: parseInt(process.env.DB_POOL_MIN || '2', 10),
    max: parseInt(process.env.DB_POOL_MAX || '10', 10),
    idleTimeoutMillis: parseInt(process.env.DB_IDLE_TIMEOUT || '30000', 10),
    connectionTimeoutMillis: parseInt(process.env.DB_CONNECTION_TIMEOUT || '2000', 10),
  },
};

// Authentication configuration
const auth = {
  jwtSecret: process.env.JWT_SECRET || 'your-secret-key',
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '1d',
  encryptionKey: process.env.ENCRYPTION_KEY || 'your-encryption-key',
  saltRounds: parseInt(process.env.SALT_ROUNDS || '10', 10),
};

// API configuration
const api = {
  openrouterApiKey: process.env.OPENROUTER_API_KEY || '',
  openrouterApiUrl: process.env.OPENROUTER_API_URL || 'https://api.openrouter.ai/api/v1',
  defaultModel: process.env.DEFAULT_MODEL || 'claude-3-7-sonnet-20240620',
  rateLimitMax: parseInt(process.env.RATE_LIMIT_MAX || '100', 10),
  rateLimitWindowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '900000', 10), // 15 minutes
};

// CORS configuration
const cors = {
  origin: process.env.CORS_ORIGIN || '*',
  methods: process.env.CORS_METHODS || 'GET,HEAD,PUT,PATCH,POST,DELETE',
  preflightContinue: process.env.CORS_PREFLIGHT_CONTINUE === 'true',
  optionsSuccessStatus: parseInt(process.env.CORS_OPTIONS_SUCCESS_STATUS || '204', 10),
  allowedHeaders: process.env.CORS_ALLOWED_HEADERS || 'Content-Type,Authorization,X-Requested-With',
  exposedHeaders: process.env.CORS_EXPOSED_HEADERS || 'Content-Range,X-Content-Range',
  credentials: process.env.CORS_CREDENTIALS === 'true',
  maxAge: parseInt(process.env.CORS_MAX_AGE || '86400', 10), // 24 hours
};

// Logging configuration
const logging = {
  level: process.env.LOG_LEVEL || (isProd ? 'info' : 'debug'),
  format: process.env.LOG_FORMAT || 'json',
  directory: process.env.LOG_DIRECTORY || path.join(__dirname, '../logs'),
  maxSize: process.env.LOG_MAX_SIZE || '10m',
  maxFiles: parseInt(process.env.LOG_MAX_FILES || '5', 10),
  console: process.env.LOG_CONSOLE !== 'false',
};

// Feature flags
const features = {
  enableAiEnhancement: process.env.ENABLE_AI_ENHANCEMENT !== 'false',
  enableDocumentComparison: process.env.ENABLE_DOCUMENT_COMPARISON !== 'false',
  enableFinancialAdvisor: process.env.ENABLE_FINANCIAL_ADVISOR !== 'false',
  enableCaching: process.env.ENABLE_CACHING !== 'false',
  enableRateLimiting: process.env.ENABLE_RATE_LIMITING !== 'false',
};

// Cache configuration
const cache = {
  ttl: parseInt(process.env.CACHE_TTL || '3600', 10), // 1 hour
  checkPeriod: parseInt(process.env.CACHE_CHECK_PERIOD || '600', 10), // 10 minutes
  maxItems: parseInt(process.env.CACHE_MAX_ITEMS || '1000', 10),
};

// Upload configuration
const upload = {
  maxFileSize: parseInt(process.env.UPLOAD_MAX_FILE_SIZE || '10485760', 10), // 10MB
  allowedMimeTypes: (process.env.UPLOAD_ALLOWED_MIME_TYPES || 'application/pdf,image/jpeg,image/png,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/csv').split(','),
  uploadDir: process.env.UPLOAD_DIR || path.join(__dirname, '../uploads'),
  tempDir: process.env.TEMP_DIR || path.join(__dirname, '../temp'),
};

// Export configuration
const config = {
  server,
  database,
  auth,
  api,
  cors,
  logging,
  features,
  cache,
  upload,
};

// Log configuration on startup (excluding sensitive data)
if (isDev) {
  const sanitizedConfig = {
    ...config,
    database: { ...config.database, key: config.database.key ? '***' : null },
    auth: { ...config.auth, jwtSecret: '***', encryptionKey: '***' },
    api: { ...config.api, openrouterApiKey: config.api.openrouterApiKey ? '***' : null },
  };
  
  logger.debug('Application configuration loaded', sanitizedConfig);
}

module.exports = config;
