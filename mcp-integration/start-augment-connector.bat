@echo off
echo Starting Augment Connector...

REM Start the MCP server in a new window
start cmd /k "cd %~dp0 && node server.js"

REM Wait for the server to start
timeout /t 3

REM Start the Augment connector
start cmd /k "cd %~dp0 && node augment-connector.js"

REM Wait for the connector to start
timeout /t 3

REM Open the DevDocs web interface
start "" "http://localhost:3000/devdocs-web.html"

echo Augment Connector started successfully!
echo MCP server is running at http://localhost:8080
echo Augment connector is running at http://localhost:3000
echo DevDocs web interface is now open in your browser.
