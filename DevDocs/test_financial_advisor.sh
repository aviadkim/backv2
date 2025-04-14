#!/bin/bash

# Script to test the financial advisor agent

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if the API key is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <openrouter-api-key> [analysis-type] [risk-profile] [investment-amount]"
    echo "Example: $0 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 portfolio medium 100000"
    exit 1
fi

# Set default parameters if not provided
ANALYSIS_TYPE="portfolio"
if [ ! -z "$2" ]; then
    ANALYSIS_TYPE="$2"
fi

RISK_PROFILE="medium"
if [ ! -z "$3" ]; then
    RISK_PROFILE="$3"
fi

INVESTMENT_AMOUNT=100000
if [ ! -z "$4" ]; then
    INVESTMENT_AMOUNT="$4"
fi

# Run the tests
python3 test_financial_advisor.py --api-key "$1" --analysis-type "$ANALYSIS_TYPE" --risk-profile "$RISK_PROFILE" --investment-amount "$INVESTMENT_AMOUNT"
