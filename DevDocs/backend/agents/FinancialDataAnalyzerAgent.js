/**
 * Financial Data Analyzer Agent
 * 
 * Specialized agent for analyzing financial data extracted from documents.
 * Identifies securities, calculates portfolio metrics, and extracts key financial information.
 */

const { v4: uuidv4 } = require('uuid');
const logger = require('../utils/logger');
const config = require('../config');
const supabase = require('../db/supabase');
const openRouter = require('../services/ai/openRouterService');
const FinancialTableDetectorAgent = require('./FinancialTableDetectorAgent');

/**
 * Financial Data Analyzer Agent class
 */
class FinancialDataAnalyzerAgent {
  /**
   * Create a new FinancialDataAnalyzerAgent
   * @param {Object} options - Agent options
   */
  constructor(options = {}) {
    this.options = {
      enhanceWithAI: true,
      confidenceThreshold: 0.7,
      maxRetries: 3,
      ...options
    };
    
    // Initialize table detector agent
    this.tableDetectorAgent = new FinancialTableDetectorAgent();
    
    logger.info('FinancialDataAnalyzerAgent initialized');
  }
  
  /**
   * Process a document to analyze financial data
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
      
      // Update document processing status
      await client
        .from('documents')
        .update({
          processing_status: 'financial_analysis_processing',
          updated_at: new Date().toISOString()
        })
        .eq('id', documentId);
      
      // Get document data
      const { data: documentData, error: dataError } = await client
        .from('document_data')
        .select('*')
        .eq('document_id', documentId)
        .order('created_at', { ascending: false });
      
      if (dataError) {
        logger.error('Error getting document data:', dataError);
        throw new Error('Error getting document data');
      }
      
      // Get OCR data
      const ocrData = documentData.find(data => data.data_type === 'ocr');
      
      // Get table data
      const tableData = documentData.find(data => data.data_type === 'tables');
      
      // If no OCR or table data, run those processes first
      if (!ocrData && !tableData) {
        // Process document with OCR and table detection
        await this.tableDetectorAgent.processDocument(documentId);
        
        // Get updated document data
        const { data: updatedData, error: updatedError } = await client
          .from('document_data')
          .select('*')
          .eq('document_id', documentId)
          .order('created_at', { ascending: false });
        
        if (updatedError) {
          logger.error('Error getting updated document data:', updatedError);
          throw new Error('Error getting updated document data');
        }
        
        // Get OCR data
        const updatedOcrData = updatedData.find(data => data.data_type === 'ocr');
        
        // Get table data
        const updatedTableData = updatedData.find(data => data.data_type === 'tables');
        
        // Analyze financial data
        const result = await this.analyzeFinancialData(documentId, updatedOcrData, updatedTableData, options);
        
        return result;
      }
      
      // Analyze financial data
      const result = await this.analyzeFinancialData(documentId, ocrData, tableData, options);
      
      return result;
    } catch (error) {
      logger.error('Error processing document for financial analysis:', error);
      
      // Update document with error
      try {
        const client = supabase.getClient();
        await client
          .from('documents')
          .update({
            processing_status: 'financial_analysis_failed',
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
   * Analyze financial data from document
   * @param {string} documentId - Document ID
   * @param {Object} ocrData - OCR data
   * @param {Object} tableData - Table data
   * @param {Object} options - Analysis options
   * @returns {Promise<Object>} Analysis results
   */
  async analyzeFinancialData(documentId, ocrData, tableData, options = {}) {
    try {
      const processingOptions = {
        ...this.options,
        ...options
      };
      
      // Initialize result
      const result = {
        document_id: documentId,
        portfolio: {
          total_value: 0,
          currency: 'USD',
          securities: [],
          asset_allocation: {}
        },
        metrics: {
          total_securities: 0,
          total_asset_classes: 0
        },
        entities: {
          isins: [],
          currencies: [],
          dates: []
        },
        analysis_date: new Date().toISOString(),
        confidence: 0
      };
      
      // Extract data from tables
      if (tableData && tableData.content && tableData.content.tables) {
        await this.extractDataFromTables(result, tableData.content.tables);
      }
      
      // Extract data from OCR text
      if (ocrData && ocrData.content && ocrData.content.text) {
        await this.extractDataFromText(result, ocrData.content.text);
      }
      
      // Enhance with AI if enabled
      if (processingOptions.enhanceWithAI) {
        await this.enhanceWithAI(result, ocrData, tableData);
      }
      
      // Calculate metrics
      this.calculateMetrics(result);
      
      // Update document with financial data
      const client = supabase.getClient();
      await client
        .from('document_data')
        .insert({
          id: uuidv4(),
          document_id: documentId,
          data_type: 'financial_data',
          content: result,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        });
      
      // Update document status
      await client
        .from('documents')
        .update({
          processing_status: 'financial_analysis_completed',
          updated_at: new Date().toISOString()
        })
        .eq('id', documentId);
      
      return result;
    } catch (error) {
      logger.error('Error analyzing financial data:', error);
      throw error;
    }
  }
  
