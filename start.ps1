# Start backend
Start-Process -FilePath "powershell" -ArgumentList "-Command cd ./backend; python app.py"

# Start MCP server
Start-Process -FilePath "powershell" -ArgumentList "-Command cd ./fast-markdown-mcp; python app.py"

# Start frontend
Start-Process -FilePath "powershell" -ArgumentList "-Command cd ./frontend; npm run dev"

Write-Host "DevDocs started. Frontend: http://localhost:3001, Backend: http://localhost:24125, MCP: http://localhost:24126"
