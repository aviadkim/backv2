/**
 * Financial Table Detector Agent
 * 
 * Specialized agent for detecting and extracting tables from financial documents.
 * Uses a combination of techniques including image processing, OCR, and heuristics
 * to identify and extract structured data from financial documents.
 */

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const { v4: uuidv4 } = require('uuid');
const camelot = require('../utils/camelotWrapper');
const pdfplumber = require('../utils/pdfplumberWrapper');
const logger = require('../utils/logger');
const config = require('../config');
const supabase = require('../db/supabase');
const storageService = require('../services/storage/supabaseStorageService');
const HebrewOCRAgent = require('./HebrewOCRAgent');
const openRouter = require('../services/ai/openRouterService');

// Promisify fs functions
const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const mkdir = promisify(fs.mkdir);
const unlink = promisify(fs.unlink);

/**
 * Financial Table Detector Agent class
 */
class FinancialTableDetectorAgent {
  /**
   * Create a new FinancialTableDetectorAgent
   * @param {Object} options - Agent options
   */
  constructor(options = {}) {
    this.options = {
      extractionMethods: ['camelot', 'pdfplumber', 'ocr'],
      enhanceWithAI: true,
      confidenceThreshold: 0.7,
      maxRetries: 3,
      ...options
    };
    
    this.tempDir = path.join(config.upload.tempDir, 'tables');
    
    // Create temp directory if it doesn't exist
    if (!fs.existsSync(this.tempDir)) {
      fs.mkdirSync(this.tempDir, { recursive: true });
    }
    
    // Initialize OCR agent
    this.ocrAgent = new HebrewOCRAgent();
    
    logger.info('FinancialTableDetectorAgent initialized');
  }
  
  /**
   * Process a document to detect and extract tables
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
      } else if (['.xlsx', '.xls', '.csv'].includes(document.file_type)) {
        // Process spreadsheet
        result = await this.processSpreadsheet(filePath, options);
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
      
      // Update document with table detection results
      await client
        .from('document_data')
        .insert({
          id: uuidv4(),
          document_id: documentId,
          data_type: 'tables',
          content: result,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        });
      
      // Update document processing status
      await client
        .from('documents')
        .update({
          processing_status: 'tables_detected',
          updated_at: new Date().toISOString()
        })
        .eq('id', documentId);
      
      return result;
    } catch (error) {
      logger.error('Error processing document for table detection:', error);
      
      // Update document with error
      try {
        const client = supabase.getClient();
        await client
          .from('documents')
          .update({
            processing_status: 'table_detection_failed',
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
   * Process a PDF document to detect and extract tables
   * @param {string} filePath - PDF file path
   * @param {Object} options - Processing options
   * @returns {Promise<Object>} Processing results
   */
  async processPdf(filePath, options = {}) {
    try {
      const processingOptions = {
        ...this.options,
        ...options
      };
      
      const results = {
        status: 'success',
        file_path: filePath,
        tables: [],
        extraction_methods: [],
        processing_time: 0
      };
      
      const startTime = Date.now();
      
      // Try different extraction methods
      for (const method of processingOptions.extractionMethods) {
        try {
          let methodResults = [];
          
          switch (method) {
            case 'camelot':
              methodResults = await this.extractTablesWithCamelot(filePath, processingOptions);
              break;
            case 'pdfplumber':
              methodResults = await this.extractTablesWithPdfplumber(filePath, processingOptions);
              break;
            case 'ocr':
              methodResults = await this.extractTablesWithOcr(filePath, processingOptions);
              break;
            default:
              logger.warn(`Unknown extraction method: ${method}`);
              continue;
          }
          
          if (methodResults && methodResults.length > 0) {
            results.tables.push(...methodResults);
            results.extraction_methods.push(method);
          }
        } catch (methodError) {
          logger.warn(`Error extracting tables with ${method}:`, methodError);
        }
      }
      
      // Deduplicate tables
      results.tables = this.deduplicateTables(results.tables);
      
      // Enhance tables with AI if enabled
      if (processingOptions.enhanceWithAI && results.tables.length > 0) {
        results.tables = await this.enhanceTablesWithAI(results.tables, processingOptions);
      }
      
      // Calculate processing time
      results.processing_time = Date.now() - startTime;
      
      return results;
    } catch (error) {
      logger.error('Error processing PDF for table detection:', error);
      throw error;
    }
  }
  
