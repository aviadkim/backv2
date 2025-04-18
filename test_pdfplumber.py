#!/usr/bin/env python
"""
Test script for extracting text and tables from a PDF using pdfplumber.
"""

import os
import sys
import argparse
import json
import re
import pdfplumber
from typing import List, Dict, Any

def extract_text(pdf_path: str) -> str:
    """
    Extract text from a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text
    """
    print(f"Extracting text from {pdf_path}")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text_parts = []
            
            for i, page in enumerate(pdf.pages):
                print(f"Processing page {i+1}/{len(pdf.pages)}")
                text = page.extract_text() or ""
                text_parts.append(text)
            
            return "\n\n".join(text_parts)
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def extract_tables(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract tables from a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of tables
    """
    print(f"Extracting tables from {pdf_path}")
    
    tables = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                print(f"Processing page {i+1}/{len(pdf.pages)}")
                
                page_tables = page.extract_tables()
                
                for j, table_data in enumerate(page_tables):
                    if not table_data or len(table_data) <= 1:
                        continue
                    
                    # Convert to pandas DataFrame format
                    headers = table_data[0]
                    rows = table_data[1:]
                    
                    # Create table dictionary
                    table = {
                        "id": f"table_{i+1}_{j+1}",
                        "page": i + 1,
                        "headers": headers,
                        "rows": rows,
                        "data": [dict(zip(headers, row)) for row in rows]
                    }
                    
                    tables.append(table)
        
        return tables
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return []

def extract_isins(text: str) -> List[str]:
    """
    Extract ISINs from text.
    
    Args:
        text: Text to extract ISINs from
        
    Returns:
        List of ISINs
    """
    print("Extracting ISINs from text")
    
    isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
    isins = re.findall(isin_pattern, text)
    
    return list(set(isins))

def main():
    """
    Main function to run the script from the command line.
    """
    parser = argparse.ArgumentParser(description='Extract text and tables from a PDF')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('--output-dir', help='Output directory')
    
    args = parser.parse_args()
    
    # Set output directory
    output_dir = args.output_dir
    if not output_dir:
        output_dir = os.path.dirname(args.pdf_path)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract text
    text = extract_text(args.pdf_path)
    
    # Save text
    text_path = os.path.join(output_dir, f"{os.path.basename(args.pdf_path).split('.')[0]}_text.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"Text saved to {text_path}")
    
    # Extract tables
    tables = extract_tables(args.pdf_path)
    
    # Save tables
    tables_path = os.path.join(output_dir, f"{os.path.basename(args.pdf_path).split('.')[0]}_tables.json")
    with open(tables_path, "w", encoding="utf-8") as f:
        json.dump(tables, f, indent=2, ensure_ascii=False)
    
    print(f"Tables saved to {tables_path}")
    
    # Extract ISINs
    isins = extract_isins(text)
    
    # Save ISINs
    isins_path = os.path.join(output_dir, f"{os.path.basename(args.pdf_path).split('.')[0]}_isins.json")
    with open(isins_path, "w", encoding="utf-8") as f:
        json.dump(isins, f, indent=2, ensure_ascii=False)
    
    print(f"Found {len(isins)} ISINs, saved to {isins_path}")
    
    # Print summary
    print("\nSummary:")
    print(f"Text length: {len(text)} characters")
    print(f"Tables: {len(tables)}")
    print(f"ISINs: {len(isins)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
