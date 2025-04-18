/**
 * Comparison Routes
 * 
 * Handles document comparison routes.
 */

const express = require('express');
const router = express.Router();
const comparisonController = require('../../controllers/comparisonController');
const { verifyToken } = require('../../middleware/authMiddleware');

// Apply authentication middleware to all routes
router.use(verifyToken);

/**
 * @route POST /api/comparison/compare
 * @description Compare two documents
 * @access Private
 */
router.post('/compare', comparisonController.compareDocuments);

/**
 * @route GET /api/comparison/:id
 * @description Get comparison result
 * @access Private
 */
router.get('/:id', comparisonController.getComparisonResult);

/**
 * @route GET /api/comparison/history/:id
 * @description Get comparison history for a document
 * @access Private
 */
router.get('/history/:id', comparisonController.getComparisonHistory);

module.exports = router;
