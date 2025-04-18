/**
 * Hebrew OCR Agent
 *
 * Performs OCR on Hebrew documents with advanced features.
 */

// Import libraries conditionally to avoid errors when testing
let createWorker;
try {
  const tesseract = require('tesseract.js');
  createWorker = tesseract.createWorker;
} catch (error) {
  // Mock createWorker for testing
  createWorker = async () => ({
    loadLanguage: async () => {},
    initialize: async () => {},
    setParameters: async () => {},
    detect: async () => ({ data: { orientation: 'normal', script: 'Hebrew', confidence: 90 } }),
    recognize: async (buffer) => ({
      data: {
        text: buffer.toString('utf8'),
        confidence: 85,
        hocr: '',
        tsv: ''
      }
    }),
    terminate: async () => {}
  });
}

const fs = require('fs').promises;
const path = require('path');
const logger = require('../../utils/logger');

// Import axios conditionally
let axios;
try {
  axios = require('axios');
} catch (error) {
  // Mock axios for testing
  axios = {
    post: async () => ({
      data: {
        choices: [{
          message: {
            content: 'Enhanced text for testing'
          }
        }]
      }
    })
  };
}

class HebrewOCRAgent {
  constructor(options = {}) {
    this.apiKey = options.apiKey || process.env.OPENROUTER_API_KEY;
    this.model = options.model || 'anthropic/claude-3-opus:beta';
    this.apiUrl = options.apiUrl || 'https://openrouter.ai/api/v1/chat/completions';
    this.logger = logger;
    this.tesseractLang = options.tesseractLang || 'heb+eng';
    this.enhanceText = options.enhanceText !== false;
    this.detectOrientation = options.detectOrientation !== false;
    this.detectHandwriting = options.detectHandwriting !== false;
    this.outputFormat = options.outputFormat || 'text';
    this.confidenceThreshold = options.confidenceThreshold || 70;
    this.tempDir = options.tempDir || path.join(process.cwd(), 'temp');
  }

  /**
   * Process a document with OCR
   * @param {Buffer|string} document - Document buffer or path
   * @param {Object} options - Processing options
   * @returns {Promise<Object>} - OCR results
   */
  async processDocument(document, options = {}) {
    this.logger.info('Processing document with Hebrew OCR');

    try {
      // Create temp directory if it doesn't exist
      await this._ensureTempDir();

      // Get document buffer
      const documentBuffer = typeof document === 'string'
        ? await fs.readFile(document)
        : document;

      // Detect orientation if enabled
      let processedBuffer = documentBuffer;
      let orientation = null;

      if (this.detectOrientation) {
        const orientationResult = await this._detectOrientation(documentBuffer);
        orientation = orientationResult.orientation;

        if (orientation !== 'normal') {
          processedBuffer = await this._rotateImage(documentBuffer, orientation);
        }
      }

      // Detect if document contains handwriting
      let containsHandwriting = false;

      if (this.detectHandwriting) {
        containsHandwriting = await this._detectHandwriting(processedBuffer);
      }

      // Perform OCR
      const ocrResult = await this._performOCR(processedBuffer, {
        ...options,
        handwriting: containsHandwriting
      });

      // Enhance text if enabled
      let enhancedText = null;

      if (this.enhanceText && ocrResult.text && this.apiKey) {
        enhancedText = await this._enhanceText(ocrResult.text);
      }

      // Format output
      const result = {
        text: enhancedText || ocrResult.text,
        original_text: ocrResult.text,
        confidence: ocrResult.confidence,
        orientation,
        contains_handwriting: containsHandwriting,
        language: 'heb+eng',
        words: ocrResult.words,
        blocks: ocrResult.blocks
      };

      // Add hOCR or other formats if requested
      if (options.includeHOCR && ocrResult.hocr) {
        result.hocr = ocrResult.hocr;
      }

      return result;
    } catch (error) {
      this.logger.error(`Error processing document with Hebrew OCR: ${error.message}`, error);
      throw error;
    }
  }

  /**
   * Ensure temp directory exists
   * @private
   */
  async _ensureTempDir() {
    try {
      await fs.mkdir(this.tempDir, { recursive: true });
    } catch (error) {
      this.logger.error(`Error creating temp directory: ${error.message}`, error);
      throw error;
    }
  }

  /**
   * Detect document orientation
   * @param {Buffer} documentBuffer - Document buffer
   * @returns {Promise<Object>} - Orientation result
   * @private
   */
  async _detectOrientation(documentBuffer) {
    this.logger.info('Detecting document orientation');

    try {
      // Create a worker for orientation detection
      const worker = await createWorker();

      // Initialize worker with OSD (orientation and script detection)
      await worker.loadLanguage('osd');
      await worker.initialize('osd');

      // Detect orientation
      const { data } = await worker.detect(documentBuffer);

      // Terminate worker
      await worker.terminate();

      return {
        orientation: data.orientation,
        script: data.script,
        confidence: data.confidence
      };
    } catch (error) {
      this.logger.error(`Error detecting orientation: ${error.message}`, error);
      return { orientation: 'normal', script: 'Hebrew', confidence: 0 };
    }
  }

  /**
   * Rotate image based on orientation
   * @param {Buffer} documentBuffer - Document buffer
   * @param {string} orientation - Detected orientation
   * @returns {Promise<Buffer>} - Rotated image buffer
   * @private
   */
  async _rotateImage(documentBuffer, orientation) {
    this.logger.info(`Rotating image to orientation: ${orientation}`);

    try {
      // In a real implementation, we would use a library like sharp or jimp
      // to rotate the image based on the orientation
      // For now, we'll just return the original buffer
      return documentBuffer;
    } catch (error) {
      this.logger.error(`Error rotating image: ${error.message}`, error);
      return documentBuffer;
    }
  }

