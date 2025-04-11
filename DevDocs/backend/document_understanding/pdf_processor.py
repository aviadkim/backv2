import os
import io
import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
import numpy as np
import pandas as pd
from PIL import Image
import pytesseract
import pdfplumber
from PyPDF2 import PdfReader
import cv2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    PDF Processor for extracting text, tables, and structure from financial documents.
    """
    
    def __init__(self, ocr_enabled: bool = True, dpi: int = 300):
        """
        Initialize the PDF Processor.
        
        Args:
            ocr_enabled: Whether to use OCR for scanned documents
            dpi: DPI for OCR processing
        """
        self.ocr_enabled = ocr_enabled
        self.dpi = dpi
        
        # Check if tesseract is installed
        if self.ocr_enabled:
            try:
                pytesseract.get_tesseract_version()
                logger.info("Tesseract OCR is available")
            except Exception as e:
                logger.warning(f"Tesseract OCR is not available: {e}")
                self.ocr_enabled = False
    
    def process_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Process a PDF file and extract its content.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted content
        """
        logger.info(f"Processing PDF: {file_path}")
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Extract text using PyPDF2 (faster but less accurate)
            basic_text = self._extract_text_with_pypdf2(file_path)
            
            # Check if the document is scanned (has little or no text)
            is_scanned = self._is_scanned_document(basic_text)
            
            # Extract text using pdfplumber (more accurate but slower)
            detailed_text = self._extract_text_with_pdfplumber(file_path)
            
            # If document is scanned and OCR is enabled, use OCR
            if is_scanned and self.ocr_enabled:
                logger.info(f"Document appears to be scanned, using OCR")
                ocr_text = self._extract_text_with_ocr(file_path)
                text = ocr_text
            else:
                text = detailed_text if detailed_text else basic_text
            
            # Extract tables
            tables = self._extract_tables(file_path)
            
            # Extract document structure
            structure = self._extract_document_structure(file_path, text)
            
            # Extract metadata
            metadata = self._extract_metadata(file_path)
            
            return {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "text": text,
                "tables": tables,
                "structure": structure,
                "metadata": metadata,
                "is_scanned": is_scanned
            }
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            raise
    
    def _extract_text_with_pypdf2(self, file_path: str) -> str:
        """
        Extract text from PDF using PyPDF2.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text
        except Exception as e:
            logger.error(f"Error extracting text with PyPDF2: {e}")
            return ""
    
    def _extract_text_with_pdfplumber(self, file_path: str) -> str:
        """
        Extract text from PDF using pdfplumber.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text
        except Exception as e:
            logger.error(f"Error extracting text with pdfplumber: {e}")
            return ""
    
    def _extract_text_with_ocr(self, file_path: str) -> str:
        """
        Extract text from PDF using OCR.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for i, page in enumerate(pdf.pages):
                    # Convert page to image
                    img = page.to_image(resolution=self.dpi)
                    img_data = img.original.convert('RGB')
                    
                    # Use pytesseract to extract text
                    page_text = pytesseract.image_to_string(img_data)
                    text += page_text + "\n\n"
                
                return text
        except Exception as e:
            logger.error(f"Error extracting text with OCR: {e}")
            return ""
    
    def _is_scanned_document(self, text: str) -> bool:
        """
        Check if a document is scanned based on the amount of extracted text.
        
        Args:
            text: Extracted text
            
        Returns:
            True if the document appears to be scanned
        """
        # If there's very little text, it's likely a scanned document
        if not text or len(text.strip()) < 100:
            return True
        
        # Check if the text contains mostly garbage characters
        alphanumeric_ratio = sum(c.isalnum() or c.isspace() for c in text) / max(len(text), 1)
        if alphanumeric_ratio < 0.7:
            return True
        
        return False
    
    def _extract_tables(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract tables from PDF.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of extracted tables
        """
        tables = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    
                    for j, table_data in enumerate(page_tables):
                        if not table_data:
                            continue
                        
                        # Convert table to pandas DataFrame
                        df = pd.DataFrame(table_data)
                        
                        # Use first row as header if it looks like a header
                        if self._is_header_row(df.iloc[0]):
                            headers = df.iloc[0].tolist()
                            df = df.iloc[1:].reset_index(drop=True)
                            df.columns = headers
                        
                        # Clean the table data
                        df = self._clean_table_data(df)
                        
                        # Convert DataFrame to dict
                        table_dict = {
                            "page": i + 1,
                            "table_index": j,
                            "headers": df.columns.tolist(),
                            "data": df.values.tolist(),
                            "num_rows": len(df),
                            "num_cols": len(df.columns)
                        }
                        
                        tables.append(table_dict)
        except Exception as e:
            logger.error(f"Error extracting tables: {e}")
        
        return tables
    
    def _is_header_row(self, row: pd.Series) -> bool:
        """
        Check if a row is likely a header row.
        
        Args:
            row: DataFrame row
            
        Returns:
            True if the row is likely a header
        """
        # Check if the row has mostly string values
        string_ratio = sum(isinstance(val, str) for val in row) / max(len(row), 1)
        
        # Check if strings are short (typical for headers)
        avg_len = sum(len(str(val)) for val in row) / max(len(row), 1)
        
        return string_ratio > 0.7 and avg_len < 20
    
    def _clean_table_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean table data.
        
        Args:
            df: DataFrame with table data
            
        Returns:
            Cleaned DataFrame
        """
        # Replace None with empty string
        df = df.fillna("")
        
        # Convert all values to strings
        df = df.applymap(lambda x: str(x).strip())
        
        # Remove empty rows
        df = df[df.astype(str).apply(lambda x: x.str.strip().str.len() > 0).any(axis=1)]
        
        # Remove empty columns
        df = df.loc[:, df.astype(str).apply(lambda x: x.str.strip().str.len() > 0).any()]
        
        return df
    
    def _extract_document_structure(self, file_path: str, text: str) -> Dict[str, Any]:
        """
        Extract document structure (headings, sections, etc.).
        
        Args:
            file_path: Path to the PDF file
            text: Extracted text
            
        Returns:
            Document structure
        """
        structure = {
            "title": self._extract_title(file_path, text),
            "sections": self._extract_sections(text),
            "page_count": self._get_page_count(file_path)
        }
        
        return structure
    
    def _extract_title(self, file_path: str, text: str) -> str:
        """
        Extract document title.
        
        Args:
            file_path: Path to the PDF file
            text: Extracted text
            
        Returns:
            Document title
        """
        # Try to extract from metadata first
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            if reader.metadata and reader.metadata.title:
                return reader.metadata.title
        
        # Try to extract from first page
        lines = text.split('\n')
        for i in range(min(5, len(lines))):
            line = lines[i].strip()
            if line and len(line) < 100 and not line.startswith('Page') and not re.match(r'^\d+$', line):
                return line
        
        # Fall back to filename
        return os.path.splitext(os.path.basename(file_path))[0]
    
    def _extract_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract document sections based on headings.
        
        Args:
            text: Extracted text
            
        Returns:
            List of sections
        """
        sections = []
        
        # Common heading patterns in financial documents
        heading_patterns = [
            r'^(?:SECTION|PART)\s+\d+[.:]\s*(.*?)$',  # "SECTION 1: SUMMARY"
            r'^\d+\.\d*\s+(.*?)$',  # "1.1 Balance Sheet"
            r'^[A-Z][A-Z\s]+:$',  # "EXECUTIVE SUMMARY:"
            r'^[A-Z][A-Z\s]+$',  # "BALANCE SHEET"
        ]
        
        lines = text.split('\n')
        current_section = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check if line matches any heading pattern
            for pattern in heading_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    if current_section:
                        current_section["end_line"] = i
                        sections.append(current_section)
                    
                    heading = match.group(1) if match.groups() else line
                    current_section = {
                        "heading": heading.strip(),
                        "start_line": i,
                        "end_line": None,
                        "level": self._determine_heading_level(line)
                    }
                    break
        
        # Add the last section
        if current_section:
            current_section["end_line"] = len(lines)
            sections.append(current_section)
        
        return sections
    
    def _determine_heading_level(self, heading: str) -> int:
        """
        Determine the heading level based on formatting.
        
        Args:
            heading: Heading text
            
        Returns:
            Heading level (1 for top-level headings)
        """
        # Count the number of dots or numbers in the heading prefix
        if re.match(r'^\d+\.\d+\.\d+', heading):
            return 3
        elif re.match(r'^\d+\.\d+', heading):
            return 2
        elif re.match(r'^\d+\.', heading):
            return 1
        elif heading.isupper():
            return 1
        else:
            return 2
    
    def _get_page_count(self, file_path: str) -> int:
        """
        Get the number of pages in the PDF.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Number of pages
        """
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            return len(reader.pages)
    
    def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract PDF metadata.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary of metadata
        """
        metadata = {}
        
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                if reader.metadata:
                    for key in reader.metadata:
                        if key.startswith('/'):
                            clean_key = key[1:].lower()
                            metadata[clean_key] = reader.metadata[key]
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
        
        return metadata