  /**
   * Extract data from tables
   * @param {Object} result - Result object to update
   * @param {Array} tables - Tables to extract data from
   * @returns {Promise<void>}
   */
  async extractDataFromTables(result, tables) {
    try {
      // Process each table
      for (const table of tables) {
        // Check if table has headers and rows
        if (!table.headers || !table.rows || table.rows.length === 0) {
          continue;
        }
        
        // Normalize headers (convert to lowercase)
        const normalizedHeaders = table.headers.map(header => 
          typeof header === 'string' ? header.toLowerCase() : ''
        );
        
        // Check if table is a securities table
        if (this.isSecuritiesTable(normalizedHeaders)) {
          await this.extractSecurities(result, table);
        }
        
        // Check if table is an asset allocation table
        if (this.isAssetAllocationTable(normalizedHeaders)) {
          await this.extractAssetAllocation(result, table);
        }
      }
    } catch (error) {
      logger.error('Error extracting data from tables:', error);
      throw error;
    }
  }
  
  /**
   * Check if table is a securities table
   * @param {Array} headers - Table headers
   * @returns {boolean} True if table is a securities table
   */
  isSecuritiesTable(headers) {
    // Check for common securities table headers
    const securityHeaders = ['security', 'name', 'instrument', 'asset', 'holding', 'position'];
    const identifierHeaders = ['isin', 'cusip', 'ticker', 'symbol'];
    const quantityHeaders = ['quantity', 'amount', 'shares', 'units'];
    const valueHeaders = ['value', 'market value', 'position value', 'total'];
    
    // Check if table has at least one header from each category
    const hasSecurityHeader = securityHeaders.some(header => headers.some(h => h.includes(header)));
    const hasIdentifierHeader = identifierHeaders.some(header => headers.some(h => h.includes(header)));
    const hasQuantityOrValueHeader = 
      quantityHeaders.some(header => headers.some(h => h.includes(header))) ||
      valueHeaders.some(header => headers.some(h => h.includes(header)));
    
    return hasSecurityHeader && (hasIdentifierHeader || hasQuantityOrValueHeader);
  }
  
  /**
   * Check if table is an asset allocation table
   * @param {Array} headers - Table headers
   * @returns {boolean} True if table is an asset allocation table
   */
  isAssetAllocationTable(headers) {
    // Check for common asset allocation table headers
    const assetClassHeaders = ['asset class', 'asset type', 'category', 'allocation'];
    const percentageHeaders = ['percentage', '%', 'allocation', 'weight'];
    const valueHeaders = ['value', 'amount', 'market value', 'total'];
    
    // Check if table has at least one header from each category
    const hasAssetClassHeader = assetClassHeaders.some(header => headers.some(h => h.includes(header)));
    const hasPercentageOrValueHeader = 
      percentageHeaders.some(header => headers.some(h => h.includes(header))) ||
      valueHeaders.some(header => headers.some(h => h.includes(header)));
    
    return hasAssetClassHeader && hasPercentageOrValueHeader;
  }
  
