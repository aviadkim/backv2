#!/bin/sh
set -e

# Start backend server
echo "Starting backend server..."
cd /app/backend
node server.js &
BACKEND_PID=$!

# Start frontend server
echo "Starting frontend server..."
cd /app/frontend
npm start &
FRONTEND_PID=$!

# Handle termination
trap 'kill $BACKEND_PID $FRONTEND_PID; exit 0' TERM INT

# Keep the container running
wait $BACKEND_PID $FRONTEND_PID
