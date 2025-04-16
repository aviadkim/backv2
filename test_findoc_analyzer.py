"""
Test script for FinDoc Analyzer v1.0

This script tests the functionality of the FinDoc Analyzer v1.0 solution.
"""
import os
import sys
import json
import argparse
from backend.processors.multi_document_processor import MultiDocumentProcessor
from backend.processors.holdings_extractor import HoldingsExtractor

def test_document_processing(pdf_path, api_key=None, output_dir="test_output"):
    """
    Test document processing functionality.
    
    Args:
        pdf_path: Path to the PDF file to test
        api_key: OpenRouter API key
        output_dir: Output directory
    """
    print(f"Testing document processing with {pdf_path}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create document processor
    processor = MultiDocumentProcessor(output_dir=output_dir, api_key=api_key)
    
    # Add and process the document
    document_id = processor.add_document(pdf_path)
    result = processor.get_document_data(document_id)
    
    # Print basic information
    print(f"Client: {result.get('client_info', {})}")
    print(f"Document date: {result.get('document_date')}")
    print(f"Portfolio value: {result.get('portfolio_value')}")
    
    # Extract bonds
    bonds = result.get("bonds", [])
    print(f"Extracted {len(bonds)} securities")
    
    # Extract comprehensive holdings information
    holdings_extractor = HoldingsExtractor(output_dir=output_dir)
    text = json.dumps(result)  # Convert result to text for extraction
    top_holdings = holdings_extractor.extract_comprehensive_holdings(text, document_id)
    
    # Print top holdings
    print("\nTop Holdings:")
    print("-" * 80)
    print(f"{'ISIN':<15} {'Description':<40} {'Value':>15} {'Percentage':>10}")
    print("-" * 80)
    
    for holding in top_holdings:
        isin = holding.get("isin", "N/A")
        description = holding.get("description", "Unknown")
        valuation = holding.get("valuation", 0)
        percentage = holding.get("percentage", 0)
        
        print(f"{isin:<15} {description[:40]:<40} {valuation:>15,.2f} {percentage:>10.2f}%")
    
    # Print asset allocation
    asset_allocation = result.get("asset_allocation", {})
    print("\nAsset Allocation:")
    print("-" * 80)
    print(f"{'Asset Class':<40} {'Value':>15} {'Percentage':>10}")
    print("-" * 80)
    
    for asset_class, data in asset_allocation.items():
        value = data.get("value", 0) if isinstance(data, dict) else 0
        percentage = data.get("percentage", 0) if isinstance(data, dict) else data
        
        print(f"{asset_class:<40} {value:>15,.2f} {percentage:>10.2f}%")
    
    print("\nTest completed successfully!")
    return result

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test FinDoc Analyzer v1.0")
    parser.add_argument("--pdf", required=True, help="Path to the PDF file to test")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--output-dir", default="test_output", help="Output directory")
    args = parser.parse_args()
    
    # Get API key from environment variable if not provided
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    
    # Run the test
    test_document_processing(args.pdf, api_key, args.output_dir)

if __name__ == "__main__":
    main()
