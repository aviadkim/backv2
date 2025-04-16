"""
Enhanced Tesseract Agent - Uses advanced Tesseract OCR techniques from GitHub.
"""
import os
import sys
import json
import re
import numpy as np
import cv2
from PIL import Image
from pdf2image import convert_from_path
import pdfplumber
import tempfile
import subprocess
import importlib.util

class EnhancedTesseractAgent:
    """Agent that uses enhanced Tesseract OCR techniques from GitHub."""
    
    def __init__(self):
        self.text_by_page = {}
        self.tables_by_page = {}
        self.images_by_page = {}
        self.is_tesseract_available = self._check_tesseract_availability()
        self.tesseract_config = r'--oem 3 --psm 6 -l eng+heb'
    
    def _check_tesseract_availability(self):
        """Check if Tesseract is available."""
        try:
            # Check if pytesseract is installed
            if importlib.util.find_spec("pytesseract") is None:
                print("pytesseract is not installed. Attempting to install...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pytesseract"])
                print("pytesseract installed successfully.")
            
            # Check if Tesseract is installed
            import pytesseract
            try:
                pytesseract.get_tesseract_version()
                print("Tesseract is installed and available.")
                return True
            except Exception:
                print("Tesseract is not installed or not in PATH.")
                print("Please install Tesseract from: https://github.com/tesseract-ocr/tesseract")
                return False
        except Exception as e:
            print(f"Error checking Tesseract availability: {str(e)}")
            return False
    
    def process(self, pdf_path):
        """Process a PDF document using enhanced Tesseract OCR."""
        print("Enhanced Tesseract Agent: Extracting text and tables...")
        
        # Create output directory
        output_dir = 'agent_results'
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert PDF to images
        self._convert_pdf_to_images(pdf_path)
        
        # Process images with Tesseract
        if self.is_tesseract_available:
            self._process_with_tesseract()
        else:
            print("Tesseract is not available. Falling back to pdfplumber.")
            self._extract_text_with_pdfplumber(pdf_path)
        
        # Save results
        ocr_results = {
            'text_by_page': self.text_by_page,
            'tables_by_page': self.tables_by_page,
            'num_pages': len(self.images_by_page)
        }
        
        with open(os.path.join(output_dir, 'enhanced_tesseract_results.json'), 'w', encoding='utf-8') as f:
            # Convert non-serializable objects to strings
            serializable_results = {
                'text_by_page': self.text_by_page,
                'num_pages': len(self.images_by_page),
                'tables_found': sum(len(tables) for tables in self.tables_by_page.values())
            }
            json.dump(serializable_results, f, indent=2)
        
        print(f"Enhanced Tesseract Agent: Extracted text from {len(self.images_by_page)} pages")
        print(f"Enhanced Tesseract Agent: Found {sum(len(tables) for tables in self.tables_by_page.values())} tables")
        
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
    
    def _preprocess_image(self, image_path, method='advanced'):
        """Preprocess image for better OCR results."""
        # Read image
        image = cv2.imread(image_path)
        
        if image is None:
            print(f"Error reading image: {image_path}")
            return None
        
        if method == 'basic':
            # Basic preprocessing
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            return thresh
        
        elif method == 'advanced':
            # Advanced preprocessing
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply bilateral filter to reduce noise while preserving edges
            filtered = cv2.bilateralFilter(gray, 9, 75, 75)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            equalized = clahe.apply(filtered)
            
            # Apply Otsu's thresholding
            _, thresh = cv2.threshold(equalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Noise removal
            kernel = np.ones((1, 1), np.uint8)
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            # Dilation to make text more prominent
            kernel = np.ones((1, 1), np.uint8)
            dilated = cv2.dilate(opening, kernel, iterations=1)
            
            return dilated
        
        elif method == 'financial':
            # Financial document specific preprocessing
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            equalized = clahe.apply(gray)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(equalized, (5, 5), 0)
            
            # Apply Otsu's thresholding
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Deskew the image
            coords = np.column_stack(np.where(thresh > 0))
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            
            # Rotate the image to deskew it
            (h, w) = thresh.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            
            return rotated
        
        else:
            return image
    
    def _process_with_tesseract(self):
        """Process images with enhanced Tesseract OCR."""
        import pytesseract
        
        # Process each page
        for page_num, image in self.images_by_page.items():
            print(f"Processing page {page_num} with Enhanced Tesseract...")
            
            # Get image path
            image_path = os.path.join('agent_results/images', f'page_{page_num}.png')
            
            # Preprocess image with different methods
            preprocessed_basic = self._preprocess_image(image_path, 'basic')
            preprocessed_advanced = self._preprocess_image(image_path, 'advanced')
            preprocessed_financial = self._preprocess_image(image_path, 'financial')
            
            # Save preprocessed images for debugging
            output_dir = 'agent_results/preprocessed'
            os.makedirs(output_dir, exist_ok=True)
            
            if preprocessed_basic is not None:
                cv2.imwrite(os.path.join(output_dir, f'page_{page_num}_basic.png'), preprocessed_basic)
            
            if preprocessed_advanced is not None:
                cv2.imwrite(os.path.join(output_dir, f'page_{page_num}_advanced.png'), preprocessed_advanced)
            
            if preprocessed_financial is not None:
                cv2.imwrite(os.path.join(output_dir, f'page_{page_num}_financial.png'), preprocessed_financial)
            
            # Extract text with Tesseract using different preprocessing methods
            text_basic = ""
            text_advanced = ""
            text_financial = ""
            
            try:
                if preprocessed_basic is not None:
                    text_basic = pytesseract.image_to_string(preprocessed_basic, config=self.tesseract_config)
            except Exception as e:
                print(f"Error extracting text with basic preprocessing: {str(e)}")
            
            try:
                if preprocessed_advanced is not None:
                    text_advanced = pytesseract.image_to_string(preprocessed_advanced, config=self.tesseract_config)
            except Exception as e:
                print(f"Error extracting text with advanced preprocessing: {str(e)}")
            
            try:
                if preprocessed_financial is not None:
                    text_financial = pytesseract.image_to_string(preprocessed_financial, config=self.tesseract_config)
            except Exception as e:
                print(f"Error extracting text with financial preprocessing: {str(e)}")
            
            # Choose the best text based on length and quality
            texts = [text_basic, text_advanced, text_financial]
            text_lengths = [len(text) for text in texts]
            
            if max(text_lengths) > 0:
                best_text = texts[text_lengths.index(max(text_lengths))]
            else:
                best_text = ""
            
            self.text_by_page[page_num] = best_text
            
            # Extract tables with Tesseract
            try:
                if preprocessed_financial is not None:
                    # Use image_to_data to get structured data
                    data = pytesseract.image_to_data(preprocessed_financial, config=self.tesseract_config, output_type=pytesseract.Output.DICT)
                    
                    # Identify potential tables based on text alignment
                    tables = self._identify_tables_from_tesseract_data(data)
                    self.tables_by_page[page_num] = tables
                else:
                    self.tables_by_page[page_num] = []
            except Exception as e:
                print(f"Error extracting tables with Tesseract: {str(e)}")
                self.tables_by_page[page_num] = []
    
    def _identify_tables_from_tesseract_data(self, data):
        """Identify tables from Tesseract data."""
        tables = []
        
        # Group text by lines
        lines = {}
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 60 and data['text'][i].strip():  # Filter by confidence and non-empty text
                line_num = data['block_num'][i] * 1000 + data['line_num'][i]
                if line_num not in lines:
                    lines[line_num] = []
                
                lines[line_num].append({
                    'text': data['text'][i],
                    'left': data['left'][i],
                    'top': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'conf': data['conf'][i]
                })
        
        # Sort lines by top position
        sorted_lines = sorted(lines.items(), key=lambda x: min(word['top'] for word in x[1]))
        
        # Identify potential tables based on consistent column alignment
        potential_table_lines = []
        current_table_lines = []
        
        for line_num, line_words in sorted_lines:
            # Sort words by left position
            sorted_words = sorted(line_words, key=lambda x: x['left'])
            
            # If this is the first line or if it aligns with the previous line, add it to the current table
            if not current_table_lines or self._lines_align(current_table_lines[-1], sorted_words):
                current_table_lines.append(sorted_words)
            else:
                # If we have at least 3 lines, consider it a table
                if len(current_table_lines) >= 3:
                    potential_table_lines.append(current_table_lines)
                
                # Start a new potential table
                current_table_lines = [sorted_words]
        
        # Add the last table if it has at least 3 lines
        if len(current_table_lines) >= 3:
            potential_table_lines.append(current_table_lines)
        
        # Convert potential table lines to structured tables
        for table_lines in potential_table_lines:
            table = self._convert_lines_to_table(table_lines)
            tables.append(table)
        
        return tables
    
    def _lines_align(self, line1, line2, tolerance=20):
        """Check if two lines align (have similar column positions)."""
        # If the lines have very different number of words, they probably don't align
        if abs(len(line1) - len(line2)) > 2:
            return False
        
        # Check if the words in the lines have similar left positions
        for i in range(min(len(line1), len(line2))):
            if abs(line1[i]['left'] - line2[i]['left']) > tolerance:
                return False
        
        return True
    
    def _convert_lines_to_table(self, table_lines):
        """Convert lines of words to a structured table."""
        # Determine the number of columns based on the maximum number of words in any line
        num_columns = max(len(line) for line in table_lines)
        
        # Create the table
        table = []
        
        for line in table_lines:
            row = []
            for i in range(num_columns):
                if i < len(line):
                    row.append(line[i]['text'])
                else:
                    row.append("")
            
            table.append(row)
        
        return table
    
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
        print("Usage: python enhanced_tesseract_agent.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    agent = EnhancedTesseractAgent()
    agent.process(pdf_path)