  /**
   * Extract securities from table
   * @param {Object} result - Result object to update
   * @param {Object} table - Table to extract securities from
   * @returns {Promise<void>}
   */
  async extractSecurities(result, table) {
    try {
      // Get column indices
      const headers = table.headers.map(header => 
        typeof header === 'string' ? header.toLowerCase() : ''
      );
      
      const nameIndex = headers.findIndex(header => 
        ['security', 'name', 'instrument', 'asset', 'holding', 'position'].some(h => header.includes(h))
      );
      
      const isinIndex = headers.findIndex(header => 
        ['isin', 'cusip', 'ticker', 'symbol'].some(h => header.includes(h))
      );
      
      const quantityIndex = headers.findIndex(header => 
        ['quantity', 'amount', 'shares', 'units'].some(h => header.includes(h))
      );
      
      const priceIndex = headers.findIndex(header => 
        ['price', 'market price', 'rate'].some(h => header.includes(h))
      );
      
      const valueIndex = headers.findIndex(header => 
        ['value', 'market value', 'position value', 'total'].some(h => header.includes(h))
      );
      
      // Process each row
      for (const row of table.rows) {
        // Skip empty rows
        if (!row || row.length === 0 || row.every(cell => !cell || cell.trim() === '')) {
          continue;
        }
        
        // Extract security data
        const security = {
          id: uuidv4(),
          name: nameIndex >= 0 && nameIndex < row.length ? row[nameIndex] : '',
          isin: isinIndex >= 0 && isinIndex < row.length ? this.extractISIN(row[isinIndex]) : '',
          quantity: quantityIndex >= 0 && quantityIndex < row.length ? this.parseNumber(row[quantityIndex]) : 0,
          price: priceIndex >= 0 && priceIndex < row.length ? this.parseNumber(row[priceIndex]) : 0,
          value: valueIndex >= 0 && valueIndex < row.length ? this.parseNumber(row[valueIndex]) : 0
        };
        
        // Calculate value if not provided
        if (security.value === 0 && security.quantity > 0 && security.price > 0) {
          security.value = security.quantity * security.price;
        }
        
        // Add security to result
        result.portfolio.securities.push(security);
        
        // Add ISIN to entities
        if (security.isin) {
          result.entities.isins.push({
            code: security.isin,
            name: security.name,
            value: security.value
          });
        }
        
        // Update portfolio total value
        result.portfolio.total_value += security.value;
      }
    } catch (error) {
      logger.error('Error extracting securities from table:', error);
      throw error;
    }
  }
  
  /**
   * Extract asset allocation from table
   * @param {Object} result - Result object to update
   * @param {Object} table - Table to extract asset allocation from
   * @returns {Promise<void>}
   */
  async extractAssetAllocation(result, table) {
    try {
      // Get column indices
      const headers = table.headers.map(header => 
        typeof header === 'string' ? header.toLowerCase() : ''
      );
      
      const assetClassIndex = headers.findIndex(header => 
        ['asset class', 'asset type', 'category', 'allocation'].some(h => header.includes(h))
      );
      
      const percentageIndex = headers.findIndex(header => 
        ['percentage', '%', 'allocation', 'weight'].some(h => header.includes(h))
      );
      
      const valueIndex = headers.findIndex(header => 
        ['value', 'amount', 'market value', 'total'].some(h => header.includes(h))
      );
      
      // Process each row
      for (const row of table.rows) {
        // Skip empty rows
        if (!row || row.length === 0 || row.every(cell => !cell || cell.trim() === '')) {
          continue;
        }
        
        // Extract asset class data
        const assetClass = assetClassIndex >= 0 && assetClassIndex < row.length ? row[assetClassIndex] : '';
        
        if (!assetClass) {
          continue;
        }
        
        // Extract percentage
        let percentage = 0;
        if (percentageIndex >= 0 && percentageIndex < row.length) {
          const percentageStr = row[percentageIndex];
          
          // Parse percentage
          if (percentageStr.includes('%')) {
            percentage = this.parseNumber(percentageStr) / 100;
          } else {
            percentage = this.parseNumber(percentageStr);
            
            // If percentage is greater than 1, assume it's a percentage value
            if (percentage > 1) {
              percentage /= 100;
            }
          }
        }
        
        // Extract value
        let value = 0;
        if (valueIndex >= 0 && valueIndex < row.length) {
          value = this.parseNumber(row[valueIndex]);
        }
        
        // Calculate percentage if not provided
        if (percentage === 0 && value > 0 && result.portfolio.total_value > 0) {
          percentage = value / result.portfolio.total_value;
        }
        
        // Calculate value if not provided
        if (value === 0 && percentage > 0 && result.portfolio.total_value > 0) {
          value = percentage * result.portfolio.total_value;
        }
        
        // Add asset allocation to result
        result.portfolio.asset_allocation[assetClass] = {
          percentage,
          value
        };
      }
    } catch (error) {
      logger.error('Error extracting asset allocation from table:', error);
      throw error;
    }
  }
  
