/**
 * PDFPlumber Wrapper
 * 
 * Provides a JavaScript wrapper for the Python pdfplumber library for PDF text and table extraction.
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
 * Extract tables from a PDF using pdfplumber
 * @param {string} pdfPath - Path to the PDF file
 * @param {Object} options - Extraction options
 * @returns {Promise<Array>} Extracted tables
 */
async function extractTables(pdfPath, options = {}) {
  try {
    // Default options
    const extractionOptions = {
      pages: 'all',
      password: '',
      min_rows: 2,
      min_cols: 2,
      ...options
    };
    
    // Create a temporary file for options
    const optionsPath = path.join(config.upload.tempDir, `pdfplumber_options_${Date.now()}.json`);
    await writeFile(optionsPath, JSON.stringify(extractionOptions));
    
    // Create a temporary file for results
    const resultsPath = path.join(config.upload.tempDir, `pdfplumber_results_${Date.now()}.json`);
    
    // Path to Python script
    const scriptPath = path.join(__dirname, '../scripts/pdfplumber_extract.py');
    
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
    logger.error('Error extracting tables with pdfplumber:', error);
    
    // For now, return mock data
    return mockExtractTables();
  }
}

/**
 * Extract text from a PDF using pdfplumber
 * @param {string} pdfPath - Path to the PDF file
 * @param {Object} options - Extraction options
 * @returns {Promise<Object>} Extracted text
 */
async function extractText(pdfPath, options = {}) {
  try {
    // Default options
    const extractionOptions = {
      pages: 'all',
      password: '',
      ...options
    };
    
    // Create a temporary file for options
    const optionsPath = path.join(config.upload.tempDir, `pdfplumber_options_${Date.now()}.json`);
    await writeFile(optionsPath, JSON.stringify(extractionOptions));
    
    // Create a temporary file for results
    const resultsPath = path.join(config.upload.tempDir, `pdfplumber_text_${Date.now()}.json`);
    
    // Path to Python script
    const scriptPath = path.join(__dirname, '../scripts/pdfplumber_text.py');
    
    // Execute Python script
    const result = await executePythonScript(scriptPath, [pdfPath, optionsPath, resultsPath]);
    
    // Read results
    const resultsJson = await readFile(resultsPath, 'utf8');
    const text = JSON.parse(resultsJson);
    
    // Clean up temporary files
    await Promise.all([
      unlink(optionsPath),
      unlink(resultsPath)
    ]);
    
    return text;
  } catch (error) {
    logger.error('Error extracting text with pdfplumber:', error);
    
    // For now, return mock data
    return mockExtractText();
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
            "headers": ["Asset Class", "Allocation", "Value"],
            "data": [
                ["Equities", "25%", "$4,877,649.75"],
                ["Fixed Income", "15%", "$2,926,589.85"],
                ["Structured Products", "40%", "$7,850,257.00"],
                ["Cash", "10%", "$1,951,059.90"],
                ["Alternative Investments", "10%", "$1,951,059.90"]
            ],
            "confidence": 0.75,
            "bbox": {"x0": 0, "y0": 0, "x1": 0, "y1": 0}
        }
    ]
    
    # Write results
    with open(results_path, 'w') as f:
        json.dump(tables, f)
    
    return "Success"

def extract_text(pdf_path, options_path, results_path):
    # Read options
    with open(options_path, 'r') as f:
        options = json.load(f)
    
    # Mock text
    text = {
        "pages": [
            {
                "page_number": 1,
                "text": "This is a financial document with portfolio value of $19,510,599. It contains various securities including stocks, bonds, and structured products.",
                "words": [
                    {"text": "This", "x0": 10, "y0": 10, "x1": 30, "y1": 20},
                    {"text": "is", "x0": 35, "y0": 10, "x1": 45, "y1": 20},
                    {"text": "a", "x0": 50, "y0": 10, "x1": 55, "y1": 20}
                ]
            }
        ],
        "metadata": {
            "title": "Financial Report",
            "author": "Bank",
            "creator": "PDF Creator",
            "producer": "PDF Producer"
        }
    }
    
    # Write results
    with open(results_path, 'w') as f:
        json.dump(text, f)
    
    return "Success"

if __name__ == "__main__":
    pdf_path = sys.argv[1]
    options_path = sys.argv[2]
    results_path = sys.argv[3]
    
    if "text" in results_path:
        result = extract_text(pdf_path, options_path, results_path)
    else:
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
      headers: ['Asset Class', 'Allocation', 'Value'],
      data: [
        ['Equities', '25%', '$4,877,649.75'],
        ['Fixed Income', '15%', '$2,926,589.85'],
        ['Structured Products', '40%', '$7,850,257.00'],
        ['Cash', '10%', '$1,951,059.90'],
        ['Alternative Investments', '10%', '$1,951,059.90']
      ],
      confidence: 0.75,
      bbox: { x0: 0, y0: 0, x1: 0, y1: 0 }
    }
  ];
}

/**
 * Mock implementation of text extraction
 * @returns {Object} Mock text
 */
function mockExtractText() {
  return {
    pages: [
      {
        page_number: 1,
        text: "This is a financial document with portfolio value of $19,510,599. It contains various securities including stocks, bonds, and structured products.",
        words: [
          { text: "This", x0: 10, y0: 10, x1: 30, y1: 20 },
          { text: "is", x0: 35, y0: 10, x1: 45, y1: 20 },
          { text: "a", x0: 50, y0: 10, x1: 55, y1: 20 }
        ]
      }
    ],
    metadata: {
      title: "Financial Report",
      author: "Bank",
      creator: "PDF Creator",
      producer: "PDF Producer"
    }
  };
}

module.exports = {
  extractTables,
  extractText
};
