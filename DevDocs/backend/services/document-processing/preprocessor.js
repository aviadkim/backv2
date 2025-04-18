/**
 * Document Preprocessor
 * 
 * Handles the initial processing of documents:
 * - PDF text extraction
 * - OCR for images and scanned documents
 * - Language detection
 * - Document structure analysis
 */

const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);
const pdfParse = require('pdf-parse');
const { createWorker } = require('tesseract.js');
const logger = require('../../utils/logger');

/**
 * Preprocess a document to extract text and prepare for further analysis
 * @param {Object} options - Preprocessing options
 * @param {string} options.filePath - Path to the document file
 * @param {string} options.workDir - Working directory for temporary files
 * @param {string} options.language - Primary language of the document
 * @param {string} options.documentType - Type of document
 * @returns {Promise<Object>} - Preprocessing results
 */
async function preprocessDocument(options) {
  const { filePath, workDir, language = 'eng', documentType } = options;
  
  // Get file extension
  const fileExt = path.extname(filePath).toLowerCase();
  
  // Create result object
  const result = {
    extractedText: '',
    pageCount: 0,
    language: language,
    documentType: documentType,
    metadata: {},
    pages: []
  };
  
  try {
    // Process based on file type
    if (fileExt === '.pdf') {
      return await processPdf(filePath, workDir, language, result);
    } else if (['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'].includes(fileExt)) {
      return await processImage(filePath, workDir, language, result);
    } else if (['.xlsx', '.xls', '.csv'].includes(fileExt)) {
      return await processSpreadsheet(filePath, workDir, result);
    } else {
      throw new Error(`Unsupported file type: ${fileExt}`);
    }
  } catch (error) {
    logger.error(`Error preprocessing document: ${error.message}`, error);
    throw error;
  }
}

/**
 * Process a PDF document
 * @param {string} filePath - Path to the PDF file
 * @param {string} workDir - Working directory
 * @param {string} language - Document language
 * @param {Object} result - Result object to populate
 * @returns {Promise<Object>} - Processing results
 */
async function processPdf(filePath, workDir, language, result) {
  logger.info(`Processing PDF: ${filePath}`);
  
  // First try to extract text directly from the PDF
  try {
    const dataBuffer = fs.readFileSync(filePath);
    const pdfData = await pdfParse(dataBuffer);
    
    result.extractedText = pdfData.text;
    result.pageCount = pdfData.numpages;
    result.metadata = {
      ...result.metadata,
      pdfInfo: pdfData.info,
      pdfVersion: pdfData.version
    };
    
    // If we got very little text, the PDF might be scanned/image-based
    if (result.extractedText.length < 100 * result.pageCount) {
      logger.info(`PDF appears to be scanned/image-based. Applying OCR...`);
      return await applyOcrToPdf(filePath, workDir, language, result);
    }
    
    // Extract text from each page separately for better structure preservation
    for (let i = 1; i <= result.pageCount; i++) {
      const pageDataBuffer = fs.readFileSync(filePath);
      const pageOptions = {
        pagerender: render_page,
        max: i,
        min: i
      };
      
      const pageData = await pdfParse(pageDataBuffer, pageOptions);
      result.pages.push({
        pageNumber: i,
        text: pageData.text,
        dimensions: pageData.dimensions || null
      });
    }
    
    return result;
  } catch (error) {
    logger.error(`Error extracting text from PDF: ${error.message}`);
    // If direct extraction fails, fall back to OCR
    return await applyOcrToPdf(filePath, workDir, language, result);
  }
}

/**
 * Apply OCR to a PDF document
 * @param {string} filePath - Path to the PDF file
 * @param {string} workDir - Working directory
 * @param {string} language - Document language
 * @param {Object} result - Result object to populate
 * @returns {Promise<Object>} - Processing results
 */
