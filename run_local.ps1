# Run the FinDoc Analyzer v1.0 application locally

# Set environment variables
$env:OPENROUTER_API_KEY = "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"
$env:PORT = "8080"
$env:FLASK_ENV = "development"

# Create necessary directories
New-Item -ItemType Directory -Path uploads, results -Force

# Run the application
python app.py
