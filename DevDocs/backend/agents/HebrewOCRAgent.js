/**
 * Hebrew OCR Agent
 * 
 * Specialized agent for extracting text from documents with Hebrew content.
 * Uses Tesseract OCR with Hebrew language support and custom preprocessing
 * to improve recognition accuracy for Hebrew text.
 */

const { createWorker } = require('tesseract.js');
const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const sharp = require('sharp');
const logger = require('../utils/logger');
const config = require('../config');
const { v4: uuidv4 } = require('uuid');
const supabase = require('../db/supabase');
const storageService = require('../services/storage/supabaseStorageService');

// Promisify fs functions
const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const mkdir = promisify(fs.mkdir);
const unlink = promisify(fs.unlink);

/**
 * Hebrew OCR Agent class
 */
class HebrewOCRAgent {
  /**
   * Create a new HebrewOCRAgent
   * @param {Object} options - Agent options
   */
  constructor(options = {}) {
    this.options = {
      languages: ['heb', 'eng'],
      preprocess: true,
      oem: 3, // OCR Engine Mode: 0 = Legacy, 1 = Neural LSTM, 2 = Legacy + LSTM, 3 = Default
      psm: 6, // Page Segmentation Mode: 6 = Assume a single uniform block of text
      ...options
    };
    
    this.tempDir = path.join(config.upload.tempDir, 'ocr');
    
    // Create temp directory if it doesn't exist
    if (!fs.existsSync(this.tempDir)) {
      fs.mkdirSync(this.tempDir, { recursive: true });
    }
    
    logger.info('HebrewOCRAgent initialized');
  }
  
  /**
   * Process an image with OCR
   * @param {string|Buffer} input - Image file path or buffer
   * @param {Object} options - Processing options
   * @returns {Promise<Object>} OCR results
   */
  async processImage(input, options = {}) {
    const processingOptions = {
      ...this.options,
      ...options
    };
    
    try {
      // Get image buffer
      let imageBuffer;
      
      if (typeof input === 'string') {
        // Input is a file path
        imageBuffer = await readFile(input);
      } else if (Buffer.isBuffer(input)) {
        // Input is already a buffer
        imageBuffer = input;
      } else {
        throw new Error('Invalid input type. Expected file path or buffer.');
      }
      
      // Preprocess image if enabled
      if (processingOptions.preprocess) {
        imageBuffer = await this.preprocessImage(imageBuffer, processingOptions);
      }
      
      // Save preprocessed image for debugging if needed
      if (processingOptions.savePreprocessed) {
        const preprocessedPath = path.join(this.tempDir, `${uuidv4()}_preprocessed.png`);
        await writeFile(preprocessedPath, imageBuffer);
        logger.debug(`Saved preprocessed image to ${preprocessedPath}`);
      }
      
      // Process image with Tesseract
      const result = await this.recognizeText(imageBuffer, processingOptions);
      
      return result;
    } catch (error) {
      logger.error('Error processing image with OCR:', error);
      throw error;
    }
  }
  
  /**
   * Preprocess image to improve OCR accuracy
   * @param {Buffer} imageBuffer - Image buffer
   * @param {Object} options - Preprocessing options
   * @returns {Promise<Buffer>} Preprocessed image buffer
   */
  async preprocessImage(imageBuffer, options = {}) {
    try {
      // Default preprocessing options
      const preprocessOptions = {
        grayscale: true,
        binarize: true,
        threshold: 128,
        denoise: true,
        deskew: true,
        resize: false,
        width: 0,
        height: 0,
        ...options
      };
      
      // Start with sharp instance
      let image = sharp(imageBuffer);
      
      // Get image metadata
      const metadata = await image.metadata();
      
      // Convert to grayscale
      if (preprocessOptions.grayscale) {
        image = image.grayscale();
      }
      
      // Apply thresholding (binarization)
      if (preprocessOptions.binarize) {
        image = image.threshold(preprocessOptions.threshold);
      }
      
      // Apply denoising
      if (preprocessOptions.denoise) {
        image = image.median(1);
      }
      
      // Resize image if needed
      if (preprocessOptions.resize && preprocessOptions.width > 0 && preprocessOptions.height > 0) {
        image = image.resize(preprocessOptions.width, preprocessOptions.height, {
          fit: 'inside',
          withoutEnlargement: true
        });
      }
      
      // Apply deskewing if needed (not directly supported by sharp)
      // For deskewing, we would need a more complex algorithm
      
      // Get processed image buffer
      const processedBuffer = await image.toBuffer();
      
      return processedBuffer;
    } catch (error) {
      logger.error('Error preprocessing image:', error);
      throw error;
    }
  }
  
