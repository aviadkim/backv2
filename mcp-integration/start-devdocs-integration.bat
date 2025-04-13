@echo off
echo Starting DevDocs Google Cloud Integration...

REM Start the MCP server in a new window
start cmd /k "cd %~dp0 && node server.js"

REM Wait for the server to start
timeout /t 3

REM Open the DevDocs web interface
start "" "%~dp0devdocs-web.html"

echo DevDocs Google Cloud Integration started successfully!
echo MCP server is running at http://localhost:8080
echo DevDocs web interface is now open in your browser.