  /**
   * Extract data from OCR text
   * @param {Object} result - Result object to update
   * @param {string} text - OCR text
   * @returns {Promise<void>}
   */
  async extractDataFromText(result, text) {
    try {
      // Extract ISINs
      const isins = this.extractISINsFromText(text);
      
      // Add ISINs to entities
      for (const isin of isins) {
        // Check if ISIN already exists
        if (!result.entities.isins.some(i => i.code === isin)) {
          result.entities.isins.push({
            code: isin,
            name: '',
            value: 0
          });
        }
      }
      
      // Extract currencies
      const currencies = this.extractCurrenciesFromText(text);
      
      // Add currencies to entities
      for (const currency of currencies) {
        if (!result.entities.currencies.includes(currency)) {
          result.entities.currencies.push(currency);
        }
      }
      
      // Extract dates
      const dates = this.extractDatesFromText(text);
      
      // Add dates to entities
      for (const date of dates) {
        if (!result.entities.dates.includes(date)) {
          result.entities.dates.push(date);
        }
      }
      
      // Set portfolio currency
      if (result.entities.currencies.length > 0) {
        result.portfolio.currency = result.entities.currencies[0];
      }
    } catch (error) {
      logger.error('Error extracting data from OCR text:', error);
      throw error;
    }
  }
  
  /**
   * Extract ISINs from text
   * @param {string} text - Text to extract ISINs from
   * @returns {Array} Extracted ISINs
   */
  extractISINsFromText(text) {
    // ISIN regex pattern
    const isinPattern = /[A-Z]{2}[A-Z0-9]{9}[0-9]/g;
    
    // Extract ISINs
    const isins = [];
    let match;
    
    while ((match = isinPattern.exec(text)) !== null) {
      isins.push(match[0]);
    }
    
    return isins;
  }
  
  /**
   * Extract ISIN from text
   * @param {string} text - Text to extract ISIN from
   * @returns {string} Extracted ISIN
   */
  extractISIN(text) {
    // ISIN regex pattern
    const isinPattern = /[A-Z]{2}[A-Z0-9]{9}[0-9]/;
    
    // Extract ISIN
    const match = text.match(isinPattern);
    
    return match ? match[0] : '';
  }
  
  /**
   * Extract currencies from text
   * @param {string} text - Text to extract currencies from
   * @returns {Array} Extracted currencies
   */
  extractCurrenciesFromText(text) {
    // Currency regex patterns
    const currencyPatterns = [
      /\$|USD|US Dollar/g,
      /€|EUR|Euro/g,
      /£|GBP|British Pound/g,
      /¥|JPY|Japanese Yen/g,
      /CHF|Swiss Franc/g,
      /ILS|₪|Israeli Shekel/g
    ];
    
    // Currency codes
    const currencyCodes = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'ILS'];
    
    // Extract currencies
    const currencies = [];
    
    for (let i = 0; i < currencyPatterns.length; i++) {
      if (currencyPatterns[i].test(text)) {
        currencies.push(currencyCodes[i]);
      }
    }
    
