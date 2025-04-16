"""
Document processor that combines extraction and database storage.
"""
import os
import logging
from typing import Dict, List, Any, Optional
import datetime
import json

from financial_document_processor.extractors.pdf_extractor import PDFExtractor
from financial_document_processor.database.db import Database

class DocumentProcessor:
    """
    Document processor that combines extraction and database storage.
    """
    
    def __init__(self, database: Database, extractor: Optional[PDFExtractor] = None):
        """
        Initialize the document processor.
        
        Args:
            database: Database connection
            extractor: PDF extractor (optional, will create one if not provided)
        """
        self.database = database
        self.extractor = extractor or PDFExtractor()
    
    def process_document(self, pdf_path: str, output_dir: Optional[str] = None, 
                         document_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a document: extract content and store in database.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save extracted data (optional)
            document_type: Type of document (e.g., "bank_statement", "portfolio_report")
        
        Returns:
            Dictionary with processing results
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Create document record
        document_data = {
            "filename": os.path.basename(pdf_path),
            "file_path": pdf_path,
            "file_size": os.path.getsize(pdf_path),
            "document_type": document_type,
            "processing_status": "processing",
            "extraction_method": "combined",
            "extraction_version": "1.0"
        }
        
        document = self.database.store_document(document_data)
        document_id = document.id
        
        try:
            # Extract content from PDF
            extraction_result = self.extractor.extract(pdf_path, output_dir)
            
            # Update document metadata
            document_metadata = extraction_result.get("metadata", {})
            self.database.update_document_status(
                document_id=document_id,
                status="extracting"
            )
            
            # Store raw text
            combined_text = ""
            for source, text in extraction_result.get("text", {}).items():
                combined_text += f"\n\n--- {source.upper()} EXTRACTION ---\n\n{text}"
            
            self.database.store_raw_text(
                document_id=document_id,
                content=combined_text,
                extraction_method="combined"
            )
            
            # Store tables
            self.database.store_tables(
                document_id=document_id,
                tables=extraction_result.get("tables", [])
            )
            
            # Extract and store securities
            securities = self.extractor.extract_securities(pdf_path)
            self.database.store_securities(
                document_id=document_id,
                securities=securities
            )
            
            # Extract and store portfolio value
            portfolio_value = self.extractor.extract_portfolio_value(pdf_path)
            if portfolio_value:
                self.database.store_portfolio_value(
                    document_id=document_id,
                    portfolio_value_data={
                        "value": portfolio_value,
                        "currency": "USD",  # Default currency
                        "value_date": datetime.datetime.now(),
                        "extraction_method": "combined",
                        "confidence_score": 0.9  # Default confidence
                    }
                )
            
            # Extract and store asset allocations
            asset_allocations = self._extract_asset_allocations(extraction_result)
            if asset_allocations:
                self.database.store_asset_allocations(
                    document_id=document_id,
                    asset_allocations=asset_allocations
                )
            
            # Update document status to completed
            self.database.update_document_status(
                document_id=document_id,
                status="completed"
            )
            
            return {
                "document_id": document_id,
                "status": "completed",
                "securities_count": len(securities),
                "portfolio_value": portfolio_value,
                "asset_allocations_count": len(asset_allocations) if asset_allocations else 0,
                "tables_count": len(extraction_result.get("tables", [])),
                "extraction_result": extraction_result if output_dir else None
            }
        
        except Exception as e:
            logging.error(f"Error processing document: {e}")
            
            # Update document status to failed
            self.database.update_document_status(
                document_id=document_id,
                status="failed"
            )
            
            return {
                "document_id": document_id,
                "status": "failed",
                "error": str(e)
            }
    
    def _extract_asset_allocations(self, extraction_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract asset allocations from extraction result.
        
        Args:
            extraction_result: Extraction result
        
        Returns:
            List of asset allocation dictionaries
        """
        asset_allocations = []
        
        # Look for asset allocation tables
        for table in extraction_result.get("tables", []):
            headers = [str(h).lower() for h in table.get("headers", [])]
            
            # Check if this looks like an asset allocation table
            asset_allocation_table = any(keyword in " ".join(headers) for keyword in 
                                       ["asset", "allocation", "class", "weight", "percentage"])
            
            if not asset_allocation_table:
                continue
            
            # Find column indices for relevant information
            asset_class_col = next((i for i, h in enumerate(headers) if any(k in h for k in ["asset", "class", "allocation"])), None)
            value_col = next((i for i, h in enumerate(headers) if any(k in h for k in ["value", "amount"])), None)
            percentage_col = next((i for i, h in enumerate(headers) if any(k in h for k in ["percentage", "weight", "%"])), None)
            
            if asset_class_col is None:
                continue
            
            # Process rows
            for row in table.get("rows", []):
                if len(row) <= asset_class_col:
                    continue
                
                asset_class = str(row[asset_class_col]).strip()
                if not asset_class:
                    continue
                
                allocation = {
                    "asset_class": asset_class,
                    "extraction_method": f"table_{table.get('extraction_method', 'unknown')}"
                }
                
                # Extract value
                if value_col is not None and len(row) > value_col:
                    try:
                        value_text = str(row[value_col]).strip()
                        value_text = value_text.replace(",", "").replace("'", "")
                        allocation["value"] = float(value_text)
                    except (ValueError, TypeError):
                        pass
                
                # Extract percentage
                if percentage_col is not None and len(row) > percentage_col:
                    try:
                        percentage_text = str(row[percentage_col]).strip()
                        percentage_text = percentage_text.replace("%", "").replace(",", "").replace("'", "")
                        allocation["percentage"] = float(percentage_text)
                    except (ValueError, TypeError):
                        pass
                
                asset_allocations.append(allocation)
        
        # If no asset allocations found in tables, try to extract from text
        if not asset_allocations:
            # Look for asset allocation patterns in text
            import re
            
            all_text = ""
            for source, text in extraction_result.get("text", {}).items():
                all_text += text + "\n\n"
            
            # Look for asset allocation section
            asset_allocation_section = None
            asset_allocation_patterns = [
                r'(?:Asset\s+Allocation|Asset\s+Class).*?(?=(?:\n\n|\Z))',
                r'(?:Portfolio\s+Allocation|Portfolio\s+Breakdown).*?(?=(?:\n\n|\Z))'
            ]
            
            for pattern in asset_allocation_patterns:
                match = re.search(pattern, all_text, re.DOTALL | re.IGNORECASE)
                if match:
                    asset_allocation_section = match.group(0)
                    break
            
            if asset_allocation_section:
                # Look for asset class patterns
                asset_class_pattern = r'([A-Za-z\s]+)\s+(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)\s+(\d{1,3}(?:\.\d{1,2})?)%'
                asset_class_matches = re.finditer(asset_class_pattern, asset_allocation_section)
                
                for match in asset_class_matches:
                    asset_class = match.group(1).strip()
                    value_str = match.group(2).strip()
                    percentage_str = match.group(3).strip()
                    
                    try:
                        value = float(value_str.replace(',', '').replace("'", ''))
                        percentage = float(percentage_str)
                        
                        allocation = {
                            "asset_class": asset_class,
                            "value": value,
                            "percentage": percentage,
                            "extraction_method": "text_pattern"
                        }
                        
                        asset_allocations.append(allocation)
                    except ValueError:
                        continue
        
        return asset_allocations
