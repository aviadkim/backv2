"""
Script to extract text from a PDF file using pdfminer.six.
"""
import sys
import io
from pathlib import Path
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdfminer.six."""
    print(f"Extracting text from PDF: {pdf_path}")
    try:
        # Create an output buffer
        output_buffer = io.StringIO()
        
        # Extract text from the PDF
        with open(pdf_path, 'rb') as file:
            extract_text_to_fp(file, output_buffer, laparams=LAParams(), 
                               output_type='text', codec='utf-8')
        
        # Get the extracted text
        text = output_buffer.getvalue()
        
        # Save the extracted text
        output_path = Path(pdf_path).with_suffix('.txt')
        with open(output_path, 'w', encoding='utf-8') as out_file:
            out_file.write(text)
        print(f"Saved extracted text to {output_path}")
        
        # Print a sample of the text
        print("\nSample of extracted text:")
        print(text[:500] + "..." if len(text) > 500 else text)
        
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf_text_pdfminer.py <pdf_file>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    extract_text_from_pdf(pdf_path)
