#!/bin/bash

# Script to test the data export and document comparison agents

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if the API key is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <openrouter-api-key> [export-format]"
    echo "Example: $0 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 excel"
    exit 1
fi

# Set default export format if not provided
EXPORT_FORMAT="json"
if [ ! -z "$2" ]; then
    EXPORT_FORMAT="$2"
fi

# Run the tests
python3 test_data_export_comparison.py --api-key "$1" --export-format "$EXPORT_FORMAT"
