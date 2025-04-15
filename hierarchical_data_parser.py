"""
Hierarchical Data Parser - Parses hierarchical financial data.

This module provides tools to parse hierarchical financial data, identifying
totals, subtotals, and their components.
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

class HierarchicalDataParser:
    """
    Parses hierarchical financial data, identifying totals, subtotals, and their components.
    """
    
    def __init__(self):
        """Initialize the hierarchical data parser."""
        self.hierarchical_data = {
            "portfolio": None,
            "asset_allocation": [],
            "securities": []
        }
        
        # Keywords for identifying totals and subtotals
        self.total_keywords = [
            "total", "sum", "subtotal", "sub-total", "sub total", "grand total"
        ]
    
    def parse(self, tables: List[Dict[str, Any]], text: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse hierarchical financial data from tables and text.
        
        Args:
            tables: List of tables extracted from the document
            text: Text extracted from the document
            output_dir: Directory to save output files (default: None)
        
        Returns:
            Dict containing hierarchical financial data
        """
        logger.info("Parsing hierarchical financial data")
        
        # Reset data
        self.hierarchical_data = {
            "portfolio": None,
            "asset_allocation": [],
            "securities": []
        }
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Parse portfolio value
            self._parse_portfolio_value(tables, text)
            
            # Parse asset allocation
            self._parse_asset_allocation(tables, text)
            
            # Parse securities
            self._parse_securities(tables, text)
            
            # Save results if output_dir is specified
            if output_dir:
                self._save_results(output_dir)
            
            logger.info("Hierarchical data parsing completed.")
            return self.hierarchical_data
            
        except Exception as e:
            logger.error(f"Error parsing hierarchical data: {str(e)}")
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
    
    def _clean_percentage(self, value: Union[str, float]) -> Optional[float]:
        """Clean a percentage value."""
        if value is None:
            return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        value_str = str(value)
        
        # Remove % symbol
        cleaned = value_str.replace("%", "")
        
        # Clean the number
        return self._clean_number(cleaned)
    
    def _parse_portfolio_value(self, tables: List[Dict[str, Any]], text: str):
        """Parse portfolio value from tables and text."""
        # Look for portfolio value in tables
        for table in tables:
            if "dataframe" not in table:
                continue
            
            df = table["dataframe"]
            
            # Convert DataFrame to string for easier searching
            df_str = df.to_string().lower()
            
            # Check if this table contains portfolio value
            if any(keyword in df_str for keyword in ["portfolio total", "total assets", "portfolio value"]):
                # Look for rows containing portfolio value
                for _, row in df.iterrows():
                    row_str = " ".join(str(x).lower() for x in row.values)
                    
                    if any(keyword in row_str for keyword in ["portfolio total", "total assets", "portfolio value"]):
                        # Extract the value
                        for cell in row:
                            value = self._clean_number(cell)
                            if value and value > 1000:  # Assume portfolio value is large
                                self.hierarchical_data["portfolio"] = {
                                    "value": value,
                                    "source": "table",
                                    "extraction_method": table.get("extraction_method", "unknown"),
                                    "table_number": table.get("table_number", 0),
                                    "page": table.get("page_number", 0)
                                }
                                break
        
        # If not found in tables, look in text
        if not self.hierarchical_data["portfolio"]:
            # Look for portfolio value in text
            portfolio_value_patterns = [
                r'Portfolio\s+Total\s*[:\s]+(\d[\d,.\']*)',
                r'Total\s+assets\s*[:\s]+(\d[\d,.\']*)',
                r'Portfolio\s+Value\s*[:\s]+(\d[\d,.\']*)',
                r'Total\s+Portfolio\s*[:\s]+(\d[\d,.\']*)',
                r'Total\s+Value\s*[:\s]+(\d[\d,.\']*)'
            ]
            
            for pattern in portfolio_value_patterns:
                match = re.search(pattern, text)
                if match:
                    value_str = match.group(1)
                    value = self._clean_number(value_str)
                    
                    if value:
                        self.hierarchical_data["portfolio"] = {
                            "value": value,
                            "source": "text",
                            "pattern": pattern,
                            "match": match.group(0)
                        }
                        break
        
        if self.hierarchical_data["portfolio"]:
            logger.info(f"Parsed portfolio value: {self.hierarchical_data['portfolio']['value']:,.2f}")
        else:
            logger.warning("Could not parse portfolio value")
    
    def _parse_asset_allocation(self, tables: List[Dict[str, Any]], text: str):
        """Parse asset allocation from tables and text."""
        # Look for asset allocation tables
        asset_allocation_tables = []
        
        for table in tables:
            if "dataframe" not in table:
                continue
            
            df = table["dataframe"]
            
            # Convert DataFrame to string for easier searching
            df_str = df.to_string().lower()
            
            # Check if this table contains asset allocation
            if any(keyword in df_str for keyword in ["asset allocation", "asset class", "allocation"]):
                asset_allocation_tables.append(table)
        
        # Process asset allocation tables
        for table in asset_allocation_tables:
            df = table["dataframe"]
            
            # Try to identify columns
            asset_class_col = None
            value_col = None
            percentage_col = None
            
            # Check column names
            for col in df.columns:
                col_str = str(col).lower()
                
                if any(keyword in col_str for keyword in ["asset", "class", "allocation"]):
                    asset_class_col = col
                elif any(keyword in col_str for keyword in ["value", "amount", "countervalue"]):
                    value_col = col
                elif any(keyword in col_str for keyword in ["percent", "weight", "%"]):
                    percentage_col = col
            
            # If columns not identified by name, try to infer from content
            if not asset_class_col or not value_col:
                # Assume first column is asset class
                asset_class_col = df.columns[0]
                
                # Look for columns containing numbers
                numeric_cols = []
                for col in df.columns:
                    if col == asset_class_col:
                        continue
                    
                    # Check if column contains numbers
                    has_numbers = False
                    for cell in df[col]:
                        if isinstance(cell, (int, float)) or (isinstance(cell, str) and re.search(r'\d', cell)):
                            has_numbers = True
                            break
                    
                    if has_numbers:
                        numeric_cols.append(col)
                
                if len(numeric_cols) >= 2:
                    # Assume first numeric column is value and second is percentage
                    value_col = numeric_cols[0]
                    percentage_col = numeric_cols[1]
                elif len(numeric_cols) == 1:
                    # Assume the only numeric column is value
                    value_col = numeric_cols[0]
            
            # Process rows
            hierarchy = []
            current_level = 0
            current_path = []
            
            for _, row in df.iterrows():
                # Skip empty rows
                if pd.isna(row[asset_class_col]) or str(row[asset_class_col]).strip() == "":
                    continue
                
                asset_class = str(row[asset_class_col]).strip()
                
                # Skip header rows
                if asset_class.lower() in ["asset class", "asset allocation", "allocation"]:
                    continue
                
                # Extract value and percentage
                value = None
                percentage = None
                
                if value_col:
                    value = self._clean_number(row[value_col])
                
                if percentage_col:
                    percentage = self._clean_percentage(row[percentage_col])
                
                # Determine level based on indentation or formatting
                level = self._determine_level(asset_class)
                
                # Update current path
                if level > current_level:
                    # Going deeper in hierarchy
                    current_path.append(asset_class)
                elif level < current_level:
                    # Going back up in hierarchy
                    current_path = current_path[:level]
                    current_path.append(asset_class)
                else:
                    # Same level
                    if current_path:
                        current_path[-1] = asset_class
                    else:
                        current_path.append(asset_class)
                
                current_level = level
                
                # Check if this is a total row
                is_total = self._is_total_row(asset_class)
                
                # Create asset allocation entry
                entry = {
                    "asset_class": asset_class,
                    "value": value,
                    "percentage": percentage,
                    "level": level,
                    "path": list(current_path),
                    "is_total": is_total,
                    "source": "table",
                    "extraction_method": table.get("extraction_method", "unknown"),
                    "table_number": table.get("table_number", 0),
                    "page": table.get("page_number", 0)
                }
                
                hierarchy.append(entry)
            
            # Add hierarchy to asset allocation
            self.hierarchical_data["asset_allocation"].extend(hierarchy)
        
        # If no asset allocation found in tables, try to extract from text
        if not self.hierarchical_data["asset_allocation"]:
            # Extract asset allocation from text
            asset_allocation_pattern = r'([A-Za-z][\w\s]+)\s+(\d[\d,.\']*)\s+(\d[\d,.\']*%)'
            
            matches = re.finditer(asset_allocation_pattern, text)
            for match in matches:
                asset_class = match.group(1).strip()
                value_str = match.group(2)
                percentage_str = match.group(3)
                
                value = self._clean_number(value_str)
                percentage = self._clean_percentage(percentage_str)
                
                # Skip if this doesn't look like an asset class
                if any(keyword in asset_class.lower() for keyword in ["page", "date", "time"]):
                    continue
                
                # Determine level and check if this is a total
                level = self._determine_level(asset_class)
                is_total = self._is_total_row(asset_class)
                
                entry = {
                    "asset_class": asset_class,
                    "value": value,
                    "percentage": percentage,
                    "level": level,
                    "path": [asset_class],
                    "is_total": is_total,
                    "source": "text"
                }
                
                self.hierarchical_data["asset_allocation"].append(entry)
        
        # Build parent-child relationships
        self._build_asset_allocation_hierarchy()
        
        logger.info(f"Parsed {len(self.hierarchical_data['asset_allocation'])} asset allocation entries")
    
    def _determine_level(self, text: str) -> int:
        """Determine the level of a text based on indentation or formatting."""
        # Count leading spaces
        leading_spaces = len(text) - len(text.lstrip())
        
        # Basic level determination
        if leading_spaces > 8:
            return 2
        elif leading_spaces > 4:
            return 1
        else:
            return 0
    
    def _is_total_row(self, text: str) -> bool:
        """Check if a text represents a total row."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.total_keywords)
    
    def _build_asset_allocation_hierarchy(self):
        """Build parent-child relationships in asset allocation."""
        if not self.hierarchical_data["asset_allocation"]:
            return
        
        # Sort by level
        sorted_entries = sorted(self.hierarchical_data["asset_allocation"], key=lambda x: x["level"])
        
        # Track parent-child relationships
        for i, entry in enumerate(sorted_entries):
            entry["children"] = []
            entry["parent"] = None
            
            # Look for parent
            if entry["level"] > 0:
                for j in range(i - 1, -1, -1):
                    potential_parent = sorted_entries[j]
                    
                    if potential_parent["level"] < entry["level"]:
                        entry["parent"] = j
                        sorted_entries[j]["children"].append(i)
                        break
        
        # Update the asset allocation with the hierarchy
        self.hierarchical_data["asset_allocation"] = sorted_entries
    
    def _parse_securities(self, tables: List[Dict[str, Any]], text: str):
        """Parse securities from tables and text."""
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
                
                # Check if this is a total row
                is_total = False
                if description:
                    is_total = self._is_total_row(description)
                
                # Create security object
                security = {
                    "isin": isin,
                    "description": description,
                    "security_type": security_type,
                    "valuation": valuation,
                    "is_total": is_total,
                    "source": "table",
                    "extraction_method": table.get("extraction_method", "unknown"),
                    "table_number": table.get("table_number", 0),
                    "page": table.get("page_number", 0)
                }
                
                self.hierarchical_data["securities"].append(security)
        
        # Extract securities from text
        isin_pattern = r'([A-Z]{2}[A-Z0-9]{9}[0-9])'
        
        isin_matches = re.finditer(isin_pattern, text)
        for match in isin_matches:
            isin = match.group(1)
            
            # Skip if this ISIN is already processed
            if any(s.get("isin") == isin for s in self.hierarchical_data["securities"]):
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
                "is_total": False,
                "source": "text"
            }
            
            self.hierarchical_data["securities"].append(security)
        
        # Identify structured products
        self._identify_structured_products()
        
        logger.info(f"Parsed {len(self.hierarchical_data['securities'])} securities")
    
    def _identify_structured_products(self):
        """Identify structured products and their totals."""
        # Look for structured products section
        structured_products_section = False
        structured_products_total = None
        
        for security in self.hierarchical_data["securities"]:
            description = security.get("description", "").lower()
            
            if "structured product" in description and security.get("is_total", False):
                structured_products_section = True
                structured_products_total = security
                break
        
        # If structured products section found, mark securities accordingly
        if structured_products_section and structured_products_total:
            # Find securities that are part of the structured products section
            for security in self.hierarchical_data["securities"]:
                if security == structured_products_total:
                    continue
                
                # Check if this security is a structured product
                description = security.get("description", "").lower()
                if "structured" in description or "certificate" in description:
                    security["security_type"] = "Structured Product"
                    security["is_structured_product"] = True
                    security["structured_products_total"] = structured_products_total.get("valuation")
    
    def _save_results(self, output_dir):
        """Save parsing results."""
        # Save hierarchical data as JSON
        json_path = os.path.join(output_dir, "hierarchical_data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.hierarchical_data, f, indent=2)
        
        logger.info(f"Saved parsing results to {json_path}")
    
    def get_portfolio_value(self) -> Optional[float]:
        """
        Get the portfolio value.
        
        Returns:
            Portfolio value or None if not found
        """
        if self.hierarchical_data["portfolio"]:
            return self.hierarchical_data["portfolio"]["value"]
        return None
    
    def get_asset_allocation_hierarchy(self) -> List[Dict[str, Any]]:
        """
        Get the asset allocation hierarchy.
        
        Returns:
            List of asset allocation entries with hierarchy information
        """
        return self.hierarchical_data["asset_allocation"]
    
    def get_securities(self, include_totals: bool = False) -> List[Dict[str, Any]]:
        """
        Get securities.
        
        Args:
            include_totals: Whether to include total rows (default: False)
        
        Returns:
            List of securities
        """
        if include_totals:
            return self.hierarchical_data["securities"]
        else:
            return [s for s in self.hierarchical_data["securities"] if not s.get("is_total", False)]
    
    def get_structured_products(self) -> List[Dict[str, Any]]:
        """
        Get structured products.
        
        Returns:
            List of structured products
        """
        return [s for s in self.hierarchical_data["securities"] if s.get("security_type") == "Structured Product"]
    
    def get_asset_class_securities(self, asset_class: str) -> List[Dict[str, Any]]:
        """
        Get securities belonging to a specific asset class.
        
        Args:
            asset_class: Asset class to filter by
        
        Returns:
            List of securities belonging to the asset class
        """
        asset_class_lower = asset_class.lower()
        
        if "bond" in asset_class_lower:
            return [s for s in self.hierarchical_data["securities"] if s.get("security_type") == "Bond"]
        elif "equity" in asset_class_lower:
            return [s for s in self.hierarchical_data["securities"] if s.get("security_type") == "Equity"]
        elif "fund" in asset_class_lower:
            return [s for s in self.hierarchical_data["securities"] if s.get("security_type") == "Fund"]
        elif "structured" in asset_class_lower:
            return [s for s in self.hierarchical_data["securities"] if s.get("security_type") == "Structured Product"]
        elif "cash" in asset_class_lower or "liquidity" in asset_class_lower:
            return [s for s in self.hierarchical_data["securities"] if s.get("security_type") == "Cash"]
        else:
            return []

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Parse hierarchical financial data.")
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
    
    # Parse hierarchical data
    parser = HierarchicalDataParser()
    result = parser.parse(tables, text, output_dir=args.output_dir)
    
    # Print summary
    print("\nHierarchical Data Parsing Summary:")
    print("================================")
    
    portfolio_value = parser.get_portfolio_value()
    if portfolio_value:
        print(f"Portfolio Value: {portfolio_value:,.2f}")
    else:
        print("Portfolio Value: Not found")
    
    print(f"Asset Allocation Entries: {len(result['asset_allocation'])}")
    print(f"Securities: {len(result['securities'])}")
    
    # Print asset allocation hierarchy
    print("\nAsset Allocation Hierarchy:")
    for entry in result["asset_allocation"]:
        if entry["level"] == 0:
            print(f"{entry['asset_class']}: {entry['value']:,.2f} ({entry['percentage']}%)")
            
            # Print children
            for child_index in entry.get("children", []):
                child = result["asset_allocation"][child_index]
                print(f"  {child['asset_class']}: {child['value']:,.2f} ({child['percentage']}%)")
    
    return 0

if __name__ == "__main__":
    main()
