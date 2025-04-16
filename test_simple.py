"""
Simple test script for PDF extraction.
"""
import os
import sys
import argparse

def test_extraction(pdf_path, output_dir=None):
    """Test PDF extraction with pdfplumber."""
    print(f"Testing PDF extraction on {pdf_path}...")
    
    try:
        import pdfplumber
        print("pdfplumber is installed")
    except ImportError:
        print("pdfplumber is not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber"])
        import pdfplumber
    
    # Create output directory
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Extract text from PDF
    with pdfplumber.open(pdf_path) as pdf:
        print(f"PDF has {len(pdf.pages)} pages")
        
        # Extract text from first page
        first_page = pdf.pages[0]
        text = first_page.extract_text()
        print(f"First page text (excerpt): {text[:200]}...")
        
        # Extract tables from first page
        tables = first_page.extract_tables()
        print(f"First page has {len(tables)} tables")
        
        # Save results
        if output_dir:
            with open(os.path.join(output_dir, "first_page.txt"), "w", encoding="utf-8") as f:
                f.write(text)
            
            if tables:
                with open(os.path.join(output_dir, "first_page_tables.txt"), "w", encoding="utf-8") as f:
                    for i, table in enumerate(tables):
                        f.write(f"Table {i+1}:\n")
                        for row in table:
                            f.write(str(row) + "\n")
                        f.write("\n")
    
    print("Extraction completed successfully")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test PDF extraction")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output-dir", help="Directory to save extracted data")
    
    args = parser.parse_args()
    
    test_extraction(args.pdf_path, args.output_dir)

if __name__ == "__main__":
    main()
