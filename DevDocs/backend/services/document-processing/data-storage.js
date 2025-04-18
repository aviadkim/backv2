/**
 * Data Storage
 * 
 * Stores processed document data in the database:
 * - Document metadata
 * - Extracted text
 * - Tables
 * - ISINs
 * - Financial data
 * - Validation results
 */

const { createClient } = require('@supabase/supabase-js');
const logger = require('../../utils/logger');

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL || 'https://dnjnsotemnfrjlotgved.supabase.co';
const supabaseKey = process.env.SUPABASE_KEY || '';
const supabase = createClient(supabaseUrl, supabaseKey);

/**
 * Store document data in the database
 * @param {Object} options - Storage options
 * @param {string} options.jobId - Job ID
 * @param {string} options.documentType - Type of document
 * @param {Object} options.metadata - Document metadata
 * @param {string} options.extractedText - Extracted text from the document
 * @param {Array} options.tables - Extracted tables from the document
 * @param {Array} options.isins - Extracted ISINs from the document
 * @param {Object} options.financialData - Extracted financial data
 * @param {Object} options.validationResult - Validation results
 * @returns {Promise<Object>} - Storage results
 */
async function storeDocumentData(options) {
  const { 
    jobId, 
    documentType, 
    metadata, 
    extractedText, 
    tables, 
    isins, 
    financialData, 
    validationResult 
  } = options;
  
  logger.info(`Storing document data for job ${jobId}`);
  
  try {
    // Store document metadata
    const documentResult = await storeDocumentMetadata(jobId, documentType, metadata, validationResult);
    
    // Store extracted text
    const textResult = await storeExtractedText(jobId, documentResult.id, extractedText);
    
    // Store tables
    const tablesResult = await storeTables(jobId, documentResult.id, tables);
    
    // Store ISINs
    const isinsResult = await storeIsins(jobId, documentResult.id, isins);
    
    // Store financial data
    const financialDataResult = await storeFinancialData(jobId, documentResult.id, financialData);
    
    logger.info(`Successfully stored document data for job ${jobId}`);
    
    return {
      documentId: documentResult.id,
      success: true,
      tables: tablesResult.count,
      isins: isinsResult.count,
      securities: financialDataResult.securitiesCount
    };
  } catch (error) {
    logger.error(`Error storing document data: ${error.message}`, error);
    
    // Try to store the error
    try {
      await storeProcessingError(jobId, error);
    } catch (storeError) {
      logger.error(`Error storing processing error: ${storeError.message}`);
    }
    
    throw error;
  }
}

/**
 * Store document metadata in the database
 * @param {string} jobId - Job ID
 * @param {string} documentType - Type of document
 * @param {Object} metadata - Document metadata
 * @param {Object} validationResult - Validation results
 * @returns {Promise<Object>} - Storage result
 */
async function storeDocumentMetadata(jobId, documentType, metadata, validationResult) {
  logger.info(`Storing document metadata for job ${jobId}`);
  
  try {
    // Create document record
    const { data, error } = await supabase
      .from('documents')
      .insert({
        job_id: jobId,
        document_type: documentType,
        filename: metadata.filename,
        processed_at: metadata.processedAt,
        language: metadata.language,
        status: validationResult.summary.validationStatus,
        validation_errors: validationResult.summary.totalErrors,
        validation_warnings: validationResult.summary.totalWarnings,
        metadata: metadata
      })
      .select()
      .single();
    
    if (error) {
      throw new Error(`Error storing document metadata: ${error.message}`);
    }
    
    return data;
  } catch (error) {
    logger.error(`Error storing document metadata: ${error.message}`);
    throw error;
  }
}

/**
 * Store extracted text in the database
 * @param {string} jobId - Job ID
 * @param {number} documentId - Document ID
 * @param {string} extractedText - Extracted text from the document
 * @returns {Promise<Object>} - Storage result
 */
async function storeExtractedText(jobId, documentId, extractedText) {
  logger.info(`Storing extracted text for job ${jobId}`);
  
  try {
    // Create text record
    const { data, error } = await supabase
      .from('document_text')
      .insert({
        document_id: documentId,
        text_content: extractedText
      })
      .select()
      .single();
    
    if (error) {
      throw new Error(`Error storing extracted text: ${error.message}`);
    }
    
    return data;
  } catch (error) {
    logger.error(`Error storing extracted text: ${error.message}`);
    throw error;
  }
}

/**
 * Store tables in the database
 * @param {string} jobId - Job ID
 * @param {number} documentId - Document ID
 * @param {Array} tables - Extracted tables from the document
 * @returns {Promise<Object>} - Storage result
 */
