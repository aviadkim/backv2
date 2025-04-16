#!/bin/bash

# Set the OpenRouter API key
export OPENROUTER_API_KEY="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"

# Run the tests
echo "Running AI Enhanced Processor tests..."
python run_tests_with_api_key.py --test-type unit

# Check if the tests passed
if [ $? -eq 0 ]; then
    echo "Tests passed successfully!"
else
    echo "Tests failed. Please check the logs for details."
fi

# Start the web interface
echo "Starting the web interface..."
python run_web_interface.py &
WEB_PID=$!

# Wait for the web interface to start
sleep 5

# Open the web interface in the browser
echo "Opening the web interface in the browser..."
python -c "import webbrowser; webbrowser.open('http://localhost:8080')"

# Wait for user input to stop the web interface
echo "Press Enter to stop the web interface..."
read

# Stop the web interface
kill $WEB_PID

echo "Test completed."
