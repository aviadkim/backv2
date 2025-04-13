# Configuring Augment with MCP Agent Mode and Web Browsing

This guide explains how to configure Augment to use the Model Context Protocol (MCP) server with agent mode and web browsing capabilities.

## Prerequisites

1. The MCP server is running at http://localhost:8080
2. The DevDocs application is deployed to Google Cloud Run

## Configuration Steps

### Step 1: Configure Augment with MCP Server

1. Open Augment
2. Go to Settings
3. Find the MCP configuration section
4. Add a new MCP server with the following details:
   - Name: Google Cloud MCP
   - URL: http://localhost:8080/mcp
   - Type: Custom
5. Save the configuration

### Step 2: Enable Agent Mode

1. In Augment, go to Settings
2. Find the Agent Mode section
3. Enable Agent Mode
4. Configure the following settings:
   - Agent Name: DevDocs Agent
   - Agent Description: An agent that can interact with Google Cloud and browse the web
   - Agent Capabilities: Google Cloud, Web Browsing, Document Processing
5. Save the configuration

### Step 3: Test the Integration

Once configured, you can test the integration by asking Augment to perform tasks like:

- "List all storage buckets in my Google Cloud project"
- "Search the web for information about Model Context Protocol"
- "Fetch the content from https://cloud.google.com/"
- "Upload a file to my storage bucket"
- "Process a document in my storage bucket"

### Step 4: Access the Deployed DevDocs Application

You can access the deployed DevDocs application at:

```
https://devdocs-service-github-456508.me-west1.run.app
```

This application includes:
- The DevDocs frontend
- The DevDocs backend
- The MCP server

## Example Agent Prompts

Here are some example prompts you can use with Augment in agent mode:

```
As a DevDocs agent, list all storage buckets in my Google Cloud project.
```

```
As a DevDocs agent, search the web for information about Model Context Protocol and summarize the results.
```

```
As a DevDocs agent, fetch the content from https://cloud.google.com/ and extract the main topics.
```

```
As a DevDocs agent, upload a file named "test.txt" with content "This is a test" to my devdocs-bucket.
```

```
As a DevDocs agent, process the document "sample.pdf" in my devdocs-bucket and extract the key information.
```
