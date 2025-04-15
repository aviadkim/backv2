"""
OCR Processor - Uses OCR to extract text from images and PDFs.
"""
import os
import re
import tempfile
import numpy as np
import cv2
from typing import List, Optional, Dict, Any, Union
from pdf2image import convert_from_path

try:
    from paddleocr import PaddleOCR
    PADDLE_OCR_AVAILABLE = True
except ImportError:
    PADDLE_OCR_AVAILABLE = False
    print("PaddleOCR not available. Install with: pip install paddleocr")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("Tesseract not available. Install with: pip install pytesseract")

class OCRProcessor:
    """
    OCR processor that can extract text from images and PDFs.
    """
    
    def __init__(self, use_paddle: bool = True, lang: str = 'en'):
        """
        Initialize the OCR processor.
        
        Args:
            use_paddle: Whether to use PaddleOCR (True) or Tesseract (False)
            lang: Language code for OCR (default: 'en')
        """
        self.use_paddle = use_paddle and PADDLE_OCR_AVAILABLE
        self.lang = lang
        self.ocr = None
        
        if self.use_paddle:
            # Initialize PaddleOCR
            try:
                self.ocr = PaddleOCR(use_angle_cls=True, lang=lang)
                print("PaddleOCR initialized successfully.")
            except Exception as e:
                print(f"Error initializing PaddleOCR: {str(e)}")
                self.use_paddle = False
        
        if not self.use_paddle and TESSERACT_AVAILABLE:
            # Use Tesseract as fallback
            print("Using Tesseract OCR.")
    
    def process_pdf(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict[int, str]:
        """
        Process a PDF file and extract text using OCR.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save intermediate files (default: None)
        
        Returns:
            Dict mapping page numbers to extracted text
        """
        print(f"Processing PDF with OCR: {pdf_path}")
        
        # Create temporary directory if output_dir is not specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            temp_dir = output_dir
        else:
            temp_dir = tempfile.mkdtemp()
        
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            
            # Process each page
            results = {}
            for i, image in enumerate(images):
                page_num = i + 1
                print(f"Processing page {page_num}/{len(images)}")
                
                # Save the image temporarily
                image_path = os.path.join(temp_dir, f"page_{page_num}.jpg")
                image.save(image_path, "JPEG")
                
                # Process the image with OCR
                text = self.process_image(image_path)
                
                # Store the result
                results[page_num] = text
                
                # Save the OCR result if output_dir is specified
                if output_dir:
                    text_path = os.path.join(output_dir, f"page_{page_num}.txt")
                    with open(text_path, "w", encoding="utf-8") as f:
                        f.write(text)
            
            # Combine all pages into a single text
            combined_text = "\n\n".join(results.values())
            
            # Save the combined text if output_dir is specified
            if output_dir:
                combined_path = os.path.join(output_dir, "combined.txt")
                with open(combined_path, "w", encoding="utf-8") as f:
                    f.write(combined_text)
            
            return results
            
        except Exception as e:
            print(f"Error processing PDF with OCR: {str(e)}")
            return {}
    
    def process_image(self, image_path: str) -> str:
        """
        Process an image and extract text using OCR.
        
        Args:
            image_path: Path to the image file
        
        Returns:
            Extracted text
        """
        try:
            # Preprocess the image to improve OCR accuracy
            image = self._preprocess_image(image_path)
            
            if self.use_paddle:
                # Use PaddleOCR
                result = self.ocr.ocr(image, cls=True)
                
                # Extract text from result
                text = ""
                for line in result:
                    for word_info in line:
                        text += word_info[1][0] + " "
                    text += "\n"
                
                return text.strip()
            
            elif TESSERACT_AVAILABLE:
                # Use Tesseract
                text = pytesseract.image_to_string(image, lang=self.lang)
                return text.strip()
            
            else:
                print("No OCR engine available.")
                return ""
            
        except Exception as e:
            print(f"Error processing image with OCR: {str(e)}")
            return ""
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess an image to improve OCR accuracy.
        
        Args:
            image_path: Path to the image file
        
        Returns:
            Preprocessed image as numpy array
        """
        try:
            # Read the image
            image = cv2.imread(image_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply noise reduction
            kernel = np.ones((1, 1), np.uint8)
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            return opening
            
        except Exception as e:
            print(f"Error preprocessing image: {str(e)}")
            return cv2.imread(image_path)
    
    def extract_financial_data(self, text: str) -> Dict[str, Any]:
        """
        Extract financial data from OCR text.
        
        Args:
            text: OCR text to extract data from
        
        Returns:
            Dict containing extracted financial data
        """
        extracted_data = {
            "bonds": [],
            "asset_allocation": {},
            "portfolio_value": None,
            "client_info": {},
            "document_date": None
        }
        
        # Extract client information
        client_match = re.search(r'([A-Z\s]+LTD\.)', text)
        if client_match:
            extracted_data["client_info"]["name"] = client_match.group(1).strip()
        
        # Extract client number
        client_num_match = re.search(r'Client\s+Number[:\s]+(\d+)', text)
        if client_num_match:
            extracted_data["client_info"]["number"] = client_num_match.group(1).strip()
        
        # Extract document date
        date_match = re.search(r'Valuation\s+as\s+of\s+(\d{2}\.\d{2}\.\d{4})', text)
        if date_match:
            extracted_data["document_date"] = date_match.group(1).strip()
        
        # Extract portfolio value
        portfolio_value_patterns = [
            r'Total\s+assets\s*[:\s]+(\d[\d,.\']*)',
            r'Portfolio\s+Total\s*[:\s]+(\d[\d,.\']*)',
            r'Total\s+assets\s*[\|\:]?\s*(\d[\d,.\']*)',
            r'Portfolio\s+Value\s*[\|\:]?\s*(\d[\d,.\']*)'
        ]
        
        for pattern in portfolio_value_patterns:
            match = re.search(pattern, text)
            if match:
                value_str = match.group(1).strip()
                value = self._clean_number(value_str)
                if value:
                    extracted_data["portfolio_value"] = value
                    break
        
        # Extract bonds
        bond_sections = re.split(r'Bonds|Structured products', text)
        
        if len(bond_sections) > 1:
            # Process each bond section
            for section in bond_sections[1:]:  # Skip the first section (before "Bonds")
                # Look for ISIN patterns
                isin_matches = re.finditer(r'ISIN:\s*([A-Z0-9]{12})', section)
                
                for isin_match in isin_matches:
                    isin = isin_match.group(1).strip()
                    
                    # Find the context around this ISIN (up to 10 lines)
                    start_pos = max(0, isin_match.start() - 500)
                    end_pos = min(len(section), isin_match.end() + 500)
                    context = section[start_pos:end_pos]
                    
                    # Create a bond object
                    bond = {'isin': isin}
                    
                    # Extract description (usually before ISIN)
                    desc_match = re.search(r'([A-Z][A-Z0-9\s\.\-\(\)]+)(?=.*ISIN)', context)
                    if desc_match:
                        bond['description'] = desc_match.group(1).strip()
                    
                    # Extract maturity date
                    maturity_match = re.search(r'Maturity:\s*(\d{2}\.\d{2}\.\d{4})', context)
                    if maturity_match:
                        bond['maturity_date'] = maturity_match.group(1).strip()
                    
                    # Extract currency
                    currency_match = re.search(r'Currency[:\s]+([A-Z]{3})', context)
                    if currency_match:
                        bond['currency'] = currency_match.group(1).strip()
                    
                    # Extract nominal
                    nominal_match = re.search(r'Nominal[:\s]+([\d\',\.]+)', context)
                    if nominal_match:
                        bond['nominal'] = self._clean_number(nominal_match.group(1))
                    
                    # Extract price
                    price_match = re.search(r'Price[:\s]+([\d\',\.]+)', context)
                    if price_match:
                        bond['price'] = self._clean_number(price_match.group(1))
                    
                    # Extract valuation
                    valuation_match = re.search(r'Valuation[:\s]+([\d\',\.]+)', context)
                    if valuation_match:
                        bond['valuation'] = self._clean_number(valuation_match.group(1))
                    
                    # Only add if we have at least ISIN
                    if 'isin' in bond:
                        extracted_data["bonds"].append(bond)
        
        # Extract asset allocation
        asset_sections = re.split(r'Asset Allocation|Assets and Liabilities Structure', text)
        
        if len(asset_sections) > 1:
            # Process each asset allocation section
            for section in asset_sections[1:]:  # Skip the first section (before "Asset Allocation")
                # Look for asset class patterns
                asset_class_matches = re.finditer(r'([A-Z][A-Za-z\s]+)\s+(\d[\d\',\.]+)\s+(\d+\.\d+)%', section)
                
                for asset_match in asset_class_matches:
                    asset_class = asset_match.group(1).strip()
                    value_str = asset_match.group(2).strip()
                    percentage_str = asset_match.group(3).strip()
                    
                    value = self._clean_number(value_str)
                    percentage = float(percentage_str) if percentage_str else None
                    
                    if value is not None and asset_class:
                        extracted_data["asset_allocation"][asset_class] = {
                            "value": value,
                            "percentage": percentage,
                            "sub_classes": {}
                        }
                
                # Look for sub-class patterns
                sub_class_matches = re.finditer(r'\s+([a-z][A-Za-z\s/]+)\s+(\d[\d\',\.]+)\s+(\d+\.\d+)%', section)
                
                current_asset_class = next(iter(extracted_data["asset_allocation"].keys())) if extracted_data["asset_allocation"] else None
                
                for sub_match in sub_class_matches:
                    sub_class = sub_match.group(1).strip()
                    value_str = sub_match.group(2).strip()
                    percentage_str = sub_match.group(3).strip()
                    
                    value = self._clean_number(value_str)
                    percentage = float(percentage_str) if percentage_str else None
                    
                    if value is not None and sub_class and current_asset_class:
                        extracted_data["asset_allocation"][current_asset_class]["sub_classes"][sub_class] = {
                            "value": value,
                            "percentage": percentage
                        }
        
        return extracted_data
    
    def _clean_number(self, value_str: str) -> Optional[float]:
        """
        Clean a number string by removing quotes and commas.
        
        Args:
            value_str: Number string to clean
        
        Returns:
            Cleaned number as float, or None if invalid
        """
        if not value_str:
            return None
        
        # Replace single quotes with nothing (European number format)
        cleaned = str(value_str).replace("'", "")
        
        # Replace commas with nothing (US number format)
        cleaned = cleaned.replace(",", "")
        
        # Remove any non-numeric characters except decimal point and negative sign
        cleaned = re.sub(r'[^\d.-]', '', cleaned)
        
        try:
            return float(cleaned)
        except ValueError:
            return None

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process documents with OCR.")
    parser.add_argument("file_path", help="Path to the PDF or image file")
    parser.add_argument("--output-dir", help="Directory to save output files")
    parser.add_argument("--use-tesseract", action="store_true", help="Use Tesseract instead of PaddleOCR")
    parser.add_argument("--lang", default="en", help="Language code for OCR (default: en)")
    
    args = parser.parse_args()
    
    # Check if the file exists
    if not os.path.exists(args.file_path):
        print(f"Error: File not found: {args.file_path}")
        return 1
    
    # Create OCR processor
    processor = OCRProcessor(use_paddle=not args.use_tesseract, lang=args.lang)
    
    # Process the file
    if args.file_path.lower().endswith('.pdf'):
        results = processor.process_pdf(args.file_path, output_dir=args.output_dir)
        
        # Extract financial data from combined text
        combined_text = "\n\n".join(results.values())
        extracted_data = processor.extract_financial_data(combined_text)
        
        # Save extracted data as JSON
        if args.output_dir:
            import json
            json_path = os.path.join(args.output_dir, "extracted_data.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(extracted_data, f, indent=2)
            print(f"Extracted data saved to: {json_path}")
        
        print("OCR processing completed.")
    else:
        text = processor.process_image(args.file_path)
        
        # Save the OCR result if output_dir is specified
        if args.output_dir:
            os.makedirs(args.output_dir, exist_ok=True)
            text_path = os.path.join(args.output_dir, "ocr_result.txt")
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"OCR result saved to: {text_path}")
        
        print("OCR processing completed.")
    
    return 0

if __name__ == "__main__":
    main()
