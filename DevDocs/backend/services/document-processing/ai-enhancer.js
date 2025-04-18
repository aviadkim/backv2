/**
 * AI Enhancer
 * 
 * Uses AI to enhance and validate financial data extraction:
 * - Fills in missing information
 * - Corrects errors in extracted data
 * - Provides additional insights
 * - Improves accuracy of extraction
 */

const axios = require('axios');
const logger = require('../../utils/logger');

/**
 * Enhance extracted data using AI
 * @param {Object} options - Enhancement options
 * @param {string} options.extractedText - Extracted text from the document
 * @param {Array} options.tables - Extracted tables from the document
 * @param {Array} options.isins - Extracted ISINs from the document
 * @param {Object} options.financialData - Extracted financial data
 * @param {string} options.documentType - Type of document
 * @returns {Promise<Object>} - Enhanced financial data
 */
async function enhanceWithAI(options) {
  const { extractedText, tables, isins, financialData, documentType } = options;
  
  logger.info(`Enhancing financial data with AI`);
  
  try {
    // Create a prompt for the AI
    const prompt = createAIPrompt(extractedText, tables, isins, financialData, documentType);
    
    // Call the OpenRouter API
    const enhancedData = await callOpenRouterAPI(prompt, financialData);
    
    logger.info(`AI enhancement completed successfully`);
    return enhancedData;
  } catch (error) {
    logger.error(`Error enhancing with AI: ${error.message}`, error);
    // Return the original data if AI enhancement fails
    return financialData;
  }
}

/**
 * Create a prompt for the AI
 * @param {string} extractedText - Extracted text from the document
 * @param {Array} tables - Extracted tables from the document
 * @param {Array} isins - Extracted ISINs from the document
 * @param {Object} financialData - Extracted financial data
 * @param {string} documentType - Type of document
 * @returns {string} - AI prompt
 */
function createAIPrompt(extractedText, tables, isins, financialData, documentType) {
  // Create a summary of the extracted data
  const dataSummary = JSON.stringify({
    portfolio_value: financialData.portfolio_value,
    asset_allocation: financialData.asset_allocation,
    securities_count: financialData.securities.length,
    isins_count: isins.length,
    tables_count: tables.length,
    document_type: documentType
  }, null, 2);
  
  // Create a summary of potential issues or missing data
  const issues = [];
  
  if (!financialData.portfolio_value) {
    issues.push("Missing portfolio value");
  }
  
  if (Object.keys(financialData.asset_allocation).length === 0) {
    issues.push("Missing asset allocation");
  }
  
  const securitiesWithMissingData = financialData.securities.filter(s => 
    !s.name || !s.quantity || !s.value || !s.price
  );
  
  if (securitiesWithMissingData.length > 0) {
    issues.push(`${securitiesWithMissingData.length} securities have missing data`);
  }
  
  // Create the prompt
  return `
You are a financial document analysis AI. You need to enhance and validate financial data extracted from a ${documentType} document.

Here's a summary of the extracted data:
${dataSummary}

${issues.length > 0 ? `Issues that need to be addressed:\n${issues.join('\n')}` : 'No major issues detected.'}

The document contains the following text excerpt:
${extractedText.substring(0, 2000)}...

Based on this information, please:
1. Validate the portfolio value and correct it if necessary
2. Fill in any missing asset allocation data
3. Enhance the securities data by filling in missing names, quantities, prices, and values
4. Correct any obvious errors in the data
5. Return the enhanced financial data in JSON format

Only include factual information that can be directly inferred from the document. Do not make up data.
`;
}

/**
 * Call the OpenRouter API to enhance the data
 * @param {string} prompt - AI prompt
 * @param {Object} originalData - Original financial data
 * @returns {Promise<Object>} - Enhanced financial data
 */
async function callOpenRouterAPI(prompt, originalData) {
  logger.info(`Calling OpenRouter API`);
  
  try {
    // Get the API key from environment variables
    const apiKey = process.env.OPENROUTER_API_KEY || 'sk-or-v1-64e1068c3a61a5e4be88c64c6992b39dbc15ad687201cb3fd05a98a9ba1e22dc8';
    
    // Make the API request
    const response = await axios.post(
      'https://openrouter.ai/api/v1/chat/completions',
      {
        model: 'anthropic/claude-3-opus:beta',
        messages: [
          { role: 'system', content: 'You are a financial document analysis AI assistant. You analyze financial documents and extract accurate information.' },
          { role: 'user', content: prompt }
        ],
        response_format: { type: 'json_object' }
      },
      {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    // Parse the response
    const aiResponse = response.data.choices[0].message.content;
    
    try {
      // Parse the JSON response
      const enhancedData = JSON.parse(aiResponse);
      
      // Merge with original data, keeping original data where AI didn't provide enhancements
      return mergeFinancialData(originalData, enhancedData);
    } catch (error) {
      logger.error(`Error parsing AI response: ${error.message}`);
      return originalData;
    }
  } catch (error) {
    logger.error(`Error calling OpenRouter API: ${error.message}`);
    return originalData;
  }
}

/**
 * Merge original and enhanced financial data
 * @param {Object} originalData - Original financial data
 * @param {Object} enhancedData - Enhanced financial data from AI
 * @returns {Object} - Merged financial data
 */
function mergeFinancialData(originalData, enhancedData) {
  // Create a deep copy of the original data
  const mergedData = JSON.parse(JSON.stringify(originalData));
  
  // Update portfolio value if AI provided one and original is missing
  if (enhancedData.portfolio_value && !originalData.portfolio_value) {
    mergedData.portfolio_value = enhancedData.portfolio_value;
  }
  
  // Merge asset allocation
  if (enhancedData.asset_allocation) {
    mergedData.asset_allocation = {
      ...originalData.asset_allocation,
      ...enhancedData.asset_allocation
    };
  }
  
  // Merge securities data
  if (enhancedData.securities && Array.isArray(enhancedData.securities)) {
    // Create a map of original securities by ISIN
    const securitiesMap = new Map();
    originalData.securities.forEach(security => {
      securitiesMap.set(security.isin, security);
    });
    
    // Update securities with enhanced data
    enhancedData.securities.forEach(enhancedSecurity => {
      if (enhancedSecurity.isin && securitiesMap.has(enhancedSecurity.isin)) {
        const originalSecurity = securitiesMap.get(enhancedSecurity.isin);
        
        // Update security with enhanced data, keeping original data where available
        securitiesMap.set(enhancedSecurity.isin, {
          ...originalSecurity,
          name: originalSecurity.name || enhancedSecurity.name,
          quantity: originalSecurity.quantity || enhancedSecurity.quantity,
          price: originalSecurity.price || enhancedSecurity.price,
          value: originalSecurity.value || enhancedSecurity.value,
          currency: originalSecurity.currency || enhancedSecurity.currency,
          securityType: originalSecurity.securityType || enhancedSecurity.securityType
        });
      } else if (enhancedSecurity.isin) {
        // Add new security
        securitiesMap.set(enhancedSecurity.isin, enhancedSecurity);
      }
    });
    
    // Update the merged data with the updated securities
    mergedData.securities = Array.from(securitiesMap.values());
  }
  
  // Merge performance data
  if (enhancedData.performance) {
    mergedData.performance = {
      ...originalData.performance,
      ...enhancedData.performance
    };
  }
  
  // Update currency if AI provided one and original is missing
  if (enhancedData.currency && !originalData.currency) {
    mergedData.currency = enhancedData.currency;
  }
  
  return mergedData;
}

module.exports = {
  enhanceWithAI
};
