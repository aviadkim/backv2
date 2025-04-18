/**
 * Node.js wrapper for the RAG Multimodal Financial Document Processor.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

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

      // Create a Python script to run the processor
      const scriptPath = this._createTempScript();

      // Prepare command arguments
      const args = [
        scriptPath,
        pdfPath,
        '--output-dir', outputDir || path.join(path.dirname(pdfPath), 'output')
      ];

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
        // Clean up temporary script
        this._cleanupTempScript(scriptPath);

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

  /**
   * Create a temporary Python script to run the processor.
   *
   * @returns {string} - Path to the temporary script
   */
  _createTempScript() {
    const scriptContent = `
import os
import sys
import argparse
import json
import logging
from typing import Dict, Any

def main():
    """
    Main function to run the script from the command line.
    """
    parser = argparse.ArgumentParser(description='Process a financial document')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('--output-dir', help='Directory to save output files')
    parser.add_argument('--languages', help='Languages for OCR (comma-separated)', default='eng,heb')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Parse languages
    languages = args.languages.split(',')

    # Import the document processor
    try:
        # Add the parent directory to the Python path
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        from enhanced_processing import DocumentProcessor, get_config

        # Create custom configuration
        config = {
            "ocr": {
                "languages": languages
            }
        }

        # Process document
        processor = DocumentProcessor(config)
        result = processor.process(args.pdf_path, args.output_dir)

        # Print summary
        print("\nProcessing Summary:")
        print(f"Document: {result['document_info']['document_name']}")
        print(f"Total Value: {result['portfolio']['total_value']} {result['portfolio']['currency']}")
        print(f"Securities: {result['metrics']['total_securities']}")
        print(f"Asset Classes: {result['metrics']['total_asset_classes']}")

        # Print accuracy
        if "accuracy" in result:
            accuracy = result["accuracy"]
            print("\nAccuracy Metrics:")
            for key, value in accuracy.items():
                print(f"{key}: {value * 100:.2f}%")

        print(f"\nProcessing Time: {result['document_info']['processing_time']:.2f} seconds")
        print(f"Output saved to: {args.output_dir or os.path.join(os.path.dirname(args.pdf_path), 'output')}")

        sys.exit(0)
    except Exception as e:
        print(f"Error processing document: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
    `;

    // Create a temporary file
    const tempDir = path.join(os.tmpdir(), 'rag_processor');
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }

    const scriptPath = path.join(tempDir, `run_processor_${Date.now()}.py`);
    fs.writeFileSync(scriptPath, scriptContent);

    return scriptPath;
  }

  /**
   * Clean up temporary script.
   *
   * @param {string} scriptPath - Path to the temporary script
   */
  _cleanupTempScript(scriptPath) {
    try {
      if (fs.existsSync(scriptPath)) {
        fs.unlinkSync(scriptPath);
      }
    } catch (error) {
      console.error(`Error cleaning up temporary script: ${error.message}`);
    }
  }
}

module.exports = RagMultimodalProcessor;
