/**
 * Test script to check the content of messos.pdf
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

async function checkPDFContent() {
  try {
    // Check different messos.pdf files
    const pdfPaths = [
      path.join(__dirname, 'messos.pdf'),
      path.join(__dirname, 'DevDocs', 'frontend', 'public', 'messos.pdf'),
      path.join(__dirname, 'DevDocs', 'public', 'messos.pdf')
    ];
    
    for (const pdfPath of pdfPaths) {
      if (fs.existsSync(pdfPath)) {
        console.log(`\nChecking ${pdfPath}...`);
        const text = await extractTextFromPDF(pdfPath);
        
        if (text) {
          // Check for key indicators
          const hasDate = text.includes('28.02.2025');
          const hasPortfolioValue = text.includes('19510599') || text.includes('19,510,599');
          const isinCount = (text.match(/[A-Z]{2}[A-Z0-9]{9}[0-9]/g) || []).length;
          
          console.log(`Contains date 28.02.2025: ${hasDate}`);
          console.log(`Contains portfolio value ~19,510,599: ${hasPortfolioValue}`);
          console.log(`Number of ISINs found: ${isinCount}`);
          
          // Print first 500 characters of the text
          console.log('\nFirst 500 characters:');
          console.log(text.substring(0, 500) + '...');
          
          // Print a section around "total" or "portfolio value" if it exists
          const totalIndex = text.toLowerCase().indexOf('total');
          if (totalIndex !== -1) {
            console.log('\nSection around "total":');
            console.log(text.substring(Math.max(0, totalIndex - 100), totalIndex + 200) + '...');
          }
          
          // Print a section around "ISIN" if it exists
          const isinIndex = text.indexOf('ISIN');
          if (isinIndex !== -1) {
            console.log('\nSection around "ISIN":');
            console.log(text.substring(Math.max(0, isinIndex - 50), isinIndex + 200) + '...');
          }
        } else {
          console.log('Failed to extract text from PDF');
        }
      } else {
        console.log(`File not found: ${pdfPath}`);
      }
    }
  } catch (error) {
    console.error('Error checking PDF content:', error);
  }
}

// Run the check
checkPDFContent();
