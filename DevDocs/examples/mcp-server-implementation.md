# MCP Web Server Implementation

This document outlines the implementation details for the MCP Web Server in Augment.

## Server Architecture

The MCP Web Server is designed as a standalone microservice that provides web browsing capabilities to all Augment projects. It follows the Model-Controller-Provider (MCP) architecture pattern.

```
┌─────────────────────────────────────────────────────────────┐
│                      MCP Web Server                          │
├─────────────┬─────────────────────────┬────────────────────┤
│             │                         │                    │
│   Models    │      Controllers        │     Providers      │
│             │                         │                    │
├─────────────┼─────────────────────────┼────────────────────┤
│ WebPage     │ BrowsingController      │ BrowsingProvider   │
│ SearchResult│ SearchController        │ SearchProvider     │
│ FinancialData│ FinancialDataController│ FinancialProvider  │
│             │                         │                    │
└─────────────┴─────────────────────────┴────────────────────┘
           │                 │                  │
           ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                         API Layer                            │
├─────────────────────────────────────────────────────────────┤
│  /fetch   │  /search   │  /extract   │  /history  │  /bookmarks │
└─────────────────────────────────────────────────────────────┘
           │                 │                  │
           ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      Augment Projects                        │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Models

The Models define the data structures used throughout the system:

```typescript
// WebPage Model
interface WebPage {
  url: string;
  title: string;
  content: string;
  html?: string;
  loadedAt: string;
  metadata?: {
    description?: string;
    keywords?: string[];
    author?: string;
    favicon?: string;
    [key: string]: any;
  };
}

// SearchResult Model
interface SearchResult {
  url: string;
  title: string;
  snippet: string;
  position: number;
}

// FinancialData Model
interface FinancialData {
  url: string;
  extractedAt: string;
  securities: Array<{
    type: string;
    identifier: string;
    name: string;
  }>;
  metrics: Record<string, string>;
  tables: Array<{
    id: string;
    headers: string[];
    rows: string[][];
  }>;
  charts: Array<{
    id: string;
    type: string;
    title: string;
    data: any;
  }>;
}
```

### 2. Controllers

The Controllers handle the business logic:

```typescript
// BrowsingController
class BrowsingController {
  async fetchPage(url: string, options?: BrowsingOptions): Promise<WebPage> {
    // Implementation details
  }
  
  _extractMetadata(html: string): WebPage['metadata'] {
    // Implementation details
  }
  
  _extractText(html: string): string {
    // Implementation details
  }
}

// SearchController
class SearchController {
  async search(query: string, options?: SearchOptions): Promise<SearchResponse> {
    // Implementation details
  }
}

// FinancialDataController
class FinancialDataController {
  async extractFinancialData(url: string, html: string): Promise<FinancialData> {
    // Implementation details
  }
  
  _extractSecurities(html: string): FinancialData['securities'] {
    // Implementation details
  }
  
  _extractMetrics(html: string): FinancialData['metrics'] {
    // Implementation details
  }
}
```

### 3. Providers

The Providers manage state and provide context:

```typescript
// BrowsingProvider
class BrowsingProvider {
  private state: BrowsingState;
  
  constructor() {
    this.state = {
      currentPage: null,
      history: [],
      bookmarks: [],
      lastSearch: null,
      loading: false,
      error: null
    };
  }
  
  async fetchPage(url: string): Promise<WebPage> {
    // Implementation details
  }
  
  async search(query: string): Promise<SearchResponse> {
    // Implementation details
  }
  
  // Other methods
}
```

## API Endpoints

The MCP Web Server exposes the following RESTful API endpoints:

### 1. Web Fetching

```
GET /api/fetch?url={url}
```

Fetches a web page and returns its content.

**Example Response:**
```json
{
  "url": "https://finance.yahoo.com/quote/AAPL",
  "title": "Apple Inc. (AAPL) Stock Price, News, Quote & History - Yahoo Finance",
  "content": "...",
  "loadedAt": "2023-07-15T12:34:56Z",
  "metadata": {
    "description": "Find the latest Apple Inc. (AAPL) stock quote, history, news and other vital information to help you with your stock trading and investing.",
    "keywords": ["AAPL", "Apple", "stock", "quote"]
  }
}
```

### 2. Web Searching

```
GET /api/search?query={query}&engine={engine}&num_results={num}
```

Searches the web and returns results.

**Example Response:**
```json
{
  "query": "Apple financial results",
  "results": [
    {
      "url": "https://investor.apple.com/investor-relations/default.aspx",
      "title": "Apple Investor Relations",
      "snippet": "View Apple Inc. (AAPL) financial statements, key financial ratios and more.",
      "position": 1
    },
    // More results...
  ],
  "totalResults": 10,
  "searchTime": 0.45,
  "searchEngine": "google",
  "searchedAt": "2023-07-15T12:34:56Z"
}
```

### 3. Financial Data Extraction

```
POST /api/extract
```

**Request Body:**
```json
{
  "url": "https://finance.yahoo.com/quote/AAPL",
  "html": "..."
}
```

**Example Response:**
```json
{
  "url": "https://finance.yahoo.com/quote/AAPL",
  "extractedAt": "2023-07-15T12:34:56Z",
  "securities": [
    {
      "type": "Ticker",
      "identifier": "AAPL",
      "name": "Apple Inc."
    }
  ],
  "metrics": {
    "marketCap": "$2.87T",
    "pe": "30.45",
    "dividend": "0.58%"
  },
  "tables": [
    {
      "id": "table-1",
      "headers": ["Metric", "Value"],
      "rows": [
        ["Open", "190.23"],
        ["High", "192.67"],
        ["Low", "189.78"]
      ]
    }
  ],
  "charts": []
}
```

### 4. History Management

```
GET /api/history
POST /api/history
DELETE /api/history
```

Manages browsing history.

### 5. Bookmark Management

```
GET /api/bookmarks
POST /api/bookmarks
DELETE /api/bookmarks/{id}
```

Manages bookmarks.

## Integration with Augment

To use the MCP Web Server in Augment:

1. Register the server in Augment's MCP configuration:

```json
{
  "name": "web",
  "endpoint": "https://mcp-web-server.augment.dev",
  "auth": {
    "type": "bearer",
    "token": "${MCP_WEB_TOKEN}"
  }
}
```

2. Use the MCP in Augment projects:

```javascript
// Example usage in an Augment project
const webPage = await augment.mcp.web.fetch("https://finance.yahoo.com/quote/AAPL");
console.log(webPage.title);

const searchResults = await augment.mcp.web.search("Apple financial results");
console.log(searchResults.results);

const financialData = await augment.mcp.web.extract(webPage.url, webPage.html);
console.log(financialData.metrics);
```

## Deployment

The MCP Web Server is deployed as a containerized application:

```dockerfile
FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

Deployed to Kubernetes with appropriate resource limits and scaling policies.
