# GCP MCP Integration for DevDocs

This guide provides instructions for integrating the Google Cloud Platform Model Context Protocol (GCP MCP) server with DevDocs, allowing AI assistants like Claude to interact directly with your Google Cloud resources.

## Overview

The GCP MCP server enables AI assistants to:

1. Query and modify GCP resources using natural language
2. Interact with your DevDocs implementation in Google Cloud
3. Manage documents, process them, and extract information
4. Access and analyze document processing results

## Prerequisites

- Node.js installed
- Google Cloud SDK installed
- GCP credentials configured locally (application default credentials)
- Claude Desktop, Cursor, or Windsurf AI assistant

## Setup

### 1. Install GCP MCP

The GCP MCP server is already included in the DevDocs repository. To set it up:

```bash
# Navigate to the gcp-mcp directory
cd gcp-mcp

# Install dependencies
npm install
```

### 2. Configure GCP Credentials

Make sure you have GCP credentials configured:

```bash
# Log in to GCP and set up application default credentials
gcloud auth application-default login
```

### 3. Configure AI Assistant

#### Claude Desktop

1. Open Claude desktop app and go to Settings -> Developer -> Edit Config
2. Add the following entry to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gcp": {
      "command": "sh",
      "args": ["-c", "cd /path/to/backv2-main/gcp-mcp && npm start"]
    }
  }
}
```

Replace `/path/to/backv2-main` with the actual path to your project directory.

#### Cursor

1. Open Cursor and go to Settings (⌘,)
2. Navigate to AI -> Model Context Protocol
3. Add a new MCP configuration:

```json
{
  "gcp": {
    "command": "cd /path/to/backv2-main/gcp-mcp && npm start"
  }
}
```

Replace `/path/to/backv2-main` with the actual path to your project directory.

#### Windsurf

1. Open `~/.windsurf/config.json` (create if it doesn't exist)
2. Add the MCP configuration:

```json
{
  "mcpServers": {
    "gcp": {
      "command": "cd /path/to/backv2-main/gcp-mcp && npm start"
    }
  }
}
```

Replace `/path/to/backv2-main` with the actual path to your project directory.

### 4. Start the GCP MCP Server

You can start the GCP MCP server using the provided scripts:

**Windows:**
```
DevDocs\mcp\start-gcp-mcp.bat
```

**Unix/Mac:**
```
chmod +x DevDocs/mcp/start-gcp-mcp.sh
./DevDocs/mcp/start-gcp-mcp.sh
```

## Using GCP MCP with DevDocs

Once the GCP MCP server is running, you can use natural language to interact with your Google Cloud resources and DevDocs implementation:

### Example Commands

#### Project Management
- "List all GCP projects I have access to"
- "Use project [your-project-id]"

#### Storage Operations
- "List all storage buckets in my project"
- "Show me the contents of the DevDocs storage bucket"
- "Upload a document to the DevDocs storage bucket"

#### Document AI Operations
- "Process a document using Document AI"
- "Show me the results of document processing"
- "Extract text from a document"

#### DevDocs Operations
- "List all documents in DevDocs"
- "Upload a new document to DevDocs"
- "Process a document in DevDocs"
- "Show me the metadata for a document"
- "Add tags to a document"
- "Search for documents with specific tags"

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure you've run `gcloud auth application-default login`
   - Check that your GCP credentials are valid

2. **Permission Errors**
   - Verify that your account has the necessary IAM roles
   - For DevDocs, you need Storage Admin and Document AI Admin roles

3. **API Errors**
   - Make sure the required APIs are enabled in your project:
     - Storage API
     - Document AI API

### Viewing Logs

To see logs from the GCP MCP server:

**Windows:**
```
type %USERPROFILE%\AppData\Local\Temp\gcp-mcp.log
```

**Unix/Mac:**
```
cat /tmp/gcp-mcp.log
```

For Claude Desktop logs:
```
tail -n 50 -f ~/Library/Logs/Claude/mcp-server-gcp.log
```

## Additional Resources

- [GCP MCP GitHub Repository](https://github.com/eniayomi/gcp-mcp)
- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Google Cloud Document AI Documentation](https://cloud.google.com/document-ai/docs)
- [Google Cloud IAM Documentation](https://cloud.google.com/iam/docs)