  /**
   * Recognize text in an image using Tesseract OCR
   * @param {Buffer} imageBuffer - Image buffer
   * @param {Object} options - Recognition options
   * @returns {Promise<Object>} Recognition results
   */
  async recognizeText(imageBuffer, options = {}) {
    try {
      // Create worker
      const worker = await createWorker();
      
      // Initialize worker with languages
      await worker.loadLanguage(options.languages.join('+'));
      await worker.initialize(options.languages.join('+'));
      
      // Set recognition parameters
      await worker.setParameters({
        tessedit_ocr_engine_mode: options.oem,
        tessedit_pageseg_mode: options.psm,
        preserve_interword_spaces: 1,
        textord_heavy_nr: 1,
        textord_force_make_prop_words: 0,
        tessedit_char_whitelist: options.whitelist || '',
        tessedit_char_blacklist: options.blacklist || ''
      });
      
      // Recognize text
      const { data } = await worker.recognize(imageBuffer);
      
      // Terminate worker
      await worker.terminate();
      
      // Process results
      const result = {
        text: data.text,
        confidence: data.confidence,
        words: data.words || [],
        lines: this.extractLines(data),
        blocks: this.extractBlocks(data),
        hocr: data.hocr,
        tsv: data.tsv
      };
      
      // Apply post-processing
      if (options.postprocess) {
        result.text = this.postprocessText(result.text, options);
      }
      
      return result;
    } catch (error) {
      logger.error('Error recognizing text:', error);
      throw error;
    }
  }
  
  /**
   * Extract lines from OCR result
   * @param {Object} data - OCR result data
   * @returns {Array} Extracted lines
   */
  extractLines(data) {
    if (!data.lines) {
      // If lines are not provided, extract from text
      return data.text.split('\\n').map(line => ({
        text: line,
        confidence: data.confidence
      }));
    }
    
    return data.lines;
  }
  
  /**
   * Extract blocks from OCR result
   * @param {Object} data - OCR result data
   * @returns {Array} Extracted blocks
   */
  extractBlocks(data) {
    if (!data.blocks) {
      // If blocks are not provided, use the whole text as a single block
      return [{
        text: data.text,
        confidence: data.confidence,
        bbox: data.bbox || { x0: 0, y0: 0, x1: 0, y1: 0 }
      }];
    }
    
    return data.blocks;
  }
  
  /**
   * Post-process OCR text
   * @param {string} text - OCR text
   * @param {Object} options - Post-processing options
   * @returns {string} Post-processed text
   */
  postprocessText(text, options = {}) {
    // Default post-processing options
    const postprocessOptions = {
      removeExtraSpaces: true,
      fixRtl: true,
      fixNumbers: true,
      ...options
    };
    
    let processedText = text;
    
    // Remove extra spaces
    if (postprocessOptions.removeExtraSpaces) {
      processedText = processedText.replace(/\s+/g, ' ').trim();
    }
    
    // Fix RTL text direction issues
    if (postprocessOptions.fixRtl) {
      // Add RTL mark at the beginning of each line
      processedText = processedText.split('\n').map(line => {
        // Check if line contains Hebrew characters
        if (/[\u0590-\u05FF]/.test(line)) {
          return '\u200F' + line;
        }
        return line;
      }).join('\n');
    }
    
    // Fix number recognition issues
    if (postprocessOptions.fixNumbers) {
      // Replace common OCR errors in numbers
      processedText = processedText
        .replace(/o/g, '0')
        .replace(/O/g, '0')
        .replace(/l/g, '1')
        .replace(/I/g, '1')
        .replace(/Z/g, '2')
        .replace(/S/g, '5')
        .replace(/B/g, '8');
    }
    
    return processedText;
  }
  
