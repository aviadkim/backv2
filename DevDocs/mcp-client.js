/**
 * MCP Client for Testing MCP Servers
 * 
 * This script provides a client to test MCP servers by sending actual MCP protocol requests.
 * Run with: node mcp-client.js <server-name> <method> [params]
 * 
 * Example: node mcp-client.js braveSearch search '{"query": "test"}'
 */

const http = require('http');
const https = require('https');
const { v4: uuidv4 } = require('uuid');

// MCP server configuration
const MCP_SERVERS = {
  braveSearch: {
    name: "Brave Search",
    port: 3000,
    host: "localhost",
    methods: ["search"]
  },
  github: {
    name: "GitHub MCP Server",
    port: 3001,
    host: "localhost",
    methods: ["getRepository", "getIssues", "getPullRequests"]
  },
  sqlite: {
    name: "SQLite",
    port: 3002,
    host: "localhost",
    methods: ["query"]
  },
  magic: {
    name: "Magic",
    port: 3003,
    host: "localhost",
    methods: ["generate"]
  },
  supabase: {
    name: "Supabase MCP",
    port: 3004,
    host: "localhost",
    methods: ["list_projects", "query"]
  },
  browserTools: {
    name: "Browser Tools MCP",
    port: 3005,
    host: "localhost",
    methods: ["getConsoleLogs", "getConsoleErrors"]
  },
  firecrawl: {
    name: "Firecrawl MCP",
    port: 3006,
    host: "localhost",
    methods: ["firecrawl_scrape"]
  },
  puppeteer: {
    name: "Puppeteer MCP",
    port: 3007,
    host: "localhost",
    methods: ["puppeteer_navigate"]
  },
  sequentialThinking: {
    name: "Sequential Thinking",
    port: 3008,
    host: "localhost",
    methods: ["solve"]
  }
};

// Sample parameters for each method
const SAMPLE_PARAMS = {
  search: { query: "financial document analysis" },
  getRepository: { owner: "aviadkim", repo: "backv2" },
  query: { query: "SELECT 1" },
  generate: { prompt: "Write a function to calculate compound interest" },
  list_projects: {},
  getConsoleLogs: { url: "https://example.com" },
  getConsoleErrors: { url: "https://example.com" },
  firecrawl_scrape: { url: "https://example.com" },
  puppeteer_navigate: { url: "https://example.com" },
  solve: { problem: "How to improve financial document analysis?" }
};

/**
 * Send an MCP request to a server
 * @param {string} serverKey - The key of the server in MCP_SERVERS
 * @param {string} method - The method to call
 * @param {object} params - The parameters to pass
 * @returns {Promise<object>} - The response from the server
 */
async function sendMcpRequest(serverKey, method, params) {
  const server = MCP_SERVERS[serverKey];
  
  if (!server) {
    throw new Error(`Unknown server: ${serverKey}`);
  }
  
  if (!server.methods.includes(method)) {
    throw new Error(`Unknown method ${method} for server ${server.name}`);
  }
  
  // Create MCP request
  const requestId = uuidv4();
  const mcpRequest = {
    jsonrpc: "2.0",
    id: requestId,
    method,
    params: params || {}
  };
  
  // Convert to JSON
  const requestData = JSON.stringify(mcpRequest);
  
  // Create HTTP request options
  const options = {
    hostname: server.host,
    port: server.port,
    path: '/',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(requestData)
    }
  };
  
  return new Promise((resolve, reject) => {
    // Create request
    const req = http.request(options, (res) => {
      let data = '';
      
      // Collect response data
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      // Process response when complete
      res.on('end', () => {
        try {
          const response = JSON.parse(data);
          resolve(response);
        } catch (error) {
          reject(new Error(`Failed to parse response: ${error.message}`));
        }
      });
    });
    
    // Handle request errors
    req.on('error', (error) => {
      reject(new Error(`Request failed: ${error.message}`));
    });
    
    // Send request
    req.write(requestData);
    req.end();
  });
}

/**
 * List all available servers and methods
 */
function listServersAndMethods() {
  console.log("Available MCP Servers and Methods:");
  console.log("==================================");
  
  for (const [key, server] of Object.entries(MCP_SERVERS)) {
    console.log(`\n${server.name} (${key}):`);
    console.log(`  Host: ${server.host}`);
    console.log(`  Port: ${server.port}`);
    console.log("  Methods:");
    
    for (const method of server.methods) {
      console.log(`    - ${method}`);
    }
  }
}

/**
 * Main function
 */
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log("MCP Client for Testing MCP Servers");
    console.log("Usage: node mcp-client.js <server-name> <method> [params]");
    console.log("Example: node mcp-client.js braveSearch search '{\"query\": \"test\"}'");
    console.log("\nUse --list to see all available servers and methods");
    return;
  }
  
  if (args[0] === '--list' || args[0] === '-l') {
    listServersAndMethods();
    return;
  }
  
  const serverKey = args[0];
  const method = args[1];
  let params = args[2] ? JSON.parse(args[2]) : null;
  
  if (!serverKey || !method) {
    console.error("Error: Both server name and method are required");
    console.log("Use --help for usage information");
    return;
  }
  
  if (!MCP_SERVERS[serverKey]) {
    console.error(`Error: Unknown server '${serverKey}'`);
    console.log("Use --list to see all available servers");
    return;
  }
  
  if (!MCP_SERVERS[serverKey].methods.includes(method)) {
    console.error(`Error: Unknown method '${method}' for server '${serverKey}'`);
    console.log(`Available methods for ${MCP_SERVERS[serverKey].name}:`);
    MCP_SERVERS[serverKey].methods.forEach(m => console.log(`  - ${m}`));
    return;
  }
  
  // Use sample parameters if none provided
  if (!params && SAMPLE_PARAMS[method]) {
    console.log(`No parameters provided. Using sample parameters:`);
    console.log(JSON.stringify(SAMPLE_PARAMS[method], null, 2));
    params = SAMPLE_PARAMS[method];
  }
  
  try {
    console.log(`Sending request to ${MCP_SERVERS[serverKey].name}...`);
    console.log(`Method: ${method}`);
    console.log(`Parameters:`, params);
    
    const response = await sendMcpRequest(serverKey, method, params);
    
    console.log("\nResponse:");
    console.log(JSON.stringify(response, null, 2));
  } catch (error) {
    console.error(`\nError:`, error.message);
    console.log("\nThis could mean:");
    console.log("1. The MCP server is not running");
    console.log("2. The server is running on a different port");
    console.log("3. The method or parameters are incorrect");
    console.log("4. There's a network issue");
    
    console.log("\nTry starting the server first, then run this client again.");
  }
}

// Run the main function
main().catch(console.error);
