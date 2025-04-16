"""
Test script for financial document processing agents.
"""
import os
import sys
import argparse
import json
from DevDocs.backend.agents.document_preprocessor_agent import DocumentPreprocessorAgent
from DevDocs.backend.agents.hebrew_ocr_agent import HebrewOCRAgent

def test_document_preprocessor(pdf_path, output_dir=None, financial=True):
    """
    Test the DocumentPreprocessorAgent with a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the output files
        financial: Whether to use financial document optimizations
        
    Returns:
        Result dictionary
    """
    print(f"\n=== Testing DocumentPreprocessorAgent with {pdf_path} ===")
    
    # Create output path if specified
    output_path = None
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "preprocessed_" + os.path.basename(pdf_path))
    
    # Create and run the agent
    agent = DocumentPreprocessorAgent()
    result = agent.process({
        'pdf_path': pdf_path,
        'output_path': output_path,
        'options': {
            'financial_doc': financial,
            'language': 'eng+heb',
            'enhance_contrast': True,
            'fix_skew': True,
            'remove_noise': True
        }
    })
    
    # Print the result
    if result['status'] == 'success':
        print(f"Document preprocessed successfully")
        print(f"Output saved to: {result.get('processed_pdf_path', 'N/A')}")
        
        # Print a sample of the extracted text
        text = result.get('text', '')
        if text:
            print("\nExtracted text sample:")
            print(text[:500] + "..." if len(text) > 500 else text)
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")
    
    return result

def test_hebrew_ocr(pdf_path, output_dir=None, financial=True):
    """
    Test the HebrewOCRAgent with a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the output files
        financial: Whether to use financial document optimizations
        
    Returns:
        Result dictionary
    """
    print(f"\n=== Testing HebrewOCRAgent with {pdf_path} ===")
    
    # Create output path if specified
    output_path = None
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "ocr_" + os.path.basename(pdf_path))
    
    # Create and run the agent
    agent = HebrewOCRAgent()
    result = agent.process({
        'pdf_path': pdf_path,
        'output_path': output_path,
        'with_positions': False,
        'language': 'eng+heb',
        'financial_doc': financial
    })
    
    # Print the result
    if result['status'] == 'success':
        print(f"OCR completed successfully")
        print(f"Output saved to: {result.get('processed_pdf_path', 'N/A')}")
        
        # Print a sample of the extracted text
        text = result.get('text', '')
        if text:
            print("\nExtracted text sample:")
            print(text[:500] + "..." if len(text) > 500 else text)
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")
    
    return result

def main():
    """
    Main function to test financial document processing agents.
    """
    parser = argparse.ArgumentParser(description="Test financial document processing agents")
    parser.add_argument("pdf_path", help="Path to the PDF file to process")
    parser.add_argument("--output-dir", help="Directory to save the output files")
    parser.add_argument("--agent", choices=["preprocessor", "ocr", "all"], default="all", 
                        help="Which agent to test (default: all)")
    parser.add_argument("--no-financial", action="store_true", 
                        help="Disable financial document optimizations")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found: {args.pdf_path}")
        return 1
    
    financial = not args.no_financial
    
    results = {}
    
    # Test the specified agents
    if args.agent in ["preprocessor", "all"]:
        results["preprocessor"] = test_document_preprocessor(args.pdf_path, args.output_dir, financial)
    
    if args.agent in ["ocr", "all"]:
        results["ocr"] = test_hebrew_ocr(args.pdf_path, args.output_dir, financial)
    
    # Save the results to a JSON file if output directory is specified
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        results_path = os.path.join(args.output_dir, "agent_results.json")
        
        # Convert any non-serializable objects to strings
        serializable_results = {}
        for agent, result in results.items():
            serializable_results[agent] = {}
            for key, value in result.items():
                if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    serializable_results[agent][key] = value
                else:
                    serializable_results[agent][key] = str(value)
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {results_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
