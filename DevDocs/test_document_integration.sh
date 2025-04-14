#!/bin/bash

# Script to test the document integration and query engine agents

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if the API key is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <openrouter-api-key> [query]"
    echo "Example: $0 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 \"What is the total value of the portfolio?\""
    exit 1
fi

# Run the tests
if [ -z "$2" ]; then
    python3 test_document_integration.py --api-key "$1"
else
    python3 test_document_integration.py --api-key "$1" --query "$2"
fi
