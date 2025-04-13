import axios from 'axios';

class MCPClient {
  constructor() {
    this.apiEndpoint = process.env.NEXT_PUBLIC_MCP_API_ENDPOINT || 'https://devdocs-mcp-server-683496987674.me-west1.run.app';
    this.isServerAvailable = true;
  }

  async getContext(query, options = {}) {
    if (!this.isServerAvailable) {
      // Return mock data if server is not available
      return {
        success: true,
        results: [
          {
            title: 'Google Cloud Platform',
            link: 'https://cloud.google.com',
            snippet: 'Google Cloud Platform lets you build, deploy, and scale applications, websites, and services on the same infrastructure as Google.'
          },
          {
            title: 'Model Context Protocol (MCP)',
            link: 'https://github.com/eniayomi/gcp-mcp',
            snippet: 'A protocol for connecting AI models with external tools and services.'
          },
          {
            title: 'DevDocs API Documentation',
            link: 'https://devdocs.io',
            snippet: 'DevDocs combines multiple API documentations in a fast, organized, and searchable interface.'
          }
        ]
      };
    }

    try {
      const response = await axios.post(`${this.apiEndpoint}/context`, {
        query,
        webSearch: options.webSearch || false,
        maxResults: options.maxResults || 5
      });

      return response.data;
    } catch (error) {
      console.error('Error fetching context from MCP:', error);
      this.isServerAvailable = false;

      // Return mock data on error
      return {
        success: true,
        results: [
          {
            title: 'Google Cloud Platform',
            link: 'https://cloud.google.com',
            snippet: 'Google Cloud Platform lets you build, deploy, and scale applications, websites, and services on the same infrastructure as Google.'
          },
          {
            title: 'Model Context Protocol (MCP)',
            link: 'https://github.com/eniayomi/gcp-mcp',
            snippet: 'A protocol for connecting AI models with external tools and services.'
          },
          {
            title: 'DevDocs API Documentation',
            link: 'https://devdocs.io',
            snippet: 'DevDocs combines multiple API documentations in a fast, organized, and searchable interface.'
          }
        ]
      };
    }
  }

  async generateResponse(query, context = [], options = {}) {
    if (!this.isServerAvailable) {
      // Return mock data if server is not available
      return {
        success: true,
        response: {
          text: `This is a mock response to: "${query}". Based on the provided context, I can help you with your DevDocs implementation.`,
          sources: context.map(c => c.title || 'Unknown source')
        }
      };
    }

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
      this.isServerAvailable = false;

      // Return mock data on error
      return {
        success: true,
        response: {
          text: `This is a mock response to: "${query}". Based on the provided context, I can help you with your DevDocs implementation.`,
          sources: context.map(c => c.title || 'Unknown source')
        }
      };
    }
  }

  async searchWeb(query, options = {}) {
    if (!this.isServerAvailable) {
      // Return mock data if server is not available
      return {
        success: true,
        results: [
          {
            title: 'Google Cloud Platform',
            link: 'https://cloud.google.com',
            snippet: 'Google Cloud Platform lets you build, deploy, and scale applications, websites, and services on the same infrastructure as Google.'
          },
          {
            title: 'Model Context Protocol (MCP)',
            link: 'https://github.com/eniayomi/gcp-mcp',
            snippet: 'A protocol for connecting AI models with external tools and services.'
          },
          {
            title: 'DevDocs API Documentation',
            link: 'https://devdocs.io',
            snippet: 'DevDocs combines multiple API documentations in a fast, organized, and searchable interface.'
          }
        ]
      };
    }

    try {
      const response = await axios.post(`${this.apiEndpoint}/search`, {
        query,
        maxResults: options.maxResults || 5
      });

      return response.data;
    } catch (error) {
      console.error('Error searching web with MCP:', error);
      this.isServerAvailable = false;

      // Return mock data on error
      return {
        success: true,
        results: [
          {
            title: 'Google Cloud Platform',
            link: 'https://cloud.google.com',
            snippet: 'Google Cloud Platform lets you build, deploy, and scale applications, websites, and services on the same infrastructure as Google.'
          },
          {
            title: 'Model Context Protocol (MCP)',
            link: 'https://github.com/eniayomi/gcp-mcp',
            snippet: 'A protocol for connecting AI models with external tools and services.'
          },
          {
            title: 'DevDocs API Documentation',
            link: 'https://devdocs.io',
            snippet: 'DevDocs combines multiple API documentations in a fast, organized, and searchable interface.'
          }
        ]
      };
    }
  }
}

// Create a singleton instance
const mcpClient = new MCPClient();

export default mcpClient;
