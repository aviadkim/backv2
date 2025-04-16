"""
Enhanced OCR Agent - Uses multiple OCR engines to extract text with high accuracy.
"""
import os
import sys
import re
import json
import numpy as np
import cv2
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import pdfplumber
from collections import defaultdict
import difflib

class EnhancedOCRAgent:
    """Agent that uses multiple OCR engines to extract text with high accuracy."""
    
    def __init__(self):
        self.text_by_page = {}
        self.images_by_page = {}
        self.best_text_by_page = {}
        self.confidence_scores = {}
        self.tesseract_config = r'--oem 3 --psm 6 -l eng+heb'
    
    def process(self, pdf_path):
        """Process a PDF document to extract text with high accuracy."""
        print("Enhanced OCR Agent: Extracting text with multiple engines...")
        
        # Create output directory
        output_dir = 'agent_results'
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert PDF to images
        self._convert_pdf_to_images(pdf_path)
        
        # Extract text with multiple engines
        self._extract_text_with_multiple_engines(pdf_path)
        
        # Vote on best text
        self._vote_on_best_text()
        
        # Save results
        ocr_results = {
            'best_text_by_page': self.best_text_by_page,
            'confidence_scores': self.confidence_scores,
            'num_pages': len(self.images_by_page)
        }
        
        with open(os.path.join(output_dir, 'ocr_results.json'), 'w', encoding='utf-8') as f:
            # Convert non-serializable objects to strings
            serializable_results = {
                'best_text_by_page': self.best_text_by_page,
                'confidence_scores': self.confidence_scores,
                'num_pages': len(self.images_by_page)
            }
            json.dump(serializable_results, f, indent=2)
        
        print(f"Enhanced OCR Agent: Extracted text from {len(self.images_by_page)} pages")
        print(f"Enhanced OCR Agent: Average confidence score: {sum(self.confidence_scores.values()) / len(self.confidence_scores) if self.confidence_scores else 0:.2f}")
        
        return ocr_results
    
    def _convert_pdf_to_images(self, pdf_path):
        """Convert PDF to images."""
        try:
            print("Converting PDF to images...")
            pages = convert_from_path(pdf_path)
            
            for i, page in enumerate(pages, 1):
                self.images_by_page[i] = page
                
                # Save image for debugging
                output_dir = 'agent_results/images'
                os.makedirs(output_dir, exist_ok=True)
                page.save(os.path.join(output_dir, f'page_{i}.png'))
        except Exception as e:
            print(f"Error converting PDF to images: {str(e)}")
            
            # Fallback to pdfplumber for page count
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    print(f"Using pdfplumber fallback. Document has {len(pdf.pages)} pages.")
            except Exception as e2:
                print(f"Error with pdfplumber fallback: {str(e2)}")
    
    def _preprocess_image(self, image, method='basic'):
        """Preprocess image for better OCR results."""
        # Convert PIL Image to numpy array for OpenCV
        if isinstance(image, Image.Image):
            image_np = np.array(image)
        else:
            image_np = image
        
        # Convert to grayscale if needed
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_np
        
        if method == 'basic':
            # Basic preprocessing
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            return thresh
        
        elif method == 'advanced':
            # Advanced preprocessing
            # Apply bilateral filter to reduce noise while preserving edges
            filtered = cv2.bilateralFilter(gray, 9, 75, 75)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Noise removal
            kernel = np.ones((1, 1), np.uint8)
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            # Dilation to make text more prominent
            kernel = np.ones((1, 1), np.uint8)
            dilated = cv2.dilate(opening, kernel, iterations=1)
            
            return dilated
        
        elif method == 'financial':
            # Financial document specific preprocessing
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            equalized = clahe.apply(gray)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(equalized, (5, 5), 0)
            
            # Apply Otsu's thresholding
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return thresh
        
        else:
            return gray
    
    def _extract_text_with_tesseract(self, image, preprocessing_method='basic'):
        """Extract text using Tesseract OCR."""
        try:
            # Preprocess image
            preprocessed = self._preprocess_image(image, preprocessing_method)
            
            # Save preprocessed image for debugging
            output_dir = 'agent_results/preprocessed'
            os.makedirs(output_dir, exist_ok=True)
            cv2.imwrite(os.path.join(output_dir, f'preprocessed_{preprocessing_method}.png'), preprocessed)
            
            # Extract text
            text = pytesseract.image_to_string(preprocessed, config=self.tesseract_config)
            
            return text
        except Exception as e:
            print(f"Error extracting text with Tesseract ({preprocessing_method}): {str(e)}")
            return ""
    
    def _extract_text_with_pdfplumber(self, pdf_path, page_num):
        """Extract text using pdfplumber."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if page_num <= len(pdf.pages):
                    return pdf.pages[page_num-1].extract_text() or ""
                else:
                    return ""
        except Exception as e:
            print(f"Error extracting text with pdfplumber: {str(e)}")
            return ""
    
    def _extract_text_with_multiple_engines(self, pdf_path):
        """Extract text with multiple engines."""
        # Extract text with pdfplumber
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    
                    if page_num not in self.text_by_page:
                        self.text_by_page[page_num] = {}
                    
                    self.text_by_page[page_num]['pdfplumber'] = text
        except Exception as e:
            print(f"Error extracting text with pdfplumber: {str(e)}")
        
        # Extract text with Tesseract using different preprocessing methods
        for page_num, image in self.images_by_page.items():
            if page_num not in self.text_by_page:
                self.text_by_page[page_num] = {}
            
            # Extract with basic preprocessing
            text_basic = self._extract_text_with_tesseract(image, 'basic')
            self.text_by_page[page_num]['tesseract_basic'] = text_basic
            
            # Extract with advanced preprocessing
            text_advanced = self._extract_text_with_tesseract(image, 'advanced')
            self.text_by_page[page_num]['tesseract_advanced'] = text_advanced
            
            # Extract with financial preprocessing
            text_financial = self._extract_text_with_tesseract(image, 'financial')
            self.text_by_page[page_num]['tesseract_financial'] = text_financial
    
    def _vote_on_best_text(self):
        """Vote on the best text for each page."""
        for page_num, texts in self.text_by_page.items():
            # Collect all non-empty texts
            all_texts = [text for text in texts.values() if text and len(text.strip()) > 0]
            
            if not all_texts:
                self.best_text_by_page[page_num] = ""
                self.confidence_scores[page_num] = 0.0
                continue
            
            if len(all_texts) == 1:
                self.best_text_by_page[page_num] = all_texts[0]
                self.confidence_scores[page_num] = 0.7  # Medium confidence for single source
                continue
            
            # Calculate similarity scores between all pairs of texts
            similarity_scores = {}
            for i, text1 in enumerate(all_texts):
                for j, text2 in enumerate(all_texts):
                    if i < j:
                        similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
                        similarity_scores[(i, j)] = similarity
            
            # Find the text with the highest average similarity to others
            avg_similarities = defaultdict(float)
            for (i, j), similarity in similarity_scores.items():
                avg_similarities[i] += similarity
                avg_similarities[j] += similarity
            
            for i in range(len(all_texts)):
                if i in avg_similarities:
                    avg_similarities[i] /= (len(all_texts) - 1)
            
            # Get the best text
            if avg_similarities:
                best_idx = max(avg_similarities.items(), key=lambda x: x[1])[0]
                best_text = all_texts[best_idx]
                confidence = avg_similarities[best_idx]
            else:
                # Fallback to the longest text
                best_text = max(all_texts, key=len)
                confidence = 0.5  # Medium-low confidence
            
            self.best_text_by_page[page_num] = best_text
            self.confidence_scores[page_num] = confidence
    
    def get_full_text(self):
        """Get the full text of the document."""
        full_text = ""
        for page_num in sorted(self.best_text_by_page.keys()):
            full_text += self.best_text_by_page[page_num] + "\n\n"
        return full_text

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python enhanced_ocr_agent.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    agent = EnhancedOCRAgent()
    agent.process(pdf_path)
