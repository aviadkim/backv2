"""
ISIN and Security Information Extractor - Extracts and validates security information.

This module provides tools to extract and validate ISIN codes and security information
from financial documents, including description, type, and valuation.
"""
import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Set, Union
import json
import pandas as pd
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ISINSecurityExtractor:
    """
    Extracts and validates ISIN codes and security information from financial documents.
    """
    
    def __init__(self):
        """Initialize the ISIN and security information extractor."""
        self.securities = []
        self.isin_validation_results = {}
    
    def extract(self, tables: List[Dict[str, Any]], text: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract and validate ISIN codes and security information.
        
        Args:
            tables: List of tables extracted from the document
            text: Text extracted from the document
            output_dir: Directory to save output files (default: None)
        
        Returns:
            Dict containing extracted securities and validation results
        """
        logger.info("Extracting ISIN codes and security information")
        
        # Reset data
        self.securities = []
        self.isin_validation_results = {}
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Extract securities from tables
            self._extract_from_tables(tables)
            
            # Extract securities from text
            self._extract_from_text(text)
            
            # Deduplicate securities
            self._deduplicate_securities()
            
            # Validate ISINs
            self._validate_isins()
            
            # Consolidate security information
            self._consolidate_security_information()
            
            # Save results if output_dir is specified
            if output_dir:
                self._save_results(output_dir)
            
            logger.info("ISIN and security information extraction completed.")
            return {
                "securities": self.securities,
                "isin_validation": self.isin_validation_results
            }
            
        except Exception as e:
            logger.error(f"Error extracting ISIN and security information: {str(e)}")
            return {"error": str(e)}
    
    def _clean_number(self, value: Union[str, float]) -> Optional[float]:
        """Clean a number by removing quotes, commas, etc."""
        if value is None:
            return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        value_str = str(value)
        
        # Replace single quotes with nothing (European number format)
        cleaned = value_str.replace("'", "")
        
        # Replace commas with nothing (US number format)
        cleaned = cleaned.replace(",", "")
        
        # Remove any non-numeric characters except decimal point and negative sign
        cleaned = re.sub(r'[^\d.-]', '', cleaned)
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def _extract_from_tables(self, tables: List[Dict[str, Any]]):
        """Extract securities from tables."""
        # Look for securities tables
        securities_tables = []
        
        for table in tables:
            if "dataframe" not in table:
                continue
            
            df = table["dataframe"]
            
            # Convert DataFrame to string for easier searching
            df_str = df.to_string().lower()
            
            # Check if this table contains securities
            if any(keyword in df_str for keyword in ["isin", "security", "description", "nominal", "quantity"]):
                securities_tables.append(table)
        
        # Process securities tables
        for table in securities_tables:
            df = table["dataframe"]
            
            # Try to identify columns
            isin_col = None
            description_col = None
            type_col = None
            valuation_col = None
            
            # Check column names
            for col in df.columns:
                col_str = str(col).lower()
                
                if "isin" in col_str:
                    isin_col = col
                elif any(keyword in col_str for keyword in ["description", "security", "name"]):
                    description_col = col
                elif any(keyword in col_str for keyword in ["type", "asset type", "security type"]):
                    type_col = col
                elif any(keyword in col_str for keyword in ["valuation", "value", "amount", "countervalue"]):
                    valuation_col = col
            
            # If columns not identified by name, try to infer from content
            if not isin_col or not description_col:
                # Look for columns containing ISINs
                for col in df.columns:
                    col_values = df[col].astype(str)
                    
                    # Check if column contains ISINs
                    has_isin = False
                    for cell in col_values:
                        if re.search(r'[A-Z]{2}[A-Z0-9]{9}[0-9]', cell):
                            has_isin = True
                            break
                    
                    if has_isin:
                        isin_col = col
                        break
                
                # Assume first column is description if not found
                if not description_col:
                    for col in df.columns:
                        if col != isin_col:
                            description_col = col
                            break
                
                # Look for columns containing numbers (potential valuation)
                if not valuation_col:
                    for col in df.columns:
                        if col == isin_col or col == description_col:
                            continue
                        
                        # Check if column contains numbers
                        has_numbers = False
                        for cell in df[col]:
                            if isinstance(cell, (int, float)) or (isinstance(cell, str) and re.search(r'\d', cell)):
                                has_numbers = True
                                break
                        
                        if has_numbers:
                            valuation_col = col
                            break
            
            # Process rows
            for _, row in df.iterrows():
                # Skip empty rows
                if (isin_col and (pd.isna(row[isin_col]) or str(row[isin_col]).strip() == "")) and \
                   (description_col and (pd.isna(row[description_col]) or str(row[description_col]).strip() == "")):
                    continue
                
                # Extract ISIN
                isin = None
                if isin_col:
                    isin_value = str(row[isin_col]).strip()
                    isin_match = re.search(r'[A-Z]{2}[A-Z0-9]{9}[0-9]', isin_value)
                    if isin_match:
                        isin = isin_match.group(0)
                
                # Skip if no ISIN found
                if not isin:
                    continue
                
                # Extract description
                description = None
                if description_col:
                    description = str(row[description_col]).strip()
                
                # Extract security type
                security_type = "Unknown"
                if type_col:
                    security_type = str(row[type_col]).strip()
                else:
                    # Try to infer security type from description
                    if description:
                        description_lower = description.lower()
                        if "bond" in description_lower or "note" in description_lower:
                            security_type = "Bond"
                        elif "equity" in description_lower or "stock" in description_lower or "share" in description_lower:
                            security_type = "Equity"
                        elif "fund" in description_lower:
                            security_type = "Fund"
                        elif "structured" in description_lower or "certificate" in description_lower:
                            security_type = "Structured Product"
                        elif "cash" in description_lower or "liquidity" in description_lower:
                            security_type = "Cash"
                
                # Extract valuation
                valuation = None
                if valuation_col:
                    valuation = self._clean_number(row[valuation_col])
                
                # Create security object
                security = {
                    "isin": isin,
                    "description": description,
                    "security_type": security_type,
                    "valuation": valuation,
                    "source": "table",
                    "extraction_method": table.get("extraction_method", "unknown"),
                    "table_number": table.get("table_number", 0),
                    "page": table.get("page_number", 0)
                }
                
                self.securities.append(security)
        
        logger.info(f"Extracted {len(self.securities)} securities from tables")
    
    def _extract_from_text(self, text: str):
        """Extract securities from text."""
        # Extract ISINs
        isin_pattern = r'([A-Z]{2}[A-Z0-9]{9}[0-9])'
        
        isin_matches = re.finditer(isin_pattern, text)
        for match in isin_matches:
            isin = match.group(1)
            
            # Skip if this ISIN is already processed
            if any(s["isin"] == isin for s in self.securities):
                continue
            
            # Get context around the ISIN
            context_start = max(0, match.start() - 200)
            context_end = min(len(text), match.end() + 200)
            context = text[context_start:context_end]
            
            # Extract description
            description = None
            description_pattern = r'([A-Za-z][\w\s]+)\s+' + re.escape(isin)
            desc_match = re.search(description_pattern, context)
            if desc_match:
                description = desc_match.group(1).strip()
            
            # If no description found, look after ISIN
            if not description:
                after_isin = text[match.end():context_end]
                lines = after_isin.strip().split("\n")
                if lines:
                    description = lines[0].strip()
            
            # Extract security type
            security_type = "Unknown"
            if description:
                description_lower = description.lower()
                if "bond" in description_lower or "note" in description_lower:
                    security_type = "Bond"
                elif "equity" in description_lower or "stock" in description_lower or "share" in description_lower:
                    security_type = "Equity"
                elif "fund" in description_lower:
                    security_type = "Fund"
                elif "structured" in description_lower or "certificate" in description_lower:
                    security_type = "Structured Product"
                elif "cash" in description_lower or "liquidity" in description_lower:
                    security_type = "Cash"
            
            # Extract valuation
            valuation = None
            valuation_pattern = r'(\d[\d,.\']*)\s*(?:USD|EUR|CHF|GBP)?'
            val_matches = re.finditer(valuation_pattern, context)
            
            for val_match in val_matches:
                val_str = val_match.group(1)
                val = self._clean_number(val_str)
                
                if val and val > 1000:  # Assume valuation is large
                    valuation = val
                    break
            
            # Create security object
            security = {
                "isin": isin,
                "description": description,
                "security_type": security_type,
                "valuation": valuation,
                "source": "text"
            }
            
            self.securities.append(security)
        
        logger.info(f"Extracted {len(self.securities)} securities from text")
    
    def _deduplicate_securities(self):
        """Deduplicate securities based on ISIN."""
        if not self.securities:
            return
        
        # Group securities by ISIN
        securities_by_isin = defaultdict(list)
        
        for security in self.securities:
            isin = security["isin"]
            securities_by_isin[isin].append(security)
        
        # Deduplicate
        deduplicated_securities = []
        
        for isin, securities in securities_by_isin.items():
            if len(securities) == 1:
                # Only one security with this ISIN
                deduplicated_securities.append(securities[0])
            else:
                # Multiple securities with the same ISIN
                # Prioritize table sources over text sources
                table_securities = [s for s in securities if s["source"] == "table"]
                
                if table_securities:
                    # Use the first table security
                    deduplicated_securities.append(table_securities[0])
                else:
                    # Use the first security
                    deduplicated_securities.append(securities[0])
        
        logger.info(f"Deduplicated {len(self.securities)} securities to {len(deduplicated_securities)} unique securities")
        self.securities = deduplicated_securities
    
    def _validate_isins(self):
        """Validate ISINs."""
        for security in self.securities:
            isin = security["isin"]
            
            # Basic format check
            if not re.match(r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$', isin):
                self.isin_validation_results[isin] = {
                    "valid": False,
                    "reason": "Invalid format"
                }
                continue
            
            # Check country code
            country_code = isin[:2]
            if not self._is_valid_country_code(country_code):
                self.isin_validation_results[isin] = {
                    "valid": False,
                    "reason": f"Invalid country code: {country_code}"
                }
                continue
            
            # Check checksum
            if not self._validate_isin_checksum(isin):
                self.isin_validation_results[isin] = {
                    "valid": False,
                    "reason": "Invalid checksum"
                }
                continue
            
            # ISIN is valid
            self.isin_validation_results[isin] = {
                "valid": True,
                "reason": "Valid ISIN"
            }
        
        # Count valid and invalid ISINs
        valid_count = sum(1 for result in self.isin_validation_results.values() if result["valid"])
        invalid_count = len(self.isin_validation_results) - valid_count
        
        logger.info(f"Validated {len(self.isin_validation_results)} ISINs: {valid_count} valid, {invalid_count} invalid")
    
    def _is_valid_country_code(self, country_code: str) -> bool:
        """Check if a country code is valid."""
        # List of valid country codes
        valid_country_codes = {
            "AD", "AE", "AF", "AG", "AI", "AL", "AM", "AO", "AQ", "AR", "AS", "AT", "AU", "AW", "AX", "AZ",
            "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BL", "BM", "BN", "BO", "BQ", "BR", "BS",
            "BT", "BV", "BW", "BY", "BZ", "CA", "CC", "CD", "CF", "CG", "CH", "CI", "CK", "CL", "CM", "CN",
            "CO", "CR", "CU", "CV", "CW", "CX", "CY", "CZ", "DE", "DJ", "DK", "DM", "DO", "DZ", "EC", "EE",
            "EG", "EH", "ER", "ES", "ET", "FI", "FJ", "FK", "FM", "FO", "FR", "GA", "GB", "GD", "GE", "GF",
            "GG", "GH", "GI", "GL", "GM", "GN", "GP", "GQ", "GR", "GS", "GT", "GU", "GW", "GY", "HK", "HM",
            "HN", "HR", "HT", "HU", "ID", "IE", "IL", "IM", "IN", "IO", "IQ", "IR", "IS", "IT", "JE", "JM",
            "JO", "JP", "KE", "KG", "KH", "KI", "KM", "KN", "KP", "KR", "KW", "KY", "KZ", "LA", "LB", "LC",
            "LI", "LK", "LR", "LS", "LT", "LU", "LV", "LY", "MA", "MC", "MD", "ME", "MF", "MG", "MH", "MK",
            "ML", "MM", "MN", "MO", "MP", "MQ", "MR", "MS", "MT", "MU", "MV", "MW", "MX", "MY", "MZ", "NA",
            "NC", "NE", "NF", "NG", "NI", "NL", "NO", "NP", "NR", "NU", "NZ", "OM", "PA", "PE", "PF", "PG",
            "PH", "PK", "PL", "PM", "PN", "PR", "PS", "PT", "PW", "PY", "QA", "RE", "RO", "RS", "RU", "RW",
            "SA", "SB", "SC", "SD", "SE", "SG", "SH", "SI", "SJ", "SK", "SL", "SM", "SN", "SO", "SR", "SS",
            "ST", "SV", "SX", "SY", "SZ", "TC", "TD", "TF", "TG", "TH", "TJ", "TK", "TL", "TM", "TN", "TO",
            "TR", "TT", "TV", "TW", "TZ", "UA", "UG", "UM", "US", "UY", "UZ", "VA", "VC", "VE", "VG", "VI",
            "VN", "VU", "WF", "WS", "XS", "YE", "YT", "ZA", "ZM", "ZW"
        }
        
        return country_code in valid_country_codes
    
    def _validate_isin_checksum(self, isin: str) -> bool:
        """Validate ISIN checksum."""
        # Convert letters to numbers
        converted = ""
        for char in isin[:-1]:  # Exclude the check digit
            if char.isalpha():
                # Convert letter to number (A=10, B=11, ..., Z=35)
                converted += str(ord(char) - ord('A') + 10)
            else:
                converted += char
        
        # Calculate checksum
        total = 0
        for i, digit in enumerate(reversed(converted)):
            value = int(digit)
            if i % 2 == 0:
                value *= 2
                if value > 9:
                    value -= 9
            total += value
        
        check_digit = (10 - (total % 10)) % 10
        
        # Compare with the actual check digit
        return check_digit == int(isin[-1])
    
    def _consolidate_security_information(self):
        """Consolidate security information from multiple sources."""
        # Group securities by ISIN
        securities_by_isin = defaultdict(list)
        
        for security in self.securities:
            isin = security["isin"]
            securities_by_isin[isin].append(security)
        
        # Consolidate information
        consolidated_securities = []
        
        for isin, securities in securities_by_isin.items():
            if len(securities) == 1:
                # Only one security with this ISIN
                consolidated_securities.append(securities[0])
            else:
                # Multiple securities with the same ISIN
                # Consolidate information
                consolidated = {
                    "isin": isin,
                    "description": None,
                    "security_type": None,
                    "valuation": None,
                    "sources": []
                }
                
                # Collect all values
                descriptions = []
                security_types = []
                valuations = []
                
                for security in securities:
                    if security["description"]:
                        descriptions.append(security["description"])
                    
                    if security["security_type"] and security["security_type"] != "Unknown":
                        security_types.append(security["security_type"])
                    
                    if security["valuation"]:
                        valuations.append(security["valuation"])
                    
                    consolidated["sources"].append({
                        "source": security["source"],
                        "extraction_method": security.get("extraction_method", "unknown"),
                        "description": security["description"],
                        "security_type": security["security_type"],
                        "valuation": security["valuation"]
                    })
                
                # Use the most common values
                if descriptions:
                    description_counts = defaultdict(int)
                    for desc in descriptions:
                        description_counts[desc] += 1
                    consolidated["description"] = max(description_counts.items(), key=lambda x: x[1])[0]
                
                if security_types:
                    type_counts = defaultdict(int)
                    for type_ in security_types:
                        type_counts[type_] += 1
                    consolidated["security_type"] = max(type_counts.items(), key=lambda x: x[1])[0]
                else:
                    consolidated["security_type"] = "Unknown"
                
                if valuations:
                    # Use the median valuation
                    valuations.sort()
                    if len(valuations) % 2 == 0:
                        consolidated["valuation"] = (valuations[len(valuations) // 2 - 1] + valuations[len(valuations) // 2]) / 2
                    else:
                        consolidated["valuation"] = valuations[len(valuations) // 2]
                
                consolidated_securities.append(consolidated)
        
        logger.info(f"Consolidated {len(self.securities)} securities to {len(consolidated_securities)} unique securities")
        self.securities = consolidated_securities
    
    def _save_results(self, output_dir):
        """Save extraction results."""
        # Save securities as JSON
        securities_path = os.path.join(output_dir, "securities.json")
        with open(securities_path, "w", encoding="utf-8") as f:
            json.dump(self.securities, f, indent=2)
        
        # Save ISIN validation results as JSON
        validation_path = os.path.join(output_dir, "isin_validation.json")
        with open(validation_path, "w", encoding="utf-8") as f:
            json.dump(self.isin_validation_results, f, indent=2)
        
        logger.info(f"Saved extraction results to {output_dir}")
    
    def get_securities(self) -> List[Dict[str, Any]]:
        """
        Get extracted securities.
        
        Returns:
            List of securities
        """
        return self.securities
    
    def get_securities_by_type(self, security_type: str) -> List[Dict[str, Any]]:
        """
        Get securities of a specific type.
        
        Args:
            security_type: Type of securities to retrieve
        
        Returns:
            List of securities of the specified type
        """
        return [s for s in self.securities if s["security_type"] == security_type]
    
    def get_valid_securities(self) -> List[Dict[str, Any]]:
        """
        Get securities with valid ISINs.
        
        Returns:
            List of securities with valid ISINs
        """
        return [s for s in self.securities if self.isin_validation_results.get(s["isin"], {}).get("valid", False)]
    
    def get_invalid_securities(self) -> List[Dict[str, Any]]:
        """
        Get securities with invalid ISINs.
        
        Returns:
            List of securities with invalid ISINs
        """
        return [s for s in self.securities if not self.isin_validation_results.get(s["isin"], {}).get("valid", False)]
    
    def get_security_by_isin(self, isin: str) -> Optional[Dict[str, Any]]:
        """
        Get a security by its ISIN.
        
        Args:
            isin: ISIN of the security to retrieve
        
        Returns:
            Security or None if not found
        """
        for security in self.securities:
            if security["isin"] == isin:
                return security
        return None
    
    def get_top_securities(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get the top N securities by valuation.
        
        Args:
            n: Number of securities to retrieve (default: 5)
        
        Returns:
            List of top N securities by valuation
        """
        # Filter securities with valuation
        securities_with_valuation = [s for s in self.securities if s.get("valuation")]
        
        # Sort by valuation (descending)
        sorted_securities = sorted(securities_with_valuation, key=lambda s: s["valuation"], reverse=True)
        
        return sorted_securities[:n]

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract and validate ISIN codes and security information.")
    parser.add_argument("tables_file", help="Path to the tables JSON file")
    parser.add_argument("text_file", help="Path to the text file")
    parser.add_argument("--output-dir", help="Directory to save output files")
    
    args = parser.parse_args()
    
    # Check if the files exist
    if not os.path.exists(args.tables_file):
        logger.error(f"Error: Tables file not found: {args.tables_file}")
        return 1
    
    if not os.path.exists(args.text_file):
        logger.error(f"Error: Text file not found: {args.text_file}")
        return 1
    
    # Read the tables
    with open(args.tables_file, "r", encoding="utf-8") as f:
        tables_data = json.load(f)
    
    # Read the text
    with open(args.text_file, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Convert tables to DataFrames
    tables = []
    for table in tables_data:
        if "data" in table and "headers" in table:
            df = pd.DataFrame(table["data"], columns=table["headers"])
            table_with_df = dict(table)
            table_with_df["dataframe"] = df
            tables.append(table_with_df)
    
    # Extract and validate ISIN codes and security information
    extractor = ISINSecurityExtractor()
    result = extractor.extract(tables, text, output_dir=args.output_dir)
    
    # Print summary
    print("\nISIN and Security Information Extraction Summary:")
    print("==============================================")
    
    print(f"Securities: {len(result['securities'])}")
    
    valid_count = sum(1 for result in extractor.isin_validation_results.values() if result["valid"])
    invalid_count = len(extractor.isin_validation_results) - valid_count
    
    print(f"Valid ISINs: {valid_count}")
    print(f"Invalid ISINs: {invalid_count}")
    
    # Print top securities
    print("\nTop 5 Securities by Valuation:")
    for i, security in enumerate(extractor.get_top_securities(5), 1):
        print(f"{i}. {security['isin']} - {security['description']}: {security['valuation']:,.2f}")
    
    # Print security types
    security_types = defaultdict(int)
    for security in result["securities"]:
        security_types[security["security_type"]] += 1
    
    print("\nSecurity Types:")
    for type_, count in security_types.items():
        print(f"{type_}: {count}")
    
    return 0

if __name__ == "__main__":
    main()
