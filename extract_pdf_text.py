"""
Simple script to extract text from a PDF file.
"""
import sys
import PyPDF2
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF."""
    print(f"Extracting text from PDF: {pdf_path}")
    try:
        # Open the PDF file
        with open(pdf_path, 'rb') as file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Get the number of pages
            num_pages = len(pdf_reader.pages)
            print(f"PDF has {num_pages} pages")
            
            # Extract text from each page
            all_text = ""
            for page_num in range(num_pages):
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    print(f"Page {page_num+1}: {len(text)} characters")
                    all_text += text + "\n\n"
                except Exception as e:
                    print(f"Error extracting text from page {page_num+1}: {e}")
            
            # Save the extracted text
            output_path = Path(pdf_path).with_suffix('.txt')
            with open(output_path, 'w', encoding='utf-8') as out_file:
                out_file.write(all_text)
            print(f"Saved extracted text to {output_path}")
            
            return all_text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf_text.py <pdf_file>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    extract_text_from_pdf(pdf_path)
