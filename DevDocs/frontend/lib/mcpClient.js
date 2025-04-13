import axios from 'axios';

class MCPClient {
  constructor() {
    this.apiEndpoint = process.env.NEXT_PUBLIC_MCP_API_ENDPOINT || 'https://devdocs-mcp-server-683496987674.me-west1.run.app';
  }

  async getContext(query, options = {}) {
    try {
      const response = await axios.post(`${this.apiEndpoint}/context`, {
        query,
        webSearch: options.webSearch || false,
        maxResults: options.maxResults || 5
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching context from MCP:', error);
      throw error;
    }
  }

  async generateResponse(query, context = [], options = {}) {
    try {
      const response = await axios.post(`${this.apiEndpoint}/generate`, {
        query,
        context,
        webSearch: options.webSearch || false,
        maxTokens: options.maxTokens || 1000
      });
      
      return response.data;
    } catch (error) {
      console.error('Error generating response with MCP:', error);
      throw error;
    }
  }

  async searchWeb(query, options = {}) {
    try {
      const response = await axios.post(`${this.apiEndpoint}/search`, {
        query,
        maxResults: options.maxResults || 5
      });
      
      return response.data;
    } catch (error) {
      console.error('Error searching web with MCP:', error);
      throw error;
    }
  }
}

// Create a singleton instance
const mcpClient = new MCPClient();

export default mcpClient;
