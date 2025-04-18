/**
 * Comparison Controller
 *
 * Handles document comparison requests.
 */

const DocumentComparisonAgent = require('../agents/DocumentComparisonAgent');
const Document = require('../models/Document');
const logger = require('../utils/logger');
const supabase = require('../db/supabase');
const { asyncHandler } = require('../middleware/errorMiddleware');
const { BadRequestError, NotFoundError } = require('../middleware/errorMiddleware');

// Initialize agents
const documentComparisonAgent = new DocumentComparisonAgent();

/**
 * Compare two documents
 * @route POST /api/comparison/compare
 * @access Private
 */
const compareDocuments = asyncHandler(async (req, res) => {
  const { documentId1, documentId2 } = req.body;
  const options = req.body.options || {};

  // Validate document IDs
  if (!documentId1 || !documentId2) {
    throw new BadRequestError('Both document IDs are required');
  }

  // Get documents
  const document1 = await Document.findById(documentId1);
  const document2 = await Document.findById(documentId2);

  try {
    // Compare documents
    const result = await documentComparisonAgent.compareDocuments(documentId1, documentId2, options);

    res.json({
      status: 'success',
      data: {
        documentId1,
        documentId2,
        result
      }
    });
  } catch (error) {
    logger.error(`Document comparison failed:`, error);

    throw new Error(`Document comparison failed: ${error.message}`);
  }
});

/**
 * Get comparison result
 * @route GET /api/comparison/:id
 * @access Private
 */
const getComparisonResult = asyncHandler(async (req, res) => {
  const comparisonId = req.params.id;

  // Get document data
  const client = supabase.getClient();
  const { data, error } = await client
    .from('document_data')
    .select('*')
    .eq('id', comparisonId)
    .eq('data_type', 'comparison')
    .single();

  if (error) {
    logger.error('Error getting comparison result:', error);
    throw new Error('Error getting comparison result');
  }

  if (!data) {
    throw new NotFoundError('Comparison result not found');
  }

  res.json({
    status: 'success',
    data: {
      id: data.id,
      documentId: data.document_id,
      result: data.content
    }
  });
});

/**
 * Get comparison history for a document
 * @route GET /api/comparison/history/:id
 * @access Private
 */
const getComparisonHistory = asyncHandler(async (req, res) => {
  const documentId = req.params.id;

  // Get document
  const document = await Document.findById(documentId);

  try {
    // Get comparison history
    const history = await documentComparisonAgent.getComparisonHistory(documentId);

    res.json({
      status: 'success',
      data: {
        documentId,
        history
      }
    });
  } catch (error) {
    logger.error(`Getting comparison history failed for document ${documentId}:`, error);

    throw new Error(`Getting comparison history failed: ${error.message}`);
  }
});

module.exports = {
  compareDocuments,
  getComparisonResult,
  getComparisonHistory
};
