# DevDocs - Documentation Management System

DevDocs is a component of the FinDoc platform that helps financial professionals access and manage documentation using Google Cloud services and AI capabilities.

## Features

- **Google Cloud Storage Integration**: Access and manage documents stored in Google Cloud Storage.
- **Web Search**: Search the web for documentation and resources.
- **Web Fetch**: Fetch content from a URL and convert it to a readable format.
- **AI Chat**: Chat with an AI assistant to get help with your documentation.

## Components

### MCP Server

The Model Context Protocol (MCP) server is deployed on Google Cloud Run and provides the following capabilities:

- **listBuckets**: List all storage buckets.
- **listFiles**: List files in a storage bucket.
- **webSearch**: Search the web for information.
- **webFetch**: Fetch content from a URL.

### Web Application

The web application provides a user-friendly interface to interact with the MCP server. It includes:

- A responsive UI with tabs for different features.
- Integration with the MCP server for accessing Google Cloud services.
- A simulated AI chat interface (to be connected to a real AI service in the future).

### Command-Line Client

The command-line client allows you to interact with the MCP server programmatically. It provides:

- A simple menu-driven interface.
- Access to all MCP server capabilities.
- Easy integration with scripts and automation.

## Getting Started

### Prerequisites

- Node.js 14 or higher
- A modern web browser
- Access to the internet

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/aviadkim/backv2.git
   cd backv2
   ```

2. Install dependencies:
   ```
   cd mcp-integration
   npm install
   ```

3. Open the web application:
   ```
   open devdocs-app.html
   ```

4. Run the command-line client:
   ```
   node devdocs-client.js
   ```

## Deployment

The MCP server is deployed on Google Cloud Run at:
https://devdocs-mcp-server-678297464867.me-west1.run.app

## Integration with FinDoc

DevDocs integrates with the main FinDoc platform to provide:

1. Documentation management for financial documents
2. AI-powered search and retrieval of financial information
3. Web browsing capabilities for financial research
4. Integration with Google Cloud for secure document storage

## Future Enhancements

- Integration with real AI services for the chat feature.
- Document upload and management capabilities.
- User authentication and authorization.
- Enhanced search capabilities with filters and sorting.
- Integration with other cloud providers.

## License

This project is proprietary and confidential, as part of the FinDoc platform.

## Contact

For questions or support, please contact the development team.
