/**
 * Extract all ISINs from messos.pdf
 * This file will not be committed to GitHub
 */

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const readFile = promisify(fs.readFile);
const pdfParse = require('pdf-parse');

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

async function extractAllISINs() {
  try {
    // Path to the PDF file
    const pdfPath = path.join(__dirname, 'messos.pdf');
    
    // Extract text from PDF
    const extractedText = await extractTextFromPDF(pdfPath);
    if (!extractedText) {
      console.error('Failed to extract text from PDF');
      return null;
    }
    
    // Find all ISINs in the text
    const isinRegex = /[A-Z]{2}[A-Z0-9]{9}[0-9]/g;
    const isins = extractedText.match(isinRegex) || [];
    
    // Remove duplicates
    const uniqueIsins = [...new Set(isins)];
    
    console.log(`Found ${uniqueIsins.length} unique ISINs:`);
    uniqueIsins.forEach((isin, index) => {
      console.log(`${index + 1}. ${isin}`);
      
      // Find context around this ISIN
      const isinIndex = extractedText.indexOf(isin);
      if (isinIndex !== -1) {
        const contextStart = Math.max(0, isinIndex - 100);
        const contextEnd = Math.min(extractedText.length, isinIndex + 200);
        const context = extractedText.substring(contextStart, contextEnd);
        
        console.log(`   Context: ${context.replace(/\\n/g, ' ').trim()}`);
        console.log('---');
      }
    });
    
    // Save the ISINs to a file
    const outputPath = path.join(__dirname, 'messos_isins.json');
    await fs.promises.writeFile(outputPath, JSON.stringify(uniqueIsins, null, 2));
    console.log(`ISINs saved to ${outputPath}`);
    
    return uniqueIsins;
  } catch (error) {
    console.error('Error extracting ISINs:', error);
    return null;
  }
}

// Run the extraction
extractAllISINs();
