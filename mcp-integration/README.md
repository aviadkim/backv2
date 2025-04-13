# Google Cloud MCP Integration

This is a Model Context Protocol (MCP) integration for Google Cloud with web browsing capabilities.

## Features

- Google Cloud Storage operations (list buckets, list files, upload/download files)
- Document AI processing
- Web search functionality
- Web content fetching

## Setup

1. Install dependencies:

```bash
npm install
```

2. Configure the `.env` file with your Google Cloud settings:

```
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_KEY_FILENAME=./path-to-your-service-account-key.json
GOOGLE_CLOUD_STORAGE_BUCKET=your-bucket-name
GOOGLE_CLOUD_DOCUMENT_AI_PROCESSOR_ID=your-processor-id
GOOGLE_CLOUD_DOCUMENT_AI_LOCATION=us
MCP_PORT=8080
```

3. Start the server:

```bash
npm start
```

## Usage with Augment

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

## API Endpoints

### POST /mcp

The main MCP endpoint that accepts actions and parameters.

Example request:

```json
{
  "action": "listBuckets",
  "parameters": {}
}
```

Available actions:
- `listBuckets`: List all storage buckets
- `listFiles`: List files in a bucket (requires `bucketName` parameter)
- `uploadFile`: Upload a file to a bucket (requires `bucketName`, `fileName`, and `fileContent` parameters)
- `downloadFile`: Download a file from a bucket (requires `bucketName` and `fileName` parameters)
- `processDocument`: Process a document with Document AI (requires `bucketName` and `fileName` parameters)
- `webSearch`: Search the web (requires `query` parameter)
- `webFetch`: Fetch content from a URL (requires `url` parameter)
