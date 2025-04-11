#!/bin/bash
echo "Starting GCP MCP server for DevDocs..."
cd "$(dirname "$0")/../../gcp-mcp"
npm start
