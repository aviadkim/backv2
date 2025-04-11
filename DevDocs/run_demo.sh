#!/bin/bash
echo "Starting the FinDoc Demo Application..."

cd frontend
echo "Installing frontend dependencies..."
npm install

echo "Starting the frontend server..."
npm run dev &

echo "Application started!"
echo "Frontend: http://localhost:3000"

echo ""
echo "Note: The document understanding features are in demo mode with mock data."
echo "To see the document understanding demo, navigate to:"
echo "http://localhost:3000/document-understanding-demo"
