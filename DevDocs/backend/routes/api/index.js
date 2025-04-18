/**
 * API Routes
 * 
 * Main entry point for all API routes.
 */

const express = require('express');
const router = express.Router();

// Import route modules
const authRoutes = require('./auth');
const healthRoutes = require('./health');

// Mount routes
router.use('/auth', authRoutes);
router.use('/health', healthRoutes);

// Add more routes as needed
// router.use('/documents', documentRoutes);
// router.use('/financial', financialRoutes);
// router.use('/organizations', organizationRoutes);

module.exports = router;
