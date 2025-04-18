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

// Mount routes
router.use('/auth', authRoutes);
router.use('/health', healthRoutes);
router.use('/documents', documentRoutes);
router.use('/ocr', ocrRoutes);

// Add more routes as needed
// router.use('/financial', financialRoutes);
// router.use('/organizations', organizationRoutes);

module.exports = router;
