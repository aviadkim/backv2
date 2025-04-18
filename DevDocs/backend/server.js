/**
 * FinDoc Backend Server
 *
 * Main entry point for the backend server
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const cookieParser = require('cookie-parser');
const path = require('path');
const { createClient } = require('@supabase/supabase-js');
const logger = require('./utils/logger');

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 8000;

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL || 'https://dnjnsotemnfrjlotgved.supabase.co';
const supabaseKey = process.env.SUPABASE_KEY || '';
const supabase = createClient(supabaseUrl, supabaseKey);

// Make Supabase client available to all routes
app.locals.supabase = supabase;

// Middleware
app.use(helmet()); // Security headers
app.use(cors()); // Enable CORS
app.use(express.json()); // Parse JSON bodies
app.use(express.urlencoded({ extended: true })); // Parse URL-encoded bodies
app.use(cookieParser()); // Parse cookies
app.use(morgan('combined', { stream: { write: message => logger.info(message.trim()) } })); // HTTP request logging
app.use(performanceMonitor.performanceMiddleware()); // Performance monitoring

// API Routes
app.use('/api/health', require('./routes/api/health'));
app.use('/api/auth', require('./routes/api/auth'));
app.use('/api/security', require('./routes/api/security'));
app.use('/api/performance', require('./routes/api/performance'));
app.use('/api/financial/process-document', require('./routes/api/financial/process-document'));
app.use('/api/financial/export-data', require('./routes/api/financial/export-data'));
app.use('/api/financial/compare-documents', require('./routes/api/financial/compare-documents'));
app.use('/api/financial/query-document', require('./routes/api/financial/query-document'));
app.use('/api/financial/integrate-documents', require('./routes/api/financial/integrate-documents'));
app.use('/api/financial/ocr-document', require('./routes/api/financial/ocr-document'));
app.use('/api/integration/external-systems', require('./routes/api/integration/external-systems'));
app.use('/api/config/api-key', require('./routes/api/config/api-key'));

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error(`Unhandled error: ${err.message}`, err);

  res.status(500).json({
    error: 'Server error',
    detail: process.env.NODE_ENV === 'production' ? 'An unexpected error occurred' : err.message
  });
});

// Initialize services
const auditService = require('./services/security/auditService');
const dataRetentionService = require('./services/security/dataRetentionService');
const gdprService = require('./services/security/gdprService');
const performanceMonitor = require('./services/performance/performanceMonitor');
const cacheService = require('./services/cache/cacheService');

// Initialize services
async function initServices() {
  try {
    // Initialize audit logging
    await auditService.initAuditLogging();

    // Initialize data retention service
    await dataRetentionService.initDataRetention();

    // Initialize GDPR service
    await gdprService.initGdprService();

    // Start performance monitoring
    performanceMonitor.startMonitoring();

    logger.info('All services initialized successfully');
  } catch (error) {
    logger.error(`Error initializing services: ${error.message}`, error);
  }
}

// Start server
app.listen(PORT, () => {
  logger.info(`Server running on port ${PORT}`);

  // Initialize services
  initServices();
});
