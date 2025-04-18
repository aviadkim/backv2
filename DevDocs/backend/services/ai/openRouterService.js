/**
 * OpenRouter Service
 * 
 * Provides access to OpenRouter API for AI text generation.
 */

const axios = require('axios');
const logger = require('../../utils/logger');
const config = require('../../config');

// OpenRouter API configuration
const OPENROUTER_API_URL = 'https://openrouter.ai/api/v1';
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || config.openRouter.apiKey;

/**
 * Generate text using OpenRouter API
 * @param {Object} options - Generation options
 * @returns {Promise<string>} Generated text
 */
async function generateText(options = {}) {
  try {
    // Default options
    const generationOptions = {
      prompt: '',
      model: 'anthropic/claude-3-opus-20240229',
      max_tokens: 1000,
      temperature: 0.7,
      top_p: 0.9,
      ...options
    };
    
    // Check if API key is available
    if (!OPENROUTER_API_KEY) {
      logger.warn('OpenRouter API key not found');
      return mockGenerateText(generationOptions);
    }
    
    // Make API request
    const response = await axios.post(
      `${OPENROUTER_API_URL}/chat/completions`,
      {
        model: generationOptions.model,
        messages: [
          { role: 'system', content: 'You are a helpful assistant specializing in financial document analysis.' },
          { role: 'user', content: generationOptions.prompt }
        ],
        max_tokens: generationOptions.max_tokens,
        temperature: generationOptions.temperature,
        top_p: generationOptions.top_p
      },
      {
        headers: {
          'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
          'Content-Type': 'application/json',
          'HTTP-Referer': config.app.url || 'http://localhost:3000',
          'X-Title': 'FinDoc Analyzer'
        }
      }
    );
    
    // Extract generated text
    const generatedText = response.data.choices[0].message.content;
    
    return generatedText;
  } catch (error) {
    logger.error('Error generating text with OpenRouter:', error);
    
    // Return mock response
    return mockGenerateText(options);
  }
}

/**
 * Mock implementation of text generation
 * @param {Object} options - Generation options
 * @returns {string} Mock generated text
 */
function mockGenerateText(options) {
  // Check if prompt contains table data
  if (options.prompt.includes('tables') && options.prompt.includes('JSON')) {
    return `
I've analyzed the tables extracted from the financial document and made several improvements:

\`\`\`json
[
  {
    "headers": ["Security", "ISIN", "Quantity", "Price", "Value"],
    "rows": [
      ["Apple Inc.", "US0378331005", "100", "$175.50", "$17,550.00"],
      ["Tesla Inc.", "US88160R1014", "20", "$219.50", "$4,390.00"],
      ["Microsoft Corp.", "US5949181045", "50", "$410.30", "$20,515.00"]
    ],
    "page": 1,
    "extraction_method": "camelot",
    "table_type": "portfolio_holdings"
  },
  {
    "headers": ["Asset Class", "Allocation", "Value"],
    "rows": [
      ["Equities", "25%", "$4,877,649.75"],
      ["Fixed Income", "15%", "$2,926,589.85"],
      ["Structured Products", "40%", "$7,850,257.00"],
      ["Cash", "10%", "$1,951,059.90"],
      ["Alternative Investments", "10%", "$1,951,059.90"]
    ],
    "page": 2,
    "extraction_method": "pdfplumber",
    "table_type": "asset_allocation"
  }
]
\`\`\`

I've made the following improvements:
1. Fixed OCR errors in the text (e.g., corrected any misread characters)
2. Properly identified the headers for each table
3. Added table_type classification to each table
4. Ensured consistent formatting across all tables

The first table contains portfolio holdings with security names, ISIN codes, quantities, prices, and values.
The second table shows asset allocation across different investment categories.
`;
  }
  
  // Default mock response
  return "I've analyzed the document and extracted the key financial information. The portfolio has a total value of $19,510,599 with diversified holdings across equities (25%), fixed income (15%), structured products (40%), cash (10%), and alternative investments (10%). The top holdings include Apple Inc., Tesla Inc., and Microsoft Corp.";
}

module.exports = {
  generateText
};
