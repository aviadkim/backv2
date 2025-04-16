#!/bin/bash

# Set the OpenRouter API key
export OPENROUTER_API_KEY="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"

# Check if a file path is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <file_path>"
    exit 1
fi

# Run the AI Enhanced Processor with all agents
echo "Running AI Enhanced Processor with all agents..."
python run_all_agents.py "$1"

# Check if the processing was successful
if [ $? -eq 0 ]; then
    echo "Processing completed successfully!"
else
    echo "Processing failed. Please check the logs for details."
fi
