/**
 * MCP Server Test Script
 * 
 * This script tests if the configured MCP servers are running and accessible.
 * Run with: node test-mcp-servers.js
 */

const { exec } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

// MCP server configuration
const MCP_SERVERS = {
  braveSearch: {
    name: "Brave Search",
    command: "node",
    args: ["C:\\Users\\Aviad\\Documents\\Cline\\MCP\\brave-search\\run-brave-search.js"],
    testPort: 3000
  },
  github: {
    name: "GitHub MCP Server",
    command: "node",
    args: ["C:\\Users\\Aviad\\AppData\\Roaming\\Roo-Code\\MCP\\github-mcp-server\\build\\index.js"],
    testPort: 3001
  },
  sqlite: {
    name: "SQLite",
    command: "uv",
    args: [
      "--directory",
      "C:\\Users\\Aviad\\Documents\\Cline\\MCP\\github.com\\modelcontextprotocol\\servers\\tree\\main\\src\\sqlite\\src\\sqlite",
      "run",
      "mcp-server-sqlite",
      "--db-path",
      "C:\\Users\\Aviad\\test.db"
    ],
    testPort: 3002
  },
  magic: {
    name: "Magic",
    command: "cmd",
    args: [
      "/c",
      "npx",
      "-y",
      "@21st-dev/magic@latest",
      "API_KEY=\"78139157260ac26a4f0dbe1e8f5b3727a47a0d24cf62c9fa08363aeee054db96\""
    ],
    testPort: 3003
  },
  supabase: {
    name: "Supabase MCP",
    command: "cmd",
    args: [
      "/c",
      "npx",
      "-y",
      "@supabase/mcp-server-supabase@latest",
      "--access-token",
      "sbp_cdcfec9d48c88f29d0e7c24a36cc450104b35055"
    ],
    testPort: 3004
  },
  browserTools: {
    name: "Browser Tools MCP",
    command: "cmd",
    args: [
      "/c",
      "npx",
      "-y",
      "@agentdeskai/browser-tools-mcp@latest"
    ],
    testPort: 3005
  },
  firecrawl: {
    name: "Firecrawl MCP",
    command: "cmd",
    args: [
      "/c",
      "set FIRECRAWL_API_KEY=fc-857417811665460e92716b92e08ec398 && npx -y firecrawl-mcp"
    ],
    testPort: 3006
  },
  puppeteer: {
    name: "Puppeteer MCP",
    command: "npx",
    args: [
      "-y",
      "@modelcontextprotocol/server-puppeteer"
    ],
    testPort: 3007
  },
  sequentialThinking: {
    name: "Sequential Thinking",
    command: "server-sequential-thinking",
    args: [],
    testPort: 3008
  }
};

// Check if a port is in use
function isPortInUse(port) {
  return new Promise((resolve) => {
    const server = http.createServer();
    
    server.once('error', (err) => {
      if (err.code === 'EADDRINUSE') {
        resolve(true); // Port is in use
      } else {
        resolve(false);
      }
    });
    
    server.once('listening', () => {
      server.close();
      resolve(false); // Port is not in use
    });
    
    server.listen(port);
  });
}

// Test if a server is running
async function testServer(server, key) {
  console.log(`\n----- Testing ${server.name} -----`);
  
  try {
    // Check if the port is in use (which might indicate the server is running)
    const portInUse = await isPortInUse(server.testPort);
    
    if (portInUse) {
      console.log(`✅ Port ${server.testPort} is in use. ${server.name} might be running.`);
    } else {
      console.log(`❌ Port ${server.testPort} is not in use. ${server.name} might not be running.`);
      
      // Try to start the server
      console.log(`Attempting to start ${server.name}...`);
      
      const command = `${server.command} ${server.args.join(' ')}`;
      console.log(`Command: ${command}`);
      
      // This will just print the command, not actually execute it for safety
      console.log(`To start this server, run the above command in a separate terminal.`);
    }
    
    // Check if the file paths exist
    if (server.args && server.args.length > 0) {
      const potentialFilePaths = server.args.filter(arg => 
        typeof arg === 'string' && 
        arg.includes('\\') && 
        (arg.endsWith('.js') || arg.endsWith('.py') || arg.endsWith('.exe'))
      );
      
      for (const filePath of potentialFilePaths) {
        if (fs.existsSync(filePath)) {
          console.log(`✅ File exists: ${filePath}`);
        } else {
          console.log(`❌ File does not exist: ${filePath}`);
        }
      }
    }
  } catch (error) {
    console.error(`Error testing ${server.name}:`, error);
  }
}

// Main function to test all servers
async function testAllServers() {
  console.log("===== MCP Server Test =====");
  console.log("This script will check if your MCP servers are running and accessible.");
  
  for (const [key, server] of Object.entries(MCP_SERVERS)) {
    await testServer(server, key);
  }
  
  console.log("\n===== Test Complete =====");
  console.log("Note: This script only checks if ports are in use and files exist.");
  console.log("It does not actually connect to the MCP servers or test their functionality.");
  console.log("To fully test an MCP server, you would need to send proper MCP protocol requests.");
}

// Run the tests
testAllServers().catch(console.error);
