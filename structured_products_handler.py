"""
Structured Products Handler - Specialized handler for structured products.

This module provides specialized handling for structured products sections
in financial documents, including detection of structured product totals
vs. individual securities.
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

class StructuredProductsHandler:
    """
    Specialized handler for structured products in financial documents.
    """

    def __init__(self):
        """Initialize the structured products handler."""
        self.structured_products = []
        self.structured_products_total = None
        self.structured_products_section = None

    def process(self, tables: List[Dict[str, Any]], text: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Process structured products from tables and text.

        Args:
            tables: List of tables extracted from the document
            text: Text extracted from the document
            output_dir: Directory to save output files (default: None)

        Returns:
            Dict containing structured products data
        """
        logger.info("Processing structured products")

        # Reset data
        self.structured_products = []
        self.structured_products_total = None
        self.structured_products_section = None

        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        try:
            # Identify structured products section
            self._identify_structured_products_section(tables, text)

            # Extract structured products
            self._extract_structured_products(tables, text)

            # Validate structured products
            self._validate_structured_products()

            # Save results if output_dir is specified
            if output_dir:
                self._save_results(output_dir)

            logger.info("Structured products processing completed.")
            return {
                "structured_products": self.structured_products,
                "structured_products_total": self.structured_products_total,
                "structured_products_section": self.structured_products_section
            }

        except Exception as e:
            logger.error(f"Error processing structured products: {str(e)}")
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

    def _identify_structured_products_section(self, tables: List[Dict[str, Any]], text: str):
        """Identify structured products section in tables and text."""
        # Look for structured products section in tables
        for table in tables:
            if "dataframe" not in table:
                continue

            df = table["dataframe"]

            # Convert DataFrame to string for easier searching
            df_str = df.to_string().lower()

            # Check if this table contains structured products
            if "structured product" in df_str or "structured products" in df_str:
                # Look for structured products total
                for _, row in df.iterrows():
                    row_str = " ".join(str(x).lower() for x in row.values)

                    if "total structured product" in row_str or "structured products total" in row_str:
                        # Extract the value
                        for cell in row:
                            value = self._clean_number(cell)
                            if value and value > 1000:  # Assume total is large
                                self.structured_products_total = {
                                    "value": value,
                                    "source": "table",
                                    "extraction_method": table.get("extraction_method", "unknown"),
                                    "table_number": table.get("table_number", 0),
                                    "page": table.get("page_number", 0)
                                }
                                self.structured_products_section = table
                                break

                # If total found, break
                if self.structured_products_total:
                    break

        # If not found in tables, look in text
        if not self.structured_products_total:
            # Look for structured products total in text
            structured_products_patterns = [
                r'Total\s+Structured\s+products?\s*[:\s]+(\d[\d,.\']*)',
                r'Structured\s+products?\s+Total\s*[:\s]+(\d[\d,.\']*)',
                r'Structured\s+products?\s*[:\s]+(\d[\d,.\']*)'
            ]

            for pattern in structured_products_patterns:
                match = re.search(pattern, text)
                if match:
                    value_str = match.group(1)
                    value = self._clean_number(value_str)

                    if value:
                        self.structured_products_total = {
                            "value": value,
                            "source": "text",
                            "pattern": pattern,
                            "match": match.group(0)
                        }
                        break

        if self.structured_products_total:
            logger.info(f"Identified structured products section with total: {self.structured_products_total['value']:,.2f}")
        else:
            logger.warning("Could not identify structured products section")

    def _extract_structured_products(self, tables: List[Dict[str, Any]], text: str):
        """Extract structured products from tables and text."""
        # If structured products section found in a table, extract from that table
        if self.structured_products_section:
            df = self.structured_products_section["dataframe"]

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

                # Skip total row
                row_str = " ".join(str(x).lower() for x in row.values if x is not None)
                if "total structured product" in row_str or "structured products total" in row_str:
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
                security_type = "Structured Product"
                if type_col:
                    security_type = str(row[type_col]).strip()

                # Extract valuation
                valuation = None
                if valuation_col:
                    valuation = self._clean_number(row[valuation_col])

                # Create structured product object
                product = {
                    "isin": isin,
                    "description": description,
                    "security_type": security_type,
                    "valuation": valuation,
                    "source": "table",
                    "extraction_method": self.structured_products_section.get("extraction_method", "unknown"),
                    "table_number": self.structured_products_section.get("table_number", 0),
                    "page": self.structured_products_section.get("page_number", 0)
                }

                self.structured_products.append(product)

        # If no structured products found in tables, try to extract from text
        if not self.structured_products:
            # Look for structured products section in text
            structured_products_section_pattern = r'Structured\s+products(?:.*?)(?=\n\n|\Z)'

            match = re.search(structured_products_section_pattern, text, re.DOTALL)
            if match:
                section_text = match.group(0)

                # Extract ISINs
                isin_pattern = r'([A-Z]{2}[A-Z0-9]{9}[0-9])'

                isin_matches = re.finditer(isin_pattern, section_text)
                for isin_match in isin_matches:
                    isin = isin_match.group(1)

                    # Get context around the ISIN
                    context_start = max(0, isin_match.start() - 100)
                    context_end = min(len(section_text), isin_match.end() + 100)
                    context = section_text[context_start:context_end]

                    # Extract description
                    description = None
                    description_pattern = r'([A-Za-z][\w\s]+)\s+' + re.escape(isin)
                    desc_match = re.search(description_pattern, context)
                    if desc_match:
                        description = desc_match.group(1).strip()

                    # If no description found, look after ISIN
                    if not description:
                        after_isin = section_text[isin_match.end():context_end]
                        lines = after_isin.strip().split("\n")
                        if lines:
                            description = lines[0].strip()

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

                    # Create structured product object
                    product = {
                        "isin": isin,
                        "description": description,
                        "security_type": "Structured Product",
                        "valuation": valuation,
                        "source": "text"
                    }

                    self.structured_products.append(product)

        logger.info(f"Extracted {len(self.structured_products)} structured products")

    def _validate_structured_products(self):
        """Validate structured products."""
        if not self.structured_products_total:
            return

        total_value = self.structured_products_total["value"]

        # Calculate sum of structured products
        products_sum = sum(product.get("valuation", 0) or 0 for product in self.structured_products)

        # Check if sum matches total
        if abs(products_sum - total_value) / total_value > 0.05:  # More than 5% difference
            logger.warning(f"Sum of structured products ({products_sum:.2f}) does not match total ({total_value:.2f})")

            # Try to identify missing products
            missing_value = total_value - products_sum

            if missing_value > 0:
                logger.warning(f"Missing structured products worth {missing_value:.2f}")

                # Add a placeholder for missing products
                self.structured_products.append({
                    "isin": None,
                    "description": "Missing structured products",
                    "security_type": "Structured Product",
                    "valuation": missing_value,
                    "source": "validation",
                    "is_placeholder": True
                })

    def _save_results(self, output_dir):
        """Save processing results."""
        # Save structured products as JSON
        json_path = os.path.join(output_dir, "structured_products.json")

        result = {
            "structured_products": self.structured_products,
            "structured_products_total": self.structured_products_total,
            "structured_products_section": None  # Can't serialize DataFrame
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        logger.info(f"Saved structured products to {json_path}")

    def get_structured_products(self) -> List[Dict[str, Any]]:
        """
        Get structured products.

        Returns:
            List of structured products
        """
        return self.structured_products

    def get_structured_products_total(self) -> Optional[Dict[str, Any]]:
        """
        Get structured products total.

        Returns:
            Structured products total or None if not found
        """
        return self.structured_products_total

    def get_structured_products_by_type(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get structured products grouped by type.

        Returns:
            Dict of structured products grouped by type
        """
        products_by_type = defaultdict(list)

        for product in self.structured_products:
            product_type = product.get("security_type", "Unknown")
            products_by_type[product_type].append(product)

        return dict(products_by_type)

    def get_structured_products_summary(self) -> Dict[str, Any]:
        """
        Get a summary of structured products.

        Returns:
            Dict containing structured products summary
        """
        total_value = self.structured_products_total["value"] if self.structured_products_total else 0
        products_sum = sum(product.get("valuation", 0) or 0 for product in self.structured_products)

        return {
            "count": len(self.structured_products),
            "total_value": total_value,
            "products_sum": products_sum,
            "difference": total_value - products_sum if total_value else None,
            "difference_percentage": (total_value - products_sum) / total_value * 100 if total_value else None
        }

def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Process structured products from financial documents.")
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

    # Process structured products
    handler = StructuredProductsHandler()
    result = handler.process(tables, text, output_dir=args.output_dir)

    # Print summary
    print("\nStructured Products Summary:")
    print("===========================")

    summary = handler.get_structured_products_summary()

    print(f"Count: {summary['count']}")
    print(f"Total Value: {summary['total_value']:,.2f}")
    print(f"Products Sum: {summary['products_sum']:,.2f}")

    if summary['difference'] is not None:
        print(f"Difference: {summary['difference']:,.2f} ({summary['difference_percentage']:.2f}%)")

    # Print structured products
    print("\nStructured Products:")
    for i, product in enumerate(handler.get_structured_products(), 1):
        print(f"{i}. {product.get('description', 'Unknown')}: {product.get('valuation', 0):,.2f}")

    return 0

if __name__ == "__main__":
    main()
