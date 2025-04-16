# Test the FinDoc Analyzer v1.0 with the Messos PDF

# Set environment variables
$env:OPENROUTER_API_KEY = "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"

# Run the test
python test_findoc_analyzer.py --pdf DevDocs/public/messos.pdf --output-dir messos_results
