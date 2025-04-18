/**
 * Financial Routes
 * 
 * Handles financial data analysis routes.
 */

const express = require('express');
const router = express.Router();
const financialController = require('../../controllers/financialController');
const { verifyToken } = require('../../middleware/authMiddleware');

// Apply authentication middleware to all routes
router.use(verifyToken);

/**
 * @route POST /api/financial/analyze/:id
 * @description Analyze financial data in a document
 * @access Private
 */
router.post('/analyze/:id', financialController.analyzeFinancialData);

/**
 * @route GET /api/financial/data/:id
 * @description Get financial data for a document
 * @access Private
 */
router.get('/data/:id', financialController.getFinancialData);

/**
 * @route GET /api/financial/portfolio/:id
 * @description Get portfolio summary for a document
 * @access Private
 */
router.get('/portfolio/:id', financialController.getPortfolioSummary);

/**
 * @route GET /api/financial/securities/:id
 * @description Get securities for a document
 * @access Private
 */
router.get('/securities/:id', financialController.getSecurities);

/**
 * @route GET /api/financial/asset-allocation/:id
 * @description Get asset allocation for a document
 * @access Private
 */
router.get('/asset-allocation/:id', financialController.getAssetAllocation);

module.exports = router;
