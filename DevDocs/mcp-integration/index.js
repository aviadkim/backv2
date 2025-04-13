// MCP Integration Module for DevDocs
const axios = require('axios');

// MCP server URL
const MCP_SERVER_URL = process.env.MCP_SERVER_URL || 'http://localhost:8080/mcp';

/**
 * DevDocs MCP Integration
 * This module provides integration between DevDocs and the MCP server
 */
class DevDocsMcpIntegration {
  /**
   * Initialize the integration
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    this.options = options;
    this.mcpServerUrl = options.mcpServerUrl || MCP_SERVER_URL;
    console.log(`DevDocs MCP Integration initialized with server: ${this.mcpServerUrl}`);
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
}

module.exports = DevDocsMcpIntegration;
