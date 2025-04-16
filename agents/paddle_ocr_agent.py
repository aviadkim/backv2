"""
PaddleOCR Agent - Uses PaddleOCR for high-accuracy text and table extraction.
"""
import os
import sys
import json
import numpy as np
import cv2
from PIL import Image
from pdf2image import convert_from_path
import pdfplumber
import tempfile
import subprocess
import importlib.util

class PaddleOCRAgent:
    """Agent that uses PaddleOCR for high-accuracy text and table extraction."""
    
    def __init__(self):
        self.text_by_page = {}
        self.tables_by_page = {}
        self.images_by_page = {}
        self.paddle_ocr = None
        self.paddle_structure = None
        self.is_paddle_available = self._check_paddle_availability()
    
    def _check_paddle_availability(self):
        """Check if PaddleOCR is available."""
        try:
            # Check if paddleocr is installed
            if importlib.util.find_spec("paddleocr") is None:
                print("PaddleOCR is not installed. Attempting to install...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "paddleocr"])
                print("PaddleOCR installed successfully.")
            
            # Import PaddleOCR
            from paddleocr import PaddleOCR, PPStructure
            self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')
            self.paddle_structure = PPStructure(table=True, ocr=True, show_log=False)
            print("PaddleOCR initialized successfully.")
            return True
        except Exception as e:
            print(f"Error initializing PaddleOCR: {str(e)}")
            print("Will fall back to other OCR methods.")
            return False
    
    def process(self, pdf_path):
        """Process a PDF document using PaddleOCR."""
        print("PaddleOCR Agent: Extracting text and tables...")
        
        # Create output directory
        output_dir = 'agent_results'
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert PDF to images
        self._convert_pdf_to_images(pdf_path)
        
        # Process images with PaddleOCR
        if self.is_paddle_available:
            self._process_with_paddle_ocr()
        else:
            print("PaddleOCR is not available. Falling back to pdfplumber.")
            self._extract_text_with_pdfplumber(pdf_path)
        
        # Save results
        ocr_results = {
            'text_by_page': self.text_by_page,
            'tables_by_page': self.tables_by_page,
            'num_pages': len(self.images_by_page)
        }
        
        with open(os.path.join(output_dir, 'paddle_ocr_results.json'), 'w', encoding='utf-8') as f:
            # Convert non-serializable objects to strings
            serializable_results = {
                'text_by_page': self.text_by_page,
                'num_pages': len(self.images_by_page),
                'tables_found': sum(len(tables) for tables in self.tables_by_page.values())
            }
            json.dump(serializable_results, f, indent=2)
        
        print(f"PaddleOCR Agent: Extracted text from {len(self.images_by_page)} pages")
        print(f"PaddleOCR Agent: Found {sum(len(tables) for tables in self.tables_by_page.values())} tables")
        
        return ocr_results
    
    def _convert_pdf_to_images(self, pdf_path):
        """Convert PDF to images."""
        try:
            print("Converting PDF to images...")
            pages = convert_from_path(pdf_path)
            
            for i, page in enumerate(pages, 1):
                self.images_by_page[i] = page
                
                # Save image for processing
                output_dir = 'agent_results/images'
                os.makedirs(output_dir, exist_ok=True)
                page_path = os.path.join(output_dir, f'page_{i}.png')
                page.save(page_path)
        except Exception as e:
            print(f"Error converting PDF to images: {str(e)}")
            
            # Fallback to pdfplumber for page count
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    print(f"Using pdfplumber fallback. Document has {len(pdf.pages)} pages.")
            except Exception as e2:
                print(f"Error with pdfplumber fallback: {str(e2)}")
    
    def _process_with_paddle_ocr(self):
        """Process images with PaddleOCR."""
        from paddleocr import PaddleOCR, PPStructure
        
        # Initialize PaddleOCR if not already initialized
        if self.paddle_ocr is None:
            self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')
        
        # Initialize PPStructure if not already initialized
        if self.paddle_structure is None:
            self.paddle_structure = PPStructure(table=True, ocr=True, show_log=False)
        
        # Process each page
        for page_num, image in self.images_by_page.items():
            print(f"Processing page {page_num} with PaddleOCR...")
            
            # Get image path
            image_path = os.path.join('agent_results/images', f'page_{page_num}.png')
            
            # Extract text with PaddleOCR
            try:
                result = self.paddle_ocr.ocr(image_path, cls=True)
                
                # Extract text
                text = ""
                for line in result:
                    for word_info in line:
                        text += word_info[1][0] + " "
                    text += "\n"
                
                self.text_by_page[page_num] = text
            except Exception as e:
                print(f"Error extracting text with PaddleOCR: {str(e)}")
                self.text_by_page[page_num] = ""
            
            # Extract tables with PPStructure
            try:
                result = self.paddle_structure(image_path)
                
                # Extract tables
                tables = []
                for res in result:
                    if res['type'] == 'table':
                        tables.append(res['res'])
                
                self.tables_by_page[page_num] = tables
            except Exception as e:
                print(f"Error extracting tables with PPStructure: {str(e)}")
                self.tables_by_page[page_num] = []
    
    def _extract_text_with_pdfplumber(self, pdf_path):
        """Extract text using pdfplumber as fallback."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text
                    text = page.extract_text() or ""
                    self.text_by_page[page_num] = text
                    
                    # Extract tables
                    tables = page.extract_tables()
                    self.tables_by_page[page_num] = tables
        except Exception as e:
            print(f"Error extracting text with pdfplumber: {str(e)}")
    
    def get_full_text(self):
        """Get the full text of the document."""
        full_text = ""
        for page_num in sorted(self.text_by_page.keys()):
            full_text += self.text_by_page[page_num] + "\n\n"
        return full_text
    
    def get_tables(self):
        """Get all tables from the document."""
        return self.tables_by_page

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python paddle_ocr_agent.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    agent = PaddleOCRAgent()
    agent.process(pdf_path)
