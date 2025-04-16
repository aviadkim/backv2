"""
Test script for OCRmyPDF integration.
"""
import os
import sys
import argparse
import subprocess
import tempfile
from pathlib import Path

# Try to import OCRProcessor, but provide a fallback if it fails
try:
    from DevDocs.backend.utils.ocr_processor import OCRProcessor
    HAS_OCRMYPDF = True
except (ImportError, ModuleNotFoundError):
    print("Warning: OCRmyPDF not installed or not found. Using fallback method.")
    HAS_OCRMYPDF = False

def main():
    """
    Main function to test OCRmyPDF integration.
    """
    parser = argparse.ArgumentParser(description="Test OCRmyPDF integration")
    parser.add_argument("pdf_path", help="Path to the PDF file to process")
    parser.add_argument("--output", help="Path to save the processed PDF file")
    parser.add_argument("--financial", action="store_true", help="Use financial document optimizations")
    parser.add_argument("--language", default="eng+heb", help="Language(s) to use for OCR")

    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found: {args.pdf_path}")
        return 1

    print(f"Processing PDF: {args.pdf_path}")
    print(f"Using financial optimizations: {args.financial}")
    print(f"Language: {args.language}")

    try:
        if HAS_OCRMYPDF:
            # Use OCRProcessor if available
            if args.financial:
                output_path = OCRProcessor.process_financial_pdf(args.pdf_path, args.output)
            else:
                output_path = OCRProcessor.process_pdf(
                    args.pdf_path,
                    args.output,
                    language=args.language,
                    deskew=True,
                    clean=True
                )

            print(f"PDF processed successfully. Output saved to: {output_path}")

            # Extract and print some text from the processed PDF
            text = OCRProcessor.extract_text_from_pdf(output_path)
            print("\nExtracted text sample:")
            print(text[:500] + "..." if len(text) > 500 else text)
        else:
            # Fallback: Use pdfminer.six directly
            try:
                from pdfminer.high_level import extract_text
            except ImportError:
                print("Error: pdfminer.six not installed. Please install it with: pip install pdfminer.six")
                return 1

            # Just extract text from the original PDF
            text = extract_text(args.pdf_path)
            print("\nExtracted text sample (using pdfminer.six):")
            print(text[:500] + "..." if len(text) > 500 else text)

            # Copy the PDF to the output path if specified
            if args.output:
                import shutil
                shutil.copy2(args.pdf_path, args.output)
                print(f"PDF copied to: {args.output}")
                output_path = args.output
            else:
                output_path = args.pdf_path

    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