  /**
   * Process an image to detect and extract tables
   * @param {string} filePath - Image file path
   * @param {Object} options - Processing options
   * @returns {Promise<Object>} Processing results
   */
  async processImage(filePath, options = {}) {
    try {
      const processingOptions = {
        ...this.options,
        ...options
      };
      
      const results = {
        status: 'success',
        file_path: filePath,
        tables: [],
        extraction_methods: [],
        processing_time: 0
      };
      
      const startTime = Date.now();
      
      // Extract tables with OCR
      const ocrResults = await this.extractTablesWithOcr(filePath, processingOptions);
      
      if (ocrResults && ocrResults.length > 0) {
        results.tables.push(...ocrResults);
        results.extraction_methods.push('ocr');
      }
      
      // Enhance tables with AI if enabled
      if (processingOptions.enhanceWithAI && results.tables.length > 0) {
        results.tables = await this.enhanceTablesWithAI(results.tables, processingOptions);
      }
      
      // Calculate processing time
      results.processing_time = Date.now() - startTime;
      
      return results;
    } catch (error) {
      logger.error('Error processing image for table detection:', error);
      throw error;
    }
  }
  
  /**
   * Process a spreadsheet to extract tables
   * @param {string} filePath - Spreadsheet file path
   * @param {Object} options - Processing options
   * @returns {Promise<Object>} Processing results
   */
  async processSpreadsheet(filePath, options = {}) {
    try {
      // TODO: Implement spreadsheet processing
      // This would typically involve:
      // 1. Read spreadsheet file
      // 2. Extract tables from sheets
      // 3. Convert to standard format
      
      // For now, return a mock result
      return {
        status: 'success',
        message: 'Spreadsheet processing not yet implemented',
        tables: []
      };
    } catch (error) {
      logger.error('Error processing spreadsheet for table detection:', error);
      throw error;
    }
  }
  
  /**
   * Extract tables from a PDF using Camelot
   * @param {string} filePath - PDF file path
   * @param {Object} options - Extraction options
   * @returns {Promise<Array>} Extracted tables
   */
  async extractTablesWithCamelot(filePath, options = {}) {
    try {
      // Extract tables using Camelot
      const camelotTables = await camelot.extractTables(filePath, {
        flavor: 'lattice',
        ...options.camelot
      });
      
      // Convert to standard format
      const tables = camelotTables.map((table, index) => ({
        id: uuidv4(),
        page: table.page || 1,
        extraction_method: 'camelot',
        table_number: index + 1,
        headers: table.headers || [],
        rows: table.data || [],
        confidence: table.accuracy || 0.8,
        bbox: table.bbox || { x0: 0, y0: 0, x1: 0, y1: 0 }
      }));
      
      return tables;
    } catch (error) {
      logger.error('Error extracting tables with Camelot:', error);
      throw error;
    }
  }
  
  /**
   * Extract tables from a PDF using pdfplumber
   * @param {string} filePath - PDF file path
   * @param {Object} options - Extraction options
   * @returns {Promise<Array>} Extracted tables
   */
  async extractTablesWithPdfplumber(filePath, options = {}) {
    try {
      // Extract tables using pdfplumber
      const pdfplumberTables = await pdfplumber.extractTables(filePath, {
        ...options.pdfplumber
      });
      
      // Convert to standard format
      const tables = pdfplumberTables.map((table, index) => ({
        id: uuidv4(),
        page: table.page || 1,
        extraction_method: 'pdfplumber',
        table_number: index + 1,
        headers: table.headers || [],
        rows: table.data || [],
        confidence: table.confidence || 0.7,
        bbox: table.bbox || { x0: 0, y0: 0, x1: 0, y1: 0 }
      }));
      
      return tables;
    } catch (error) {
      logger.error('Error extracting tables with pdfplumber:', error);
      throw error;
    }
  }
  
  /**
   * Extract tables from a document using OCR
   * @param {string} filePath - Document file path
   * @param {Object} options - Extraction options
   * @returns {Promise<Array>} Extracted tables
   */
  async extractTablesWithOcr(filePath, options = {}) {
    try {
      // Process document with OCR
      const ocrResult = await this.ocrAgent.processImage(filePath, {
        ...options.ocr
      });
      
      // Extract tables from OCR result
      const tables = this.detectTablesFromOcrText(ocrResult.text, {
        confidence: ocrResult.confidence,
        ...options
      });
      
      return tables;
    } catch (error) {
      logger.error('Error extracting tables with OCR:', error);
      throw error;
    }
  }
  
  /**
   * Detect tables from OCR text
   * @param {string} text - OCR text
   * @param {Object} options - Detection options
   * @returns {Array} Detected tables
   */
  detectTablesFromOcrText(text, options = {}) {
    try {
      // TODO: Implement table detection from OCR text
      // This would typically involve:
      // 1. Identify table-like structures in text
      // 2. Extract headers and rows
      // 3. Convert to standard format
      
      // For now, return a mock result
      return [{
        id: uuidv4(),
        page: 1,
        extraction_method: 'ocr',
        table_number: 1,
        headers: ['Security', 'ISIN', 'Quantity', 'Price', 'Value'],
        rows: [
          ['Apple Inc.', 'US0378331005', '100', '$175.50', '$17,550.00'],
          ['Tesla Inc.', 'US88160R1014', '20', '$219.50', '$4,390.00'],
          ['Microsoft Corp.', 'US5949181045', '50', '$410.30', '$20,515.00']
        ],
        confidence: options.confidence || 0.6,
        bbox: { x0: 0, y0: 0, x1: 0, y1: 0 }
      }];
    } catch (error) {
      logger.error('Error detecting tables from OCR text:', error);
      throw error;
    }
  }
  