  /**
   * Detect if document contains handwriting
   * @param {Buffer} documentBuffer - Document buffer
   * @returns {Promise<boolean>} - Whether document contains handwriting
   * @private
   */
  async _detectHandwriting(documentBuffer) {
    this.logger.info('Detecting handwriting in document');

    try {
      // In a real implementation, we would use a machine learning model
      // to detect if the document contains handwriting
      // For now, we'll just return false
      return false;
    } catch (error) {
      this.logger.error(`Error detecting handwriting: ${error.message}`, error);
      return false;
    }
  }

  /**
   * Perform OCR on document
   * @param {Buffer} documentBuffer - Document buffer
   * @param {Object} options - OCR options
   * @returns {Promise<Object>} - OCR result
   * @private
   */
  async _performOCR(documentBuffer, options = {}) {
    this.logger.info('Performing OCR on document');

    try {
      // Create a worker for OCR
      const worker = await createWorker();

      // Initialize worker with Hebrew and English languages
      await worker.loadLanguage(this.tesseractLang);
      await worker.initialize(this.tesseractLang);

      // Set additional parameters for handwriting if detected
      if (options.handwriting) {
        await worker.setParameters({
          tessedit_ocr_engine_mode: 2, // Use LSTM only
          tessjs_create_hocr: options.includeHOCR === true,
          tessjs_create_tsv: true
        });
      } else {
        await worker.setParameters({
          tessjs_create_hocr: options.includeHOCR === true,
          tessjs_create_tsv: true
        });
      }

      // Perform OCR
      const { data } = await worker.recognize(documentBuffer);

      // Extract words and blocks from TSV
      const words = this._extractWordsFromTSV(data.tsv);
      const blocks = this._extractBlocksFromText(data.text);

      // Terminate worker
      await worker.terminate();

      return {
        text: data.text,
        confidence: data.confidence,
        hocr: data.hocr,
        words,
        blocks
      };
    } catch (error) {
      this.logger.error(`Error performing OCR: ${error.message}`, error);
      return { text: '', confidence: 0, words: [], blocks: [] };
    }
  }

  /**
   * Extract words from TSV
   * @param {string} tsv - TSV data
   * @returns {Array} - Words with position and confidence
   * @private
   */
  _extractWordsFromTSV(tsv) {
    if (!tsv) return [];

    try {
      const lines = tsv.split('\n');
      const words = [];

      // Skip header line
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;

        const parts = line.split('\t');
        if (parts.length < 12) continue;

        // Extract word data
        const word = {
          text: parts[11],
          confidence: parseFloat(parts[10]),
          bbox: {
            x: parseInt(parts[6]),
            y: parseInt(parts[7]),
            width: parseInt(parts[8]) - parseInt(parts[6]),
            height: parseInt(parts[9]) - parseInt(parts[7])
          }
        };

        // Only include words with confidence above threshold
        if (word.confidence >= this.confidenceThreshold) {
          words.push(word);
        }
      }

      return words;
    } catch (error) {
      this.logger.error(`Error extracting words from TSV: ${error.message}`, error);
      return [];
    }
  }

  /**
   * Extract text blocks from OCR text
   * @param {string} text - OCR text
   * @returns {Array} - Text blocks
   * @private
   */
  _extractBlocksFromText(text) {
    if (!text) return [];

    try {
      // Split text into paragraphs
      const paragraphs = text.split(/\n\s*\n/);

      // Create blocks
      return paragraphs.map((paragraph, index) => ({
        id: `block_${index + 1}`,
        text: paragraph.trim(),
        type: this._detectBlockType(paragraph)
      })).filter(block => block.text);
    } catch (error) {
      this.logger.error(`Error extracting blocks from text: ${error.message}`, error);
      return [];
    }
  }

  /**
   * Detect block type
   * @param {string} text - Block text
   * @returns {string} - Block type
   * @private
   */
  _detectBlockType(text) {
    if (!text) return 'unknown';

    // Check if block is a table
    if (text.includes('|') || text.includes('\t')) {
      return 'table';
    }

    // Check if block is a header
    if (text.length < 100 && text.toUpperCase() === text) {
      return 'header';
    }

    // Check if block is a list
    if (text.split('\n').some(line => line.match(/^[\s]*[•\-\*\d]+[\.\)]\s/))) {
      return 'list';
    }

    // Default to paragraph
    return 'paragraph';
  }

  /**
   * Enhance OCR text using AI
   * @param {string} text - OCR text
   * @returns {Promise<string>} - Enhanced text
   * @private
   */
  async _enhanceText(text) {
    this.logger.info('Enhancing OCR text with AI');

    if (!this.apiKey) {
      this.logger.warn('API key not configured. Skipping text enhancement.');
      return text;
    }

    try {
      // Create a prompt for the AI
      const prompt = `
I need you to correct and enhance the following text that was extracted from a document using OCR. The text may contain errors, especially with Hebrew characters. Please fix any obvious OCR errors, correct the formatting, and ensure the text is readable.

OCR TEXT:
${text}

Please return only the corrected text without any explanations or additional comments.
`;

      // Call the OpenRouter API
      const response = await axios.post(
        this.apiUrl,
        {
          model: this.model,
          messages: [
            { role: 'system', content: 'You are a Hebrew and English OCR correction assistant. You correct OCR errors in text, especially for Hebrew text.' },
            { role: 'user', content: prompt }
          ]
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      // Extract the enhanced text
      const enhancedText = response.data.choices[0].message.content;

      return enhancedText;
    } catch (error) {
      this.logger.error(`Error enhancing text: ${error.message}`, error);
      return text;
    }
  }
}

module.exports = HebrewOCRAgent;
