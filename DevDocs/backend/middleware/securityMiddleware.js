/**
 * Security Middleware
 * 
 * Provides security-related middleware for the application:
 * - CORS configuration
 * - Security headers (Helmet)
 * - Rate limiting
 * - Content Security Policy
 */

const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const logger = require('../utils/logger');

// CORS configuration
const corsOptions = {
  origin: (origin, callback) => {
    // Allow requests with no origin (like mobile apps, curl, etc.)
    if (!origin) return callback(null, true);
    
    // Define allowed origins
    const allowedOrigins = [
      // Development origins
      'http://localhost:3000',
      'http://localhost:3001',
      'http://localhost:3002',
      
      // Production origins
      process.env.FRONTEND_URL,
      process.env.PRODUCTION_URL,
      'https://findoc-analyzer.web.app'
    ].filter(Boolean); // Remove undefined/null values
    
    // Check if the origin is allowed
    if (allowedOrigins.indexOf(origin) !== -1 || process.env.NODE_ENV === 'development') {
      callback(null, true);
    } else {
      logger.warn(`CORS blocked request from origin: ${origin}`);
      callback(new Error('Not allowed by CORS'));
    }
  },
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  credentials: true,
  maxAge: 86400 // 24 hours
};

// Rate limiting configuration
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  standardHeaders: true,
  legacyHeaders: false,
  message: 'Too many requests from this IP, please try again after 15 minutes',
  skip: (req) => process.env.NODE_ENV === 'development', // Skip rate limiting in development
  handler: (req, res) => {
    logger.warn(`Rate limit exceeded for IP: ${req.ip}`);
    res.status(429).json({
      status: 'error',
      message: 'Too many requests, please try again later'
    });
  }
});

// Content Security Policy configuration
const cspOptions = {
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
    styleSrc: ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
    fontSrc: ["'self'", 'https://fonts.gstatic.com'],
    imgSrc: ["'self'", 'data:', 'blob:'],
    connectSrc: ["'self'", process.env.SUPABASE_URL, 'https://api.openrouter.ai'],
    frameSrc: ["'self'"],
    objectSrc: ["'none'"],
    upgradeInsecureRequests: []
  }
};

// Export middleware functions
module.exports = {
  // Apply CORS
  cors: () => cors(corsOptions),
  
  // Apply Helmet security headers
  helmet: () => helmet({
    contentSecurityPolicy: process.env.NODE_ENV === 'production' ? cspOptions : false
  }),
  
  // Apply rate limiting
  rateLimit: () => apiLimiter,
  
  // Apply all security middleware
  applyAll: (app) => {
    app.use(cors(corsOptions));
    app.use(helmet({
      contentSecurityPolicy: process.env.NODE_ENV === 'production' ? cspOptions : false
    }));
    app.use('/api/', apiLimiter);
    
    logger.info('Security middleware applied');
  }
};
