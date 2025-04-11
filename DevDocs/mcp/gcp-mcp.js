/**
 * Google Cloud MCP Integration
 * This module provides integration with Google Cloud MCP
 */

const fs = require('fs');
const path = require('path');
const axios = require('axios');

// Load configuration
const configPath = path.join(__dirname, 'gcp-mcp-config.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// MCP server URL
const MCP_SERVER_URL = config.mcpServerUrl || 'https://devdocs-mcp-server-678297464867.me-west1.run.app/mcp';

/**
 * Google Cloud MCP Provider
 * @type {Object}
 */
const gcpProvider = {
  /**
   * Make a request to the MCP server
   * @param {string} action - The action to perform
   * @param {Object} parameters - The parameters for the action
   * @returns {Promise<Object>} - The response from the MCP server
   */
  async mcpRequest(action, parameters = {}) {
    try {
      console.log(`Making MCP request to ${MCP_SERVER_URL} for action ${action}`);
      const response = await axios.post(MCP_SERVER_URL, {
        action,
        parameters
      });
      return response.data;
    } catch (error) {
      console.error(`Error making MCP request for action ${action}:`, error.message);
      throw new Error(`MCP request failed: ${error.message}`);
    }
  },

  /**
   * List all storage buckets in the Google Cloud project
   * @returns {Promise<Array<string>>} - Array of bucket names
   */
  async listBuckets() {
    const response = await this.mcpRequest('listBuckets');
    return response.result;
  },

  /**
   * List files in a storage bucket
   * @param {string} bucketName - The name of the bucket
   * @returns {Promise<Array<string>>} - Array of file names
   */
  async listFiles(bucketName) {
    const response = await this.mcpRequest('listFiles', { bucketName });
    return response.result;
  },

  /**
   * Search the web for information
   * @param {string} query - The search query
   * @returns {Promise<Array<Object>>} - Array of search results
   */
  async webSearch(query) {
    const response = await this.mcpRequest('webSearch', { query });
    return response.result;
  },

  /**
   * Fetch content from a URL
   * @param {string} url - The URL to fetch
   * @returns {Promise<Object>} - The fetched content
   */
  async webFetch(url) {
    const response = await this.mcpRequest('webFetch', { url });
    return response.result;
  }
};

module.exports = {
  gcpProvider
};
