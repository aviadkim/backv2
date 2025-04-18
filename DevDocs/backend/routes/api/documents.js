/**
 * Document Routes
 * 
 * Handles document upload, retrieval, and management routes.
 */

const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { promisify } = require('util');
const documentController = require('../../controllers/documentController');
const { verifyToken } = require('../../middleware/authMiddleware');
const config = require('../../config');

// Create temp directory if it doesn't exist
const mkdir = promisify(fs.mkdir);
mkdir(config.upload.tempDir, { recursive: true }).catch(err => {
  console.error('Error creating temp directory:', err);
});

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, config.upload.tempDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = `${Date.now()}-${Math.round(Math.random() * 1E9)}`;
    cb(null, `${uniqueSuffix}-${file.originalname}`);
  }
});

const fileFilter = (req, file, cb) => {
  // Check file type
  const fileType = path.extname(file.originalname).toLowerCase();
  const allowedTypes = ['.pdf', '.xlsx', '.xls', '.csv', '.jpg', '.jpeg', '.png'];
  
  if (allowedTypes.includes(fileType)) {
    cb(null, true);
  } else {
    cb(new Error(`Invalid file type. Allowed types: ${allowedTypes.join(', ')}`), false);
  }
};

const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: config.upload.maxFileSize
  }
});

// Apply authentication middleware to all routes
router.use(verifyToken);

/**
 * @route POST /api/documents
 * @description Upload a document
 * @access Private
 */
router.post('/', upload.single('file'), documentController.uploadDocument);

/**
 * @route GET /api/documents
 * @description Get all documents
 * @access Private
 */
router.get('/', documentController.getDocuments);

/**
 * @route GET /api/documents/:id
 * @description Get a document by ID
 * @access Private
 */
router.get('/:id', documentController.getDocumentById);

/**
 * @route PUT /api/documents/:id
 * @description Update a document
 * @access Private
 */
router.put('/:id', documentController.updateDocument);

/**
 * @route DELETE /api/documents/:id
 * @description Delete a document
 * @access Private
 */
router.delete('/:id', documentController.deleteDocument);

/**
 * @route GET /api/documents/:id/download
 * @description Download a document
 * @access Private
 */
router.get('/:id/download', documentController.downloadDocument);

/**
 * @route GET /api/documents/:id/data
 * @description Get document data
 * @access Private
 */
router.get('/:id/data', documentController.getDocumentData);

/**
 * @route POST /api/documents/:id/data
 * @description Add document data
 * @access Private
 */
router.post('/:id/data', documentController.addDocumentData);

/**
 * @route POST /api/documents/:id/process
 * @description Process a document
 * @access Private
 */
router.post('/:id/process', documentController.processDocument);

module.exports = router;
