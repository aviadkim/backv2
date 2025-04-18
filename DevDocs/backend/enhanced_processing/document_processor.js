/**
 * Document Processor Module
 *
 * This module provides a Node.js wrapper for the enhanced document processing pipeline.
 * It uses the Python implementation for the actual processing.
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const logger = require('../utils/logger');

class DocumentProcessor {
  /**
   * Initialize the DocumentProcessor.
   *
   * @param {string} apiKey - API key for AI services
   */
  constructor(apiKey) {
    this.apiKey = apiKey;
    logger.info('Initialized DocumentProcessor');
  }

  /**
   * Process a financial document.
   *
   * @param {string} pdfPath - Path to the PDF file
   * @param {string} outputDir - Directory to save output files
   * @param {string[]} languages - List of languages for OCR
   * @returns {Promise<object>} - Processed financial data
   */
  async process(pdfPath, outputDir, languages = ['eng', 'heb']) {
    return new Promise((resolve, reject) => {
      logger.info(`Processing document: ${pdfPath}`);
      logger.info(`Output directory: ${outputDir}`);

      // Create output directory
      fs.mkdirSync(outputDir, { recursive: true });

      // Path to the Python script
      const scriptPath = path.join(__dirname, 'run_processor.py');

      // Check if the script exists
      if (!fs.existsSync(scriptPath)) {
        logger.error(`Python script not found: ${scriptPath}`);
        return reject(new Error('Processing script not found'));
      }

      // Prepare command arguments
      const args = [
        scriptPath,
        pdfPath,
        outputDir,
        '--languages', languages.join(',')
      ];

      // Set API key in environment
      const env = { ...process.env };
      if (this.apiKey) {
        env.GOOGLE_API_KEY = this.apiKey;
      }

      // Spawn Python process
      const pythonProcess = spawn('python', args, { env });

      // Collect stdout
      let output = '';
      pythonProcess.stdout.on('data', (data) => {
        output += data.toString();
        logger.debug(`Python process output: ${data.toString()}`);

        // Log progress updates
        const progressMatch = data.toString().match(/Progress: (\d+)%/);
        if (progressMatch && progressMatch[1]) {
          logger.info(`Processing progress: ${progressMatch[1]}%`);
        }
      });

      // Collect stderr
      let errorOutput = '';
      pythonProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
        logger.error(`Python process error: ${data.toString()}`);
      });

      // Handle process completion
      pythonProcess.on('close', (code) => {
        if (code === 0) {
          // Process completed successfully
          try {
            // Read result file
            const resultPath = path.join(outputDir, `${path.basename(pdfPath, '.pdf')}_processed.json`);

            if (fs.existsSync(resultPath)) {
              const resultData = JSON.parse(fs.readFileSync(resultPath, 'utf8'));
              logger.info(`Processing complete, extracted ${resultData.portfolio?.securities?.length || 0} securities`);
              resolve(resultData);
            } else {
              // Result file not found, try to create a basic result
              logger.warn('Result file not found, creating basic result');

              // Create basic result
              const basicResult = this._createBasicResult(pdfPath, outputDir);
              resolve(basicResult);
            }
          } catch (error) {
            // Error reading result file
            logger.error(`Error reading result: ${error.message}`);
            reject(error);
          }
        } else {
          // Process failed
          logger.error(`Python process failed with code ${code}: ${errorOutput}`);
          reject(new Error(`Processing failed: ${errorOutput || `Process exited with code ${code}`}`));
        }
      });
    });
  }

  /**
   * Create a basic result when the Python process fails.
   *
   * @param {string} pdfPath - Path to the PDF file
   * @param {string} outputDir - Output directory
   * @returns {object} - Basic result
   * @private
   */
  _createBasicResult(pdfPath, outputDir) {
    // Try to extract text from PDF
    let text = '';
    try {
      // Use pdfjs-dist if available
      const pdfjs = require('pdfjs-dist');
      const data = fs.readFileSync(pdfPath);
      const pdf = pdfjs.getDocument(data);

      // Extract text from first page
      const page = pdf.getPage(1);
      text = page.getTextContent().then(content => {
        return content.items.map(item => item.str).join(' ');
      });
    } catch (error) {
      logger.warn(`Error extracting text from PDF: ${error.message}`);
    }

    // Create basic result
    const result = {
      portfolio: {
        total_value: 0,
        currency: 'USD',
        securities: [],
        asset_allocation: {}
      },
      metrics: {
        total_securities: 0,
        total_asset_classes: 0
      },
      document_info: {
        document_id: path.basename(pdfPath, '.pdf'),
        document_name: path.basename(pdfPath),
        document_date: new Date().toISOString().split('T')[0],
        processing_date: new Date().toISOString(),
        processing_time: 0
      }
    };

    // Save basic result
    const resultPath = path.join(outputDir, `${path.basename(pdfPath, '.pdf')}_processed.json`);
    fs.writeFileSync(resultPath, JSON.stringify(result, null, 2));

    return result;
  }
}

module.exports = DocumentProcessor;
