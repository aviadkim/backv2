/**
 * Financial Document Processing API
 * 
 * Handles the processing of financial documents:
 * - Receives document uploads
 * - Processes documents through the pipeline
 * - Returns processing results
 */

const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const { processDocument } = require('../../../services/document-processing');
const logger = require('../../../utils/logger');

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(process.cwd(), 'uploads');
    
    // Create upload directory if it doesn't exist
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    // Generate a unique filename
    const uniqueId = uuidv4();
    const fileExt = path.extname(file.originalname);
    const fileName = `${uniqueId}${fileExt}`;
    
    cb(null, fileName);
  }
});

// Create multer upload instance
const upload = multer({
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB
  },
  fileFilter: (req, file, cb) => {
    // Accept only PDF, Excel, and CSV files
    const allowedExtensions = ['.pdf', '.xlsx', '.xls', '.csv'];
    const fileExt = path.extname(file.originalname).toLowerCase();
    
    if (allowedExtensions.includes(fileExt)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only PDF, Excel, and CSV files are allowed.'));
    }
  }
});

/**
 * @route POST /api/financial/process-document
 * @desc Process a financial document
 * @access Public
 */
router.post('/process-document', upload.single('file'), async (req, res) => {
  try {
    // Check if file was uploaded
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }
    
    // Get document type from request
    const documentType = req.body.document_type || 'financial';
    
    // Get language from request
    const language = req.body.language || 'en';
    
    // Get use_ai flag from request
    const useAI = req.body.use_ai !== 'false';
    
    // Get metadata from request
    const metadata = req.body.metadata ? JSON.parse(req.body.metadata) : {};
    
    // Process the document
    const result = await processDocument({
      filePath: req.file.path,
      documentType,
      language,
      useAI,
      metadata: {
        ...metadata,
        originalFilename: req.file.originalname,
        mimeType: req.file.mimetype,
        size: req.file.size
      }
    });
    
    // Clean up the uploaded file
    fs.unlinkSync(req.file.path);
    
    // Return the processing results
    return res.status(200).json(result);
  } catch (error) {
    logger.error(`Error processing document: ${error.message}`, error);
    
    // Clean up the uploaded file if it exists
    if (req.file && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }
    
    return res.status(500).json({ 
      error: 'Error processing document', 
      detail: error.message 
    });
  }
});

/**
 * @route GET /api/financial/documents
 * @desc Get a list of processed documents
 * @access Public
 */
router.get('/documents', async (req, res) => {
  try {
    // Get query parameters
    const limit = parseInt(req.query.limit) || 10;
    const offset = parseInt(req.query.offset) || 0;
    const documentType = req.query.document_type;
    
    // Create query
    let query = supabase
      .from('documents')
      .select('id, job_id, document_type, filename, processed_at, status, validation_errors, validation_warnings')
      .order('processed_at', { ascending: false })
      .range(offset, offset + limit - 1);
    
    // Add document type filter if provided
    if (documentType) {
      query = query.eq('document_type', documentType);
    }
    
    // Execute query
    const { data, error, count } = await query;
    
    if (error) {
      throw new Error(`Error fetching documents: ${error.message}`);
    }
    
    return res.status(200).json({
      documents: data,
      count: count,
      limit: limit,
      offset: offset
    });
  } catch (error) {
    logger.error(`Error fetching documents: ${error.message}`, error);
    
    return res.status(500).json({ 
      error: 'Error fetching documents', 
      detail: error.message 
    });
  }
});

/**
 * @route GET /api/financial/documents/:id
 * @desc Get a specific document by ID
 * @access Public
 */
router.get('/documents/:id', async (req, res) => {
  try {
    const documentId = req.params.id;
    
    // Get document
    const { data: document, error: documentError } = await supabase
      .from('documents')
      .select('*')
      .eq('id', documentId)
      .single();
    
    if (documentError) {
      throw new Error(`Error fetching document: ${documentError.message}`);
    }
    
    if (!document) {
      return res.status(404).json({ error: 'Document not found' });
    }
    
    // Get document text
    const { data: textData, error: textError } = await supabase
      .from('document_text')
      .select('text_content')
      .eq('document_id', documentId)
      .single();
    
    // Get document tables
    const { data: tables, error: tablesError } = await supabase
      .from('document_tables')
      .select('*')
      .eq('document_id', documentId);
    
    // Get document ISINs
    const { data: isins, error: isinsError } = await supabase
      .from('document_isins')
      .select('*')
      .eq('document_id', documentId);
    
    // Get portfolio data
    const { data: portfolio, error: portfolioError } = await supabase
      .from('portfolios')
      .select('*')
      .eq('document_id', documentId)
      .single();
    
    // Get securities
    let securities = [];
    if (portfolio) {
      const { data: securitiesData, error: securitiesError } = await supabase
        .from('securities')
        .select('*')
        .eq('portfolio_id', portfolio.id);
      
      if (!securitiesError) {
        securities = securitiesData;
      }
    }
    
    // Combine all data
    const result = {
      document,
      text: textData ? textData.text_content : null,
      tables: tables || [],
      isins: isins || [],
      portfolio: portfolio || null,
      securities: securities
    };
    
    return res.status(200).json(result);
  } catch (error) {
    logger.error(`Error fetching document: ${error.message}`, error);
    
    return res.status(500).json({ 
      error: 'Error fetching document', 
      detail: error.message 
    });
  }
});

module.exports = router;
