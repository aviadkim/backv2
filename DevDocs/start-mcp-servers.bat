@echo off
echo Starting MCP Servers...
echo.

echo Starting Brave Search MCP Server...
start "Brave Search MCP" cmd /c "node C:\Users\Aviad\Documents\Cline\MCP\brave-search\run-brave-search.js"

echo Starting GitHub MCP Server...
start "GitHub MCP" cmd /c "node C:\Users\Aviad\AppData\Roaming\Roo-Code\MCP\github-mcp-server\build\index.js"

echo Starting SQLite MCP Server...
start "SQLite MCP" cmd /c "uv --directory C:\Users\Aviad\Documents\Cline\MCP\github.com\modelcontextprotocol\servers\tree\main\src\sqlite\src\sqlite run mcp-server-sqlite --db-path C:\Users\Aviad\test.db"

echo Starting Magic MCP Server...
start "Magic MCP" cmd /c "npx -y @21st-dev/magic@latest API_KEY=\"78139157260ac26a4f0dbe1e8f5b3727a47a0d24cf62c9fa08363aeee054db96\""

echo Starting Supabase MCP Server...
start "Supabase MCP" cmd /c "npx -y @supabase/mcp-server-supabase@latest --access-token sbp_cdcfec9d48c88f29d0e7c24a36cc450104b35055"

echo Starting Browser Tools MCP Server...
start "Browser Tools MCP" cmd /c "npx -y @agentdeskai/browser-tools-mcp@latest"

echo Starting Firecrawl MCP Server...
start "Firecrawl MCP" cmd /c "set FIRECRAWL_API_KEY=fc-857417811665460e92716b92e08ec398 && npx -y firecrawl-mcp"

echo Starting Puppeteer MCP Server...
start "Puppeteer MCP" cmd /c "npx -y @modelcontextprotocol/server-puppeteer"

echo Starting Sequential Thinking MCP Server...
start "Sequential Thinking MCP" cmd /c "server-sequential-thinking"

echo.
echo All MCP servers have been started in separate windows.
echo Use the mcp-client.js script to test them.
echo Example: node mcp-client.js braveSearch search "{\"query\": \"test\"}"
echo.
echo Press any key to exit...
pause > nul
