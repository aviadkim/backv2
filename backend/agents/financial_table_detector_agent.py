"""
Financial Table Detector Agent for FinDoc Analyzer v1.0

This agent detects and extracts tables from financial documents.
"""
import os
import logging
import tempfile
from typing import Dict, Any, List, Optional
import camelot
import pandas as pd
import numpy as np
from PIL import Image
import cv2
import pytesseract

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialTableDetectorAgent:
    """
    Agent for detecting and extracting tables from financial documents.
    """
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the FinancialTableDetectorAgent.
        
        Args:
            api_key: OpenRouter API key for AI-enhanced processing
            **kwargs: Additional arguments
        """
        self.api_key = api_key
        logger.info("FinancialTableDetectorAgent initialized")
    
    def process(self, image_path: str, **kwargs) -> Dict[str, Any]:
        """
        Detect and extract tables from a document.
        
        Args:
            image_path: Path to the document image or PDF
            **kwargs: Additional arguments
            
        Returns:
            Dictionary with table detection results
        """
        logger.info(f"Detecting tables in document: {image_path}")
        
        try:
            # Check if the file is a PDF
            if image_path.lower().endswith('.pdf'):
                tables = self._extract_tables_from_pdf(image_path)
            else:
                tables = self._extract_tables_from_image(image_path)
            
            # Enhance tables with AI if API key is provided
            if self.api_key:
                tables = self._enhance_tables_with_ai(tables)
            
            return {
                "status": "success",
                "tables": tables,
                "count": len(tables)
            }
        except Exception as e:
            logger.error(f"Error detecting tables: {e}")
            return {
                "status": "error",
                "error": str(e),
                "tables": [],
                "count": 0
            }
    
    def _extract_tables_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract tables from a PDF document using Camelot.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of extracted tables
        """
        logger.info(f"Extracting tables from PDF: {pdf_path}")
        
        # Extract tables using Camelot
        tables_lattice = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
        tables_stream = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
        
        # Combine tables from both methods
        all_tables = []
        
        # Process lattice tables
        for i, table in enumerate(tables_lattice):
            if table.df.size > 0:
                all_tables.append({
                    "id": f"lattice_{i}",
                    "page": table.page,
                    "data": table.df.to_dict('records'),
                    "headers": table.df.columns.tolist(),
                    "accuracy": table.accuracy,
                    "method": "lattice"
                })
        
        # Process stream tables
        for i, table in enumerate(tables_stream):
            if table.df.size > 0:
                all_tables.append({
                    "id": f"stream_{i}",
                    "page": table.page,
                    "data": table.df.to_dict('records'),
                    "headers": table.df.columns.tolist(),
                    "accuracy": table.accuracy,
                    "method": "stream"
                })
        
        # Filter out low-quality tables
        filtered_tables = [table for table in all_tables if table["accuracy"] > 50]
        
        logger.info(f"Extracted {len(filtered_tables)} tables from PDF")
        return filtered_tables
    
    def _extract_tables_from_image(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Extract tables from an image using OpenCV and Tesseract.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of extracted tables
        """
        logger.info(f"Extracting tables from image: {image_path}")
        
        # Read the image
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size
        min_area = img.shape[0] * img.shape[1] * 0.01  # 1% of image area
        table_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
        
        tables = []
        for i, contour in enumerate(table_contours):
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Extract the table region
            table_img = img[y:y+h, x:x+w]
            
            # Save the table image temporarily
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp:
                temp_path = temp.name
                cv2.imwrite(temp_path, table_img)
            
            # Extract text from the table image using Tesseract
            text = pytesseract.image_to_string(Image.open(temp_path))
            
            # Parse the text into rows and columns
            rows = [row.strip() for row in text.split('\n') if row.strip()]
            
            # Try to determine headers and data
            headers = rows[0].split() if rows else []
            data = []
            for row in rows[1:]:
                cells = row.split()
                if len(cells) == len(headers):
                    data.append(dict(zip(headers, cells)))
            
            tables.append({
                "id": f"image_{i}",
                "page": 1,  # Assume single page for images
                "data": data,
                "headers": headers,
                "accuracy": 70,  # Estimated accuracy
                "method": "image"
            })
            
            # Clean up temporary file
            os.unlink(temp_path)
        
        logger.info(f"Extracted {len(tables)} tables from image")
        return tables
    
    def _enhance_tables_with_ai(self, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance tables with AI processing.
        
        Args:
            tables: List of extracted tables
            
        Returns:
            List of enhanced tables
        """
        logger.info("Enhancing tables with AI")
        
        # This would use the OpenRouter API to enhance tables
        # For now, we'll just return the original tables
        
        return tables
