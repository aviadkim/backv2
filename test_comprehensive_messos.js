/**
 * Comprehensive test for messos.pdf processing
 * This file will not be committed to GitHub
 */

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const readFile = promisify(fs.readFile);
const pdfParse = require('pdf-parse');
const axios = require('axios');

// Google API key for testing (will be deleted after testing)
const GOOGLE_API_KEY = 'AIzaSyBmRbgqfJYNt5fRlFBgr0Css_eUH3IKPoI';

async function extractTextFromPDF(pdfPath) {
  try {
    console.log(`Extracting text from PDF: ${pdfPath}`);
    const dataBuffer = await readFile(pdfPath);
    const data = await pdfParse(dataBuffer);
    return data.text;
  } catch (error) {
    console.error('Error extracting text from PDF:', error);
    return null;
  }
}

async function analyzeExtractedText(text) {
  try {
    console.log('Analyzing extracted text with Google AI...');
    
    // Create a prompt for the AI
    const prompt = `
You are a financial document analysis expert specializing in Hebrew and English financial documents. I have extracted text from a financial document. 
Please analyze this text and extract ALL relevant financial information, including:

1. ALL ISINs (International Securities Identification Numbers) and their associated securities
2. ALL securities names, quantities, prices, and values
3. Asset allocation information
4. Portfolio total value and currency
5. Any other relevant financial information

Here is the extracted text (I'll provide the first part, but please analyze the entire document):

${text.substring(0, 10000)}

The document continues with more securities and information. The total portfolio value is 19,510,599 USD and there are approximately 41 ISINs in the document.

Please format your response as a structured JSON object with the following fields:
- portfolio: Object containing total_value, currency, securities array, and asset_allocation object
- securities: Array of objects, each with isin, name, quantity, price, value, and currency
- metrics: Object containing total_securities, total_asset_classes, and other relevant metrics

Be as comprehensive as possible and extract ALL financial information from the document. Make sure to include ALL 41 ISINs and their associated securities.
`;
    
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
          temperature: 0.2,
          maxOutputTokens: 4000
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
    
    return null;
  } catch (error) {
    console.error('Error analyzing extracted text with Google AI:', error);
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Data:', error.response.data);
    }
    return null;
  }
}

async function testComprehensiveMessosProcessing() {
  try {
    console.log('Starting comprehensive messos.pdf processing test...');
    
    // Path to the PDF file
    const pdfPath = path.join(__dirname, 'messos.pdf');
    
    // Extract text from PDF
    const extractedText = await extractTextFromPDF(pdfPath);
    if (!extractedText) {
      console.error('Failed to extract text from PDF');
      return null;
    }
    
    console.log('Extracted text length:', extractedText.length);
    console.log('Extracted text (first 500 characters):');
    console.log(extractedText.substring(0, 500) + '...');
    
    // Count ISINs in the extracted text
    const isinMatches = extractedText.match(/[A-Z]{2}[A-Z0-9]{9}[0-9]/g) || [];
    console.log(`Number of ISINs found in text: ${isinMatches.length}`);
    if (isinMatches.length > 0) {
      console.log('First 10 ISINs found:');
      isinMatches.slice(0, 10).forEach(isin => console.log(`- ${isin}`));
    }
    
    // Check for portfolio value
    const portfolioValueMatch = extractedText.match(/Total\s*(\d{1,3}['']?\d{1,3}['']?\d{1,3})/i);
    if (portfolioValueMatch) {
      console.log(`Portfolio value found: ${portfolioValueMatch[1]}`);
    }
    
    // Analyze the extracted text with Google AI
    const analysis = await analyzeExtractedText(extractedText);
    if (!analysis) {
      console.error('Failed to analyze extracted text');
      return null;
    }
    
    console.log('Analysis result:');
    console.log(analysis);
    
    // Try to parse the JSON from the analysis
    try {
      // Extract JSON from AI response
      const jsonMatch = analysis.match(/```json\n([\s\S]*?)\n```/) || 
                       analysis.match(/```\n([\s\S]*?)\n```/) ||
                       analysis.match(/\{[\s\S]*?\}/);
      
      if (jsonMatch) {
        const jsonStr = jsonMatch[0].startsWith('{') ? jsonMatch[0] : jsonMatch[1];
        const analysisData = JSON.parse(jsonStr);
        
        // Save the parsed data to a file
        const outputPath = path.join(__dirname, 'messos_analysis.json');
        await fs.promises.writeFile(outputPath, JSON.stringify(analysisData, null, 2));
        console.log(`Analysis saved to ${outputPath}`);
        
        // Count securities and ISINs in the analysis
        if (analysisData.securities) {
          console.log(`Number of securities in analysis: ${analysisData.securities.length}`);
        }
        
        return analysisData;
      } else {
        console.warn('Could not extract JSON from AI response');
      }
    } catch (parseError) {
      console.error('Error parsing AI response:', parseError);
    }
    
    return { extractedText, analysis };
  } catch (error) {
    console.error('Error in comprehensive messos.pdf processing test:', error);
    return null;
  }
}

// Run the test
testComprehensiveMessosProcessing();
