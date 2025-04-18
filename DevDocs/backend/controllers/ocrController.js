/**
 * OCR Controller
 * 
 * Handles OCR processing requests for documents.
 */

const HebrewOCRAgent = require('../agents/HebrewOCRAgent');
const FinancialTableDetectorAgent = require('../agents/FinancialTableDetectorAgent');
const Document = require('../models/Document');
const logger = require('../utils/logger');
const { asyncHandler } = require('../middleware/errorMiddleware');
const { BadRequestError, NotFoundError } = require('../middleware/errorMiddleware');
const path = require('path');
const fs = require('fs');
const { promisify } = require('util');
const config = require('../config');

// Promisify fs functions
const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const unlink = promisify(fs.unlink);

// Initialize agents
const hebrewOCRAgent = new HebrewOCRAgent();
const financialTableDetectorAgent = new FinancialTableDetectorAgent();

/**
 * Process a document with OCR
 * @route POST /api/ocr/process/:id
 * @access Private
 */
const processDocumentWithOcr = asyncHandler(async (req, res) => {
  const documentId = req.params.id;
  const options = req.body.options || {};
  
  // Get document
  const document = await Document.findById(documentId);
  
  // Update document status
  await Document.update(documentId, {
    processingStatus: 'ocr_processing'
  });
  
  try {
    // Process document with OCR
    const result = await hebrewOCRAgent.processDocument(documentId, options);
    
    // Update document status
    await Document.update(documentId, {
      processingStatus: 'ocr_completed'
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
      processingStatus: 'ocr_failed',
      processingError: error.message
    });
    
    logger.error(`OCR processing failed for document ${documentId}:`, error);
    
    throw new Error(`OCR processing failed: ${error.message}`);
  }
});

/**
 * Detect tables in a document
 * @route POST /api/ocr/detect-tables/:id
 * @access Private
 */
const detectTables = asyncHandler(async (req, res) => {
  const documentId = req.params.id;
  const options = req.body.options || {};
  
  // Get document
  const document = await Document.findById(documentId);
  
  // Update document status
  await Document.update(documentId, {
    processingStatus: 'table_detection_processing'
  });
  
  try {
    // Detect tables in document
    const result = await financialTableDetectorAgent.processDocument(documentId, options);
    
    // Update document status
    await Document.update(documentId, {
      processingStatus: 'table_detection_completed'
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
      processingStatus: 'table_detection_failed',
      processingError: error.message
    });
    
    logger.error(`Table detection failed for document ${documentId}:`, error);
    
    throw new Error(`Table detection failed: ${error.message}`);
  }
});

/**
 * Process an image with OCR
 * @route POST /api/ocr/process-image
 * @access Private
 */
const processImageWithOcr = asyncHandler(async (req, res) => {
  // Check if file was uploaded
  if (!req.file) {
    throw new BadRequestError('No file uploaded');
  }
  
  // Check file type
  const fileType = path.extname(req.file.originalname).toLowerCase();
  const allowedTypes = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'];
  
  if (!allowedTypes.includes(fileType)) {
    throw new BadRequestError(`Invalid file type. Allowed types: ${allowedTypes.join(', ')}`);
  }
  
  // Get options
  const options = req.body.options ? JSON.parse(req.body.options) : {};
  
  try {
    // Process image with OCR
    const result = await hebrewOCRAgent.processImage(req.file.path, options);
    
    // Clean up temporary file
    await unlink(req.file.path);
    
    res.json({
      status: 'success',
      data: {
        result
      }
    });
  } catch (error) {
    // Clean up temporary file
    try {
      await unlink(req.file.path);
    } catch (unlinkError) {
      logger.warn(`Error deleting temporary file: ${unlinkError.message}`);
    }
    
    logger.error('OCR processing failed for image:', error);
    
    throw new Error(`OCR processing failed: ${error.message}`);
  }
});

/**
 * Get OCR results for a document
 * @route GET /api/ocr/results/:id
 * @access Private
 */
const getOcrResults = asyncHandler(async (req, res) => {
  const documentId = req.params.id;
  
  // Get document data
  const data = await Document.getData(documentId, 'ocr');
  
  if (!data || data.length === 0) {
    throw new NotFoundError('OCR results not found for this document');
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
 * Get table detection results for a document
 * @route GET /api/ocr/table-results/:id
 * @access Private
 */
const getTableResults = asyncHandler(async (req, res) => {
  const documentId = req.params.id;
  
  // Get document data
  const data = await Document.getData(documentId, 'tables');
  
  if (!data || data.length === 0) {
    throw new NotFoundError('Table detection results not found for this document');
  }
  
  res.json({
    status: 'success',
    data: {
      documentId,
      results: data
    }
  });
});

module.exports = {
  processDocumentWithOcr,
  detectTables,
  processImageWithOcr,
  getOcrResults,
  getTableResults
};
