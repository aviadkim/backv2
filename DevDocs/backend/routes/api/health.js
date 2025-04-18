/**
 * Health Check API
 * 
 * Provides health check endpoints for the API.
 */

const express = require('express');
const router = express.Router();
const { createClient } = require('@supabase/supabase-js');
const logger = require('../../utils/logger');

/**
 * @route GET /api/health
 * @desc Get API health status
 * @access Public
 */
router.get('/', (req, res) => {
  try {
    return res.status(200).json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version || '1.0.0',
      environment: process.env.NODE_ENV || 'development'
    });
  } catch (error) {
    logger.error(`Error checking health: ${error.message}`, error);
    
    return res.status(500).json({ 
      status: 'error',
      error: error.message 
    });
  }
});

/**
 * @route GET /api/health/db
 * @desc Check database connection
 * @access Public
 */
router.get('/db', async (req, res) => {
  try {
    // Initialize Supabase client
    const supabaseUrl = process.env.SUPABASE_URL || 'https://dnjnsotemnfrjlotgved.supabase.co';
    const supabaseKey = process.env.SUPABASE_KEY || '';
    
    if (!supabaseKey) {
      return res.status(500).json({
        status: 'error',
        message: 'Supabase key is not configured'
      });
    }
    
    const supabase = createClient(supabaseUrl, supabaseKey);
    
    // Test database connection
    const { data, error } = await supabase.from('documents').select('id').limit(1);
    
    if (error) {
      throw new Error(`Database connection error: ${error.message}`);
    }
    
    return res.status(200).json({
      status: 'ok',
      message: 'Database connection successful',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error(`Error checking database health: ${error.message}`, error);
    
    return res.status(500).json({ 
      status: 'error',
      error: error.message 
    });
  }
});

/**
 * @route GET /api/health/dependencies
 * @desc Check dependencies status
 * @access Public
 */
router.get('/dependencies', async (req, res) => {
  try {
    // Check OpenRouter API key
    const openrouterApiKey = process.env.OPENROUTER_API_KEY || '';
    const openrouterStatus = openrouterApiKey ? 'configured' : 'not configured';
    
    // Check Supabase connection
    const supabaseUrl = process.env.SUPABASE_URL || 'https://dnjnsotemnfrjlotgved.supabase.co';
    const supabaseKey = process.env.SUPABASE_KEY || '';
    let supabaseStatus = 'not configured';
    
    if (supabaseKey) {
      try {
        const supabase = createClient(supabaseUrl, supabaseKey);
        const { data, error } = await supabase.from('documents').select('id').limit(1);
        
        supabaseStatus = error ? 'error' : 'connected';
      } catch (error) {
        supabaseStatus = 'error';
      }
    }
    
    return res.status(200).json({
      status: 'ok',
      dependencies: {
        openrouter: openrouterStatus,
        supabase: supabaseStatus
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error(`Error checking dependencies health: ${error.message}`, error);
    
    return res.status(500).json({ 
      status: 'error',
      error: error.message 
    });
  }
});

module.exports = router;
