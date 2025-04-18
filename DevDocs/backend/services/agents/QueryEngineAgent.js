/**
 * Query Engine Agent
 * 
 * Processes natural language queries about financial documents and returns relevant information.
 */

const axios = require('axios');
const logger = require('../../utils/logger');

class QueryEngineAgent {
  constructor(options = {}) {
    this.apiKey = options.apiKey || process.env.OPENROUTER_API_KEY;
    this.model = options.model || 'anthropic/claude-3-opus:beta';
    this.apiUrl = options.apiUrl || 'https://openrouter.ai/api/v1/chat/completions';
    this.logger = logger;
  }

  /**
   * Process a natural language query
   * @param {string} query - The natural language query
   * @param {Object} documentData - The document data to query against
   * @param {Object} options - Query options
   * @returns {Promise<Object>} - Query results
   */
  async processQuery(query, documentData, options = {}) {
    this.logger.info(`Processing query: ${query}`);
    
    try {
      if (!this.apiKey) {
        throw new Error('API key not configured');
      }
      
      // Prepare document data for the prompt
      const documentContext = this._prepareDocumentContext(documentData);
      
      // Create a prompt for the AI
      const prompt = this._createQueryPrompt(query, documentContext, options);
      
      // Call the OpenRouter API
      const response = await axios.post(
        this.apiUrl,
        {
          model: this.model,
          messages: [
            { role: 'system', content: 'You are a financial document analysis assistant. You analyze financial documents and answer questions about them accurately and concisely.' },
            { role: 'user', content: prompt }
          ],
          response_format: { type: 'json_object' }
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      // Parse the response
      const aiResponse = response.data.choices[0].message.content;
      
      try {
        // Parse the JSON response
        const parsedResponse = JSON.parse(aiResponse);
        
        return {
          query,
          response: parsedResponse.response,
          data: parsedResponse.data || null,
          confidence: parsedResponse.confidence || null
        };
      } catch (error) {
        this.logger.error(`Error parsing AI response: ${error.message}`);
        return {
          query,
          response: 'Error parsing response: Invalid response format',
          data: null,
          confidence: 0
        };
      }
    } catch (error) {
      this.logger.error(`Error processing query: ${error.message}`, error);
      
      return {
        query,
        response: `Error processing query: ${error.message}`,
        data: null,
        confidence: 0
      };
    }
  }

  /**
   * Prepare document context for the prompt
   * @param {Object} documentData - The document data
   * @returns {string} - Document context
   * @private
   */
  _prepareDocumentContext(documentData) {
    let context = '';
    
    // Add basic document information
    if (documentData.id) {
      context += `Document ID: ${documentData.id}\n`;
    }
    
    if (documentData.filename) {
      context += `Filename: ${documentData.filename}\n`;
    }
    
    if (documentData.processed_at) {
      context += `Processed at: ${documentData.processed_at}\n`;
    }
    
    if (documentData.document_type) {
      context += `Document type: ${documentData.document_type}\n`;
    }
    
    context += '\n';
    
    // Add portfolio information
    if (documentData.portfolio_value) {
      context += `Portfolio value: $${documentData.portfolio_value.toLocaleString()}\n`;
    }
    
    // Add asset allocation
    if (documentData.asset_allocation) {
      context += 'Asset allocation:\n';
      
      Object.entries(documentData.asset_allocation).forEach(([assetClass, allocation]) => {
        context += `- ${assetClass}: ${(allocation * 100).toFixed(2)}%\n`;
      });
      
      context += '\n';
    }
    
    // Add securities
    if (documentData.securities && documentData.securities.length > 0) {
      context += `Securities (${documentData.securities.length}):\n`;
      
      documentData.securities.forEach(security => {
        context += `- ${security.name} (${security.isin}): `;
        
        if (security.quantity) {
          context += `${security.quantity.toLocaleString()} shares, `;
        }
        
        if (security.price) {
          context += `$${security.price.toLocaleString()} per share, `;
        }
        
        if (security.value) {
          context += `$${security.value.toLocaleString()} total`;
        }
        
        context += '\n';
      });
      
      context += '\n';
    }
    
    // Add performance information
    if (documentData.performance) {
      context += 'Performance:\n';
      
      Object.entries(documentData.performance).forEach(([period, value]) => {
        context += `- ${period}: ${(value * 100).toFixed(2)}%\n`;
      });
      
      context += '\n';
    }
    
    return context;
  }

  /**
   * Create a prompt for the AI
   * @param {string} query - The natural language query
   * @param {string} documentContext - The document context
   * @param {Object} options - Query options
   * @returns {string} - Prompt
   * @private
   */
  _createQueryPrompt(query, documentContext, options) {
    return `
I need you to analyze the following financial document data and answer a question about it.

DOCUMENT DATA:
${documentContext}

USER QUESTION:
${query}

Please provide a detailed and accurate answer based solely on the information provided in the document data.
If the information needed to answer the question is not available in the document data, please state that clearly.

Return your response as a JSON object with the following structure:
{
  "response": "Your detailed answer to the user's question",
  "data": {
    // Any relevant structured data that supports your answer
    // For example, if the question is about top holdings, include the top holdings data
    // If the question is about asset allocation, include the asset allocation data
  },
  "confidence": 0.95 // A number between 0 and 1 indicating your confidence in the answer
}
`;
  }
}

module.exports = QueryEngineAgent;
