"""
ISIN Extractor Agent for the RAG Multimodal Financial Document Processor.
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional, Tuple

from ..utils import ensure_dir, extract_isins, find_context, is_valid_isin

logger = logging.getLogger(__name__)

class ISINExtractorAgent:
    """
    ISIN Extractor Agent for extracting ISINs and related information.
    """
    
    def __init__(self, config):
        """
        Initialize the ISIN Extractor Agent.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.output_config = config["output"]
        
        logger.info("Initialized ISIN Extractor Agent")
    
    def process(self, ocr_results: Dict[str, Any], table_results: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """
        Process OCR and table results to extract ISINs.
        
        Args:
            ocr_results: OCR results
            table_results: Table detection results
            output_dir: Output directory
            
        Returns:
            Dictionary with ISIN extraction results
        """
        logger.info("Extracting ISINs from document")
        
        # Create output directory
        isins_dir = os.path.join(output_dir, "isins")
        ensure_dir(isins_dir)
        
        # Extract ISINs from OCR text
        text_isins = self._extract_isins_from_text(ocr_results["text"])
        
        # Extract ISINs from tables
        table_isins = self._extract_isins_from_tables(table_results["tables"])
        
        # Combine results
        all_isins = self._combine_isins(text_isins, table_isins)
        
        # Save results
        self._save_isins(all_isins, isins_dir)
        
        logger.info(f"ISIN extraction complete, found {len(all_isins)} ISINs")
        
        return {
            "isins": all_isins,
            "isins_dir": isins_dir
        }
    
    def _extract_isins_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract ISINs from text.
        
        Args:
            text: Text to extract ISINs from
            
        Returns:
            List of ISIN dictionaries
        """
        logger.info("Extracting ISINs from text")
        
        # Extract ISINs
        isin_codes = extract_isins(text)
        
        # Process each ISIN
        isins = []
        for isin in isin_codes:
            # Skip invalid ISINs
            if not is_valid_isin(isin):
                continue
            
            # Find context around ISIN
            context = find_context(text, isin, window=100)
            
            # Extract name
            name = self._extract_name_from_context(context, isin)
            
            # Extract quantity
            quantity = self._extract_quantity_from_context(context)
            
            # Extract price
            price = self._extract_price_from_context(context)
            
            # Extract value
            value = self._extract_value_from_context(context)
            
            # Extract currency
            currency = self._extract_currency_from_context(context)
            
            # Create ISIN dictionary
            isin_dict = {
                "isin": isin,
                "name": name,
                "quantity": quantity,
                "price": price,
                "value": value,
                "currency": currency,
                "source": "text",
                "context": context
            }
            
            isins.append(isin_dict)
        
        logger.info(f"Found {len(isins)} ISINs in text")
        
        return isins
    
    def _extract_isins_from_tables(self, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract ISINs from tables.
        
        Args:
            tables: List of tables
            
        Returns:
            List of ISIN dictionaries
        """
        logger.info("Extracting ISINs from tables")
        
        isins = []
        
        for table in tables:
            # Check if this table contains ISINs
            isin_column_index = -1
            headers = table["headers"]
            
            # Look for ISIN column
            for i, header in enumerate(headers):
                header_text = str(header).upper()
                if "ISIN" in header_text or "SECURITY" in header_text or "INSTRUMENT" in header_text:
                    isin_column_index = i
                    break
            
            # If no ISIN column found, check all cells
            if isin_column_index == -1:
                for row in table["rows"]:
                    for i, cell in enumerate(row):
                        cell_text = str(cell)
                        if re.search(r'[A-Z]{2}[A-Z0-9]{9}[0-9]', cell_text):
                            isin_column_index = i
                            break
                    if isin_column_index != -1:
                        break
            
            # If still no ISIN column found, skip this table
            if isin_column_index == -1:
                continue
            
            # Find columns for other data
            name_column_index = -1
            quantity_column_index = -1
            price_column_index = -1
            value_column_index = -1
            currency_column_index = -1
            
            for i, header in enumerate(headers):
                header_text = str(header).upper()
                
                if "NAME" in header_text or "DESCRIPTION" in header_text or "SECURITY" in header_text:
                    name_column_index = i
                
                if "QUANTITY" in header_text or "QTY" in header_text or "AMOUNT" in header_text:
                    quantity_column_index = i
                
                if "PRICE" in header_text or "RATE" in header_text:
                    price_column_index = i
                
                if "VALUE" in header_text or "TOTAL" in header_text or "MARKET" in header_text:
                    value_column_index = i
                
                if "CURRENCY" in header_text or "CCY" in header_text:
                    currency_column_index = i
            
            # Process each row
            for row in table["rows"]:
                if isin_column_index >= len(row):
                    continue
                
                # Get ISIN
                isin_cell = str(row[isin_column_index])
                isin_match = re.search(r'[A-Z]{2}[A-Z0-9]{9}[0-9]', isin_cell)
                
                if not isin_match:
                    continue
                
                isin = isin_match.group(0)
                
                # Skip invalid ISINs
                if not is_valid_isin(isin):
                    continue
                
                # Get name
                name = None
                if name_column_index != -1 and name_column_index < len(row):
                    name = str(row[name_column_index])
                
                # Get quantity
                quantity = None
                if quantity_column_index != -1 and quantity_column_index < len(row):
                    quantity_str = str(row[quantity_column_index])
                    quantity = self._parse_numeric_value(quantity_str)
                
                # Get price
                price = None
                if price_column_index != -1 and price_column_index < len(row):
                    price_str = str(row[price_column_index])
                    price = self._parse_numeric_value(price_str)
                
                # Get value
                value = None
                if value_column_index != -1 and value_column_index < len(row):
                    value_str = str(row[value_column_index])
                    value = self._parse_numeric_value(value_str)
                
                # Get currency
                currency = None
                if currency_column_index != -1 and currency_column_index < len(row):
                    currency = str(row[currency_column_index])
                
                # Create ISIN dictionary
                isin_dict = {
                    "isin": isin,
                    "name": name,
                    "quantity": quantity,
                    "price": price,
                    "value": value,
                    "currency": currency,
                    "source": f"table_{table['id']}",
                    "context": str(row)
                }
                
                isins.append(isin_dict)
        
        logger.info(f"Found {len(isins)} ISINs in tables")
        
        return isins
    
    def _combine_isins(self, text_isins: List[Dict[str, Any]], table_isins: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Combine ISINs from text and tables.
        
        Args:
            text_isins: ISINs from text
            table_isins: ISINs from tables
            
        Returns:
            Combined list of ISINs
        """
        # Create a map of ISINs to dictionaries
        isin_map = {}
        
        # Add table ISINs first (higher quality)
        for isin_dict in table_isins:
            isin = isin_dict["isin"]
            isin_map[isin] = isin_dict
        
        # Add text ISINs if they provide additional information
        for isin_dict in text_isins:
            isin = isin_dict["isin"]
            
            if isin in isin_map:
                # Merge with existing ISIN
                existing = isin_map[isin]
                
                # Keep non-null values
                for field in ["name", "quantity", "price", "value", "currency"]:
                    if existing[field] is None and isin_dict[field] is not None:
                        existing[field] = isin_dict[field]
            else:
                # Add new ISIN
                isin_map[isin] = isin_dict
        
        # Convert back to list
        return list(isin_map.values())
    
    def _save_isins(self, isins: List[Dict[str, Any]], output_dir: str) -> None:
        """
        Save ISINs to files.
        
        Args:
            isins: List of ISINs
            output_dir: Output directory
        """
        # Save all ISINs to a single JSON file
        import json
        with open(os.path.join(output_dir, "isins.json"), "w", encoding="utf-8") as f:
            json.dump(isins, f, indent=2, ensure_ascii=False)
        
        # Save to CSV
        import csv
        with open(os.path.join(output_dir, "isins.csv"), "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ISIN", "Name", "Quantity", "Price", "Value", "Currency", "Source"])
            
            for isin in isins:
                writer.writerow([
                    isin["isin"],
                    isin["name"],
                    isin["quantity"],
                    isin["price"],
                    isin["value"],
                    isin["currency"],
                    isin["source"]
                ])
    
    def _extract_name_from_context(self, context: str, isin: str) -> Optional[str]:
        """
        Extract security name from context.
        
        Args:
            context: Context around ISIN
            isin: ISIN code
            
        Returns:
            Security name or None
        """
        # Try to find name before ISIN
        name_before = re.search(r'([A-Z][A-Z\s\-\&\.]+(?:\d+(?:\.\d+)?%?)?)(?:\s+|\n)' + re.escape(isin), context)
        if name_before:
            return name_before.group(1).strip()
        
        # Try to find name after ISIN
        name_after = re.search(re.escape(isin) + r'(?:\s+|\n)([A-Z][A-Z\s\-\&\.]+(?:\d+(?:\.\d+)?%?)?)', context)
        if name_after:
            return name_after.group(1).strip()
        
        return None
    
    def _extract_quantity_from_context(self, context: str) -> Optional[float]:
        """
        Extract quantity from context.
        
        Args:
            context: Context around ISIN
            
        Returns:
            Quantity or None
        """
        # Look for quantity patterns
        quantity_patterns = [
            r'(?:QTY|QUANTITY|AMOUNT)[:\s]+([0-9,\'\.]+)',
            r'([0-9,\'\.]+)(?:\s+|\n)(?:UNITS|SHARES)'
        ]
        
        for pattern in quantity_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return self._parse_numeric_value(match.group(1))
        
        return None
    
    def _extract_price_from_context(self, context: str) -> Optional[float]:
        """
        Extract price from context.
        
        Args:
            context: Context around ISIN
            
        Returns:
            Price or None
        """
        # Look for price patterns
        price_patterns = [
            r'(?:PRICE|RATE)[:\s]+([0-9,\'\.]+)',
            r'([0-9,\'\.]+)(?:\s+|\n)(?:PER UNIT|PER SHARE)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return self._parse_numeric_value(match.group(1))
        
        return None
    
    def _extract_value_from_context(self, context: str) -> Optional[float]:
        """
        Extract value from context.
        
        Args:
            context: Context around ISIN
            
        Returns:
            Value or None
        """
        # Look for value patterns
        value_patterns = [
            r'(?:VALUE|TOTAL|MARKET VALUE)[:\s]+([0-9,\'\.]+)',
            r'([0-9,\'\.]+)(?:\s+|\n)(?:TOTAL|VALUE)'
        ]
        
        for pattern in value_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return self._parse_numeric_value(match.group(1))
        
        return None
    
    def _extract_currency_from_context(self, context: str) -> Optional[str]:
        """
        Extract currency from context.
        
        Args:
            context: Context around ISIN
            
        Returns:
            Currency or None
        """
        # Look for currency patterns
        currency_patterns = [
            r'(?:CURRENCY|CCY)[:\s]+([A-Z]{3})',
            r'([A-Z]{3})(?:\s+|\n)(?:CURRENCY|CCY)',
            r'(USD|EUR|GBP|CHF|JPY)'
        ]
        
        for pattern in currency_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        return None
    
    def _parse_numeric_value(self, value_str: str) -> Optional[float]:
        """
        Parse a numeric value from a string.
        
        Args:
            value_str: String to parse
            
        Returns:
            Parsed numeric value
        """
        if not value_str:
            return None
        
        # Remove non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d\.]', '', value_str.replace(',', '.').replace("'", ''))
        
        try:
            return float(cleaned)
        except ValueError:
            return None
