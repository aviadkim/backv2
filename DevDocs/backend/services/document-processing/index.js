/**
 * Document Processing Service
 * 
 * This service coordinates the processing of financial documents through various stages:
 * 1. Document preprocessing (OCR, text extraction)
 * 2. Table detection and extraction
 * 3. ISIN and security identification
 * 4. Financial data analysis
 * 5. Data validation and storage
 */

const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const { preprocessDocument } = require('./preprocessor');
const { detectTables } = require('./table-detector');
const { extractISINs } = require('./isin-extractor');
const { analyzeFinancialData } = require('./financial-analyzer');
const { validateData } = require('./data-validator');
const { storeDocumentData } = require('./data-storage');
const { enhanceWithAI } = require('./ai-enhancer');
const logger = require('../../utils/logger');

/**
 * Process a financial document through the complete pipeline
 * @param {Object} options - Processing options
 * @param {string} options.filePath - Path to the document file
 * @param {string} options.documentType - Type of document (e.g., 'statement', 'portfolio', 'trade')
 * @param {string} options.language - Primary language of the document (e.g., 'en', 'he')
 * @param {boolean} options.useAI - Whether to use AI enhancement
 * @param {Object} options.metadata - Additional metadata about the document
 * @returns {Promise<Object>} - Processing results
 */
async function processDocument(options) {
  const { 
    filePath, 
    documentType = 'financial', 
    language = 'en',
    useAI = true,
    metadata = {}
  } = options;

  // Create a unique ID for this processing job
  const jobId = uuidv4();
  const workDir = path.join(process.cwd(), 'temp', jobId);
  
  // Create working directory
  fs.mkdirSync(workDir, { recursive: true });
  
  logger.info(`Starting document processing job ${jobId} for ${filePath}`);
  
  try {
    // Step 1: Preprocess the document (OCR, text extraction)
    logger.info(`[${jobId}] Preprocessing document`);
    const preprocessingResult = await preprocessDocument({
      filePath,
      workDir,
      language,
      documentType
    });
    
    // Step 2: Detect and extract tables
    logger.info(`[${jobId}] Detecting tables`);
    const tablesResult = await detectTables({
      ...preprocessingResult,
      workDir,
      documentType
    });
    
    // Step 3: Extract ISINs and securities
    logger.info(`[${jobId}] Extracting ISINs`);
    const isinsResult = await extractISINs({
      ...preprocessingResult,
      tables: tablesResult.tables,
      workDir
    });
    
    // Step 4: Analyze financial data
    logger.info(`[${jobId}] Analyzing financial data`);
    const financialData = await analyzeFinancialData({
      ...preprocessingResult,
      tables: tablesResult.tables,
      isins: isinsResult.isins,
      documentType,
      workDir
    });
    
    // Step 5: Enhance with AI if enabled
    let enhancedData = { ...financialData };
    if (useAI) {
      logger.info(`[${jobId}] Enhancing with AI`);
      enhancedData = await enhanceWithAI({
        ...preprocessingResult,
        tables: tablesResult.tables,
        isins: isinsResult.isins,
        financialData,
        documentType
      });
    }
    
    // Step 6: Validate the extracted data
    logger.info(`[${jobId}] Validating data`);
    const validationResult = await validateData({
      ...enhancedData,
      documentType
    });
    
    // Step 7: Store the results
    logger.info(`[${jobId}] Storing results`);
    const storageResult = await storeDocumentData({
      jobId,
      documentType,
      metadata: {
        ...metadata,
        filename: path.basename(filePath),
        processedAt: new Date().toISOString(),
        language
      },
      extractedText: preprocessingResult.extractedText,
      tables: tablesResult.tables,
      isins: isinsResult.isins,
      financialData: enhancedData,
      validationResult
    });
    
    // Clean up temporary files
    fs.rmSync(workDir, { recursive: true, force: true });
    
    logger.info(`[${jobId}] Document processing completed successfully`);
    
    // Return the processing results
    return {
      jobId,
      documentType,
      extractedText: preprocessingResult.extractedText.substring(0, 1000) + '...',
      pageCount: preprocessingResult.pageCount,
      tables: tablesResult.tables,
      isins: isinsResult.isins,
      financialData: enhancedData,
      validationResult: validationResult.summary,
      storageResult
    };
  } catch (error) {
    logger.error(`[${jobId}] Error processing document: ${error.message}`, error);
    
    // Clean up temporary files
    fs.rmSync(workDir, { recursive: true, force: true });
    
    throw error;
  }
}

module.exports = {
  processDocument
};
