
import os
import sys
import json
import pytesseract
from pdf2image import convert_from_path
import camelot
import cv2
import numpy as np
import pandas as pd
from PIL import Image

def process_pdf(pdf_path, output_dir):
    """Process a PDF file and extract text, tables, and perform OCR."""
    print(f"Processing PDF: {pdf_path}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract text using PyPDF2
    text_output = os.path.join(output_dir, "extracted_text.txt")
    tables_output = os.path.join(output_dir, "extracted_tables.json")
    ocr_output = os.path.join(output_dir, "ocr_text.txt")
    
    # Convert PDF to images for OCR
    print("Converting PDF to images...")
    images = convert_from_path(pdf_path)
    
    # Perform OCR on each page
    print("Performing OCR...")
    ocr_text = ""
    for i, image in enumerate(images):
        page_text = pytesseract.image_to_string(image, lang='eng+heb')
        ocr_text += f"\n\n--- PAGE {i+1} ---\n\n{page_text}"
    
    # Save OCR text
    with open(ocr_output, "w", encoding="utf-8") as f:
        f.write(ocr_text)
    
    # Extract tables using Camelot
    print("Extracting tables...")
    try:
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
        print(f"Found {len(tables)} tables")
        
        # Convert tables to JSON
        tables_data = []
        for i, table in enumerate(tables):
            df = table.df
            tables_data.append({
                "table_number": i+1,
                "page": table.page,
                "headers": df.iloc[0].tolist(),
                "data": df.iloc[1:].values.tolist()
            })
        
        # Save tables data
        with open(tables_output, "w", encoding="utf-8") as f:
            json.dump(tables_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error extracting tables: {e}")
        tables_data = []
    
    # Combine all extracted data
    result = {
        "ocr_text": ocr_text,
        "tables": tables_data
    }
    
    # Save combined result
    combined_output = os.path.join(output_dir, "combined_result.json")
    with open(combined_output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Processing complete. Results saved to {output_dir}")
    return result

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process_pdf.py <pdf_path> <output_dir>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    process_pdf(pdf_path, output_dir)
  