#!/usr/bin/env python
"""
Run Processor Script

This script provides a command-line interface to run the document processor.
It handles the imports correctly to avoid relative import issues.
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, Any, List, Optional

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to run the script from the command line.
    """
    parser = argparse.ArgumentParser(description='Process a financial document')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('output_dir', help='Directory to save output files')
    parser.add_argument('--languages', help='Languages for OCR (comma-separated)', default='eng,heb')
    parser.add_argument('--api-key', help='API key for AI services')
    
    args = parser.parse_args()
    
    # Parse languages
    languages = args.languages.split(',')
    
    # Get API key from environment if not provided
    api_key = args.api_key or os.environ.get('GOOGLE_API_KEY') or os.environ.get('OPENAI_API_KEY')
    
    # Import the document processor
    try:
        from document_processor_impl import DocumentProcessor
        
        # Create processor
        processor = DocumentProcessor(api_key=api_key)
        
        # Process document
        result = processor.process(args.pdf_path, args.output_dir, languages)
        
        # Print summary
        print(f"Processing complete, extracted {len(result.get('portfolio', {}).get('securities', []))} securities")
        print(f"Total value: {result.get('portfolio', {}).get('total_value')} {result.get('portfolio', {}).get('currency')}")
        
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
