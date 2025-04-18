/**
 * FinDoc Backend Server
 *
 * Main entry point for the backend server
 */

const express = require('express');
const morgan = require('morgan');
const cookieParser = require('cookie-parser');
const path = require('path');
const logger = require('./utils/logger');
const config = require('./config');
const supabase = require('./db/supabase');

// Initialize Express app
const app = express();
const PORT = config.server.port;

// Make Supabase client available to all routes
try {
  app.locals.supabase = supabase.getClient();
} catch (error) {
  logger.warn('Supabase client not available:', error.message);
}

// Import middleware
const securityMiddleware = require('./middleware/securityMiddleware');
const authMiddleware = require('./middleware/authMiddleware');

// Initialize services
const auditService = require('./services/security/auditService');
const dataRetentionService = require('./services/security/dataRetentionService');
const gdprService = require('./services/security/gdprService');
const performanceMonitor = require('./services/performance/performanceMonitor');
const cacheService = require('./services/cache/cacheService');
const storageService = require('./services/storage/supabaseStorageService');

// Middleware
securityMiddleware.applyAll(app); // Apply security middleware (CORS, Helmet, Rate Limiting)
app.use(express.json()); // Parse JSON bodies
app.use(express.urlencoded({ extended: true })); // Parse URL-encoded bodies
app.use(cookieParser()); // Parse cookies
app.use(morgan('combined', { stream: { write: message => logger.info(message.trim()) } })); // HTTP request logging
app.use(performanceMonitor.performanceMiddleware()); // Performance monitoring

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));
app.use('/output', express.static(path.join(__dirname, 'output'))); // Serve output files

// API Routes
app.use('/api', require('./routes/api'));

// Legacy API Routes (for backward compatibility)
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

// Enhanced Processing Routes
app.use('/api/enhanced', require('./routes/enhancedProcessingRoutes'));

// Import error handling middleware
const { errorHandler, notFoundHandler } = require('./middleware/errorMiddleware');

// 404 handler - must be after all routes
app.use(notFoundHandler);

// Error handling middleware - must be the last middleware
app.use(errorHandler);

// Initialize services
async function initServices() {
  try {
    // Initialize audit logging
    await auditService.initAuditLogging();

    // Initialize data retention service
    await dataRetentionService.initDataRetention();

    // Initialize GDPR service
    await gdprService.initGdprService();

    // Initialize cache service
    cacheService.initCacheService();

    // Initialize storage service
    await storageService.initStorage();

    // Start performance monitoring
    performanceMonitor.startMonitoring();

    // Check database connection
    const dbConnected = await supabase.checkConnection();
    if (dbConnected) {
      logger.info('Database connection successful');
    } else {
      logger.warn('Database connection failed');
    }

    logger.info('All services initialized successfully');
  } catch (error) {
    logger.error(`Error initializing services: ${error.message}`, error);
  }
}

// Start server
const server = app.listen(PORT, () => {
  logger.info(`Server running on port ${PORT}`);

  // Initialize services
  initServices();
});

// Graceful shutdown handler
const gracefulShutdown = (signal) => {
  logger.info(`Received ${signal}. Shutting down gracefully...`);

  // Close server
  server.close(() => {
    logger.info('HTTP server closed');

    // Perform cleanup
    try {
      // Flush cache
      cacheService.flush();
      logger.info('Cache flushed');

      // Stop performance monitoring
      performanceMonitor.stopMonitoring();
      logger.info('Performance monitoring stopped');

      logger.info('Cleanup completed');
      process.exit(0);
    } catch (error) {
      logger.error('Error during cleanup:', error);
      process.exit(1);
    }
  });

  // Force shutdown after timeout
  setTimeout(() => {
    logger.error('Forced shutdown due to timeout');
    process.exit(1);
  }, 10000); // 10 seconds
};

// Handle termination signals
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Handle uncaught exceptions and unhandled rejections
process.on('uncaughtException', (error) => {
  logger.error('Uncaught exception:', error);
  gracefulShutdown('uncaughtException');
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled rejection at:', promise, 'reason:', reason);
  // Don't shut down for unhandled rejections
});