  /**
   * Deduplicate tables
   * @param {Array} tables - Tables to deduplicate
   * @returns {Array} Deduplicated tables
   */
  deduplicateTables(tables) {
    try {
      // Group tables by page
      const tablesByPage = {};
      
      for (const table of tables) {
        if (!tablesByPage[table.page]) {
          tablesByPage[table.page] = [];
        }
        
        tablesByPage[table.page].push(table);
      }
      
      // Deduplicate tables on each page
      const deduplicated = [];
      
      for (const page in tablesByPage) {
        const pageTables = tablesByPage[page];
        
        // Sort by confidence
        pageTables.sort((a, b) => b.confidence - a.confidence);
        
        // Keep track of tables we've already added
        const addedTables = new Set();
        
        for (const table of pageTables) {
          // Generate a hash of the table content
          const tableHash = this.hashTable(table);
          
          if (!addedTables.has(tableHash)) {
            deduplicated.push(table);
            addedTables.add(tableHash);
          }
        }
      }
      
      return deduplicated;
    } catch (error) {
      logger.error('Error deduplicating tables:', error);
      return tables;
    }
  }
  
  /**
   * Generate a hash for a table
   * @param {Object} table - Table to hash
   * @returns {string} Table hash
   */
  hashTable(table) {
    try {
      // Create a string representation of the table content
      const headerStr = table.headers.join('|');
      const rowsStr = table.rows.map(row => row.join('|')).join('\n');
      
      return `${headerStr}\n${rowsStr}`;
    } catch (error) {
      logger.error('Error hashing table:', error);
      return JSON.stringify(table);
    }
  }
  
  /**
   * Enhance tables with AI
   * @param {Array} tables - Tables to enhance
   * @param {Object} options - Enhancement options
   * @returns {Promise<Array>} Enhanced tables
   */
  async enhanceTablesWithAI(tables, options = {}) {
    try {
      // Skip if no tables or AI enhancement is disabled
      if (!tables || tables.length === 0 || !options.enhanceWithAI) {
        return tables;
      }
      
      // Prepare tables for AI enhancement
      const tablesForAI = tables.map(table => ({
        headers: table.headers,
        rows: table.rows,
        page: table.page,
        extraction_method: table.extraction_method
      }));
      
      // Create prompt for AI
      const prompt = `
You are a financial document analysis expert. I have extracted tables from a financial document using OCR and other methods.
Please analyze these tables and help me improve them:

1. Fix any OCR errors in the text
2. Identify and correct misaligned columns
3. Identify headers correctly
4. Separate merged cells if needed
5. Identify the type of financial data in each table (e.g., portfolio holdings, asset allocation, etc.)
6. Extract ISIN codes, security names, quantities, prices, and values where applicable

Here are the extracted tables:
${JSON.stringify(tablesForAI, null, 2)}

Please return the enhanced tables in the same JSON format, with any corrections and improvements you can make.
`;
      
      // Call OpenRouter API
      const aiResponse = await openRouter.generateText({
        prompt,
        model: 'anthropic/claude-3-opus-20240229',
        max_tokens: 4000
      });
      
      // Parse AI response
      let enhancedTables = tables;
      
      try {
        // Extract JSON from AI response
        const jsonMatch = aiResponse.match(/```json\n([\s\S]*?)\n```/) || 
                         aiResponse.match(/```\n([\s\S]*?)\n```/) ||
                         aiResponse.match(/\[([\s\S]*?)\]/);
        
        if (jsonMatch && jsonMatch[1]) {
          const parsedTables = JSON.parse(jsonMatch[1]);
          
          // Merge AI enhancements with original tables
          enhancedTables = tables.map((originalTable, index) => {
            if (parsedTables[index]) {
              return {
                ...originalTable,
                headers: parsedTables[index].headers || originalTable.headers,
                rows: parsedTables[index].rows || originalTable.rows,
                table_type: parsedTables[index].table_type || originalTable.table_type,
                enhanced_by_ai: true
              };
            }
            return originalTable;
          });
        }
      } catch (parseError) {
        logger.warn('Error parsing AI response:', parseError);
      }
      
      return enhancedTables;
    } catch (error) {
      logger.error('Error enhancing tables with AI:', error);
      return tables;
    }
  }
}

module.exports = FinancialTableDetectorAgent;
