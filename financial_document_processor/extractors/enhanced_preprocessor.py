"""
Enhanced PDF preprocessor for financial documents.
"""
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
import json
import tempfile
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import required libraries
try:
    import pdfplumber
    import PyPDF2
    import cv2
    import numpy as np
    from pdf2image import convert_from_path
    import pytesseract
    from unstructured.partition.pdf import partition_pdf
    LIBRARIES_AVAILABLE = True
except ImportError as e:
    LIBRARIES_AVAILABLE = False
    logger.warning(f"Some libraries are not available: {e}")
    logger.warning("Install with: pip install pdfplumber PyPDF2 opencv-python pdf2image pytesseract unstructured")

class EnhancedPreprocessor:
    """Enhanced PDF preprocessor for financial documents."""
    
    def __init__(self, ocr_languages: str = "eng"):
        """
        Initialize the preprocessor.
        
        Args:
            ocr_languages: Languages to use for OCR (e.g., "eng+heb" for English and Hebrew)
        """
        if not LIBRARIES_AVAILABLE:
            raise ImportError("Required libraries not available")
        
        self.ocr_languages = ocr_languages
        logger.info(f"Initialized enhanced preprocessor with OCR languages: {ocr_languages}")
    
    def preprocess(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Preprocess a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save preprocessed files (optional)
        
        Returns:
            Dictionary with preprocessing results
        """
        logger.info(f"Preprocessing PDF: {pdf_path}")
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Extract metadata
        metadata = self._extract_metadata(pdf_path)
        
        # Extract text with pdfplumber
        pdfplumber_text = self._extract_text_with_pdfplumber(pdf_path)
        
        # Extract text with PyPDF2
        pypdf2_text = self._extract_text_with_pypdf2(pdf_path)
        
        # Extract text with OCR
        ocr_text = self._extract_text_with_ocr(pdf_path)
        
        # Extract text with unstructured
        unstructured_result = self._extract_with_unstructured(pdf_path)
        
        # Detect tables
        tables = self._detect_tables(pdf_path)
        
        # Combine results
        result = {
            "metadata": metadata,
            "text": {
                "pdfplumber": pdfplumber_text,
                "pypdf2": pypdf2_text,
                "ocr": ocr_text,
                "unstructured": unstructured_result.get("text", "")
            },
            "elements": unstructured_result.get("elements", []),
            "tables": tables
        }
        
        # Save results if output directory is specified
        if output_dir:
            # Save combined text
            with open(os.path.join(output_dir, "combined_text.txt"), "w", encoding="utf-8") as f:
                f.write(pdfplumber_text + "\n\n" + pypdf2_text + "\n\n" + ocr_text + "\n\n" + unstructured_result.get("text", ""))
            
            # Save metadata
            with open(os.path.join(output_dir, "metadata.json"), "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
            
            # Save tables
            with open(os.path.join(output_dir, "tables.json"), "w", encoding="utf-8") as f:
                json.dump(tables, f, indent=2)
        
        logger.info(f"Preprocessing completed for {pdf_path}")
        return result
    
    def _extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract metadata from the PDF."""
        logger.info(f"Extracting metadata from {pdf_path}")
        
        metadata = {
            "filename": os.path.basename(pdf_path),
            "path": pdf_path,
            "size_bytes": os.path.getsize(pdf_path)
        }
        
        # Extract metadata with PyPDF2
        try:
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                metadata["page_count"] = len(reader.pages)
                metadata["pdf_info"] = reader.metadata
                
                # Extract creation date
                if hasattr(reader.metadata, "/CreationDate"):
                    metadata["creation_date"] = reader.metadata.get("/CreationDate", "")
                
                # Extract modification date
                if hasattr(reader.metadata, "/ModDate"):
                    metadata["modification_date"] = reader.metadata.get("/ModDate", "")
        except Exception as e:
            logger.warning(f"Error extracting metadata with PyPDF2: {e}")
        
        # Extract metadata with pdfplumber
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if not metadata.get("page_count"):
                    metadata["page_count"] = len(pdf.pages)
                
                if not metadata.get("pdf_info") and hasattr(pdf, "metadata"):
                    metadata["pdf_info"] = pdf.metadata
        except Exception as e:
            logger.warning(f"Error extracting metadata with pdfplumber: {e}")
        
        return metadata
    
    def _extract_text_with_pdfplumber(self, pdf_path: str) -> str:
        """Extract text from PDF using pdfplumber."""
        logger.info(f"Extracting text with pdfplumber from {pdf_path}")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    text += f"\n\n--- Page {i+1} ---\n\n{page_text}"
                
                return text
        except Exception as e:
            logger.warning(f"Error extracting text with pdfplumber: {e}")
            return ""
    
    def _extract_text_with_pypdf2(self, pdf_path: str) -> str:
        """Extract text from PDF using PyPDF2."""
        logger.info(f"Extracting text with PyPDF2 from {pdf_path}")
        
        try:
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    text += f"\n\n--- Page {i+1} ---\n\n{page_text}"
                
                return text
        except Exception as e:
            logger.warning(f"Error extracting text with PyPDF2: {e}")
            return ""
    
    def _extract_text_with_ocr(self, pdf_path: str) -> str:
        """Extract text from PDF using OCR."""
        logger.info(f"Extracting text with OCR from {pdf_path}")
        
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            
            text = ""
            for i, image in enumerate(images):
                # Save image to temporary file
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
                    temp_path = temp.name
                    image.save(temp_path, "PNG")
                
                # Perform OCR
                page_text = pytesseract.image_to_string(temp_path, lang=self.ocr_languages)
                text += f"\n\n--- Page {i+1} (OCR) ---\n\n{page_text}"
                
                # Remove temporary file
                os.unlink(temp_path)
            
            return text
        except Exception as e:
            logger.warning(f"Error extracting text with OCR: {e}")
            return ""
    
    def _extract_with_unstructured(self, pdf_path: str) -> Dict[str, Any]:
        """Extract content using unstructured."""
        logger.info(f"Extracting content with unstructured from {pdf_path}")
        
        try:
            # Extract elements from PDF
            elements = partition_pdf(
                pdf_path,
                strategy="auto",
                languages=[self.ocr_languages],
                ocr_enabled=True
            )
            
            # Process elements
            result = {"elements": [], "text": ""}
            text_elements = []
            
            for element in elements:
                element_dict = {
                    "type": element.category,
                    "text": element.text,
                    "metadata": element.metadata.to_dict() if hasattr(element.metadata, "to_dict") else {}
                }
                result["elements"].append(element_dict)
                text_elements.append(element.text)
            
            # Combine text
            result["text"] = "\n\n".join(text_elements)
            
            return result
        except Exception as e:
            logger.warning(f"Error extracting with unstructured: {e}")
            return {"elements": [], "text": ""}
    
    def _detect_tables(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Detect tables in the PDF."""
        logger.info(f"Detecting tables in {pdf_path}")
        
        tables = []
        
        # Detect tables with pdfplumber
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    for j, table_data in enumerate(page_tables):
                        tables.append({
                            "page": i + 1,
                            "table_number": j + 1,
                            "extraction_method": "pdfplumber",
                            "data": table_data
                        })
        except Exception as e:
            logger.warning(f"Error detecting tables with pdfplumber: {e}")
        
        # Detect tables with OpenCV
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            
            for i, image in enumerate(images):
                # Save image to temporary file
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
                    temp_path = temp.name
                    image.save(temp_path, "PNG")
                
                # Load image with OpenCV
                img = cv2.imread(temp_path)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Apply threshold
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
                
                # Find contours
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # Filter contours by size
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    if w > 100 and h > 100:  # Minimum size for a table
                        tables.append({
                            "page": i + 1,
                            "extraction_method": "opencv",
                            "coordinates": {"x": x, "y": y, "width": w, "height": h}
                        })
                
                # Remove temporary file
                os.unlink(temp_path)
        except Exception as e:
            logger.warning(f"Error detecting tables with OpenCV: {e}")
        
        return tables
    
    def detect_financial_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect financial entities in text.
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with detected entities
        """
        logger.info("Detecting financial entities in text")
        
        entities = {
            "securities": [],
            "currencies": [],
            "percentages": [],
            "monetary_values": [],
            "dates": []
        }
        
        # Detect securities (ISIN)
        isin_pattern = r'ISIN:?\s*([A-Z]{2}[A-Z0-9]{9}[0-9])'
        isin_matches = re.finditer(isin_pattern, text)
        
        for match in isin_matches:
            isin = match.group(1)
            
            # Get context around the ISIN (200 characters before and after)
            context_start = max(0, match.start() - 200)
            context_end = min(len(text), match.end() + 200)
            context = text[context_start:context_end]
            
            entities["securities"].append({
                "type": "ISIN",
                "value": isin,
                "position": match.start(),
                "context": context
            })
        
        # Detect currencies
        currency_pattern = r'([€$£¥])\s*\d+(?:[.,]\d+)?|\d+(?:[.,]\d+)?\s*([€$£¥])'
        currency_matches = re.finditer(currency_pattern, text)
        
        for match in currency_matches:
            currency = match.group(1) or match.group(2)
            
            entities["currencies"].append({
                "value": currency,
                "position": match.start(),
                "text": match.group(0)
            })
        
        # Detect percentages
        percentage_pattern = r'(\d+(?:\.\d+)?)%'
        percentage_matches = re.finditer(percentage_pattern, text)
        
        for match in percentage_matches:
            percentage = float(match.group(1))
            
            entities["percentages"].append({
                "value": percentage,
                "position": match.start(),
                "text": match.group(0)
            })
        
        # Detect monetary values
        monetary_pattern = r'(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)'
        monetary_matches = re.finditer(monetary_pattern, text)
        
        for match in monetary_matches:
            value_str = match.group(1)
            value_str = value_str.replace(",", "")
            
            try:
                value = float(value_str)
                
                # Only consider values above a certain threshold
                if value > 1000:
                    entities["monetary_values"].append({
                        "value": value,
                        "position": match.start(),
                        "text": match.group(0)
                    })
            except ValueError:
                pass
        
        # Detect dates
        date_patterns = [
            r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})',  # DD/MM/YYYY or MM/DD/YYYY
            r'(\d{4})[/\-\.](\d{1,2})[/\-\.](\d{1,2})'     # YYYY/MM/DD
        ]
        
        for pattern in date_patterns:
            date_matches = re.finditer(pattern, text)
            
            for match in date_matches:
                entities["dates"].append({
                    "text": match.group(0),
                    "position": match.start()
                })
        
        return entities
