/**
 * Advisor Controller
 * 
 * Handles financial advisor requests.
 */

const FinancialAdvisorAgent = require('../agents/FinancialAdvisorAgent');
const Document = require('../models/Document');
const logger = require('../utils/logger');
const { asyncHandler } = require('../middleware/errorMiddleware');
const { BadRequestError, NotFoundError } = require('../middleware/errorMiddleware');

// Initialize agents
const financialAdvisorAgent = new FinancialAdvisorAgent();

/**
 * Analyze portfolio and provide recommendations
 * @route POST /api/advisor/analyze/:id
 * @access Private
 */
const analyzePortfolio = asyncHandler(async (req, res) => {
  const documentId = req.params.id;
  const options = req.body.options || {};
  
  // Get document
  const document = await Document.findById(documentId);
  
  try {
    // Analyze portfolio
    const result = await financialAdvisorAgent.analyzePortfolio(documentId, options);
    
    res.json({
      status: 'success',
      data: {
        documentId,
        result
      }
    });
  } catch (error) {
    logger.error(`Portfolio analysis failed for document ${documentId}:`, error);
    
    throw new Error(`Portfolio analysis failed: ${error.message}`);
  }
});

/**
 * Get advisor analysis for a document
 * @route GET /api/advisor/analysis/:id
 * @access Private
 */
const getAdvisorAnalysis = asyncHandler(async (req, res) => {
  const documentId = req.params.id;
  
  // Get document
  const document = await Document.findById(documentId);
  
  try {
    // Get advisor analysis
    const analysis = await financialAdvisorAgent.getAdvisorAnalysis(documentId);
    
    res.json({
      status: 'success',
      data: {
        documentId,
        analysis
      }
    });
  } catch (error) {
    logger.error(`Getting advisor analysis failed for document ${documentId}:`, error);
    
    throw new Error(`Getting advisor analysis failed: ${error.message}`);
  }
});

/**
 * Get recommendations for a document
 * @route GET /api/advisor/recommendations/:id
 * @access Private
 */
const getRecommendations = asyncHandler(async (req, res) => {
  const documentId = req.params.id;
  
  // Get document
  const document = await Document.findById(documentId);
  
  try {
    // Get advisor analysis
    const analysis = await financialAdvisorAgent.getAdvisorAnalysis(documentId);
    
    // Extract recommendations
    const recommendations = analysis.recommendations || [];
    
    res.json({
      status: 'success',
      data: {
        documentId,
        recommendations
      }
    });
  } catch (error) {
    logger.error(`Getting recommendations failed for document ${documentId}:`, error);
    
    throw new Error(`Getting recommendations failed: ${error.message}`);
  }
});

/**
 * Get risk analysis for a document
 * @route GET /api/advisor/risk/:id
 * @access Private
 */
const getRiskAnalysis = asyncHandler(async (req, res) => {
  const documentId = req.params.id;
  
  // Get document
  const document = await Document.findById(documentId);
  
  try {
    // Get advisor analysis
    const analysis = await financialAdvisorAgent.getAdvisorAnalysis(documentId);
    
    // Extract risk analysis
    const riskAnalysis = analysis.risk_analysis || {};
    
    res.json({
      status: 'success',
      data: {
        documentId,
        riskAnalysis
      }
    });
  } catch (error) {
    logger.error(`Getting risk analysis failed for document ${documentId}:`, error);
    
    throw new Error(`Getting risk analysis failed: ${error.message}`);
  }
});

module.exports = {
  analyzePortfolio,
  getAdvisorAnalysis,
  getRecommendations,
  getRiskAnalysis
};