async function applyOcrToPdf(filePath, workDir, language, result) {
  logger.info(`Applying OCR to PDF: ${filePath}`);
  
  // Convert PDF to images using poppler
  const imagesDir = path.join(workDir, 'images');
  fs.mkdirSync(imagesDir, { recursive: true });
  
  try {
    // Use pdftoppm to convert PDF pages to images
    const pdfFilename = path.basename(filePath, '.pdf');
    await execPromise(`pdftoppm -png -r 300 "${filePath}" "${path.join(imagesDir, pdfFilename)}"`);
    
    // Get all generated images
    const imageFiles = fs.readdirSync(imagesDir)
      .filter(file => file.endsWith('.png'))
      .sort((a, b) => {
        // Sort numerically by page number
        const numA = parseInt(a.match(/-(\d+)\.png$/)[1]);
        const numB = parseInt(b.match(/-(\d+)\.png$/)[1]);
        return numA - numB;
      });
    
    result.pageCount = imageFiles.length;
    result.extractedText = '';
    
    // Process each image with OCR
    const worker = await createWorker(language);
    
    for (let i = 0; i < imageFiles.length; i++) {
      const imagePath = path.join(imagesDir, imageFiles[i]);
      const { data } = await worker.recognize(imagePath);
      
      result.extractedText += data.text + '\n\n';
      result.pages.push({
        pageNumber: i + 1,
        text: data.text,
        dimensions: { width: data.width, height: data.height }
      });
    }
    
    await worker.terminate();
    return result;
  } catch (error) {
    logger.error(`Error applying OCR to PDF: ${error.message}`);
    throw error;
  }
}

/**
 * Process an image document
 * @param {string} filePath - Path to the image file
 * @param {string} workDir - Working directory
 * @param {string} language - Document language
 * @param {Object} result - Result object to populate
 * @returns {Promise<Object>} - Processing results
 */
async function processImage(filePath, workDir, language, result) {
  logger.info(`Processing image: ${filePath}`);
  
  try {
    // Apply OCR to the image
    const worker = await createWorker(language);
    const { data } = await worker.recognize(filePath);
    
    result.extractedText = data.text;
    result.pageCount = 1;
    result.pages.push({
      pageNumber: 1,
      text: data.text,
      dimensions: { width: data.width, height: data.height }
    });
    
    await worker.terminate();
    return result;
  } catch (error) {
    logger.error(`Error processing image: ${error.message}`);
    throw error;
  }
}

/**
 * Process a spreadsheet document
 * @param {string} filePath - Path to the spreadsheet file
 * @param {string} workDir - Working directory
 * @param {Object} result - Result object to populate
 * @returns {Promise<Object>} - Processing results
 */
async function processSpreadsheet(filePath, workDir, result) {
  logger.info(`Processing spreadsheet: ${filePath}`);
  
  const fileExt = path.extname(filePath).toLowerCase();
  
  try {
    let data;
    
    if (fileExt === '.csv') {
      // Process CSV file
      const csv = require('csv-parser');
      const results = [];
      
      await new Promise((resolve, reject) => {
        fs.createReadStream(filePath)
          .pipe(csv())
          .on('data', (data) => results.push(data))
          .on('end', () => resolve())
          .on('error', (error) => reject(error));
      });
      
      data = results;
    } else {
      // Process Excel file
      const XLSX = require('xlsx');
      const workbook = XLSX.readFile(filePath);
      
      data = {};
      workbook.SheetNames.forEach(sheetName => {
        data[sheetName] = XLSX.utils.sheet_to_json(workbook.Sheets[sheetName]);
      });
    }
    
    // Convert data to text representation
    let textContent = '';
    
    if (Array.isArray(data)) {
      // CSV data
      if (data.length > 0) {
        // Add headers
        textContent += Object.keys(data[0]).join('\t') + '\n';
        
        // Add rows
        data.forEach(row => {
          textContent += Object.values(row).join('\t') + '\n';
        });
      }
    } else {
      // Excel data
      Object.keys(data).forEach(sheetName => {
        textContent += `Sheet: ${sheetName}\n`;
        
        const sheet = data[sheetName];
        if (sheet.length > 0) {
          // Add headers
          textContent += Object.keys(sheet[0]).join('\t') + '\n';
          
          // Add rows
          sheet.forEach(row => {
            textContent += Object.values(row).join('\t') + '\n';
          });
        }
        
        textContent += '\n';
      });
    }
    
    result.extractedText = textContent;
    result.pageCount = 1;
    result.metadata.rawData = data;
    result.pages.push({
      pageNumber: 1,
      text: textContent
    });
    
    return result;
  } catch (error) {
    logger.error(`Error processing spreadsheet: ${error.message}`);
    throw error;
  }
}

/**
 * Custom page renderer for PDF.js
 */
function render_page(pageData) {
  // Get page dimensions
  const dimensions = {
    width: pageData.getViewport(1.0).width,
    height: pageData.getViewport(1.0).height
  };
  
  return pageData.getTextContent()
    .then(function(textContent) {
      let lastY, text = '';
      
      for (let item of textContent.items) {
        if (lastY == item.transform[5] || !lastY) {
          text += item.str;
        } else {
          text += '\n' + item.str;
        }
        lastY = item.transform[5];
      }
      
      return { text, dimensions };
    });
}

module.exports = {
  preprocessDocument
};
