/**
 * Document type definition
 * @typedef {Object} Document
 * @property {string} id - Document ID
 * @property {string} title - Document title
 * @property {string} filePath - Path to the file in storage
 * @property {string} fileName - Original file name
 * @property {string} fileType - File type (e.g., PDF, DOCX)
 * @property {number} fileSize - File size in bytes
 * @property {string} [content] - Document content (if extracted)
 * @property {Object} [metadata] - Additional metadata
 * @property {string[]} [tags] - Document tags
 * @property {string} [organizationId] - Organization ID
 * @property {string} [createdBy] - User ID who created the document
 * @property {string} createdAt - Creation timestamp
 * @property {string} updatedAt - Last update timestamp
 */

/**
 * Document upload options
 * @typedef {Object} DocumentUploadOptions
 * @property {string} [title] - Document title
 * @property {string} [description] - Document description
 * @property {string[]} [tags] - Document tags
 * @property {Object} [processingOptions] - Processing options
 * @property {boolean} [processingOptions.extractText] - Whether to extract text
 * @property {boolean} [processingOptions.extractTables] - Whether to extract tables
 * @property {boolean} [processingOptions.ocrEnabled] - Whether to use OCR
 * @property {boolean} [processingOptions.detectHeaders] - Whether to detect headers
 * @property {string} [processingOptions.sheetNames] - Sheet names to process
 * @property {boolean} [processingOptions.convertFormulas] - Whether to convert formulas
 * @property {boolean} [processingOptions.extractMetadata] - Whether to extract metadata
 */

// Export the types for JSDoc
export {};
