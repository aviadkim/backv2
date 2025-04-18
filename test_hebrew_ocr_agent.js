/**
 * Test script for HebrewOCRAgent
 * This file will not be committed to GitHub
 */

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const readFile = promisify(fs.readFile);
const axios = require('axios');

// Google API key for testing (will be deleted after testing)
const GOOGLE_API_KEY = 'AIzaSyBmRbgqfJYNt5fRlFBgr0Css_eUH3IKPoI';

// Mock the required modules
const mockLogger = {
  info: console.log,
  error: console.error,
  warn: console.warn,
  debug: console.log
};

// Mock the OpenRouter service
const mockOpenRouterService = {
  generateText: async ({ prompt, model, max_tokens, temperature }) => {
    console.log('Generating text with Google AI...');
    console.log('Prompt:', prompt.substring(0, 100) + '...');
    
    try {
      // Call Google AI API
      const response = await axios.post(
        `https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key=${GOOGLE_API_KEY}`,
        {
          contents: [
            {
              parts: [
                {
                  text: prompt
                }
              ]
            }
          ],
          generationConfig: {
            temperature: temperature || 0.2,
            maxOutputTokens: max_tokens || 2000
          }
        },
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
      
      if (response.data && response.data.candidates && response.data.candidates.length > 0) {
        const content = response.data.candidates[0].content;
        if (content && content.parts && content.parts.length > 0) {
          return content.parts[0].text;
        }
      }
      
      return "No response from AI";
    } catch (error) {
      console.error('Error calling Google AI:', error);
      if (error.response) {
        console.error('Status:', error.response.status);
        console.error('Data:', error.response.data);
      }
      return "Error calling AI: " + error.message;
    }
  }
};

// Create a simplified version of the HebrewOCRAgent
class HebrewOCRAgent {
  constructor(options = {}) {
    this.options = {
      model: 'anthropic/claude-3-opus-20240229',
      maxTokens: 4000,
      temperature: 0.7,
      ...options
    };
    
    console.log('HebrewOCRAgent initialized');
  }
  
  async processDocument(options) {
    try {
      console.log(`Processing document: ${options.fileName}`);
      
      // Extract text from PDF using a simple approach
      // In a real implementation, this would use OCR and more sophisticated techniques
      const pdfText = await this.extractTextFromPDF(options.buffer);
      
      // Analyze the extracted text
      const result = await this.analyzeText(pdfText, options.fileName);
      
      return result;
    } catch (error) {
      console.error('Error processing document:', error);
      throw error;
    }
  }
  
  async extractTextFromPDF(buffer) {
    try {
      // In a real implementation, this would use OCR and more sophisticated techniques
      // For this test, we'll just return a sample text
      return `
euioaeuioa
Valuation
as of 28.02.2025
Swift CBLUCH2280A // Clearing 8490 // CHE-105.962.409 IVA
Tel. +41 44 218 10 20 // Fax +41 44218 1029 // info@corner.ch // corner.ch
Cornèr Banca SA
// Töd istrasse27 // Postfach 16 40 // 8027 Zürich_Switzerland // Hauptsitz Via Canova 16, 6901 Lugano_Switzerland
MESSOS ENTERPRISES LTD.
366223
Client Number //
USD
Valuation currency //
Undefined
Investment profile //
Medium-high
Risk Profile //

Index
MESSOS ENTERPRISES LTD.
Valuation as of 28.02.2025
Client Number // 366223

Asset Allocation
Equities: 12.58%
Fixed Income: 87.42%

Currency Allocation
USD: 100%

Performance Overview
YTD: +2.45%
1 Year: +5.67%
3 Years: +12.34%

Top Holdings
1. UBS Group 4.25% 2028 (XS2315191069): $198,600.00 (23.46%)
2. Credit Suisse 3.75% 2026 (XS2281342878): $195,000.00 (23.04%)
3. US Treasury Bond 4.25% 2028 (US91282CFX29): $151,875.00 (17.94%)
4. US Treasury Bond 3.5% 2033 (US91282CJL79): $98,750.00 (11.67%)
5. Apple Inc. 3.85% 2043 (US037833DX25): $95,750.00 (11.31%)

Asset Listing
Equities:
- Meta Platforms Inc. (US30303M1027): 40 shares, $485.20/share, $19,408.00
- Microsoft Corp. (US5949181045): 50 shares, $410.30/share, $20,515.00
- Apple Inc. (US0378331005): 100 shares, $175.50/share, $17,550.00
- NVIDIA Corp. (US67066G1040): 15 shares, $890.50/share, $13,357.50
- Johnson & Johnson (US4781601046): 60 shares, $157.80/share, $9,468.00
- Coca-Cola Co. (US1912161007): 120 shares, $60.15/share, $7,218.00
- Amazon.com Inc. (US0231351067): 30 shares, $178.75/share, $5,362.50
- Alphabet Inc. (US02079K1079): 25 shares, $175.85/share, $4,396.25
- Tesla Inc. (US88160R1014): 20 shares, $219.50/share, $4,390.00
- Walmart Inc. (US9311421039): 80 shares, $59.75/share, $4,780.00

Fixed Income:
- UBS Group 4.25% 2028 (XS2315191069): $200,000 nominal, 99.30% price, $198,600.00
- Credit Suisse 3.75% 2026 (XS2281342878): $200,000 nominal, 97.50% price, $195,000.00
- US Treasury Bond 4.25% 2028 (US91282CFX29): $150,000 nominal, 101.25% price, $151,875.00
- US Treasury Bond 3.5% 2033 (US91282CJL79): $100,000 nominal, 98.75% price, $98,750.00
- Apple Inc. 3.85% 2043 (US037833DX25): $100,000 nominal, 95.75% price, $95,750.00

Total Portfolio Value: $846,420.25 USD
      `;
    } catch (error) {
      console.error('Error extracting text from PDF:', error);
      throw error;
    }
  }
  
  async analyzeText(text, fileName) {
    try {
      console.log('Analyzing text...');
      
      // Create a prompt for the AI
      const prompt = `
You are a financial document analysis expert specializing in Hebrew and English financial documents. I have extracted text from a financial document. 
Please analyze this text and extract all relevant financial information, including:

1. All ISINs (International Securities Identification Numbers) and their associated securities
2. All securities names, quantities, prices, and values
3. Asset allocation information
4. Portfolio total value and currency
5. Any other relevant financial information

Here is the extracted text:

${text}

Please format your response as a structured JSON object with the following fields:
- portfolio: Object containing total_value, currency, securities array, and asset_allocation object
- securities: Array of objects, each with isin, name, quantity, price, value, and currency
- metrics: Object containing total_securities, total_asset_classes, and other relevant metrics

Be as comprehensive as possible and extract ALL financial information from the document.
`;
      
      // Call AI service
      const aiResponse = await mockOpenRouterService.generateText({
        prompt,
        model: this.options.model,
        max_tokens: this.options.maxTokens,
        temperature: this.options.temperature
      });
      
      // Parse AI response
      try {
        // Extract JSON from AI response
        const jsonMatch = aiResponse.match(/```json\n([\s\S]*?)\n```/) || 
                         aiResponse.match(/```\n([\s\S]*?)\n```/) ||
                         aiResponse.match(/\{[\s\S]*?\}/);
        
        if (jsonMatch) {
          const jsonStr = jsonMatch[0].startsWith('{') ? jsonMatch[0] : jsonMatch[1];
          const analysisData = JSON.parse(jsonStr);
          return analysisData;
        } else {
          console.warn('Could not extract JSON from AI response');
          return { error: 'Could not extract structured data', text: aiResponse };
        }
      } catch (parseError) {
        console.error('Error parsing AI response:', parseError);
        return { error: 'Error parsing AI response', text: aiResponse };
      }
    } catch (error) {
      console.error('Error analyzing text:', error);
      throw error;
    }
  }
}

async function testHebrewOCRAgent() {
  try {
    console.log('Testing HebrewOCRAgent...');
    
    // Create an instance of the HebrewOCRAgent
    const ocrAgent = new HebrewOCRAgent({
      model: 'anthropic/claude-3-opus-20240229',
      maxTokens: 4000,
      temperature: 0.7
    });
    
    // Path to the PDF file
    const pdfPath = path.join(__dirname, 'messos.pdf');
    
    // Read the PDF file
    const pdfBuffer = await readFile(pdfPath);
    
    // Process the document
    console.log('Processing document...');
    const result = await ocrAgent.processDocument({
      buffer: pdfBuffer,
      fileName: 'messos.pdf',
      language: 'heb+eng'
    });
    
    console.log('Processing result:');
    console.log(JSON.stringify(result, null, 2));
    
    return result;
  } catch (error) {
    console.error('Error testing HebrewOCRAgent:', error);
    return null;
  }
}

// Run the test
testHebrewOCRAgent();
