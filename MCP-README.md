# Google Cloud MCP Integration with DevDocs

This project provides a Model Context Protocol (MCP) integration for Google Cloud with web browsing capabilities. It allows Augment and DevDocs to interact with Google Cloud services and browse the web.

## Features

- Google Cloud Storage operations (list buckets, list files, upload/download files)
- Document AI processing
- Web search functionality
- Web content fetching

## Setup

1. Install dependencies:

```bash
cd mcp-integration
npm install
```

2. Start the MCP server:

```bash
cd mcp-integration
node server.js
```

The server will start on http://localhost:8080.

## Testing

You can test the MCP integration using the provided test pages:

### Basic MCP Test

1. Open the test.html file in your browser
2. Select an action from the dropdown
3. Fill in the required parameters
4. Click "Execute" to see the results

### DevDocs Integration Test

1. Open the devdocs-web.html file in your browser
2. Use the sidebar to select different actions
3. Click on buckets and files to interact with them
4. Upload files and process documents
5. Search the web and fetch content from URLs

You can also run the DevDocs integration example script:

```bash
node devdocs-example.js
```

Or use the start script to launch both the MCP server and the DevDocs web interface:

```bash
start-devdocs-integration.bat
```

## Using with Augment

1. Configure Augment to use this MCP server:
   - Open Augment
   - Go to Settings
   - Find the MCP configuration section
   - Add a new MCP server with the URL `http://localhost:8080`
   - Save the configuration

2. Test the integration by asking Augment to perform tasks like:
   - "List all storage buckets in my Google Cloud project"
   - "Search the web for information about XYZ"
   - "Fetch the content from URL"

## Troubleshooting

If you encounter any issues:

1. Check the server logs for error messages
2. Verify that the service account has the necessary permissions
3. Make sure the .env file is configured correctly
4. Restart the server if needed

## Security Considerations

- The service account key is sensitive information. Keep it secure and do not share it.
- Consider using more secure authentication methods in a production environment.
- Implement proper access controls to restrict who can use the MCP server.
