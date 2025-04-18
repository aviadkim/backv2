/**
 * Query Engine Agent
 * 
 * Specialized agent for answering natural language queries about financial documents.
 * Uses AI to understand questions and extract relevant information from processed documents.
 */

const { v4: uuidv4 } = require('uuid');
const logger = require('../utils/logger');
const config = require('../config');
const supabase = require('../db/supabase');
const openRouter = require('../services/ai/openRouterService');

/**
 * Query Engine Agent class
 */
class QueryEngineAgent {
  /**
   * Create a new QueryEngineAgent
   * @param {Object} options - Agent options
   */
  constructor(options = {}) {
    this.options = {
      model: 'anthropic/claude-3-opus-20240229',
      maxTokens: 4000,
      temperature: 0.7,
      ...options
    };
    
    logger.info('QueryEngineAgent initialized');
  }
  
  /**
   * Answer a query about a document
   * @param {string} documentId - Document ID
   * @param {string} query - User query
   * @param {Object} options - Query options
   * @returns {Promise<Object>} Query result
   */
  async answerQuery(documentId, query, options = {}) {
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
      
      // Get financial data
      const financialData = documentData.find(data => data.data_type === 'financial_data');
      
      // Check if we have enough data to answer the query
      if (!ocrData && !tableData && !financialData) {
        throw new Error('No processed data found for this document');
      }
      
      // Generate answer
      const result = await this.generateAnswer(document, documentData, query, options);
      
      // Save query and answer
      await client
        .from('document_data')
        .insert({
          id: uuidv4(),
          document_id: documentId,
          data_type: 'query',
          content: {
            query,
            answer: result.answer,
            timestamp: new Date().toISOString(),
            sources: result.sources
          },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        });
      
      return result;
    } catch (error) {
      logger.error('Error answering query:', error);
      throw error;
    }
  }
  
  /**
   * Generate answer to a query
   * @param {Object} document - Document object
   * @param {Array} documentData - Document data
   * @param {string} query - User query
   * @param {Object} options - Query options
   * @returns {Promise<Object>} Generated answer
   */
  async generateAnswer(document, documentData, query, options = {}) {
    try {
      const queryOptions = {
        ...this.options,
        ...options
      };
      
      // Extract relevant data
      const ocrData = documentData.find(data => data.data_type === 'ocr');
      const tableData = documentData.find(data => data.data_type === 'tables');
      const financialData = documentData.find(data => data.data_type === 'financial_data');
      
      // Create context for the query
      const context = this.createQueryContext(document, ocrData, tableData, financialData);
      
      // Create prompt for AI
      const prompt = `
You are a financial document analysis expert. I have a document with the following information:

Document Name: ${document.name}
Document Type: ${document.file_type}
Document Status: ${document.status}

${context}

User Query: ${query}

Please answer the query based on the information provided. Be specific and provide exact numbers, dates, and other details from the document when relevant. If the information needed to answer the query is not available in the provided context, please state that clearly.

Format your response in a clear, concise manner. If the query is about numerical data, include the exact figures in your response. If the query is about trends or comparisons, explain the patterns you observe in the data.

If you're unsure about any aspect of your answer, indicate your level of confidence and explain why you're uncertain.
`;
      
      // Call OpenRouter API
      const aiResponse = await openRouter.generateText({
        prompt,
        model: queryOptions.model,
        max_tokens: queryOptions.maxTokens,
        temperature: queryOptions.temperature
      });
      
      // Extract sources
      const sources = [];
      
      if (ocrData) {
        sources.push({
          type: 'ocr',
          id: ocrData.id
        });
      }
      
      if (tableData) {
        sources.push({
          type: 'tables',
          id: tableData.id
        });
      }
      
      if (financialData) {
        sources.push({
          type: 'financial_data',
          id: financialData.id
        });
      }
      
      return {
        query,
        answer: aiResponse,
        sources,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      logger.error('Error generating answer:', error);
      throw error;
    }
  }
  
  /**
   * Create context for a query
   * @param {Object} document - Document object
   * @param {Object} ocrData - OCR data
   * @param {Object} tableData - Table data
   * @param {Object} financialData - Financial data
   * @returns {string} Query context
   */
  createQueryContext(document, ocrData, tableData, financialData) {
    let context = '';
    
    // Add financial data to context
    if (financialData && financialData.content) {
      context += `
Financial Data:
- Portfolio Total Value: ${financialData.content.portfolio.total_value} ${financialData.content.portfolio.currency}
- Total Securities: ${financialData.content.metrics.total_securities}
- Total Asset Classes: ${financialData.content.metrics.total_asset_classes}

Asset Allocation:
${Object.entries(financialData.content.portfolio.asset_allocation)
  .map(([assetClass, data]) => `- ${assetClass}: ${(data.percentage * 100).toFixed(2)}% (${data.value} ${financialData.content.portfolio.currency})`)
  .join('\n')}

Top Securities:
${financialData.content.portfolio.securities
  .sort((a, b) => b.value - a.value)
  .slice(0, 10)
  .map(security => `- ${security.name} (${security.isin}): ${security.value} ${financialData.content.portfolio.currency}`)
  .join('\n')}
`;
    }
    
    // Add table data to context
    if (tableData && tableData.content && tableData.content.tables) {
      context += `
Tables:
${tableData.content.tables.map((table, index) => `
Table ${index + 1}:
Headers: ${table.headers.join(', ')}
${table.rows.map(row => row.join(', ')).join('\n')}
`).join('\n')}
`;
    }
    
    // Add OCR data to context
    if (ocrData && ocrData.content && ocrData.content.text) {
      // Limit OCR text to avoid token limits
      const maxOcrLength = 2000;
      const ocrText = ocrData.content.text.length > maxOcrLength
        ? ocrData.content.text.substring(0, maxOcrLength) + '...'
        : ocrData.content.text;
      
      context += `
OCR Text:
${ocrText}
`;
    }
    
    return context;
  }
  
  /**
   * Get previous queries for a document
   * @param {string} documentId - Document ID
   * @returns {Promise<Array>} Previous queries
   */
  async getPreviousQueries(documentId) {
    try {
      // Get document data
      const client = supabase.getClient();
      const { data, error } = await client
        .from('document_data')
        .select('*')
        .eq('document_id', documentId)
        .eq('data_type', 'query')
        .order('created_at', { ascending: false });
      
      if (error) {
        logger.error('Error getting previous queries:', error);
        throw new Error('Error getting previous queries');
      }
      
      return data.map(item => item.content);
    } catch (error) {
      logger.error('Error in getPreviousQueries:', error);
      throw error;
    }
  }
}

module.exports = QueryEngineAgent;
