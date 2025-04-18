# MCP Server Integration for Development

This directory contains tools for integrating Model Context Protocol (MCP) servers into the development environment. These tools are for development purposes only and should not be used in production or pushed to GitHub.

## What is MCP?

Model Context Protocol (MCP) is a protocol for AI agents to access external tools and services. It allows AI models to interact with databases, search engines, web browsers, and other services through a standardized interface.

## Available MCP Servers

The following MCP servers are configured for development:

1. **Brave Search** - Search the web using Brave Search
2. **GitHub** - Interact with GitHub repositories
3. **SQLite** - Execute SQL queries against a SQLite database
4. **Magic** - Generate code and other content
5. **Supabase** - Interact with Supabase projects and databases
6. **Browser Tools** - Get console logs and errors from web pages
7. **Firecrawl** - Scrape web pages
8. **Puppeteer** - Navigate web pages using Puppeteer
9. **Sequential Thinking** - Solve problems using sequential thinking

## Getting Started

### 1. Start the MCP Servers

Run the `start-mcp-servers.bat` script to start all MCP servers:

```bash
.\start-mcp-servers.bat
```

This will start each MCP server in a separate command prompt window.

### 2. Test the MCP Servers

Use the `mcp-client.js` script to test if the MCP servers are running and responding:

```bash
node mcp-client.js --list  # List all available servers and methods
node mcp-client.js braveSearch search '{"query": "financial document analysis"}'  # Test Brave Search
node mcp-client.js github getRepository '{"owner": "aviadkim", "repo": "backv2"}'  # Test GitHub
```

### 3. Check Server Status

Use the `test-mcp-servers.js` script to check if the MCP servers are running:

```bash
node test-mcp-servers.js
```

## Using MCP in Development

The `mcpClient.js` utility in the `frontend/utils` directory provides functions for interacting with MCP servers during development. This utility is only used in development mode and not in production.

Example usage:

```javascript
import mcpClient from '../utils/mcpClient';

// Search the web
const searchResults = await mcpClient.searchWeb('financial document analysis');

// Get information about a GitHub repository
const repoInfo = await mcpClient.getGithubRepo('aviadkim', 'backv2');

// Execute an SQL query
const queryResults = await mcpClient.executeSqlQuery('SELECT * FROM documents');
```

## MCP Testing Page

A development-only MCP testing page is available at `/mcp-test`. This page allows you to test MCP server functionality during development.

## Security Considerations

- **NEVER** push MCP configurations with secrets to GitHub
- MCP servers are for development use only and should not be used in production
- The MCP testing page is only available in development mode

## Troubleshooting

If you encounter issues with the MCP servers:

1. Make sure the servers are running (check the command prompt windows)
2. Verify that the ports are not being used by other applications
3. Check that the file paths in the configuration are correct
4. Ensure that the required dependencies are installed

## Additional Resources

- [Model Context Protocol Documentation](https://github.com/modelcontextprotocol/protocol)
- [MCP Server Implementation Guide](https://github.com/modelcontextprotocol/servers)
