#!/usr/bin/env python
"""
Command-line interface for the RAG Multimodal Financial Document Processor.
"""

import os
import sys
import argparse
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """
    Main function to run the script from the command line.
    """
    parser = argparse.ArgumentParser(description='Process a financial document')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('--output-dir', help='Directory to save output files')
    parser.add_argument('--languages', help='Languages for OCR (comma-separated)', default='eng,heb')
    parser.add_argument('--api-key', help='API key for AI services')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set API key in environment if provided
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key
    
    # Import the document processor
    try:
        from rag_multimodal_processor import DocumentProcessor, get_config
    except ImportError:
        print("Error: Could not import DocumentProcessor. Make sure the package is installed.")
        sys.exit(1)
    
    # Parse languages
    languages = args.languages.split(',')
    
    # Create custom configuration
    config = {
        "ocr": {
            "languages": languages
        }
    }
    
    # Process document
    try:
        processor = DocumentProcessor(config)
        result = processor.process(args.pdf_path, args.output_dir)
        
        # Print summary
        print("\nProcessing Summary:")
        print(f"Document: {result['document_info']['document_name']}")
        print(f"Total Value: {result['portfolio']['total_value']} {result['portfolio']['currency']}")
        print(f"Securities: {result['metrics']['total_securities']}")
        print(f"Asset Classes: {result['metrics']['total_asset_classes']}")
        
        # Print accuracy
        if "accuracy" in result:
            accuracy = result["accuracy"]
            print("\nAccuracy Metrics:")
            for key, value in accuracy.items():
                print(f"{key}: {value * 100:.2f}%")
        
        print(f"\nProcessing Time: {result['document_info']['processing_time']:.2f} seconds")
        print(f"Output saved to: {args.output_dir or os.path.join(os.path.dirname(args.pdf_path), 'output')}")
        
        sys.exit(0)
    except Exception as e:
        print(f"Error processing document: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
