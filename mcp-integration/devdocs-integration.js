const axios = require('axios');
const fs = require('fs');
const path = require('path');

// MCP server URL
const MCP_SERVER_URL = 'http://localhost:8080/mcp';

/**
 * DevDocs Google Cloud Integration
 * This module provides integration between DevDocs and Google Cloud via MCP
 */
class DevDocsGoogleCloudIntegration {
  /**
   * Initialize the integration
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    this.options = options;
    this.mcpServerUrl = options.mcpServerUrl || MCP_SERVER_URL;
    console.log(`DevDocs Google Cloud Integration initialized with MCP server: ${this.mcpServerUrl}`);
  }

  /**
   * Make a request to the MCP server
   * @param {string} action - The action to perform
   * @param {Object} parameters - The parameters for the action
   * @returns {Promise<Object>} - The response from the MCP server
   */
  async mcpRequest(action, parameters = {}) {
    try {
      const response = await axios.post(this.mcpServerUrl, {
        action,
        parameters
      });
      return response.data;
    } catch (error) {
      console.error(`Error making MCP request for action ${action}:`, error.message);
      throw new Error(`MCP request failed: ${error.message}`);
    }
  }

  /**
   * List all storage buckets in the Google Cloud project
   * @returns {Promise<Array<string>>} - Array of bucket names
   */
  async listBuckets() {
    const response = await this.mcpRequest('listBuckets');
    return response.result;
  }

  /**
   * List files in a storage bucket
   * @param {string} bucketName - The name of the bucket
   * @returns {Promise<Array<string>>} - Array of file names
   */
  async listFiles(bucketName) {
    const response = await this.mcpRequest('listFiles', { bucketName });
    return response.result;
  }

  /**
   * Upload a file to a storage bucket
   * @param {string} bucketName - The name of the bucket
   * @param {string} fileName - The name of the file
   * @param {string|Buffer} fileContent - The content of the file
   * @returns {Promise<Object>} - The response from the MCP server
   */
  async uploadFile(bucketName, fileName, fileContent) {
    // Convert file content to base64 if it's not already
    let content = fileContent;
    if (Buffer.isBuffer(fileContent)) {
      content = fileContent.toString('base64');
    } else if (typeof fileContent === 'string' && !fileContent.match(/^[A-Za-z0-9+/=]+$/)) {
      content = Buffer.from(fileContent).toString('base64');
    }

    const response = await this.mcpRequest('uploadFile', {
      bucketName,
      fileName,
      fileContent: content
    });
    return response.result;
  }

  /**
   * Download a file from a storage bucket
   * @param {string} bucketName - The name of the bucket
   * @param {string} fileName - The name of the file
   * @returns {Promise<Buffer>} - The file content as a Buffer
   */
  async downloadFile(bucketName, fileName) {
    const response = await this.mcpRequest('downloadFile', {
      bucketName,
      fileName
    });
    return Buffer.from(response.result.content, 'base64');
  }

  /**
   * Process a document using Document AI
   * @param {string} bucketName - The name of the bucket
   * @param {string} fileName - The name of the file
   * @returns {Promise<Object>} - The processed document
   */
  async processDocument(bucketName, fileName) {
    const response = await this.mcpRequest('processDocument', {
      bucketName,
      fileName
    });
    return response.result;
  }

  /**
   * Search the web for information
   * @param {string} query - The search query
   * @returns {Promise<Array<Object>>} - Array of search results
   */
  async webSearch(query) {
    const response = await this.mcpRequest('webSearch', { query });
    return response.result;
  }

  /**
   * Fetch content from a URL
   * @param {string} url - The URL to fetch
   * @returns {Promise<Object>} - The fetched content
   */
  async webFetch(url) {
    const response = await this.mcpRequest('webFetch', { url });
    return response.result;
  }

  /**
   * Upload a document to Google Cloud and process it
   * @param {string} filePath - The path to the document
   * @returns {Promise<Object>} - The processed document
   */
  async uploadAndProcessDocument(filePath) {
    const bucketName = 'devdocs-bucket';
    const fileName = path.basename(filePath);
    
    // Read the file
    const fileContent = fs.readFileSync(filePath);
    
    // Upload the file to Google Cloud Storage
    await this.uploadFile(bucketName, fileName, fileContent);
    
    // Process the document using Document AI
    const processedDocument = await this.processDocument(bucketName, fileName);
    
    return processedDocument;
  }
}

module.exports = DevDocsGoogleCloudIntegration;
