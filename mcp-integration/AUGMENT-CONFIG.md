# Configuring Augment with MCP

This guide explains how to configure Augment to use the Model Context Protocol (MCP) server for Google Cloud and web browsing capabilities.

## Prerequisites

1. The MCP server is running at http://localhost:8080
2. The Augment connector is running at http://localhost:3000 (optional)

## Configuration Steps

### Option 1: Direct MCP Integration

1. Open Augment
2. Go to Settings
3. Find the MCP configuration section
4. Add a new MCP server with the following details:
   - Name: Google Cloud MCP
   - URL: http://localhost:8080/mcp
   - Type: Custom
5. Save the configuration

### Option 2: Using the Augment Connector

1. Open Augment
2. Go to Settings
3. Find the API configuration section
4. Add a new API endpoint with the following details:
   - Name: DevDocs Google Cloud
   - URL: http://localhost:3000/api/augment
   - Method: POST
   - Headers: Content-Type: application/json
5. Save the configuration

## Testing the Integration

Once configured, you can test the integration by asking Augment to perform tasks like:

- "List all storage buckets in my Google Cloud project"
- "List files in the devdocs-bucket"
- "Upload a file to my storage bucket"
- "Process a document in my storage bucket"
- "Search the web for information about Google Cloud"
- "Fetch the content from https://cloud.google.com/"

## Troubleshooting

If you encounter any issues:

1. Make sure the MCP server is running at http://localhost:8080
2. Check the server logs for error messages
3. Verify that the service account has the necessary permissions
4. Try restarting the MCP server and Augment

## Example Prompts

Here are some example prompts you can use with Augment:

```
List all storage buckets in my Google Cloud project
```

```
Search the web for information about Model Context Protocol
```

```
Fetch the content from https://cloud.google.com/
```

```
Upload a file named "test.txt" with content "This is a test" to my devdocs-bucket
```

```
Process the document "sample.pdf" in my devdocs-bucket
```
