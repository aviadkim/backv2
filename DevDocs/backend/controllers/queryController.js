/**
 * Query Controller
 * 
 * Handles query requests for documents.
 */

const QueryEngineAgent = require('../agents/QueryEngineAgent');
const Document = require('../models/Document');
const logger = require('../utils/logger');
const { asyncHandler } = require('../middleware/errorMiddleware');
const { BadRequestError, NotFoundError } = require('../middleware/errorMiddleware');

// Initialize agents
const queryEngineAgent = new QueryEngineAgent();

/**
 * Answer a query about a document
 * @route POST /api/query/answer/:id
 * @access Private
 */
const answerQuery = asyncHandler(async (req, res) => {
  const documentId = req.params.id;
  const { query } = req.body;
  const options = req.body.options || {};
  
  // Validate query
  if (!query) {
    throw new BadRequestError('Query is required');
  }
  
  // Get document
  const document = await Document.findById(documentId);
  
  try {
    // Answer query
    const result = await queryEngineAgent.answerQuery(documentId, query, options);
    
    res.json({
      status: 'success',
      data: {
        documentId,
        query,
        answer: result.answer,
        sources: result.sources,
        timestamp: result.timestamp
      }
    });
  } catch (error) {
    logger.error(`Query answering failed for document ${documentId}:`, error);
    
    throw new Error(`Query answering failed: ${error.message}`);
  }
});

/**
 * Get previous queries for a document
 * @route GET /api/query/history/:id
 * @access Private
 */
const getQueryHistory = asyncHandler(async (req, res) => {
  const documentId = req.params.id;
  
  // Get document
  const document = await Document.findById(documentId);
  
  try {
    // Get previous queries
    const queries = await queryEngineAgent.getPreviousQueries(documentId);
    
    res.json({
      status: 'success',
      data: {
        documentId,
        queries
      }
    });
  } catch (error) {
    logger.error(`Getting query history failed for document ${documentId}:`, error);
    
    throw new Error(`Getting query history failed: ${error.message}`);
  }
});

module.exports = {
  answerQuery,
  getQueryHistory
};
