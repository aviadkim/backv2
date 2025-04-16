"""
Multi-Document Processor for FinDoc Analyzer v1.0

This module processes multiple financial documents and extracts structured data.
"""
import os
import logging
import json
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiDocumentProcessor:
    """
    Processor for handling multiple financial documents.
    """
    
    def __init__(self, output_dir: str = "test_output", api_key: Optional[str] = None):
        """
        Initialize the MultiDocumentProcessor.
        
        Args:
            output_dir: Directory to save output files
            api_key: OpenRouter API key for AI-enhanced processing
        """
        self.output_dir = output_dir
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self.documents = {}
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info("MultiDocumentProcessor initialized")
    
    def add_document(self, document_path: str, document_id: Optional[str] = None) -> str:
        """
        Add a document to the processor.
        
        Args:
            document_path: Path to the document
            document_id: Optional identifier for the document
            
        Returns:
            Document ID
        """
        if not document_id:
            document_id = os.path.basename(document_path)
        
        self.documents[document_id] = {
            "path": document_path,
            "processed": False,
            "data": {}
        }
        
        logger.info(f"Added document: {document_id}")
        return document_id
    
    def process_document(self, document_id: str) -> Dict[str, Any]:
        """
        Process a document.
        
        Args:
            document_id: Identifier of the document to process
            
        Returns:
            Dictionary with processing results
        """
        if document_id not in self.documents:
            raise ValueError(f"Document '{document_id}' not found")
        
        document = self.documents[document_id]
        document_path = document["path"]
        
        logger.info(f"Processing document: {document_id}")
        
        try:
            # Extract text from the document
            text = self._extract_text(document_path)
            
            # Extract client information
            client_info = self._extract_client_info(text)
            
            # Extract document date
            document_date = self._extract_document_date(text)
            
            # Extract portfolio value
            portfolio_value = self._extract_portfolio_value(text)
            
            # Extract bonds
            bonds = self._extract_bonds(text)
            
            # Extract asset allocation
            asset_allocation = self._extract_asset_allocation(text)
            
            # Save the results
            result = {
                "client_info": client_info,
                "document_date": document_date,
                "portfolio_value": portfolio_value,
                "bonds": bonds,
                "asset_allocation": asset_allocation
            }
            
            document["data"] = result
            document["processed"] = True
            
            # Save the extraction to a file
            extraction_path = os.path.join(self.output_dir, f"{document_id.replace('.pdf', '')}_extraction.json")
            with open(extraction_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Document processed: {document_id}")
            return result
        
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            document["error"] = str(e)
            return {"error": str(e)}
    
    def get_document_data(self, document_id: str) -> Dict[str, Any]:
        """
        Get the data for a document.
        
        Args:
            document_id: Identifier of the document
            
        Returns:
            Dictionary with document data
        """
        if document_id not in self.documents:
            raise ValueError(f"Document '{document_id}' not found")
        
        document = self.documents[document_id]
        
        if not document["processed"]:
            return self.process_document(document_id)
        
        return document["data"]
    
    def _extract_text(self, document_path: str) -> str:
        """
        Extract text from a document.
        
        Args:
            document_path: Path to the document
            
        Returns:
            Extracted text
        """
        logger.info(f"Extracting text from: {document_path}")
        
        # Check if the document is a PDF
        if document_path.lower().endswith('.pdf'):
            # Try to use pdfplumber
            try:
                import pdfplumber
                
                with pdfplumber.open(document_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                
                return text
            except ImportError:
                logger.warning("pdfplumber not available")
            
            # Try to use PyPDF2
            try:
                from PyPDF2 import PdfReader
                
                reader = PdfReader(document_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                
                return text
            except ImportError:
                logger.warning("PyPDF2 not available")
        
        # If it's a text file or we couldn't extract text from PDF
        try:
            with open(document_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with a different encoding
            with open(document_path, "r", encoding="latin-1") as f:
                return f.read()
    
    def _extract_client_info(self, text: str) -> Dict[str, str]:
        """
        Extract client information from text.
        
        Args:
            text: Text to extract client information from
            
        Returns:
            Dictionary with client information
        """
        # Extract client name
        client_name_pattern = r'(?:Client|Customer|Account Holder|Name)(?:\s*:|\s+)([A-Z\s\.]+(?:LTD\.?|INC\.?|LLC\.?|CORP\.?|SA\.?|AG\.?|GMBH\.?|PLC\.?)?)'
        client_name_match = re.search(client_name_pattern, text, re.IGNORECASE)
        client_name = client_name_match.group(1).strip() if client_name_match else ""
        
        # Extract client number
        client_number_pattern = r'(?:Client|Customer|Account)(?:\s+Number|\s+ID|\s+#|\s*:)(?:\s*//|\s*:|\s+)(\d+)'
        client_number_match = re.search(client_number_pattern, text, re.IGNORECASE)
        client_number = client_number_match.group(1).strip() if client_number_match else ""
        
        return {
            "name": client_name,
            "number": client_number
        }
    
    def _extract_document_date(self, text: str) -> str:
        """
        Extract document date from text.
        
        Args:
            text: Text to extract document date from
            
        Returns:
            Document date as string
        """
        # Look for common date formats
        date_patterns = [
            r'(?:as of|dated|date:?|valuation date)\s+(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
            r'(?:as of|dated|date:?|valuation date)\s+(\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{2,4})',
            r'(\d{1,2}\.\d{1,2}\.\d{2,4})'
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, text, re.IGNORECASE)
            if date_match:
                return date_match.group(1).strip()
        
        return ""
    
    def _extract_portfolio_value(self, text: str) -> float:
        """
        Extract portfolio value from text.
        
        Args:
            text: Text to extract portfolio value from
            
        Returns:
            Portfolio value as float
        """
        # Look for portfolio value patterns
        value_patterns = [
            r'(?:Portfolio|Total|Assets)(?:\s+Value|\s+Amount|\s+Sum)(?:\s*:|\s+)(?:USD|EUR|CHF|GBP)?\s*([\d,\'\.]+)',
            r'(?:Portfolio|Total|Assets)(?:\s+Value|\s+Amount|\s+Sum)(?:\s*:|\s+)([\d,\'\.]+)\s*(?:USD|EUR|CHF|GBP)',
            r'Total\s+(?:USD|EUR|CHF|GBP)\s*([\d,\'\.]+)'
        ]
        
        for pattern in value_patterns:
            value_match = re.search(pattern, text, re.IGNORECASE)
            if value_match:
                value_str = value_match.group(1).replace(",", "").replace("'", "")
                try:
                    return float(value_str)
                except ValueError:
                    pass
        
        return 0.0
    
    def _extract_bonds(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract bonds from text.
        
        Args:
            text: Text to extract bonds from
            
        Returns:
            List of bonds
        """
        bonds = []
        
        # Extract ISINs
        isin_pattern = r'(?:ISIN:|ISIN\s+|ISIN=|ISIN\s*:\s*|^|\s)([A-Z]{2}[A-Z0-9]{10})(?:\s|$|,|\.|;|//)'
        isin_matches = re.finditer(isin_pattern, text, re.MULTILINE)
        
        for match in isin_matches:
            isin = match.group(1)
            
            # Get context around the ISIN
            context_start = max(0, match.start() - 200)
            context_end = min(len(text), match.end() + 200)
            context = text[context_start:context_end]
            
            # Extract bond details
            bond = {
                "isin": isin,
                "currency": context
            }
            
            bonds.append(bond)
        
        return bonds
    
    def _extract_asset_allocation(self, text: str) -> Dict[str, Dict[str, Any]]:
        """
        Extract asset allocation from text.
        
        Args:
            text: Text to extract asset allocation from
            
        Returns:
            Dictionary with asset allocation
        """
        asset_allocation = {}
        
        # Look for asset allocation in text
        allocation_pattern = r'(?:Total|Asset Class)\s+([A-Za-z\s/]+)\s+(?:USD|EUR|CHF|GBP)?\s*([\d,\'\.]+)\s+(\d+\.\d+)%'
        allocation_matches = re.finditer(allocation_pattern, text, re.IGNORECASE)
        
        for match in allocation_matches:
            asset_class = match.group(1).strip()
            value_str = match.group(2).replace(",", "").replace("'", "")
            percentage = float(match.group(3))
            
            try:
                value = float(value_str)
            except ValueError:
                value = 0.0
            
            asset_allocation[asset_class] = {
                "value": value,
                "percentage": percentage,
                "sub_classes": {}
            }
        
        return asset_allocation
