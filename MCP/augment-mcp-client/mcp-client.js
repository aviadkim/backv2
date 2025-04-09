/**
 * MCP Client for Augment
 * 
 * This client interacts with the MCP Server to generate components.
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');

class MCPClient {
  constructor(serverUrl = 'http://localhost:3030') {
    this.serverUrl = serverUrl;
  }

  /**
   * Check if the MCP Server is running
   */
  async isServerRunning() {
    try {
      const response = await axios.get(`${this.serverUrl}/health`);
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get available projects
   */
  async getProjects() {
    try {
      const response = await axios.get(`${this.serverUrl}/projects`);
      return response.data.projects;
    } catch (error) {
      console.error('Error getting projects:', error.message);
      throw error;
    }
  }

  /**
   * Get project structure
   */
  async getProjectStructure(projectId) {
    try {
      const response = await axios.get(`${this.serverUrl}/projects/${projectId}`);
      return response.data.project;
    } catch (error) {
      console.error(`Error getting project structure for ${projectId}:`, error.message);
      throw error;
    }
  }

  /**
   * Generate a component
   */
  async generateComponent(projectId, type, name, description = '') {
    try {
      const response = await axios.post(`${this.serverUrl}/generate`, {
        projectId,
        type,
        name,
        description
      });
      
      return response.data.result;
    } catch (error) {
      console.error(`Error generating ${type} component:`, error.message);
      throw error;
    }
  }

  /**
   * Add a new project
   */
  async addProject(projectId, rootPath, structure) {
    try {
      const response = await axios.post(`${this.serverUrl}/projects`, {
        projectId,
        rootPath,
        structure
      });
      
      return response.data.project;
    } catch (error) {
      console.error(`Error adding project ${projectId}:`, error.message);
      throw error;
    }
  }
}

module.exports = MCPClient;
