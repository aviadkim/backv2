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
const documentRoutes = require('./documents');
const ocrRoutes = require('./ocr');
const financialRoutes = require('./financial');
const queryRoutes = require('./query');
const comparisonRoutes = require('./comparison');
const exportRoutes = require('./export');
const advisorRoutes = require('./advisor');

// Mount routes
router.use('/auth', authRoutes);
router.use('/health', healthRoutes);
router.use('/documents', documentRoutes);
router.use('/ocr', ocrRoutes);
router.use('/financial', financialRoutes);
router.use('/query', queryRoutes);
router.use('/comparison', comparisonRoutes);
router.use('/export', exportRoutes);
router.use('/advisor', advisorRoutes);

// Add more routes as needed
// router.use('/organizations', organizationRoutes);

module.exports = router;
