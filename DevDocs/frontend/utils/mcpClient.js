/**
 * MCP Client Utility for Development
 * 
 * This utility provides functions to interact with MCP servers during development.
 * It is only used in development mode and not in production.
 */

// Check if we're in development mode
const isDevelopment = process.env.NODE_ENV !== 'production';

// MCP server configuration for development
const MCP_SERVERS = {
  braveSearch: "github.com/modelcontextprotocol/servers/tree/main/src/brave-search",
  github: "github-mcp-server",
  sqlite: "github.com/modelcontextprotocol/servers/tree/main/src/sqlite",
  magic: "@21st-dev/magic",
  supabase: "github.com/supabase-community/supabase-mcp",
  browserTools: "github.com/AgentDeskAI/browser-tools-mcp",
  firecrawl: "github.com/mendableai/firecrawl-mcp-server",
  puppeteer: "github.com/modelcontextprotocol/servers/tree/main/src/puppeteer",
  sequentialThinking: "github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking"
};

/**
 * Call an MCP server function
 * @param {string} server - The MCP server to call
 * @param {string} method - The method to call on the server
 * @param {object} params - The parameters to pass to the method
 * @returns {Promise<any>} - The result of the MCP call
 */
async function callMcp(server, method, params = {}) {
  if (!isDevelopment) {
    console.warn('MCP client is only available in development mode');
    return null;
  }

  try {
    // In a real implementation, this would use the MCP protocol to call the server
    // For now, we'll just log the call and return a mock response
    console.log(`[MCP] Calling ${server}.${method} with params:`, params);
    
    // Mock responses for development
    switch (server) {
      case MCP_SERVERS.braveSearch:
        if (method === 'search') {
          return { results: [{ title: 'Mock search result', url: 'https://example.com' }] };
        }
        break;
      case MCP_SERVERS.github:
        if (method === 'getRepository') {
          return { name: 'backv2', owner: 'aviadkim', stars: 5 };
        }
        break;
      case MCP_SERVERS.supabase:
        if (method === 'list_projects') {
          return [{ name: "aviadkim's Project", id: "dnjnsotemnfrjlotgved" }];
        }
        break;
      // Add more mock responses as needed
    }
    
    return { success: true, message: 'Mock MCP response' };
  } catch (error) {
    console.error(`[MCP] Error calling ${server}.${method}:`, error);
    throw error;
  }
}

/**
 * Search the web using Brave Search
 * @param {string} query - The search query
 * @returns {Promise<any>} - The search results
 */
export async function searchWeb(query) {
  return callMcp(MCP_SERVERS.braveSearch, 'search', { query });
}

/**
 * Get information about a GitHub repository
 * @param {string} owner - The repository owner
 * @param {string} repo - The repository name
 * @returns {Promise<any>} - The repository information
 */
export async function getGithubRepo(owner, repo) {
  return callMcp(MCP_SERVERS.github, 'getRepository', { owner, repo });
}

/**
 * Execute an SQL query using SQLite
 * @param {string} query - The SQL query
 * @returns {Promise<any>} - The query results
 */
export async function executeSqlQuery(query) {
  return callMcp(MCP_SERVERS.sqlite, 'query', { query });
}

/**
 * List Supabase projects
 * @returns {Promise<any>} - The list of projects
 */
export async function listSupabaseProjects() {
  return callMcp(MCP_SERVERS.supabase, 'list_projects', {});
}

/**
 * Get console logs from a webpage
 * @param {string} url - The URL of the webpage
 * @returns {Promise<any>} - The console logs
 */
export async function getWebConsoleLogs(url) {
  return callMcp(MCP_SERVERS.browserTools, 'getConsoleLogs', { url });
}

/**
 * Scrape a webpage using Firecrawl
 * @param {string} url - The URL to scrape
 * @returns {Promise<any>} - The scraped content
 */
export async function scrapeWebpage(url) {
  return callMcp(MCP_SERVERS.firecrawl, 'firecrawl_scrape', { url });
}

/**
 * Navigate to a webpage using Puppeteer
 * @param {string} url - The URL to navigate to
 * @returns {Promise<any>} - The page content
 */
export async function navigateWithPuppeteer(url) {
  return callMcp(MCP_SERVERS.puppeteer, 'puppeteer_navigate', { url });
}

/**
 * Perform sequential thinking on a problem
 * @param {string} problem - The problem to solve
 * @returns {Promise<any>} - The solution
 */
export async function solveWithSequentialThinking(problem) {
  return callMcp(MCP_SERVERS.sequentialThinking, 'solve', { problem });
}

export default {
  isDevelopment,
  MCP_SERVERS,
  callMcp,
  searchWeb,
  getGithubRepo,
  executeSqlQuery,
  listSupabaseProjects,
  getWebConsoleLogs,
  scrapeWebpage,
  navigateWithPuppeteer,
  solveWithSequentialThinking
};
