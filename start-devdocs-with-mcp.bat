@echo off
echo Starting DevDocs with MCP Integration...

REM Start the MCP server in a new window
start cmd /k "cd mcp-integration && node server.js"

REM Wait for the server to start
timeout /t 3

REM Start the DevDocs backend
start cmd /k "cd DevDocs\backend && python app.py"

REM Wait for the backend to start
timeout /t 3

REM Start the DevDocs frontend
start cmd /k "cd DevDocs\frontend && npm run dev"

echo DevDocs with MCP Integration started successfully!
echo MCP server is running at http://localhost:8080
echo DevDocs backend is running at http://localhost:24125
echo DevDocs frontend is running at http://localhost:3000
echo.
echo You can access the MCP integration at http://localhost:3000/mcp-integration
