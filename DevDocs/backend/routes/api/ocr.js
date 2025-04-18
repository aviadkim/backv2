/**
 * OCR Routes
 * 
 * Handles OCR processing routes.
 */

const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { promisify } = require('util');
const ocrController = require('../../controllers/ocrController');
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
  const allowedTypes = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'];
  
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
 * @route POST /api/ocr/process/:id
 * @description Process a document with OCR
 * @access Private
 */
router.post('/process/:id', ocrController.processDocumentWithOcr);

/**
 * @route POST /api/ocr/detect-tables/:id
 * @description Detect tables in a document
 * @access Private
 */
router.post('/detect-tables/:id', ocrController.detectTables);

/**
 * @route POST /api/ocr/process-image
 * @description Process an image with OCR
 * @access Private
 */
router.post('/process-image', upload.single('image'), ocrController.processImageWithOcr);

/**
 * @route GET /api/ocr/results/:id
 * @description Get OCR results for a document
 * @access Private
 */
router.get('/results/:id', ocrController.getOcrResults);

/**
 * @route GET /api/ocr/table-results/:id
 * @description Get table detection results for a document
 * @access Private
 */
router.get('/table-results/:id', ocrController.getTableResults);

module.exports = router;
