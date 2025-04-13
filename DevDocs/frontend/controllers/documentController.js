import documentRepository from '../repositories/documentRepository';

class DocumentController {
  /**
   * Get all documents
   */
  async getAllDocuments() {
    try {
      return await documentRepository.getAllDocuments();
    } catch (error) {
      console.error('Error in DocumentController.getAllDocuments:', error);
      throw error;
    }
  }

  /**
   * Get a document by ID
   */
  async getDocumentById(id) {
    try {
      return await documentRepository.getDocumentById(id);
    } catch (error) {
      console.error(`Error in DocumentController.getDocumentById(${id}):`, error);
      throw error;
    }
  }

  /**
   * Upload a document
   */
  async uploadDocument(file, options) {
    try {
      // Validate file
      this.validateFile(file);
      
      // Process options
      const processedOptions = this.processUploadOptions(file, options);
      
      // Upload document
      return await documentRepository.uploadDocument(file, processedOptions);
    } catch (error) {
      console.error('Error in DocumentController.uploadDocument:', error);
      throw error;
    }
  }

  /**
   * Delete a document
   */
  async deleteDocument(id) {
    try {
      return await documentRepository.deleteDocument(id);
    } catch (error) {
      console.error(`Error in DocumentController.deleteDocument(${id}):`, error);
      throw error;
    }
  }

  /**
   * Validate a file before upload
   */
  validateFile(file) {
    // Check file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      throw new Error(`File size exceeds the maximum allowed size of 10MB`);
    }
    
    // Check file type
    const fileName = file.name.toLowerCase();
    const allowedExtensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv', '.txt'];
    const hasAllowedExtension = allowedExtensions.some(ext => fileName.endsWith(ext));
    
    if (!hasAllowedExtension) {
      throw new Error(`File type not allowed. Allowed types: PDF, DOC, DOCX, XLS, XLSX, CSV, TXT`);
    }
  }

  /**
   * Process upload options based on file type
   */
  processUploadOptions(file, options = {}) {
    const fileName = file.name.toLowerCase();
    const fileExt = fileName.split('.').pop() || '';
    
    // Create a new options object to avoid modifying the original
    const processedOptions = {
      ...options,
      processingOptions: { ...options?.processingOptions }
    };
    
    // Set default title if not provided
    if (!processedOptions.title) {
      processedOptions.title = fileName.replace(`.${fileExt}`, '');
    }
    
    // Set default processing options based on file type
    if (['xlsx', 'xls', 'csv'].includes(fileExt)) {
      // Excel/CSV defaults
      processedOptions.processingOptions = {
        ...processedOptions.processingOptions,
        extractTables: processedOptions.processingOptions?.extractTables ?? true,
        detectHeaders: processedOptions.processingOptions?.detectHeaders ?? true,
        sheetNames: processedOptions.processingOptions?.sheetNames ?? 'all',
        convertFormulas: processedOptions.processingOptions?.convertFormulas ?? true
      };
    } else if (fileExt === 'pdf') {
      // PDF defaults
      processedOptions.processingOptions = {
        ...processedOptions.processingOptions,
        ocrEnabled: processedOptions.processingOptions?.ocrEnabled ?? true,
        extractTables: processedOptions.processingOptions?.extractTables ?? true,
        extractText: processedOptions.processingOptions?.extractText ?? true,
        extractMetadata: processedOptions.processingOptions?.extractMetadata ?? true
      };
    }
    
    return processedOptions;
  }
}

export default new DocumentController();
