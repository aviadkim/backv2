@echo off
echo Starting the application...

REM Start the backend server
start cmd /k "cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && python app.py"

REM Start the frontend server
start cmd /k "cd frontend && npm install && npm run dev"

echo Application started!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3002
