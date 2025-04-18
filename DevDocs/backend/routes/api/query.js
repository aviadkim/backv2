/**
 * Query Routes
 * 
 * Handles query routes for documents.
 */

const express = require('express');
const router = express.Router();
const queryController = require('../../controllers/queryController');
const { verifyToken } = require('../../middleware/authMiddleware');

// Apply authentication middleware to all routes
router.use(verifyToken);

/**
 * @route POST /api/query/answer/:id
 * @description Answer a query about a document
 * @access Private
 */
router.post('/answer/:id', queryController.answerQuery);

/**
 * @route GET /api/query/history/:id
 * @description Get previous queries for a document
 * @access Private
 */
router.get('/history/:id', queryController.getQueryHistory);

module.exports = router;
