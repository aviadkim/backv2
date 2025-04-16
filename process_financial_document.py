"""
Financial Document Processing System - Main Orchestrator.

This script orchestrates multiple specialized agents to extract and understand
financial documents with high accuracy.
"""
import os
import sys
import argparse
import json
import time
import shutil
from agents.document_structure_agent import DocumentStructureAgent
from agents.financial_value_agent import FinancialValueAgent
from agents.securities_agent import SecuritiesAgent
from agents.validation_agent import ValidationAgent
from agents.report_agent import ReportAgent
from agents.bank_report_agent import BankReportAgent
from agents.enhanced_ocr_agent import EnhancedOCRAgent
from agents.paddle_ocr_agent import PaddleOCRAgent
from agents.enhanced_tesseract_agent import EnhancedTesseractAgent
from github_ocr_fallback import GitHubOCRFallback

def process_document(pdf_path, output_dir='agent_results', open_report=True, use_github_fallback=False, paddle_only=False, tesseract_only=False):
    """
    Process a financial document using multiple specialized agents.

    Args:
        pdf_path: Path to the PDF document
        output_dir: Directory to save results
        open_report: Whether to open the report in a browser
        use_github_fallback: Whether to use GitHub OCR fallback if standard OCR fails

    Returns:
        Path to the generated report
    """
    print(f"Processing financial document: {pdf_path}")
    start_time = time.time()

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Step 0: Multi-Engine OCR
    print("\n=== Step 0: Multi-Engine OCR ===")
    ocr_results = None

    # Use the specified OCR engine or try all of them in sequence
    if paddle_only:
        # Use only PaddleOCR
        print("\n--- Using PaddleOCR Only ---")
        try:
            paddle_agent = PaddleOCRAgent()
            paddle_results = paddle_agent.process(pdf_path)
            if paddle_results and paddle_results.get('text_by_page'):
                print(f"PaddleOCR successful with {len(paddle_results['text_by_page'])} pages")
                ocr_results = paddle_results
        except Exception as e:
            print(f"Error during PaddleOCR: {str(e)}")

    elif tesseract_only:
        # Use only Enhanced Tesseract
        print("\n--- Using Enhanced Tesseract Only ---")
        try:
            tesseract_agent = EnhancedTesseractAgent()
            tesseract_results = tesseract_agent.process(pdf_path)
            if tesseract_results and tesseract_results.get('text_by_page'):
                print(f"Enhanced Tesseract successful with {len(tesseract_results['text_by_page'])} pages")
                ocr_results = tesseract_results
        except Exception as e:
            print(f"Error during Enhanced Tesseract: {str(e)}")

    else:
        # Try all OCR engines in sequence
        # Try PaddleOCR first (best for tables and complex layouts)
        print("\n--- Trying PaddleOCR ---")
        try:
            paddle_agent = PaddleOCRAgent()
            paddle_results = paddle_agent.process(pdf_path)
            if paddle_results and paddle_results.get('text_by_page'):
                print(f"PaddleOCR successful with {len(paddle_results['text_by_page'])} pages")
                ocr_results = paddle_results
        except Exception as e:
            print(f"Error during PaddleOCR: {str(e)}")

        # If PaddleOCR failed, try Enhanced Tesseract
        if not ocr_results:
            print("\n--- Trying Enhanced Tesseract ---")
            try:
                tesseract_agent = EnhancedTesseractAgent()
                tesseract_results = tesseract_agent.process(pdf_path)
                if tesseract_results and tesseract_results.get('text_by_page'):
                    print(f"Enhanced Tesseract successful with {len(tesseract_results['text_by_page'])} pages")
                    ocr_results = tesseract_results
            except Exception as e:
                print(f"Error during Enhanced Tesseract: {str(e)}")

        # If both failed, try standard OCR
        if not ocr_results:
            print("\n--- Trying Standard OCR ---")
            try:
                ocr_agent = EnhancedOCRAgent()
                standard_results = ocr_agent.process(pdf_path)
                if standard_results and standard_results.get('best_text_by_page'):
                    print(f"Standard OCR successful with {len(standard_results['best_text_by_page'])} pages")
                    ocr_results = {
                        'text_by_page': standard_results['best_text_by_page'],
                        'tables_by_page': {}
                    }
            except Exception as e:
                print(f"Error during standard OCR: {str(e)}")

    # If all OCR methods failed and GitHub fallback is enabled, try GitHub OCR tools
    if not ocr_results and use_github_fallback:
        print("\n--- Trying GitHub OCR Fallback ---")
        github_fallback = GitHubOCRFallback()
        github_results = github_fallback.process(pdf_path)

        if github_results and any(result.get('text') for result in github_results.values()):
            print("GitHub OCR fallback successful")
            # Convert GitHub results to OCR results format
            ocr_results = {
                'text_by_page': {1: next(result.get('text') for result in github_results.values() if result.get('text'))},
                'tables_by_page': {},
                'num_pages': 1
            }

    # Step 1: Document Structure Analysis
    print("\n=== Step 1: Document Structure Analysis ===")
    structure_agent = DocumentStructureAgent()
    document_structure = structure_agent.process(pdf_path)

    # Step 2: Financial Value Extraction
    print("\n=== Step 2: Financial Value Extraction ===")
    value_agent = FinancialValueAgent()
    financial_values = value_agent.process(pdf_path, document_structure)

    # Step 3: Securities Extraction
    print("\n=== Step 3: Securities Extraction ===")
    securities_agent = SecuritiesAgent()
    securities = securities_agent.process(pdf_path, document_structure, financial_values)

    # Step 4: Validation and Reconciliation
    print("\n=== Step 4: Validation and Reconciliation ===")
    validation_agent = ValidationAgent()
    validation_results = validation_agent.process(document_structure, financial_values, securities)

    # Step 5: Report Generation
    print("\n=== Step 5: Report Generation ===")
    # Generate standard report
    report_agent = ReportAgent()
    report_path = report_agent.process(document_structure, financial_values, securities, validation_results)

    # Generate bank-like report
    print("\n=== Step 6: Bank Report Generation ===")
    bank_report_agent = BankReportAgent()
    bank_report_path = bank_report_agent.process(document_structure, financial_values, securities, validation_results)

    # Return the bank report path for opening in browser
    report_path = bank_report_path

    # Calculate processing time
    end_time = time.time()
    processing_time = end_time - start_time

    print(f"\nDocument processing completed in {processing_time:.2f} seconds")
    print(f"Report generated: {report_path}")

    # Open report in browser if requested
    if open_report:
        try:
            import webbrowser
            report_url = f"file://{os.path.abspath(report_path)}"
            print(f"Opening report in browser: {report_url}")
            webbrowser.open(report_url)
        except Exception as e:
            print(f"Error opening report in browser: {str(e)}")

    return report_path

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Process a financial document using multiple specialized agents")
    parser.add_argument("pdf_path", help="Path to the PDF document")
    parser.add_argument("--output-dir", default="agent_results", help="Directory to save results")
    parser.add_argument("--no-open", action="store_true", help="Don't open the report in a browser")
    parser.add_argument("--github-fallback", action="store_true", help="Use GitHub OCR fallback if standard OCR fails")
    parser.add_argument("--qa-mode", action="store_true", help="Enable Q&A mode after processing")
    parser.add_argument("--paddle-only", action="store_true", help="Use only PaddleOCR for text extraction")
    parser.add_argument("--tesseract-only", action="store_true", help="Use only Enhanced Tesseract for text extraction")

    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found: {args.pdf_path}")
        return 1

    report_path = process_document(args.pdf_path, args.output_dir, not args.no_open, args.github_fallback, args.paddle_only, args.tesseract_only)

    # If Q&A mode is enabled, start the Q&A robot agent
    if args.qa_mode and report_path:
        try:
            from qa_robot_agent import QARobotAgent
            print("\n=== Starting Q&A Robot Agent ===")
            qa_agent = QARobotAgent()
            qa_agent.load_data(args.output_dir)
            qa_agent.start_interactive_session()
        except Exception as e:
            print(f"Error starting Q&A Robot Agent: {str(e)}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
