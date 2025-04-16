#!/usr/bin/env python
"""
Command-line interface for the Financial Document Analysis System.
"""
import os
import sys
import argparse
from financial_document_analysis_system import FinancialDocumentAnalysisSystem

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Analyze financial documents.")
    parser.add_argument("file_path", help="Path to the financial document")
    parser.add_argument("--api-key", help="API key for AI services")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model to use for AI processing")
    parser.add_argument("--output-dir", help="Directory to save output files")
    parser.add_argument("--no-zerox", action="store_true", help="Disable ZeroX processing")
    parser.add_argument("--question", help="Question to answer (if provided, skips interactive mode)")
    parser.add_argument("--report", action="store_true", help="Generate a report")
    
    args = parser.parse_args()
    
    # Check if the file exists
    if not os.path.exists(args.file_path):
        print(f"Error: File not found: {args.file_path}")
        return 1
    
    # Create the system
    system = FinancialDocumentAnalysisSystem(api_key=args.api_key, model=args.model)
    
    # Process the document
    print(f"Processing document: {args.file_path}")
    system.process_document(args.file_path, output_dir=args.output_dir, use_zerox=not args.no_zerox)
    
    # Generate a report if requested
    if args.report:
        report_path = system.generate_report(output_dir=args.output_dir)
        if report_path:
            print(f"Report generated: {report_path}")
            # Open the report in the default browser
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(report_path)}")
    
    # Answer a specific question if provided
    if args.question:
        answer = system.answer_question(args.question)
        print(f"\nQuestion: {args.question}")
        print(f"Answer: {answer}\n")
    # Otherwise, start interactive session
    else:
        system.start_interactive_session()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
