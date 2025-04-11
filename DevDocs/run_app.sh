#!/bin/bash
echo "Starting the application..."

# Start the backend server
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py &
cd ..

# Start the frontend server
cd frontend
npm install
npm run dev &

echo "Application started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3002"
