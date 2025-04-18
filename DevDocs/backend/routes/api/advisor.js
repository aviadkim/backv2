/**
 * Advisor Routes
 * 
 * Handles financial advisor routes.
 */

const express = require('express');
const router = express.Router();
const advisorController = require('../../controllers/advisorController');
const { verifyToken } = require('../../middleware/authMiddleware');

// Apply authentication middleware to all routes
router.use(verifyToken);

/**
 * @route POST /api/advisor/analyze/:id
 * @description Analyze portfolio and provide recommendations
 * @access Private
 */
router.post('/analyze/:id', advisorController.analyzePortfolio);

/**
 * @route GET /api/advisor/analysis/:id
 * @description Get advisor analysis for a document
 * @access Private
 */
router.get('/analysis/:id', advisorController.getAdvisorAnalysis);

/**
 * @route GET /api/advisor/recommendations/:id
 * @description Get recommendations for a document
 * @access Private
 */
router.get('/recommendations/:id', advisorController.getRecommendations);

/**
 * @route GET /api/advisor/risk/:id
 * @description Get risk analysis for a document
 * @access Private
 */
router.get('/risk/:id', advisorController.getRiskAnalysis);

module.exports = router;
