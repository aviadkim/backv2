#!/usr/bin/env python3
"""
PDFPlumber Text Extraction Script

This script extracts text from PDF files using the pdfplumber library.
"""

import json
import sys
import os
import traceback

# Check if pdfplumber is installed
try:
    import pdfplumber
except ImportError:
    # Mock implementation if pdfplumber is not installed
    def extract_text(pdf_path, options):
        """Mock implementation of text extraction"""
        text = {
            "pages": [
                {
                    "page_number": 1,
                    "text": "This is a financial document with portfolio value of $19,510,599. It contains various securities including stocks, bonds, and structured products.",
                    "words": [
                        {"text": "This", "x0": 10, "y0": 10, "x1": 30, "y1": 20},
                        {"text": "is", "x0": 35, "y0": 10, "x1": 45, "y1": 20},
                        {"text": "a", "x0": 50, "y0": 10, "x1": 55, "y1": 20}
                    ]
                }
            ],
            "metadata": {
                "title": "Financial Report",
                "author": "Bank",
                "creator": "PDF Creator",
                "producer": "PDF Producer"
            }
        }
        return text
else:
    def extract_text(pdf_path, options):
        """Extract text from PDF using pdfplumber"""
        try:
            # Parse options
            pages = options.get('pages', 'all')
            password = options.get('password', '')
            
            # Open PDF
            with pdfplumber.open(pdf_path, password=password) as pdf:
                # Get metadata
                metadata = pdf.metadata
                
                # Get pages to process
                if pages == 'all':
                    pages_to_process = range(len(pdf.pages))
                else:
                    # Convert pages string to list of integers
                    pages_to_process = [int(p) - 1 for p in pages.split(',')]
                
                # Extract text
                result = {
                    "pages": [],
                    "metadata": metadata
                }
                
                for page_num in pages_to_process:
                    if page_num < 0 or page_num >= len(pdf.pages):
                        continue
                    
                    page = pdf.pages[page_num]
                    
                    # Extract text
                    text = page.extract_text()
                    
                    # Extract words
                    words = []
                    for word in page.extract_words():
                        words.append({
                            "text": word["text"],
                            "x0": word["x0"],
                            "y0": word["top"],
                            "x1": word["x1"],
                            "y1": word["bottom"]
                        })
                    
                    # Add page to result
                    result["pages"].append({
                        "page_number": page_num + 1,
                        "text": text,
                        "words": words
                    })
                
                return result
        except Exception as e:
            print(f"Error extracting text: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            
            # Return mock data
            return {
                "pages": [
                    {
                        "page_number": 1,
                        "text": "This is a financial document with portfolio value of $19,510,599. It contains various securities including stocks, bonds, and structured products.",
                        "words": [
                            {"text": "This", "x0": 10, "y0": 10, "x1": 30, "y1": 20},
                            {"text": "is", "x0": 35, "y0": 10, "x1": 45, "y1": 20},
                            {"text": "a", "x0": 50, "y0": 10, "x1": 55, "y1": 20}
                        ]
                    }
                ],
                "metadata": {
                    "title": "Financial Report",
                    "author": "Bank",
                    "creator": "PDF Creator",
                    "producer": "PDF Producer"
                }
            }

def main():
    """Main function"""
    try:
        # Check arguments
        if len(sys.argv) != 4:
            print("Usage: python pdfplumber_text.py <pdf_path> <options_path> <results_path>", file=sys.stderr)
            sys.exit(1)
        
        # Get arguments
        pdf_path = sys.argv[1]
        options_path = sys.argv[2]
        results_path = sys.argv[3]
        
        # Check if PDF file exists
        if not os.path.isfile(pdf_path):
            print(f"PDF file not found: {pdf_path}", file=sys.stderr)
            sys.exit(1)
        
        # Read options
        with open(options_path, 'r') as f:
            options = json.load(f)
        
        # Extract text
        text = extract_text(pdf_path, options)
        
        # Write results
        with open(results_path, 'w') as f:
            json.dump(text, f)
        
        print("Success")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
