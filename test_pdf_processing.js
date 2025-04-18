/**
 * Test script for PDF processing
 * This file will not be committed to GitHub
 */

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const readFile = promisify(fs.readFile);

// Import the HebrewOCRAgent
const HebrewOCRAgent = require('./DevDocs/backend/agents/HebrewOCRAgent');

// API key should be loaded from environment variables or GitHub secrets
const API_KEY = process.env.OPENROUTER_API_KEY || process.env.CLAUDE_API_KEY || '';

async function testPDFProcessing() {
  try {
    console.log('Testing PDF processing with HebrewOCRAgent...');

    // Create an instance of the HebrewOCRAgent
    const ocrAgent = new HebrewOCRAgent({
      apiKey: API_KEY
    });

    // Path to the PDF file
    const pdfPath = path.join(__dirname, 'messos.pdf');

    // Read the PDF file
    const pdfBuffer = await readFile(pdfPath);

    // Process the PDF
    console.log('Processing PDF...');
    const result = await ocrAgent.processDocument({
      buffer: pdfBuffer,
      fileName: 'messos.pdf',
      language: 'heb+eng'
    });

    console.log('PDF processing result:');
    console.log(JSON.stringify(result, null, 2));

    return result;
  } catch (error) {
    console.error('Error processing PDF:', error);
    return null;
  }
}

// Run the test
testPDFProcessing();
