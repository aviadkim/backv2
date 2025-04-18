/**
 * Comprehensive test for PDF processing
 * This file will not be committed to GitHub
 */

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const readFile = promisify(fs.readFile);
const { exec } = require('child_process');
const execPromise = promisify(exec);
const axios = require('axios');

// Google API key for testing (will be deleted after testing)
const GOOGLE_API_KEY = 'AIzaSyBmRbgqfJYNt5fRlFBgr0Css_eUH3IKPoI';

// Check if Python is available
async function checkPython() {
  try {
    const { stdout } = await execPromise('python --version');
    console.log('Python version:', stdout.trim());
    return true;
  } catch (error) {
    console.error('Python is not available:', error.message);
    return false;
  }
}

// Check if required Python packages are installed
async function checkPythonPackages() {
  try {
    const packages = ['pytesseract', 'pdf2image', 'camelot-py', 'opencv-python', 'numpy', 'pandas'];
    for (const pkg of packages) {
      try {
        await execPromise(`python -c "import ${pkg.replace('-', '_')}"`, { timeout: 5000 });
        console.log(`✅ ${pkg} is installed`);
      } catch (error) {
        console.error(`❌ ${pkg} is not installed:`, error.message);
        console.log(`Installing ${pkg}...`);
        await execPromise(`pip install ${pkg}`, { timeout: 60000 });
      }
    }
    return true;
  } catch (error) {
    console.error('Error checking Python packages:', error.message);
    return false;
  }
}

// Create a Python script for comprehensive PDF processing
async function createPythonScript() {
  const scriptContent = `
import os
import sys
import json
import pytesseract
from pdf2image import convert_from_path
import camelot
import cv2
import numpy as np
import pandas as pd
from PIL import Image

def process_pdf(pdf_path, output_dir):
    """Process a PDF file and extract text, tables, and perform OCR."""
    print(f"Processing PDF: {pdf_path}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract text using PyPDF2
    text_output = os.path.join(output_dir, "extracted_text.txt")
    tables_output = os.path.join(output_dir, "extracted_tables.json")
    ocr_output = os.path.join(output_dir, "ocr_text.txt")
    
    # Convert PDF to images for OCR
    print("Converting PDF to images...")
    images = convert_from_path(pdf_path)
    
    # Perform OCR on each page
    print("Performing OCR...")
    ocr_text = ""
    for i, image in enumerate(images):
        page_text = pytesseract.image_to_string(image, lang='eng+heb')
        ocr_text += f"\\n\\n--- PAGE {i+1} ---\\n\\n{page_text}"
    
    # Save OCR text
    with open(ocr_output, "w", encoding="utf-8") as f:
        f.write(ocr_text)
    
    # Extract tables using Camelot
    print("Extracting tables...")
    try:
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
        print(f"Found {len(tables)} tables")
        
        # Convert tables to JSON
        tables_data = []
        for i, table in enumerate(tables):
            df = table.df
            tables_data.append({
                "table_number": i+1,
                "page": table.page,
                "headers": df.iloc[0].tolist(),
                "data": df.iloc[1:].values.tolist()
            })
        
        # Save tables data
        with open(tables_output, "w", encoding="utf-8") as f:
            json.dump(tables_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error extracting tables: {e}")
        tables_data = []
    
    # Combine all extracted data
    result = {
        "ocr_text": ocr_text,
        "tables": tables_data
    }
    
    # Save combined result
    combined_output = os.path.join(output_dir, "combined_result.json")
    with open(combined_output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Processing complete. Results saved to {output_dir}")
    return result

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process_pdf.py <pdf_path> <output_dir>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    process_pdf(pdf_path, output_dir)
  `;
  
  const scriptPath = path.join(__dirname, 'process_pdf.py');
  await fs.promises.writeFile(scriptPath, scriptContent);
  console.log(`Python script created at ${scriptPath}`);
  return scriptPath;
}

// Run the Python script to process the PDF
async function processPDFWithPython(pdfPath) {
  try {
    const outputDir = path.join(__dirname, 'pdf_output');
    await fs.promises.mkdir(outputDir, { recursive: true });
    
    const scriptPath = await createPythonScript();
    
    console.log(`Running Python script to process ${pdfPath}...`);
    const { stdout, stderr } = await execPromise(`python ${scriptPath} "${pdfPath}" "${outputDir}"`, { timeout: 300000 });
    
    console.log('Python script output:');
    console.log(stdout);
    
    if (stderr) {
      console.error('Python script errors:');
      console.error(stderr);
    }
    
    // Read the combined result
    const combinedResultPath = path.join(outputDir, 'combined_result.json');
    if (fs.existsSync(combinedResultPath)) {
      const combinedResult = JSON.parse(await fs.promises.readFile(combinedResultPath, 'utf-8'));
      return combinedResult;
    } else {
      console.error('Combined result file not found');
      return null;
    }
  } catch (error) {
    console.error('Error processing PDF with Python:', error.message);
    return null;
  }
}

// Analyze the extracted data with Google AI
async function analyzeExtractedData(extractedData) {
  try {
    console.log('Analyzing extracted data with Google AI...');
    
    // Create a prompt for the AI
    const prompt = `
You are a financial document analysis expert. I have extracted text and tables from a financial document. 
Please analyze this data and extract all relevant financial information, including:

1. All ISINs (International Securities Identification Numbers) and their associated securities
2. All securities names, quantities, prices, and values
3. Asset allocation information
4. Portfolio total value and currency
5. Any other relevant financial information

Here is the extracted data:

OCR TEXT (first 2000 characters):
${extractedData.ocr_text.substring(0, 2000)}...

TABLES (if available):
${JSON.stringify(extractedData.tables, null, 2)}

Please format your response as a structured JSON object with the following fields:
- portfolio: Object containing total_value, currency, securities array, and asset_allocation object
- securities: Array of objects, each with isin, name, quantity, price, value, and currency
- metrics: Object containing total_securities, total_asset_classes, and other relevant metrics

Be as comprehensive as possible and extract ALL financial information from the document.
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
          maxOutputTokens: 2000
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
    console.error('Error analyzing extracted data with Google AI:', error);
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Data:', error.response.data);
    }
    return null;
  }
}

async function testComprehensivePDFProcessing() {
  try {
    console.log('Starting comprehensive PDF processing test...');
    
    // Check if Python is available
    const pythonAvailable = await checkPython();
    if (!pythonAvailable) {
      console.error('Python is required for this test');
      return null;
    }
    
    // Check if required Python packages are installed
    await checkPythonPackages();
    
    // Path to the PDF file
    const pdfPath = path.join(__dirname, 'messos.pdf');
    
    // Process the PDF with Python
    const extractedData = await processPDFWithPython(pdfPath);
    if (!extractedData) {
      console.error('Failed to process PDF');
      return null;
    }
    
    console.log('Extracted OCR text (first 500 characters):');
    console.log(extractedData.ocr_text.substring(0, 500) + '...');
    
    console.log('Extracted tables count:', extractedData.tables.length);
    if (extractedData.tables.length > 0) {
      console.log('First table headers:', extractedData.tables[0].headers);
    }
    
    // Analyze the extracted data with Google AI
    const analysis = await analyzeExtractedData(extractedData);
    if (!analysis) {
      console.error('Failed to analyze extracted data');
      return null;
    }
    
    console.log('Analysis result:');
    console.log(analysis);
    
    return { extractedData, analysis };
  } catch (error) {
    console.error('Error in comprehensive PDF processing test:', error);
    return null;
  }
}

// Run the test
testComprehensivePDFProcessing();
