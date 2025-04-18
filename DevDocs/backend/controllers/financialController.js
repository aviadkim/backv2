/**
 * Financial Controller
 * 
 * Handles financial data analysis requests for documents.
 */

const FinancialDataAnalyzerAgent = require('../agents/FinancialDataAnalyzerAgent');
const Document = require('../models/Document');
const logger = require('../utils/logger');
const { asyncHandler } = require('../middleware/errorMiddleware');
const { BadRequestError, NotFoundError } = require('../middleware/errorMiddleware');

// Initialize agents
const financialDataAnalyzerAgent = new FinancialDataAnalyzerAgent();

/**
 * Analyze financial data in a document
 * @route POST /api/financial/analyze/:id
 * @access Private
 */
const analyzeFinancialData = asyncHandler(async (req, res) => {
  const documentId = req.params.id;
  const options = req.body.options || {};
  
  // Get document
  const document = await Document.findById(documentId);
  
  // Update document status
  await Document.update(documentId, {
    processingStatus: 'financial_analysis_processing'
  });
  
  try {
    // Analyze financial data
    const result = await financialDataAnalyzerAgent.processDocument(documentId, options);
    
    // Update document status
    await Document.update(documentId, {
      processingStatus: 'financial_analysis_completed'
    });
    
    res.json({
      status: 'success',
      data: {
        documentId,
        result
      }
    });
  } catch (error) {
    // Update document status
    await Document.update(documentId, {
      processingStatus: 'financial_analysis_failed',
      processingError: error.message
    });
    
    logger.error(`Financial analysis failed for document ${documentId}:`, error);
    
    throw new Error(`Financial analysis failed: ${error.message}`);
  }
});

/**
 * Get financial data for a document
 * @route GET /api/financial/data/:id
 * @access Private
 */
const getFinancialData = asyncHandler(async (req, res) => {
  const documentId = req.params.id;
  
  // Get document data
  const data = await Document.getData(documentId, 'financial_data');
  
  if (!data || data.length === 0) {
    throw new NotFoundError('Financial data not found for this document');
  }
  
  res.json({
    status: 'success',
    data: {
      documentId,
      results: data
    }
  });
});

/**
 * Get portfolio summary for a document
 * @route GET /api/financial/portfolio/:id
 * @access Private
 */
const getPortfolioSummary = asyncHandler(async (req, res) => {
  const documentId = req.params.id;
  
  // Get document data
  const data = await Document.getData(documentId, 'financial_data');
  
  if (!data || data.length === 0) {
    throw new NotFoundError('Financial data not found for this document');
  }
  
  // Get latest financial data
  const financialData = data[0].content;
  
  // Extract portfolio summary
  const summary = {
    documentId,
    totalValue: financialData.portfolio.total_value,
    currency: financialData.portfolio.currency,
    totalSecurities: financialData.metrics.total_securities,
    totalAssetClasses: financialData.metrics.total_asset_classes,
    assetAllocation: financialData.portfolio.asset_allocation,
    topHoldings: financialData.portfolio.securities
      .sort((a, b) => b.value - a.value)
      .slice(0, 10)
      .map(security => ({
        name: security.name,
        isin: security.isin,
        value: security.value,
        percentage: security.value / financialData.portfolio.total_value
      }))
  };
  
  res.json({
    status: 'success',
    data: summary
  });
});

/**
 * Get securities for a document
 * @route GET /api/financial/securities/:id
 * @access Private
 */
const getSecurities = asyncHandler(async (req, res) => {
  const documentId = req.params.id;
  
  // Get document data
  const data = await Document.getData(documentId, 'financial_data');
  
  if (!data || data.length === 0) {
    throw new NotFoundError('Financial data not found for this document');
  }
  
  // Get latest financial data
  const financialData = data[0].content;
  
  // Extract securities
  const securities = financialData.portfolio.securities.map(security => ({
    id: security.id,
    name: security.name,
    isin: security.isin,
    quantity: security.quantity,
    price: security.price,
    value: security.value,
    percentage: security.value / financialData.portfolio.total_value
  }));
  
  res.json({
    status: 'success',
    data: {
      documentId,
      totalValue: financialData.portfolio.total_value,
      currency: financialData.portfolio.currency,
      securities
    }
  });
});

/**
 * Get asset allocation for a document
 * @route GET /api/financial/asset-allocation/:id
 * @access Private
 */
const getAssetAllocation = asyncHandler(async (req, res) => {
  const documentId = req.params.id;
  
  // Get document data
  const data = await Document.getData(documentId, 'financial_data');
  
  if (!data || data.length === 0) {
    throw new NotFoundError('Financial data not found for this document');
  }
  
  // Get latest financial data
  const financialData = data[0].content;
  
  // Extract asset allocation
  const assetAllocation = Object.entries(financialData.portfolio.asset_allocation).map(([assetClass, data]) => ({
    assetClass,
    percentage: data.percentage,
    value: data.value
  }));
  
  res.json({
    status: 'success',
    data: {
      documentId,
      totalValue: financialData.portfolio.total_value,
      currency: financialData.portfolio.currency,
      assetAllocation
    }
  });
});

module.exports = {
  analyzeFinancialData,
  getFinancialData,
  getPortfolioSummary,
  getSecurities,
  getAssetAllocation
};
