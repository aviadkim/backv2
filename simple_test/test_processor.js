/**
 * Simple test script for the RAG Multimodal Financial Document Processor.
 */

const fs = require('fs');
const path = require('path');
const RagMultimodalProcessor = require('../backend/enhanced_processing/node_wrapper');

// Get API key from environment
const apiKey = process.env.OPENAI_API_KEY || process.env.GOOGLE_API_KEY;

// Create output directory
const outputDir = path.join(__dirname, 'output');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// Create processor
const processor = new RagMultimodalProcessor({
  apiKey,
  languages: ['eng', 'heb'],
  verbose: true
});

// Set progress callback
processor.setProgressCallback((progress) => {
  console.log(`Processing: ${Math.round(progress * 100)}%`);
});

// Process document
async function testProcessor() {
  try {
    // Check if PDF file exists
    const pdfPath = path.join(__dirname, 'messos.pdf');
    if (!fs.existsSync(pdfPath)) {
      console.error(`PDF file not found: ${pdfPath}`);
      console.log('Please place a PDF file named "messos.pdf" in the simple_test directory');
      return;
    }

    console.log(`Processing document: ${pdfPath}`);
    console.log(`Output directory: ${outputDir}`);

    // Process document
    const result = await processor.process(pdfPath, outputDir);

    console.log('\nProcessing complete!');
    console.log(`Document: ${result.document_info.document_name}`);
    console.log(`Total Value: ${result.portfolio.total_value.toLocaleString()} ${result.portfolio.currency}`);
    console.log(`Securities: ${result.metrics.total_securities}`);
    console.log(`Asset Classes: ${result.metrics.total_asset_classes}`);

    // Extract ISINs to a separate file
    const isins = result.portfolio.securities.map(security => security.isin);
    fs.writeFileSync(path.join(__dirname, 'messos_isins.json'), JSON.stringify(isins, null, 2));
    console.log(`Extracted ${isins.length} ISINs to messos_isins.json`);

    // Extract text to a separate file
    if (fs.existsSync(path.join(outputDir, 'ocr', 'ocr_text.txt'))) {
      const text = fs.readFileSync(path.join(outputDir, 'ocr', 'ocr_text.txt'), 'utf8');
      fs.writeFileSync(path.join(__dirname, 'messos_text.txt'), text);
      console.log(`Extracted text to messos_text.txt`);
    }

    // Extract tables to a separate file
    if (fs.existsSync(path.join(outputDir, 'tables', 'tables.json'))) {
      const tables = JSON.parse(fs.readFileSync(path.join(outputDir, 'tables', 'tables.json'), 'utf8'));
      fs.writeFileSync(path.join(__dirname, 'messos_tables.json'), JSON.stringify(tables, null, 2));
      console.log(`Extracted ${tables.length} tables to messos_tables.json`);
    }

    // Print accuracy
    if (result.accuracy) {
      console.log('\nAccuracy Metrics:');
      for (const [key, value] of Object.entries(result.accuracy)) {
        console.log(`${key}: ${(value * 100).toFixed(2)}%`);
      }
    }

    console.log(`\nProcessing Time: ${result.document_info.processing_time.toFixed(2)} seconds`);
  } catch (error) {
    console.error(`Error processing document: ${error.message}`);
    console.error(error.stack);
  }
}

// Run test
testProcessor();
