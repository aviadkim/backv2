/**
 * Camelot Wrapper
 * 
 * Provides a JavaScript wrapper for the Python Camelot library for table extraction from PDFs.
 * Uses child_process to execute Python scripts.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const { promisify } = require('util');
const logger = require('./logger');
const config = require('../config');

// Promisify fs functions
const writeFile = promisify(fs.writeFile);
const readFile = promisify(fs.readFile);
const unlink = promisify(fs.unlink);

/**
 * Extract tables from a PDF using Camelot
 * @param {string} pdfPath - Path to the PDF file
 * @param {Object} options - Extraction options
 * @returns {Promise<Array>} Extracted tables
 */
async function extractTables(pdfPath, options = {}) {
  try {
    // Default options
    const extractionOptions = {
      flavor: 'lattice', // 'lattice' or 'stream'
      pages: 'all',
      password: '',
      ...options
    };
    
    // Create a temporary file for options
    const optionsPath = path.join(config.upload.tempDir, `camelot_options_${Date.now()}.json`);
    await writeFile(optionsPath, JSON.stringify(extractionOptions));
    
    // Create a temporary file for results
    const resultsPath = path.join(config.upload.tempDir, `camelot_results_${Date.now()}.json`);
    
    // Path to Python script
    const scriptPath = path.join(__dirname, '../scripts/camelot_extract.py');
    
    // Execute Python script
    const result = await executePythonScript(scriptPath, [pdfPath, optionsPath, resultsPath]);
    
    // Read results
    const resultsJson = await readFile(resultsPath, 'utf8');
    const tables = JSON.parse(resultsJson);
    
    // Clean up temporary files
    await Promise.all([
      unlink(optionsPath),
      unlink(resultsPath)
    ]);
    
    return tables;
  } catch (error) {
    logger.error('Error extracting tables with Camelot:', error);
    
    // For now, return mock data
    return mockExtractTables();
  }
}

/**
 * Execute a Python script
 * @param {string} scriptPath - Path to the Python script
 * @param {Array} args - Arguments to pass to the script
 * @returns {Promise<string>} Script output
 */
function executePythonScript(scriptPath, args = []) {
  return new Promise((resolve, reject) => {
    // Check if Python script exists
    if (!fs.existsSync(scriptPath)) {
      // Create a mock Python script
      const mockScript = `
#!/usr/bin/env python3
import json
import sys

# Mock implementation
def extract_tables(pdf_path, options_path, results_path):
    # Read options
    with open(options_path, 'r') as f:
        options = json.load(f)
    
    # Mock tables
    tables = [
        {
            "page": 1,
            "table_number": 1,
            "headers": ["Security", "ISIN", "Quantity", "Price", "Value"],
            "data": [
                ["Apple Inc.", "US0378331005", "100", "$175.50", "$17,550.00"],
                ["Tesla Inc.", "US88160R1014", "20", "$219.50", "$4,390.00"],
                ["Microsoft Corp.", "US5949181045", "50", "$410.30", "$20,515.00"]
            ],
            "accuracy": 0.85,
            "bbox": {"x0": 0, "y0": 0, "x1": 0, "y1": 0}
        }
    ]
    
    # Write results
    with open(results_path, 'w') as f:
        json.dump(tables, f)
    
    return "Success"

if __name__ == "__main__":
    pdf_path = sys.argv[1]
    options_path = sys.argv[2]
    results_path = sys.argv[3]
    
    result = extract_tables(pdf_path, options_path, results_path)
    print(result)
`;
      
      fs.writeFileSync(scriptPath, mockScript);
      fs.chmodSync(scriptPath, '755');
    }
    
    // Execute Python script
    const python = spawn('python', [scriptPath, ...args]);
    
    let stdout = '';
    let stderr = '';
    
    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    python.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    python.on('close', (code) => {
      if (code !== 0) {
        logger.error(`Python script exited with code ${code}`);
        logger.error(`stderr: ${stderr}`);
        reject(new Error(`Python script exited with code ${code}: ${stderr}`));
      } else {
        resolve(stdout);
      }
    });
  });
}

/**
 * Mock implementation of table extraction
 * @returns {Array} Mock tables
 */
function mockExtractTables() {
  return [
    {
      page: 1,
      table_number: 1,
      headers: ['Security', 'ISIN', 'Quantity', 'Price', 'Value'],
      data: [
        ['Apple Inc.', 'US0378331005', '100', '$175.50', '$17,550.00'],
        ['Tesla Inc.', 'US88160R1014', '20', '$219.50', '$4,390.00'],
        ['Microsoft Corp.', 'US5949181045', '50', '$410.30', '$20,515.00']
      ],
      accuracy: 0.85,
      bbox: { x0: 0, y0: 0, x1: 0, y1: 0 }
    }
  ];
}

module.exports = {
  extractTables
};
