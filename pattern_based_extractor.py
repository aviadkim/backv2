"""
Pattern-Based Financial Line Extractor - Extracts financial data using pattern matching.

This module provides tools to extract financial data from text using pattern matching,
focusing on common financial line formats and key-value pairs.
"""
import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
import json
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PatternBasedExtractor:
    """
    Extracts financial data from text using pattern matching.
    """
    
    def __init__(self):
        """Initialize the pattern-based extractor."""
        self.patterns = {
            "portfolio_value": [
                r'Portfolio\s+Total\s*[:\s]+(\d[\d,.\']*)',
                r'Total\s+assets\s*[:\s]+(\d[\d,.\']*)',
                r'Portfolio\s+Value\s*[:\s]+(\d[\d,.\']*)',
                r'Total\s+Portfolio\s*[:\s]+(\d[\d,.\']*)',
                r'Total\s+Value\s*[:\s]+(\d[\d,.\']*)'
            ],
            "isin": [
                r'ISIN[:\s]+([A-Z]{2}[A-Z0-9]{9}[0-9])',
                r'ISIN\s*[:\s]*\s*([A-Z]{2}[A-Z0-9]{9}[0-9])',
                r'([A-Z]{2}[A-Z0-9]{9}[0-9])'
            ],
            "security_valuation": [
                r'Valuation\s+in\s+price\s+currency\s*[:\s]+(\d[\d,.\']*)',
                r'Valuation\s*[:\s]+(\d[\d,.\']*)',
                r'Value\s*[:\s]+(\d[\d,.\']*)',
                r'(\d[\d,.\']*)(?:\s*(?:USD|EUR|CHF|GBP))?'
            ],
            "security_description": [
                r'Description[:\s]+(.+?)(?=ISIN|Valuation|$)',
                r'Security[:\s]+(.+?)(?=ISIN|Valuation|$)',
                r'Name[:\s]+(.+?)(?=ISIN|Valuation|$)'
            ],
            "security_type": [
                r'Type[:\s]+(\w+)',
                r'Asset\s+Type[:\s]+(\w+)',
                r'Security\s+Type[:\s]+(\w+)'
            ],
            "asset_allocation": [
                r'(\w[\w\s]+)\s+(\d[\d,.\']*)\s+(\d[\d,.\']*%)',
                r'(\w[\w\s]+)\s+(\d[\d,.\']*)\s+\((\d[\d,.\']*%)\)',
                r'(\w[\w\s]+)(?:\s*:\s*|\s+)(\d[\d,.\']*)\s+(\d[\d,.\']*%)'
            ],
            "key_value_pair": [
                r'([A-Za-z][\w\s]+)[:\s]+(\d[\d,.\']*)',
                r'([A-Za-z][\w\s]+)[:\s]+([A-Za-z0-9][\w\s,.\']*)'
            ],
            "percentage": [
                r'(\d[\d,.\']*%)',
                r'(\d[\d,.\']*)\s*%',
                r'(\d[\d,.\']*)\s*percent'
            ],
            "date": [
                r'(\d{2}[./-]\d{2}[./-]\d{4})',
                r'(\d{4}[./-]\d{2}[./-]\d{2})',
                r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})'
            ],
            "currency": [
                r'Currency[:\s]+([A-Z]{3})',
                r'([A-Z]{3})\s+\d[\d,.\']*',
                r'(\d[\d,.\']*)\s+([A-Z]{3})'
            ],
            "structured_product": [
                r'Structured\s+products?\s*[:\s]+(\d[\d,.\']*)',
                r'Structured\s+products?\s*\(([^)]+)\)\s*[:\s]+(\d[\d,.\']*)',
                r'Structured\s+products?\s+\(([^)]+)\)\s+(\d[\d,.\']*)\s+(\d[\d,.\']*%)'
            ]
        }
        
        self.extracted_data = {
            "portfolio_value": [],
            "securities": [],
            "asset_allocation": [],
            "key_value_pairs": [],
            "dates": [],
            "currencies": [],
            "structured_products": []
        }
        
        self.financial_line_patterns = [
            # Pattern for "Label 123,456.78 12.34%"
            r'([A-Za-z][\w\s]+)\s+(\d[\d,.\']*)\s+(\d[\d,.\']*%)',
            
            # Pattern for "Label: 123,456.78"
            r'([A-Za-z][\w\s]+):\s+(\d[\d,.\']*)',
            
            # Pattern for "Label 123,456.78"
            r'([A-Za-z][\w\s]+)\s+(\d[\d,.\']*)',
            
            # Pattern for "Label (123,456.78)"
            r'([A-Za-z][\w\s]+)\s+\((\d[\d,.\']*)\)',
            
            # Pattern for "Label: 123,456.78 (12.34%)"
            r'([A-Za-z][\w\s]+):\s+(\d[\d,.\']*)\s+\((\d[\d,.\']*%)\)',
            
            # Pattern for "Label 123,456.78 USD"
            r'([A-Za-z][\w\s]+)\s+(\d[\d,.\']*)\s+([A-Z]{3})'
        ]
    
    def extract(self, text: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract financial data from text using pattern matching.
        
        Args:
            text: Text to extract data from
            output_dir: Directory to save output files (default: None)
        
        Returns:
            Dict containing extracted financial data
        """
        logger.info(f"Extracting financial data from text ({len(text)} chars)")
        
        # Reset data
        self.extracted_data = {
            "portfolio_value": [],
            "securities": [],
            "asset_allocation": [],
            "key_value_pairs": [],
            "dates": [],
            "currencies": [],
            "structured_products": []
        }
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Extract portfolio value
            self._extract_portfolio_value(text)
            
            # Extract securities
            self._extract_securities(text)
            
            # Extract asset allocation
            self._extract_asset_allocation(text)
            
            # Extract key-value pairs
            self._extract_key_value_pairs(text)
            
            # Extract dates
            self._extract_dates(text)
            
            # Extract currencies
            self._extract_currencies(text)
            
            # Extract structured products
            self._extract_structured_products(text)
            
            # Extract financial lines
            self._extract_financial_lines(text)
            
            # Save results if output_dir is specified
            if output_dir:
                self._save_results(output_dir)
            
            logger.info("Financial data extraction completed.")
            return self.extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting financial data: {str(e)}")
            return {"error": str(e)}
    
    def _clean_number(self, value: str) -> Optional[float]:
        """Clean a number by removing quotes, commas, etc."""
        if not value:
            return None
        
        # Replace single quotes with nothing (European number format)
        cleaned = value.replace("'", "")
        
        # Replace commas with nothing (US number format)
        cleaned = cleaned.replace(",", "")
        
        # Remove any non-numeric characters except decimal point and negative sign
        cleaned = re.sub(r'[^\d.-]', '', cleaned)
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def _clean_percentage(self, value: str) -> Optional[float]:
        """Clean a percentage value."""
        if not value:
            return None
        
        # Remove % symbol
        cleaned = value.replace("%", "")
        
        # Clean the number
        return self._clean_number(cleaned)
    
    def _extract_portfolio_value(self, text: str):
        """Extract portfolio value from text."""
        for pattern in self.patterns["portfolio_value"]:
            matches = re.finditer(pattern, text)
            for match in matches:
                value_str = match.group(1)
                value = self._clean_number(value_str)
                
                if value:
                    self.extracted_data["portfolio_value"].append({
                        "value": value,
                        "source": "text",
                        "pattern": pattern,
                        "match": match.group(0)
                    })
        
        logger.info(f"Extracted {len(self.extracted_data['portfolio_value'])} portfolio values")
    
    def _extract_securities(self, text: str):
        """Extract securities from text."""
        # Find all ISINs
        isin_matches = []
        for pattern in self.patterns["isin"]:
            for match in re.finditer(pattern, text):
                isin = match.group(1)
                if self._is_valid_isin(isin):
                    isin_matches.append({
                        "isin": isin,
                        "start": match.start(),
                        "end": match.end()
                    })
        
        # For each ISIN, extract surrounding information
        for isin_match in isin_matches:
            isin = isin_match["isin"]
            
            # Check if this ISIN is already processed
            if any(s["isin"] == isin for s in self.extracted_data["securities"]):
                continue
            
            # Get context around the ISIN
            context_start = max(0, isin_match["start"] - 200)
            context_end = min(len(text), isin_match["end"] + 200)
            context = text[context_start:context_end]
            
            # Extract description
            description = None
            for pattern in self.patterns["security_description"]:
                desc_match = re.search(pattern, context)
                if desc_match:
                    description = desc_match.group(1).strip()
                    break
            
            # If no description found, use text before ISIN
            if not description:
                before_isin = text[context_start:isin_match["start"]]
                lines = before_isin.strip().split("\n")
                if lines:
                    description = lines[-1].strip()
            
            # Extract security type
            security_type = "Unknown"
            for pattern in self.patterns["security_type"]:
                type_match = re.search(pattern, context)
                if type_match:
                    security_type = type_match.group(1).strip()
                    break
            
            # Guess security type from context
            if security_type == "Unknown":
                lower_context = context.lower()
                if "bond" in lower_context or "note" in lower_context:
                    security_type = "Bond"
                elif "equity" in lower_context or "stock" in lower_context or "share" in lower_context:
                    security_type = "Equity"
                elif "fund" in lower_context:
                    security_type = "Fund"
                elif "structured" in lower_context or "certificate" in lower_context:
                    security_type = "Structured Product"
                elif "cash" in lower_context or "liquidity" in lower_context:
                    security_type = "Cash"
            
            # Extract valuation
            valuation = None
            for pattern in self.patterns["security_valuation"]:
                val_match = re.search(pattern, context)
                if val_match:
                    valuation_str = val_match.group(1)
                    valuation = self._clean_number(valuation_str)
                    break
            
            # Create security object
            security = {
                "isin": isin,
                "description": description,
                "security_type": security_type,
                "valuation": valuation,
                "source": "text"
            }
            
            self.extracted_data["securities"].append(security)
        
        logger.info(f"Extracted {len(self.extracted_data['securities'])} securities")
    
    def _is_valid_isin(self, isin: str) -> bool:
        """Check if an ISIN is valid."""
        # Basic format check
        if not re.match(r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$', isin):
            return False
        
        # TODO: Implement checksum validation
        
        return True
    
    def _extract_asset_allocation(self, text: str):
        """Extract asset allocation from text."""
        for pattern in self.patterns["asset_allocation"]:
            matches = re.finditer(pattern, text)
            for match in matches:
                asset_class = match.group(1).strip()
                
                # Skip if this looks like a security or contains an ISIN
                if re.search(r'[A-Z]{2}[A-Z0-9]{9}[0-9]', asset_class):
                    continue
                
                # Extract value and percentage
                if len(match.groups()) >= 3:
                    value_str = match.group(2)
                    percentage_str = match.group(3)
                    
                    value = self._clean_number(value_str)
                    percentage = self._clean_percentage(percentage_str)
                    
                    if value or percentage:
                        self.extracted_data["asset_allocation"].append({
                            "asset_class": asset_class,
                            "value": value,
                            "percentage": percentage,
                            "source": "text"
                        })
        
        logger.info(f"Extracted {len(self.extracted_data['asset_allocation'])} asset allocations")
    
    def _extract_key_value_pairs(self, text: str):
        """Extract key-value pairs from text."""
        for pattern in self.patterns["key_value_pair"]:
            matches = re.finditer(pattern, text)
            for match in matches:
                key = match.group(1).strip()
                value_str = match.group(2).strip()
                
                # Try to convert value to number
                try:
                    value = self._clean_number(value_str)
                except ValueError:
                    value = value_str
                
                self.extracted_data["key_value_pairs"].append({
                    "key": key,
                    "value": value,
                    "source": "text"
                })
        
        logger.info(f"Extracted {len(self.extracted_data['key_value_pairs'])} key-value pairs")
    
    def _extract_dates(self, text: str):
        """Extract dates from text."""
        for pattern in self.patterns["date"]:
            matches = re.finditer(pattern, text)
            for match in matches:
                date_str = match.group(1)
                
                self.extracted_data["dates"].append({
                    "date": date_str,
                    "source": "text"
                })
        
        logger.info(f"Extracted {len(self.extracted_data['dates'])} dates")
    
    def _extract_currencies(self, text: str):
        """Extract currencies from text."""
        for pattern in self.patterns["currency"]:
            matches = re.finditer(pattern, text)
            for match in matches:
                if len(match.groups()) == 1:
                    currency = match.group(1)
                    
                    self.extracted_data["currencies"].append({
                        "currency": currency,
                        "source": "text"
                    })
                elif len(match.groups()) == 2:
                    # Pattern with amount and currency
                    amount_str = match.group(1)
                    currency = match.group(2)
                    
                    amount = self._clean_number(amount_str)
                    
                    self.extracted_data["currencies"].append({
                        "currency": currency,
                        "amount": amount,
                        "source": "text"
                    })
        
        logger.info(f"Extracted {len(self.extracted_data['currencies'])} currencies")
    
    def _extract_structured_products(self, text: str):
        """Extract structured products from text."""
        for pattern in self.patterns["structured_product"]:
            matches = re.finditer(pattern, text)
            for match in matches:
                if len(match.groups()) == 1:
                    # Simple pattern with just value
                    value_str = match.group(1)
                    value = self._clean_number(value_str)
                    
                    if value:
                        self.extracted_data["structured_products"].append({
                            "type": "Structured products",
                            "value": value,
                            "source": "text"
                        })
                elif len(match.groups()) == 2:
                    # Pattern with type and value
                    product_type = match.group(1).strip()
                    value_str = match.group(2)
                    value = self._clean_number(value_str)
                    
                    if value:
                        self.extracted_data["structured_products"].append({
                            "type": f"Structured products ({product_type})",
                            "value": value,
                            "source": "text"
                        })
                elif len(match.groups()) == 3:
                    # Pattern with type, value, and percentage
                    product_type = match.group(1).strip()
                    value_str = match.group(2)
                    percentage_str = match.group(3)
                    
                    value = self._clean_number(value_str)
                    percentage = self._clean_percentage(percentage_str)
                    
                    if value:
                        self.extracted_data["structured_products"].append({
                            "type": f"Structured products ({product_type})",
                            "value": value,
                            "percentage": percentage,
                            "source": "text"
                        })
        
        logger.info(f"Extracted {len(self.extracted_data['structured_products'])} structured products")
    
    def _extract_financial_lines(self, text: str):
        """Extract financial lines from text."""
        # Split text into lines
        lines = text.split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try each pattern
            for pattern in self.financial_line_patterns:
                match = re.search(pattern, line)
                if match:
                    # Extract components
                    label = match.group(1).strip()
                    
                    # Skip if this looks like a header
                    if label.lower() in ["page", "date", "time", "report"]:
                        continue
                    
                    # Process based on the number of groups
                    if len(match.groups()) == 2:
                        # Label and value
                        value_str = match.group(2)
                        value = self._clean_number(value_str)
                        
                        if value is not None:
                            # Determine the type of financial line
                            line_type = self._determine_financial_line_type(label, line)
                            
                            if line_type == "asset_allocation":
                                self.extracted_data["asset_allocation"].append({
                                    "asset_class": label,
                                    "value": value,
                                    "source": "text"
                                })
                            elif line_type == "portfolio_value" and "total" in label.lower():
                                self.extracted_data["portfolio_value"].append({
                                    "value": value,
                                    "source": "text",
                                    "pattern": pattern,
                                    "match": line
                                })
                            else:
                                self.extracted_data["key_value_pairs"].append({
                                    "key": label,
                                    "value": value,
                                    "source": "text"
                                })
                    
                    elif len(match.groups()) == 3:
                        # Label, value, and percentage/currency
                        value_str = match.group(2)
                        third_str = match.group(3)
                        
                        value = self._clean_number(value_str)
                        
                        # Check if third group is a percentage
                        if "%" in third_str:
                            percentage = self._clean_percentage(third_str)
                            
                            # Determine the type of financial line
                            line_type = self._determine_financial_line_type(label, line)
                            
                            if line_type == "asset_allocation":
                                self.extracted_data["asset_allocation"].append({
                                    "asset_class": label,
                                    "value": value,
                                    "percentage": percentage,
                                    "source": "text"
                                })
                            else:
                                self.extracted_data["key_value_pairs"].append({
                                    "key": label,
                                    "value": value,
                                    "percentage": percentage,
                                    "source": "text"
                                })
                        
                        # Check if third group is a currency
                        elif re.match(r'^[A-Z]{3}$', third_str):
                            currency = third_str
                            
                            self.extracted_data["key_value_pairs"].append({
                                "key": label,
                                "value": value,
                                "currency": currency,
                                "source": "text"
                            })
                    
                    # Found a match, move to next line
                    break
    
    def _determine_financial_line_type(self, label: str, line: str) -> str:
        """Determine the type of financial line based on label and context."""
        label_lower = label.lower()
        line_lower = line.lower()
        
        # Check for portfolio value
        if "total" in label_lower and ("portfolio" in label_lower or "assets" in label_lower):
            return "portfolio_value"
        
        # Check for asset allocation
        if any(keyword in label_lower for keyword in ["bonds", "equities", "liquidity", "cash", "structured", "real estate", "alternative", "precious metals"]):
            return "asset_allocation"
        
        # Check for structured products
        if "structured" in label_lower:
            return "structured_product"
        
        # Default to key-value pair
        return "key_value_pair"
    
    def _save_results(self, output_dir):
        """Save extraction results."""
        # Save extracted data as JSON
        json_path = os.path.join(output_dir, "pattern_extracted_data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.extracted_data, f, indent=2)
        
        logger.info(f"Saved extraction results to {json_path}")
    
    def get_best_portfolio_value(self) -> Optional[float]:
        """Get the best portfolio value based on frequency."""
        if not self.extracted_data["portfolio_value"]:
            return None
        
        # Count occurrences of each value
        value_counts = defaultdict(int)
        for item in self.extracted_data["portfolio_value"]:
            value = item["value"]
            value_counts[value] += 1
        
        # Find the most frequent value
        most_frequent_value = max(value_counts.items(), key=lambda x: x[1])[0]
        
        return most_frequent_value
    
    def get_securities_by_type(self, security_type: str) -> List[Dict[str, Any]]:
        """
        Get securities of a specific type.
        
        Args:
            security_type: Type of securities to retrieve
        
        Returns:
            List of securities of the specified type
        """
        return [s for s in self.extracted_data["securities"] if s["security_type"] == security_type]
    
    def get_asset_allocation_by_class(self, asset_class: str) -> List[Dict[str, Any]]:
        """
        Get asset allocation for a specific asset class.
        
        Args:
            asset_class: Asset class to retrieve
        
        Returns:
            List of asset allocations for the specified class
        """
        return [a for a in self.extracted_data["asset_allocation"] if asset_class.lower() in a["asset_class"].lower()]
    
    def get_structured_products(self) -> List[Dict[str, Any]]:
        """
        Get all structured products.
        
        Returns:
            List of structured products
        """
        # Combine structured products from dedicated extraction and asset allocation
        products = list(self.extracted_data["structured_products"])
        
        # Add structured products from asset allocation
        for allocation in self.extracted_data["asset_allocation"]:
            if "structured" in allocation["asset_class"].lower():
                products.append(allocation)
        
        return products

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract financial data from text using pattern matching.")
    parser.add_argument("file_path", help="Path to the text file")
    parser.add_argument("--output-dir", help="Directory to save output files")
    
    args = parser.parse_args()
    
    # Check if the file exists
    if not os.path.exists(args.file_path):
        logger.error(f"Error: File not found: {args.file_path}")
        return 1
    
    # Read the text file
    with open(args.file_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Extract financial data
    extractor = PatternBasedExtractor()
    result = extractor.extract(text, output_dir=args.output_dir)
    
    # Print summary
    print("\nPattern-Based Extraction Summary:")
    print("===============================")
    
    portfolio_value = extractor.get_best_portfolio_value()
    if portfolio_value:
        print(f"Portfolio Value: {portfolio_value:,.2f}")
    else:
        print("Portfolio Value: Not found")
    
    print(f"Securities: {len(result['securities'])}")
    print(f"Asset Allocations: {len(result['asset_allocation'])}")
    print(f"Key-Value Pairs: {len(result['key_value_pairs'])}")
    print(f"Dates: {len(result['dates'])}")
    print(f"Currencies: {len(result['currencies'])}")
    print(f"Structured Products: {len(result['structured_products'])}")
    
    return 0

if __name__ == "__main__":
    main()