    return currencies;
  }
  
  /**
   * Extract dates from text
   * @param {string} text - Text to extract dates from
   * @returns {Array} Extracted dates
   */
  extractDatesFromText(text) {
    // Date regex patterns
    const datePatterns = [
      // MM/DD/YYYY or DD/MM/YYYY
      /\b(0?[1-9]|1[0-2])[\/\-](0?[1-9]|[12][0-9]|3[01])[\/\-](19|20)\d{2}\b/g,
      // YYYY/MM/DD
      /\b(19|20)\d{2}[\/\-](0?[1-9]|1[0-2])[\/\-](0?[1-9]|[12][0-9]|3[01])\b/g,
      // Month DD, YYYY
      /\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(0?[1-9]|[12][0-9]|3[01]),\s+(19|20)\d{2}\b/g
    ];
    
    // Extract dates
    const dates = [];
    
    for (const pattern of datePatterns) {
      let match;
      while ((match = pattern.exec(text)) !== null) {
        dates.push(match[0]);
      }
    }
    
    return dates;
  }
  
  /**
   * Parse number from string
   * @param {string} value - String to parse
   * @returns {number} Parsed number
   */
  parseNumber(value) {
    if (!value || typeof value !== 'string') {
      return 0;
    }
    
    // Remove currency symbols and commas
    const cleanValue = value.replace(/[$€£¥₪]/g, '').replace(/,/g, '');
    
    // Extract number
    const match = cleanValue.match(/-?\d+(\.\d+)?/);
    
    return match ? parseFloat(match[0]) : 0;
  }
  
  /**
   * Enhance financial data with AI
   * @param {Object} result - Result object to update
   * @param {Object} ocrData - OCR data
   * @param {Object} tableData - Table data
   * @returns {Promise<void>}
   */
  async enhanceWithAI(result, ocrData, tableData) {
    try {
      // Skip if no OCR or table data
      if (!ocrData && !tableData) {
        return;
      }
      
      // Create prompt for AI
      const prompt = `
You are a financial document analysis expert. I have extracted data from a financial document and need your help to enhance and validate it.

Here is the extracted data:
${JSON.stringify(result, null, 2)}

${ocrData ? `Here is the OCR text from the document:
${ocrData.content.text}` : ''}

${tableData ? `Here are the tables extracted from the document:
${JSON.stringify(tableData.content.tables, null, 2)}` : ''}

Please analyze this data and help me:
1. Identify any missing securities or asset classes
2. Correct any errors in the extracted data
3. Provide additional insights about the portfolio
4. Validate the ISINs and other financial identifiers
5. Ensure the portfolio total value is correct

Please return the enhanced financial data in the same JSON format, with any corrections and improvements you can make.
`;
      
      // Call OpenRouter API
      const aiResponse = await openRouter.generateText({
        prompt,
        model: 'anthropic/claude-3-opus-20240229',
        max_tokens: 4000
      });
      
      // Parse AI response
      try {
        // Extract JSON from AI response
        const jsonMatch = aiResponse.match(/```json\n([\s\S]*?)\n```/) || 
                         aiResponse.match(/```\n([\s\S]*?)\n```/) ||
                         aiResponse.match(/\{[\s\S]*?\}/);
        
        if (jsonMatch) {
          const jsonStr = jsonMatch[0].startsWith('{') ? jsonMatch[0] : jsonMatch[1];
          const enhancedData = JSON.parse(jsonStr);
          
          // Update result with enhanced data
          if (enhancedData.portfolio) {
            result.portfolio = enhancedData.portfolio;
          }
          
          if (enhancedData.metrics) {
            result.metrics = enhancedData.metrics;
          }
          
          if (enhancedData.entities) {
            result.entities = enhancedData.entities;
          }
          
          // Set AI enhanced flag
          result.ai_enhanced = true;
        }
      } catch (parseError) {
        logger.warn('Error parsing AI response:', parseError);
      }
    } catch (error) {
      logger.error('Error enhancing financial data with AI:', error);
    }
  }
  
  /**
   * Calculate metrics
   * @param {Object} result - Result object to update
   * @returns {void}
   */
  calculateMetrics(result) {
    // Calculate total securities
    result.metrics.total_securities = result.portfolio.securities.length;
    
    // Calculate total asset classes
    result.metrics.total_asset_classes = Object.keys(result.portfolio.asset_allocation).length;
    
    // Calculate total value
    if (result.portfolio.total_value === 0 && result.portfolio.securities.length > 0) {
      result.portfolio.total_value = result.portfolio.securities.reduce(
        (total, security) => total + security.value, 0
      );
    }
    
    // Set confidence
    result.confidence = 0.8;
  }
}

module.exports = FinancialDataAnalyzerAgent;
