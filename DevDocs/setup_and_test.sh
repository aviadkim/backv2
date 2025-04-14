#!/bin/bash

# Script to install dependencies and run tests

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if the API key is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <openrouter-api-key>"
    echo "Example: $0 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"
    exit 1
fi

# Run the setup and test script
python3 setup_and_test.py --api-key "$1"
