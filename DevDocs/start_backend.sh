#!/bin/bash

# Script to start the backend API server

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if the OpenRouter API key is set
if [ -z "$OPENROUTER_API_KEY" ]; then
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
    fi
    
    if [ -z "$OPENROUTER_API_KEY" ]; then
        echo "OpenRouter API key is not set. Please set the OPENROUTER_API_KEY environment variable or create a .env file."
        echo "You can set up the API key using the setup_openrouter_key.py script:"
        echo "  python backend/scripts/setup_openrouter_key.py --api-key YOUR_API_KEY"
        exit 1
    fi
fi

# Start the backend API server
echo "Starting backend API server..."
cd backend
python main.py --reload
