/**
 * Run Enhanced Processing
 * 
 * This script runs the enhanced document processing pipeline on a PDF file.
 * It's a simple command-line tool for testing the enhanced processing.
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// Import the document processor
const DocumentProcessor = require('./DevDocs/backend/enhanced_processing/document_processor');

// Parse command line arguments
const args = process.argv.slice(2);
if (args.length < 1) {
  console.error('Usage: node run_enhanced_processing.js <pdf_path> [output_dir]');
  process.exit(1);
}

const pdfPath = args[0];
const outputDir = args[1] || path.join(path.dirname(pdfPath), 'enhanced_output');

// Check if the PDF file exists
if (!fs.existsSync(pdfPath)) {
  console.error(`PDF file not found: ${pdfPath}`);
  process.exit(1);
}

// Create output directory
fs.mkdirSync(outputDir, { recursive: true });

// Get API key from environment
const apiKey = process.env.GOOGLE_API_KEY;

console.log(`Processing document: ${pdfPath}`);
console.log(`Output directory: ${outputDir}`);

// Create processor
const processor = new DocumentProcessor(apiKey);

// Process document
processor.process(pdfPath, outputDir, ['eng', 'heb'])
  .then(result => {
    console.log(`Processing complete, extracted ${result.portfolio.securities.length} securities`);
    console.log(`Total value: ${result.portfolio.total_value} ${result.portfolio.currency}`);
    console.log(`Asset classes: ${Object.keys(result.portfolio.asset_allocation).length}`);
    
    // Print securities
    console.log('\nSecurities:');
    result.portfolio.securities.slice(0, 5).forEach(security => {
      console.log(`- ${security.name || 'Unnamed'} (${security.isin}): ${security.value} ${security.currency}`);
    });
    if (result.portfolio.securities.length > 5) {
      console.log(`... and ${result.portfolio.securities.length - 5} more`);
    }
    
    // Print asset allocation
    console.log('\nAsset Allocation:');
    Object.entries(result.portfolio.asset_allocation).forEach(([assetClass, allocation]) => {
      console.log(`- ${assetClass}: ${allocation.value} ${result.portfolio.currency} (${(allocation.weight * 100).toFixed(2)}%)`);
    });
    
    console.log(`\nResult saved to ${path.join(outputDir, path.basename(pdfPath, '.pdf') + '_processed.json')}`);
  })
  .catch(error => {
    console.error(`Error processing document: ${error.message}`);
    process.exit(1);
  });
