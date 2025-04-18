/**
 * Node.js wrapper for the RAG Multimodal Financial Document Processor.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class RagMultimodalProcessor {
  /**
   * Initialize the processor.
   * 
   * @param {Object} options - Options
   * @param {string} options.apiKey - API key for AI services
   * @param {string[]} options.languages - Languages for OCR
   * @param {boolean} options.verbose - Enable verbose logging
   */
  constructor(options = {}) {
    this.apiKey = options.apiKey;
    this.languages = options.languages || ['eng', 'heb'];
    this.verbose = options.verbose || false;
  }

  /**
   * Process a financial document.
   * 
   * @param {string} pdfPath - Path to the PDF file
   * @param {string} outputDir - Directory to save output files
   * @returns {Promise<Object>} - Processed financial data
   */
  async process(pdfPath, outputDir) {
    return new Promise((resolve, reject) => {
      // Check if the PDF file exists
      if (!fs.existsSync(pdfPath)) {
        return reject(new Error(`PDF file not found: ${pdfPath}`));
      }

      // Create output directory
      if (outputDir) {
        fs.mkdirSync(outputDir, { recursive: true });
      }

      // Prepare command arguments
      const args = [
        'process_document.py',
        pdfPath
      ];

      if (outputDir) {
        args.push('--output-dir', outputDir);
      }

      if (this.languages && this.languages.length > 0) {
        args.push('--languages', this.languages.join(','));
      }

      if (this.apiKey) {
        args.push('--api-key', this.apiKey);
      }

      if (this.verbose) {
        args.push('--verbose');
      }

      // Set environment variables
      const env = { ...process.env };
      if (this.apiKey) {
        env.OPENAI_API_KEY = this.apiKey;
      }

      // Spawn Python process
      const pythonProcess = spawn('python', args, { env });

      // Collect stdout
      let output = '';
      pythonProcess.stdout.on('data', (data) => {
        const dataStr = data.toString();
        output += dataStr;
        
        // Log progress updates
        const progressMatch = dataStr.match(/Progress: (\d+)%/);
        if (progressMatch && progressMatch[1]) {
          const progress = parseInt(progressMatch[1]) / 100;
          this.onProgress && this.onProgress(progress);
        }
        
        // Log verbose output
        if (this.verbose) {
          console.log(dataStr);
        }
      });

      // Collect stderr
      let errorOutput = '';
      pythonProcess.stderr.on('data', (data) => {
        const dataStr = data.toString();
        errorOutput += dataStr;
        
        // Log errors
        console.error(dataStr);
      });

      // Handle process completion
      pythonProcess.on('close', (code) => {
        if (code === 0) {
          // Process completed successfully
          try {
            // Read result file
            const resultPath = path.join(outputDir || path.join(path.dirname(pdfPath), 'output'), 'final', `${path.basename(pdfPath, '.pdf')}_processed.json`);
            
            if (fs.existsSync(resultPath)) {
              const resultData = JSON.parse(fs.readFileSync(resultPath, 'utf8'));
              resolve(resultData);
            } else {
              // Result file not found
              reject(new Error('Result file not found'));
            }
          } catch (error) {
            // Error reading result file
            reject(error);
          }
        } else {
          // Process failed
          reject(new Error(`Processing failed: ${errorOutput || `Process exited with code ${code}`}`));
        }
      });
    });
  }

  /**
   * Set progress callback.
   * 
   * @param {Function} callback - Progress callback
   */
  setProgressCallback(callback) {
    this.onProgress = callback;
  }
}

module.exports = RagMultimodalProcessor;
