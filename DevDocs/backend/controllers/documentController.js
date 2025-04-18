/**
 * Document Controller
 *
 * Handles document upload, retrieval, and management.
 */

const Document = require('../models/Document');
const logger = require('../utils/logger');
const { asyncHandler } = require('../middleware/errorMiddleware');
const { BadRequestError, NotFoundError } = require('../middleware/errorMiddleware');
const path = require('path');
const fs = require('fs');
const { promisify } = require('util');
const config = require('../config');
const storageService = require('../services/storage/supabaseStorageService');

// Promisify fs functions
const readFile = promisify(fs.readFile);
const stat = promisify(fs.stat);

/**
 * Upload a document
 * @route POST /api/documents
 * @access Private
 */
const uploadDocument = asyncHandler(async (req, res) => {
  // Check if file was uploaded
  if (!req.file) {
    throw new BadRequestError('No file uploaded');
  }

  // Check file type
  const fileType = path.extname(req.file.originalname).toLowerCase();
  const allowedTypes = ['.pdf', '.xlsx', '.xls', '.csv', '.jpg', '.jpeg', '.png'];

  if (!allowedTypes.includes(fileType)) {
    throw new BadRequestError(`Invalid file type. Allowed types: ${allowedTypes.join(', ')}`);
  }

  // Check file size
  if (req.file.size > config.upload.maxFileSize) {
    throw new BadRequestError(`File too large. Maximum size: ${config.upload.maxFileSize / 1024 / 1024}MB`);
  }

  // Create document
  const document = await Document.create({
    name: req.body.name || req.file.originalname,
    description: req.body.description || '',
    organizationId: req.body.organizationId || req.user.organizationId,
    userId: req.user.id
  }, req.file);

  // Log document upload
  logger.info(`Document uploaded: ${document.id}`);

  res.status(201).json({
    status: 'success',
    data: {
      document
    }
  });
});

/**
 * Get all documents
 * @route GET /api/documents
 * @access Private
 */
const getDocuments = asyncHandler(async (req, res) => {
  const { page, limit, sortBy, sortOrder, status, search } = req.query;

  // Get documents by organization or user
  let result;

  if (req.query.organizationId) {
    result = await Document.getByOrganization(req.query.organizationId, {
      page: parseInt(page) || 1,
      limit: parseInt(limit) || 10,
      sortBy: sortBy || 'created_at',
      sortOrder: sortOrder || 'desc',
      status,
      search
    });
  } else {
    result = await Document.getByUser(req.user.id, {
      page: parseInt(page) || 1,
      limit: parseInt(limit) || 10,
      sortBy: sortBy || 'created_at',
      sortOrder: sortOrder || 'desc',
      status,
      search
    });
  }

  res.json({
    status: 'success',
    data: result
  });
});

/**
 * Get a document by ID
 * @route GET /api/documents/:id
 * @access Private
 */
const getDocumentById = asyncHandler(async (req, res) => {
  const document = await Document.findById(req.params.id);

  res.json({
    status: 'success',
    data: {
      document
    }
  });
});

/**
 * Update a document
 * @route PUT /api/documents/:id
 * @access Private
 */
const updateDocument = asyncHandler(async (req, res) => {
  const { name, description, status, processingStatus, processingError, metadata } = req.body;

  // Update document
  const document = await Document.update(req.params.id, {
    name,
    description,
    status,
    processingStatus,
    processingError,
    metadata
  });

  // Log document update
  logger.info(`Document updated: ${document.id}`);

  res.json({
    status: 'success',
    data: {
      document
    }
  });
});

/**
 * Delete a document
 * @route DELETE /api/documents/:id
 * @access Private
 */
const deleteDocument = asyncHandler(async (req, res) => {
  await Document.delete(req.params.id);

  // Log document deletion
  logger.info(`Document deleted: ${req.params.id}`);

  res.json({
    status: 'success',
    message: 'Document deleted successfully'
  });
});

/**
 * Download a document
 * @route GET /api/documents/:id/download
 * @access Private
 */
const downloadDocument = asyncHandler(async (req, res) => {
  const document = await Document.findById(req.params.id);

  // Check if document has storage metadata
  if (!document.metadata || !document.metadata.storage || !document.metadata.storage.path) {
    throw new NotFoundError('Document storage information not found');
  }

  try {
    // Get file from storage
    const fileBuffer = await storageService.downloadFile(document.metadata.storage.path);

    // Set content type and attachment header
    res.setHeader('Content-Type', document.contentType);
    res.setHeader('Content-Disposition', `attachment; filename="${document.name}${document.fileType}"`);

    // Send file
    res.send(fileBuffer);

    // Log document download
    logger.info(`Document downloaded: ${document.id}`);
  } catch (error) {
    logger.error(`Error downloading document: ${error.message}`);
    throw new NotFoundError('Document file not found');
  }
});

/**
 * Get document data
 * @route GET /api/documents/:id/data
 * @access Private
 */
const getDocumentData = asyncHandler(async (req, res) => {
  const { dataType } = req.query;

  const data = await Document.getData(req.params.id, dataType);

  res.json({
    status: 'success',
    data
  });
});

/**
 * Add document data
 * @route POST /api/documents/:id/data
 * @access Private
 */
const addDocumentData = asyncHandler(async (req, res) => {
  const { dataType, content } = req.body;

  if (!dataType || !content) {
    throw new BadRequestError('Data type and content are required');
  }

  const data = await Document.addData(req.params.id, dataType, content);

  // Log document data addition
  logger.info(`Document data added: ${data.id}`);

  res.status(201).json({
    status: 'success',
    data
  });
});

/**
 * Process a document
 * @route POST /api/documents/:id/process
 * @access Private
 */
const processDocument = asyncHandler(async (req, res) => {
  // Get document
  const document = await Document.findById(req.params.id);

  // Update document status
  await Document.update(req.params.id, {
    processingStatus: 'processing'
  });

  // TODO: Implement document processing
  // This would typically involve:
  // 1. Queue the document for processing
  // 2. Process the document asynchronously
  // 3. Update the document status when processing is complete

  // For now, just log the request
  logger.info(`Document processing requested: ${document.id}`);

  res.json({
    status: 'success',
    message: 'Document processing started',
    data: {
      documentId: document.id,
      processingStatus: 'processing'
    }
  });
});

module.exports = {
  uploadDocument,
  getDocuments,
  getDocumentById,
  updateDocument,
  deleteDocument,
  downloadDocument,
  getDocumentData,
  addDocumentData,
  processDocument
};