  /**
   * Process a document with OCR
   * @param {string} documentId - Document ID
   * @param {Object} options - Processing options
   * @returns {Promise<Object>} Processing results
   */
  async processDocument(documentId, options = {}) {
    try {
      // Get document from database
      const client = supabase.getClient();
      const { data: document, error } = await client
        .from('documents')
        .select('*')
        .eq('id', documentId)
        .single();
      
      if (error) {
        logger.error('Error getting document:', error);
        throw new Error('Error getting document');
      }
      
      if (!document) {
        throw new Error('Document not found');
      }
      
      // Check if document has storage metadata
      if (!document.metadata || !document.metadata.storage || !document.metadata.storage.path) {
        throw new Error('Document storage information not found');
      }
      
      // Get file from storage
      const fileBuffer = await storageService.downloadFile(document.metadata.storage.path);
      
      // Create a unique processing ID
      const processingId = uuidv4();
      
      // Create processing directory
      const processingDir = path.join(this.tempDir, processingId);
      await mkdir(processingDir, { recursive: true });
      
      // Save file to processing directory
      const filePath = path.join(processingDir, path.basename(document.metadata.storage.path));
      await writeFile(filePath, fileBuffer);
      
      // Process file based on type
      let result;
      
      if (document.file_type === '.pdf') {
        // Process PDF
        result = await this.processPdf(filePath, options);
      } else if (['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'].includes(document.file_type)) {
        // Process image
        result = await this.processImage(filePath, options);
      } else {
        throw new Error(`Unsupported file type: ${document.file_type}`);
      }
      
      // Clean up processing directory
      try {
        await unlink(filePath);
        fs.rmdirSync(processingDir);
      } catch (cleanupError) {
        logger.warn(`Error cleaning up processing directory: ${cleanupError.message}`);
      }
      
      // Update document with OCR results
      await client
        .from('document_data')
        .insert({
          id: uuidv4(),
          document_id: documentId,
          data_type: 'ocr',
          content: result,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        });
      
      // Update document processing status
      await client
        .from('documents')
        .update({
          processing_status: 'ocr_completed',
          updated_at: new Date().toISOString()
        })
        .eq('id', documentId);
      
      return result;
    } catch (error) {
      logger.error('Error processing document with OCR:', error);
      
      // Update document with error
      try {
        const client = supabase.getClient();
        await client
          .from('documents')
          .update({
            processing_status: 'ocr_failed',
            processing_error: error.message,
            updated_at: new Date().toISOString()
          })
          .eq('id', documentId);
      } catch (updateError) {
        logger.error('Error updating document status:', updateError);
      }
      
      throw error;
    }
  }
  
  /**
   * Process a PDF document with OCR
   * @param {string} filePath - PDF file path
   * @param {Object} options - Processing options
   * @returns {Promise<Object>} Processing results
   */
  async processPdf(filePath, options = {}) {
    try {
      // TODO: Implement PDF processing with OCR
      // This would typically involve:
      // 1. Convert PDF pages to images
      // 2. Process each image with OCR
      // 3. Combine results
      
      // For now, return a mock result
      return {
        status: 'success',
        message: 'PDF processing not yet implemented',
        pages: []
      };
    } catch (error) {
      logger.error('Error processing PDF with OCR:', error);
      throw error;
    }
  }
}

module.exports = HebrewOCRAgent;
