/**
 * OCR Document API
 * 
 * Handles OCR processing of financial documents.
 */

const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs').promises;
const logger = require('../../../utils/logger');
const { HebrewOCRAgent } = require('../../../services/agents');

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: async (req, file, cb) => {
    const uploadDir = path.join(process.cwd(), 'uploads');
    try {
      await fs.mkdir(uploadDir, { recursive: true });
      cb(null, uploadDir);
    } catch (error) {
      cb(error);
    }
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage,
  limits: {
    fileSize: 10 * 1024 * 1024 // 10 MB
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['.pdf', '.png', '.jpg', '.jpeg', '.tif', '.tiff'];
    const ext = path.extname(file.originalname).toLowerCase();
    
    if (allowedTypes.includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only PDF, PNG, JPG, and TIFF files are allowed.'));
    }
  }
});

/**
 * @route POST /api/financial/ocr-document
 * @desc Process a document with OCR
 * @access Public
 */
router.post('/', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }
    
    const filePath = req.file.path;
    const options = req.body.options ? JSON.parse(req.body.options) : {};
    
    logger.info(`Processing OCR for file: ${req.file.originalname}`);
    
    // Create a HebrewOCRAgent instance
    const ocrAgent = new HebrewOCRAgent({
      apiKey: process.env.OPENROUTER_API_KEY,
      enhanceText: options.enhanceText !== false,
      detectOrientation: options.detectOrientation !== false,
      detectHandwriting: options.detectHandwriting !== false,
      outputFormat: options.outputFormat || 'text',
      confidenceThreshold: options.confidenceThreshold || 70
    });
    
    // Process the document
    const documentBuffer = await fs.readFile(filePath);
    const ocrResult = await ocrAgent.processDocument(documentBuffer, {
      includeHOCR: options.includeHOCR === true
    });
    
    // Clean up the uploaded file
    await fs.unlink(filePath);
    
    // Return the OCR result
    return res.status(200).json({
      filename: req.file.originalname,
      processed_at: new Date().toISOString(),
      ...ocrResult
    });
  } catch (error) {
    logger.error(`Error processing OCR: ${error.message}`, error);
    
    // Clean up the uploaded file if it exists
    if (req.file && req.file.path) {
      try {
        await fs.unlink(req.file.path);
      } catch (unlinkError) {
        logger.error(`Error deleting uploaded file: ${unlinkError.message}`);
      }
    }
    
    return res.status(500).json({ error: 'Error processing OCR', detail: error.message });
  }
});

/**
 * @route POST /api/financial/ocr-text
 * @desc Enhance OCR text
 * @access Public
 */
router.post('/enhance', async (req, res) => {
  try {
    const { text } = req.body;
    
    if (!text) {
      return res.status(400).json({ error: 'Text is required' });
    }
    
    logger.info('Enhancing OCR text');
    
    // Create a HebrewOCRAgent instance
    const ocrAgent = new HebrewOCRAgent({
      apiKey: process.env.OPENROUTER_API_KEY
    });
    
    // Enhance the text
    const enhancedText = await ocrAgent._enhanceText(text);
    
    // Return the enhanced text
    return res.status(200).json({
      original_text: text,
      enhanced_text: enhancedText,
      processed_at: new Date().toISOString()
    });
  } catch (error) {
    logger.error(`Error enhancing OCR text: ${error.message}`, error);
    return res.status(500).json({ error: 'Error enhancing OCR text', detail: error.message });
  }
});

module.exports = router;
