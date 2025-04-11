import fs from 'fs';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import PdfProcessor from './pdf_processor';

class DocumentService {
  constructor() {
    this.pdfProcessor = new PdfProcessor();
    this.documentsDir = path.join(process.cwd(), 'data', 'documents');
    
    // Ensure documents directory exists
    if (!fs.existsSync(this.documentsDir)) {
      fs.mkdirSync(this.documentsDir, { recursive: true });
    }
  }
  
  /**
   * Save a document
   * @param {string} filename - Original filename
   * @param {Buffer} fileData - File data
   * @param {object} metadata - Additional metadata
   * @returns {Promise<object>} - Saved document info
   */
  async saveDocument(filename, fileData, metadata = {}) {
    try {
      // Generate a unique ID for the document
      const documentId = uuidv4();
      
      // Create document directory
      const documentDir = path.join(this.documentsDir, documentId);
      fs.mkdirSync(documentDir, { recursive: true });
      
      // Save the file
      const filePath = path.join(documentDir, filename);
      fs.writeFileSync(filePath, fileData);
      
      // Save metadata
      const documentInfo = {
        id: documentId,
        filename,
        originalName: filename,
        path: filePath,
        size: fileData.length,
        mimeType: metadata.mimeType || this.getMimeType(filename),
        createdAt: new Date().toISOString(),
        ...metadata
      };
      
      const metadataPath = path.join(documentDir, 'metadata.json');
      fs.writeFileSync(metadataPath, JSON.stringify(documentInfo, null, 2));
      
      return documentInfo;
    } catch (error) {
      console.error('Error saving document:', error);
      throw error;
    }
  }
  
  /**
   * Get document by ID
   * @param {string} documentId - Document ID
   * @returns {Promise<object>} - Document info
   */
  async getDocument(documentId) {
    try {
      const metadataPath = path.join(this.documentsDir, documentId, 'metadata.json');
      
      if (!fs.existsSync(metadataPath)) {
        throw new Error(`Document not found: ${documentId}`);
      }
      
      const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
      return metadata;
    } catch (error) {
      console.error('Error getting document:', error);
      throw error;
    }
  }
  
  /**
   * Process a document
   * @param {string} documentId - Document ID
   * @returns {Promise<object>} - Processed document data
   */
  async processDocument(documentId) {
    try {
      // Get document info
      const document = await this.getDocument(documentId);
      
      // Check if document exists
      if (!document) {
        throw new Error(`Document not found: ${documentId}`);
      }
      
      // Check if document is already processed
      const processedPath = path.join(this.documentsDir, documentId, 'processed.json');
      if (fs.existsSync(processedPath)) {
        return JSON.parse(fs.readFileSync(processedPath, 'utf8'));
      }
      
      // Process document based on mime type
      let processedData;
      if (document.mimeType === 'application/pdf') {
        // Read the PDF file
        const fileData = fs.readFileSync(document.path);
        
        // Extract text from PDF
        const { text, pageTexts, metadata } = await this.pdfProcessor.extractText(fileData);
        
        // Save extracted text
        const textPath = path.join(this.documentsDir, documentId, 'text.txt');
        fs.writeFileSync(textPath, text);
        
        // Save page texts
        const pageTextsPath = path.join(this.documentsDir, documentId, 'page_texts.json');
        fs.writeFileSync(pageTextsPath, JSON.stringify(pageTexts, null, 2));
        
        // Analyze the text
        processedData = await this.pdfProcessor.analyzeText(text);
        
        // Add document metadata
        processedData.metadata = {
          ...metadata,
          documentId,
          filename: document.filename,
          originalName: document.originalName,
          mimeType: document.mimeType,
          size: document.size,
          createdAt: document.createdAt,
          processedAt: new Date().toISOString()
        };
      } else {
        throw new Error(`Unsupported document type: ${document.mimeType}`);
      }
      
      // Save processed data
      fs.writeFileSync(processedPath, JSON.stringify(processedData, null, 2));
      
      return processedData;
    } catch (error) {
      console.error('Error processing document:', error);
      throw error;
    }
  }
  
  /**
   * Answer a question about a document
   * @param {string} documentId - Document ID
   * @param {string} question - Question to answer
   * @returns {Promise<string>} - Answer to the question
   */
  async answerQuestion(documentId, question) {
    try {
      // Get document info
      const document = await this.getDocument(documentId);
      
      // Check if document exists
      if (!document) {
        throw new Error(`Document not found: ${documentId}`);
      }
      
      // Get document text
      const textPath = path.join(this.documentsDir, documentId, 'text.txt');
      if (!fs.existsSync(textPath)) {
        // Process document if not already processed
        await this.processDocument(documentId);
      }
      
      const text = fs.readFileSync(textPath, 'utf8');
      
      // Answer the question
      const answer = await this.pdfProcessor.answerQuestion(text, question);
      
      return answer;
    } catch (error) {
      console.error('Error answering question:', error);
      throw error;
    }
  }
  
  /**
   * Generate a custom table based on a prompt
   * @param {string} documentId - Document ID
   * @param {string} prompt - Prompt for table generation
   * @returns {Promise<Array<object>>} - Generated table data
   */
  async generateTable(documentId, prompt) {
    try {
      // Get document info
      const document = await this.getDocument(documentId);
      
      // Check if document exists
      if (!document) {
        throw new Error(`Document not found: ${documentId}`);
      }
      
      // Get document text
      const textPath = path.join(this.documentsDir, documentId, 'text.txt');
      if (!fs.existsSync(textPath)) {
        // Process document if not already processed
        await this.processDocument(documentId);
      }
      
      const text = fs.readFileSync(textPath, 'utf8');
      
      // Generate the table
      const tableData = await this.pdfProcessor.generateTable(text, prompt);
      
      return tableData;
    } catch (error) {
      console.error('Error generating table:', error);
      throw error;
    }
  }
  
  /**
   * Get MIME type from filename
   * @param {string} filename - Filename
   * @returns {string} - MIME type
   */
  getMimeType(filename) {
    const ext = path.extname(filename).toLowerCase();
    
    switch (ext) {
      case '.pdf':
        return 'application/pdf';
      case '.doc':
        return 'application/msword';
      case '.docx':
        return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
      case '.xls':
        return 'application/vnd.ms-excel';
      case '.xlsx':
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      case '.ppt':
        return 'application/vnd.ms-powerpoint';
      case '.pptx':
        return 'application/vnd.openxmlformats-officedocument.presentationml.presentation';
      case '.txt':
        return 'text/plain';
      case '.csv':
        return 'text/csv';
      case '.json':
        return 'application/json';
      case '.xml':
        return 'application/xml';
      case '.html':
        return 'text/html';
      case '.htm':
        return 'text/html';
      default:
        return 'application/octet-stream';
    }
  }
}

export default DocumentService;
