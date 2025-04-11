/**
 * MCP Index - Entry point for the MCP system
 */

const { vercelProvider } = require('./vercel-mcp');
const { supabaseProvider } = require('./supabase-mcp');

// Export providers
module.exports = {
  vercel: vercelProvider,
  supabase: supabaseProvider
};
