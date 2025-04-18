/**
 * Export Routes
 * 
 * Handles data export routes.
 */

const express = require('express');
const router = express.Router();
const exportController = require('../../controllers/exportController');
const { verifyToken } = require('../../middleware/authMiddleware');

// Apply authentication middleware to all routes
router.use(verifyToken);

/**
 * @route POST /api/export/:id
 * @description Export document data
 * @access Private
 */
router.post('/:id', exportController.exportDocument);

/**
 * @route GET /api/export/formats
 * @description Get export formats
 * @access Private
 */
router.get('/formats', exportController.getExportFormats);

module.exports = router;
