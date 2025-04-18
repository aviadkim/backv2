/**
 * Test script for the RAG Multimodal Financial Document Processor.
 */

const RagMultimodalProcessor = require('./node_wrapper');
const path = require('path');
const fs = require('fs');

// Get command line arguments
const args = process.argv.slice(2);
if (args.length < 1) {
  console.error('Usage: node test_processor.js <pdf_path> [output_dir]');
  process.exit(1);
}

const pdfPath = args[0];
const outputDir = args[1] || path.join(path.dirname(pdfPath), 'rag_output');

// Check if the PDF file exists
if (!fs.existsSync(pdfPath)) {
  console.error(`PDF file not found: ${pdfPath}`);
  process.exit(1);
}

// Create output directory
fs.mkdirSync(outputDir, { recursive: true });

// Get API key from environment
const apiKey = process.env.OPENAI_API_KEY || process.env.GOOGLE_API_KEY;

console.log(`Processing document: ${pdfPath}`);
console.log(`Output directory: ${outputDir}`);

// Create processor
const processor = new RagMultimodalProcessor({
  apiKey,
  languages: ['eng', 'heb'],
  verbose: true
});

// Set progress callback
processor.setProgressCallback((progress) => {
  const percent = Math.round(progress * 100);
  process.stdout.write(`\rProcessing: ${percent}%`);
});

// Process document
processor.process(pdfPath, outputDir)
  .then(result => {
    console.log('\n');
    console.log(`Processing complete, extracted ${result.metrics.total_securities} securities`);
    console.log(`Total value: ${result.portfolio.total_value} ${result.portfolio.currency}`);
    console.log(`Asset classes: ${result.metrics.total_asset_classes}`);
    
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
    
    // Print accuracy
    if (result.accuracy) {
      console.log('\nAccuracy:');
      Object.entries(result.accuracy).forEach(([metric, value]) => {
        console.log(`- ${metric}: ${(value * 100).toFixed(2)}%`);
      });
    }
    
    console.log(`\nResult saved to ${path.join(outputDir, 'final', path.basename(pdfPath, '.pdf') + '_processed.json')}`);
  })
  .catch(error => {
    console.error(`Error processing document: ${error.message}`);
    process.exit(1);
  });
