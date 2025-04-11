@echo off
start cmd /k "cd backend && python app.py"
start cmd /k "cd fast-markdown-mcp && python app.py"
start cmd /k "cd frontend && npm run dev"
echo DevDocs started. Frontend: http://localhost:3001, Backend: http://localhost:24125, MCP: http://localhost:24126