async function storeTables(jobId, documentId, tables) {
  logger.info(`Storing ${tables.length} tables for job ${jobId}`);
  
  try {
    // Create table records
    const tableRecords = tables.map(table => ({
      document_id: documentId,
      table_id: table.id,
      page: table.page,
      extraction_method: table.extraction_method,
      table_number: table.table_number,
      headers: table.headers,
      rows: table.rows,
      accuracy: table.accuracy || null,
      bbox: table.bbox || null
    }));
    
    // Insert tables in batches to avoid hitting size limits
    const batchSize = 10;
    let insertedCount = 0;
    
    for (let i = 0; i < tableRecords.length; i += batchSize) {
      const batch = tableRecords.slice(i, i + batchSize);
      
      const { data, error } = await supabase
        .from('document_tables')
        .insert(batch);
      
      if (error) {
        throw new Error(`Error storing tables batch: ${error.message}`);
      }
      
      insertedCount += batch.length;
    }
    
    return { count: insertedCount };
  } catch (error) {
    logger.error(`Error storing tables: ${error.message}`);
    throw error;
  }
}

/**
 * Store ISINs in the database
 * @param {string} jobId - Job ID
 * @param {number} documentId - Document ID
 * @param {Array} isins - Extracted ISINs from the document
 * @returns {Promise<Object>} - Storage result
 */
async function storeIsins(jobId, documentId, isins) {
  logger.info(`Storing ${isins.length} ISINs for job ${jobId}`);
  
  try {
    // Create ISIN records
    const isinRecords = isins.map(isin => ({
      document_id: documentId,
      isin: isin.code,
      name: isin.name || null,
      quantity: isin.quantity || null,
      value: isin.value || null,
      source: isin.source || null,
      security_type: isin.securityType || null
    }));
    
    // Insert ISINs in batches to avoid hitting size limits
    const batchSize = 50;
    let insertedCount = 0;
    
    for (let i = 0; i < isinRecords.length; i += batchSize) {
      const batch = isinRecords.slice(i, i + batchSize);
      
      const { data, error } = await supabase
        .from('document_isins')
        .insert(batch);
      
      if (error) {
        throw new Error(`Error storing ISINs batch: ${error.message}`);
      }
      
      insertedCount += batch.length;
    }
    
    return { count: insertedCount };
  } catch (error) {
    logger.error(`Error storing ISINs: ${error.message}`);
    throw error;
  }
}

/**
 * Store financial data in the database
 * @param {string} jobId - Job ID
 * @param {number} documentId - Document ID
 * @param {Object} financialData - Extracted financial data
 * @returns {Promise<Object>} - Storage result
 */
async function storeFinancialData(jobId, documentId, financialData) {
  logger.info(`Storing financial data for job ${jobId}`);
  
  try {
    // Store portfolio data
    const { data: portfolioData, error: portfolioError } = await supabase
      .from('portfolios')
      .insert({
        document_id: documentId,
        portfolio_value: financialData.portfolio_value,
        currency: financialData.currency,
        asset_allocation: financialData.asset_allocation,
        performance: financialData.performance
      })
      .select()
      .single();
    
    if (portfolioError) {
      throw new Error(`Error storing portfolio data: ${portfolioError.message}`);
    }
    
    // Store securities
    const portfolioId = portfolioData.id;
    let securitiesCount = 0;
    
    if (financialData.securities && financialData.securities.length > 0) {
      // Create security records
      const securityRecords = financialData.securities.map(security => ({
        portfolio_id: portfolioId,
        document_id: documentId,
        isin: security.isin,
        name: security.name || null,
        quantity: security.quantity || null,
        price: security.price || null,
        value: security.value || null,
        currency: security.currency || financialData.currency || null,
        security_type: security.securityType || null
      }));
      
      // Insert securities in batches to avoid hitting size limits
      const batchSize = 50;
      
      for (let i = 0; i < securityRecords.length; i += batchSize) {
        const batch = securityRecords.slice(i, i + batchSize);
        
        const { data, error } = await supabase
          .from('securities')
          .insert(batch);
        
        if (error) {
          throw new Error(`Error storing securities batch: ${error.message}`);
        }
        
        securitiesCount += batch.length;
      }
    }
    
    return { 
      portfolioId: portfolioId,
      securitiesCount: securitiesCount
    };
  } catch (error) {
    logger.error(`Error storing financial data: ${error.message}`);
    throw error;
  }
}

/**
 * Store processing error in the database
 * @param {string} jobId - Job ID
 * @param {Error} error - Processing error
 * @returns {Promise<Object>} - Storage result
 */
async function storeProcessingError(jobId, error) {
  logger.info(`Storing processing error for job ${jobId}`);
  
  try {
    // Create error record
    const { data, error: insertError } = await supabase
      .from('processing_errors')
      .insert({
        job_id: jobId,
        error_message: error.message,
        error_stack: error.stack,
        error_time: new Date().toISOString()
      })
      .select()
      .single();
    
    if (insertError) {
      throw new Error(`Error storing processing error: ${insertError.message}`);
    }
    
    return data;
  } catch (error) {
    logger.error(`Error storing processing error: ${error.message}`);
    throw error;
  }
}

module.exports = {
  storeDocumentData
};
