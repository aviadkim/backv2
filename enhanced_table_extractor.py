"""
Enhanced Table Extractor - Extracts tables from financial documents using multiple methods.

This module provides tools to extract tables from financial documents using
multiple extraction methods (Camelot, pdfplumber, Tabula) and classify them
based on their content.
"""
import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
import json
import pandas as pd
from collections import defaultdict

# Import extraction libraries
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logging.warning("pdfplumber library not available. Install with: pip install pdfplumber")

try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False
    logging.warning("Camelot library not available. Install with: pip install camelot-py")

try:
    from tabula import read_pdf as tabula_read_pdf
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False
    logging.warning("Tabula library not available. Install with: pip install tabula-py")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedTableExtractor:
    """
    Extracts tables from financial documents using multiple methods and
    classifies them based on their content.
    """
    
    def __init__(self):
        """Initialize the enhanced table extractor."""
        self.tables = []
        self.classified_tables = {
            "securities": [],
            "asset_allocation": [],
            "portfolio_summary": [],
            "performance": [],
            "cash_accounts": [],
            "structured_products": [],
            "other": []
        }
        
    def extract(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract tables from a financial document using multiple methods.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save output files (default: None)
        
        Returns:
            Dict containing extracted tables
        """
        logger.info(f"Extracting tables from: {pdf_path}")
        
        # Reset data
        self.tables = []
        self.classified_tables = {
            "securities": [],
            "asset_allocation": [],
            "portfolio_summary": [],
            "performance": [],
            "cash_accounts": [],
            "structured_products": [],
            "other": []
        }
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Extract tables using multiple methods
            if PDFPLUMBER_AVAILABLE:
                pdfplumber_tables = self._extract_with_pdfplumber(pdf_path)
                self.tables.extend(pdfplumber_tables)
                logger.info(f"Extracted {len(pdfplumber_tables)} tables with pdfplumber")
            
            if CAMELOT_AVAILABLE:
                camelot_tables = self._extract_with_camelot(pdf_path)
                self.tables.extend(camelot_tables)
                logger.info(f"Extracted {len(camelot_tables)} tables with camelot")
            
            if TABULA_AVAILABLE:
                tabula_tables = self._extract_with_tabula(pdf_path)
                self.tables.extend(tabula_tables)
                logger.info(f"Extracted {len(tabula_tables)} tables with tabula")
            
            # Deduplicate tables
            self._deduplicate_tables()
            
            # Classify tables
            self._classify_tables()
            
            # Save results if output_dir is specified
            if output_dir:
                self._save_results(output_dir)
            
            logger.info(f"Table extraction completed. Found {len(self.tables)} unique tables.")
            return {
                "tables": self.tables,
                "classified_tables": self.classified_tables
            }
            
        except Exception as e:
            logger.error(f"Error extracting tables: {str(e)}")
            return {"error": str(e)}
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract tables using pdfplumber."""
        tables = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_number = i + 1
                    
                    # Extract tables
                    page_tables = page.extract_tables()
                    
                    for j, table_data in enumerate(page_tables):
                        if not table_data:
                            continue
                        
                        # Convert to DataFrame for easier processing
                        df = pd.DataFrame(table_data)
                        
                        # Use the first row as header if it looks like a header
                        if len(df) > 1:
                            headers = df.iloc[0].tolist()
                            if any(str(h).strip() for h in headers):
                                df.columns = headers
                                df = df.iloc[1:]
                        
                        # Clean the DataFrame
                        df = self._clean_dataframe(df)
                        
                        # Skip empty tables
                        if df.empty:
                            continue
                        
                        # Create table object
                        table = {
                            "page_number": page_number,
                            "table_number": j + 1,
                            "extraction_method": "pdfplumber",
                            "data": df.values.tolist(),
                            "headers": df.columns.tolist(),
                            "rows": len(df),
                            "columns": len(df.columns),
                            "dataframe": df,
                            "table_type": None  # Will be classified later
                        }
                        
                        tables.append(table)
        
        except Exception as e:
            logger.warning(f"Error extracting tables with pdfplumber: {str(e)}")
        
        return tables
    
    def _extract_with_camelot(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract tables using camelot."""
        tables = []
        
        try:
            # Try lattice mode first (for tables with borders)
            lattice_tables = camelot.read_pdf(pdf_path, pages="all", flavor="lattice")
            
            # Process lattice tables
            for i, table in enumerate(lattice_tables):
                # Convert to DataFrame
                df = table.df
                
                # Clean the DataFrame
                df = self._clean_dataframe(df)
                
                # Skip empty tables
                if df.empty:
                    continue
                
                # Create table object
                table_obj = {
                    "page_number": table.page,
                    "table_number": i + 1,
                    "extraction_method": "camelot_lattice",
                    "data": df.values.tolist(),
                    "headers": df.columns.tolist(),
                    "rows": len(df),
                    "columns": len(df.columns),
                    "dataframe": df,
                    "accuracy": table.accuracy,
                    "table_type": None  # Will be classified later
                }
                
                tables.append(table_obj)
            
            # Try stream mode (for tables without borders)
            stream_tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")
            
            # Process stream tables
            for i, table in enumerate(stream_tables):
                # Convert to DataFrame
                df = table.df
                
                # Clean the DataFrame
                df = self._clean_dataframe(df)
                
                # Skip empty tables
                if df.empty:
                    continue
                
                # Create table object
                table_obj = {
                    "page_number": table.page,
                    "table_number": i + 1,
                    "extraction_method": "camelot_stream",
                    "data": df.values.tolist(),
                    "headers": df.columns.tolist(),
                    "rows": len(df),
                    "columns": len(df.columns),
                    "dataframe": df,
                    "accuracy": table.accuracy,
                    "table_type": None  # Will be classified later
                }
                
                tables.append(table_obj)
        
        except Exception as e:
            logger.warning(f"Error extracting tables with camelot: {str(e)}")
        
        return tables
    
    def _extract_with_tabula(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract tables using tabula."""
        tables = []
        
        try:
            # Extract all tables
            tabula_tables = tabula_read_pdf(pdf_path, pages="all", multiple_tables=True)
            
            for i, df in enumerate(tabula_tables):
                # Clean the DataFrame
                df = self._clean_dataframe(df)
                
                # Skip empty tables
                if df.empty:
                    continue
                
                # Create table object
                table_obj = {
                    "page_number": None,  # Tabula doesn't provide page info in this mode
                    "table_number": i + 1,
                    "extraction_method": "tabula",
                    "data": df.values.tolist(),
                    "headers": df.columns.tolist(),
                    "rows": len(df),
                    "columns": len(df.columns),
                    "dataframe": df,
                    "table_type": None  # Will be classified later
                }
                
                tables.append(table_obj)
        
        except Exception as e:
            logger.warning(f"Error extracting tables with tabula: {str(e)}")
        
        return tables
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean a DataFrame by removing empty rows and columns."""
        # Make a copy to avoid modifying the original
        df = df.copy()
        
        # Convert all values to strings
        df = df.astype(str)
        
        # Replace 'None' and 'nan' with empty strings
        df = df.replace(["None", "nan", "NaN", "None", "none"], "")
        
        # Strip whitespace
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].str.strip()
        
        # Remove rows where all values are empty
        df = df.loc[~df.apply(lambda x: x.astype(str).str.strip().eq("").all(), axis=1)]
        
        # Remove columns where all values are empty
        df = df.loc[:, ~df.apply(lambda x: x.astype(str).str.strip().eq("").all(), axis=0)]
        
        return df
    
    def _deduplicate_tables(self):
        """Deduplicate tables based on content similarity."""
        if not self.tables:
            return
        
        # Sort tables by number of rows (descending) to prioritize larger tables
        sorted_tables = sorted(self.tables, key=lambda t: t["rows"], reverse=True)
        
        unique_tables = []
        
        for table in sorted_tables:
            # Check if this table is a duplicate
            is_duplicate = False
            
            for unique_table in unique_tables:
                # Skip if tables are from different pages
                if table["page_number"] != unique_table["page_number"] and table["page_number"] is not None and unique_table["page_number"] is not None:
                    continue
                
                # Check if tables have similar structure
                if abs(table["rows"] - unique_table["rows"]) <= 2 and abs(table["columns"] - unique_table["columns"]) <= 2:
                    # Check content similarity
                    similarity = self._calculate_table_similarity(table, unique_table)
                    
                    if similarity > 0.8:  # More than 80% similar
                        is_duplicate = True
                        
                        # Keep the table with higher accuracy if available
                        if "accuracy" in table and "accuracy" in unique_table:
                            if table["accuracy"] > unique_table["accuracy"]:
                                # Replace the existing table with this one
                                unique_tables.remove(unique_table)
                                unique_tables.append(table)
                        break
            
            if not is_duplicate:
                unique_tables.append(table)
        
        logger.info(f"Deduplicated {len(self.tables)} tables to {len(unique_tables)} unique tables")
        self.tables = unique_tables
    
    def _calculate_table_similarity(self, table1: Dict[str, Any], table2: Dict[str, Any]) -> float:
        """Calculate similarity between two tables."""
        # Convert tables to strings for comparison
        table1_str = str(table1["data"])
        table2_str = str(table2["data"])
        
        # Calculate Jaccard similarity
        set1 = set(table1_str.split())
        set2 = set(table2_str.split())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _classify_tables(self):
        """Classify tables based on their content."""
        for table in self.tables:
            # Convert table to string for pattern matching
            table_str = str(table["data"]).lower()
            headers_str = str(table["headers"]).lower()
            
            # Check for securities table
            if (
                any(keyword in headers_str for keyword in ["isin", "security", "description", "nominal", "quantity"]) or
                any(keyword in table_str for keyword in ["isin:", "security:", "bond", "equity", "stock"])
            ):
                table["table_type"] = "securities"
                self.classified_tables["securities"].append(table)
                continue
            
            # Check for asset allocation table
            if (
                any(keyword in headers_str for keyword in ["asset", "allocation", "class", "weight"]) or
                any(keyword in table_str for keyword in ["asset allocation", "asset class", "bonds", "equities", "liquidity"])
            ):
                table["table_type"] = "asset_allocation"
                self.classified_tables["asset_allocation"].append(table)
                continue
            
            # Check for portfolio summary table
            if (
                any(keyword in headers_str for keyword in ["portfolio", "summary", "total", "assets"]) or
                any(keyword in table_str for keyword in ["portfolio total", "total assets", "portfolio value"])
            ):
                table["table_type"] = "portfolio_summary"
                self.classified_tables["portfolio_summary"].append(table)
                continue
            
            # Check for performance table
            if (
                any(keyword in headers_str for keyword in ["performance", "return", "profit", "loss"]) or
                any(keyword in table_str for keyword in ["performance", "return", "ytd", "mtd", "profit and loss"])
            ):
                table["table_type"] = "performance"
                self.classified_tables["performance"].append(table)
                continue
            
            # Check for cash accounts table
            if (
                any(keyword in headers_str for keyword in ["cash", "account", "liquidity"]) or
                any(keyword in table_str for keyword in ["cash account", "liquidity", "current account", "savings"])
            ):
                table["table_type"] = "cash_accounts"
                self.classified_tables["cash_accounts"].append(table)
                continue
            
            # Check for structured products table
            if (
                any(keyword in headers_str for keyword in ["structured", "product", "certificate"]) or
                any(keyword in table_str for keyword in ["structured product", "certificate", "note", "warrant"])
            ):
                table["table_type"] = "structured_products"
                self.classified_tables["structured_products"].append(table)
                continue
            
            # If no specific type is identified
            table["table_type"] = "other"
            self.classified_tables["other"].append(table)
        
        # Log classification results
        for table_type, tables in self.classified_tables.items():
            logger.info(f"Classified {len(tables)} tables as '{table_type}'")
    
    def _save_results(self, output_dir):
        """Save extraction results."""
        # Create a serializable version of the tables
        serializable_tables = []
        
        for table in self.tables:
            # Create a copy without the DataFrame
            table_copy = dict(table)
            if "dataframe" in table_copy:
                del table_copy["dataframe"]
            
            serializable_tables.append(table_copy)
        
        # Save tables as JSON
        tables_path = os.path.join(output_dir, "extracted_tables.json")
        with open(tables_path, "w", encoding="utf-8") as f:
            json.dump(serializable_tables, f, indent=2)
        
        # Save classified tables as JSON
        classified_tables = {}
        for table_type, tables in self.classified_tables.items():
            classified_tables[table_type] = []
            
            for table in tables:
                # Create a copy without the DataFrame
                table_copy = dict(table)
                if "dataframe" in table_copy:
                    del table_copy["dataframe"]
                
                classified_tables[table_type].append(table_copy)
        
        classified_path = os.path.join(output_dir, "classified_tables.json")
        with open(classified_path, "w", encoding="utf-8") as f:
            json.dump(classified_tables, f, indent=2)
        
        # Save each table as CSV
        tables_dir = os.path.join(output_dir, "tables")
        os.makedirs(tables_dir, exist_ok=True)
        
        for i, table in enumerate(self.tables):
            if "dataframe" in table:
                csv_path = os.path.join(tables_dir, f"table_{table['page_number']}_{table['table_number']}_{table['extraction_method']}.csv")
                table["dataframe"].to_csv(csv_path, index=False)
        
        logger.info(f"Saved extraction results to {output_dir}")
    
    def get_tables_by_type(self, table_type: str) -> List[Dict[str, Any]]:
        """
        Get tables of a specific type.
        
        Args:
            table_type: Type of tables to retrieve
        
        Returns:
            List of tables of the specified type
        """
        return self.classified_tables.get(table_type, [])
    
    def get_table_as_dataframe(self, table: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """
        Get a table as a pandas DataFrame.
        
        Args:
            table: Table object
        
        Returns:
            DataFrame or None if conversion fails
        """
        if "dataframe" in table:
            return table["dataframe"]
        
        try:
            # Convert data to DataFrame
            df = pd.DataFrame(table["data"], columns=table["headers"])
            return df
        except Exception as e:
            logger.warning(f"Error converting table to DataFrame: {str(e)}")
            return None
    
    def extract_values_from_table(self, table: Dict[str, Any], column_keywords: List[str], value_column_keywords: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Extract values from a table based on column keywords.
        
        Args:
            table: Table object
            column_keywords: Keywords to identify the column containing entity names
            value_column_keywords: Keywords to identify the column containing values (default: None)
        
        Returns:
            List of extracted values
        """
        df = self.get_table_as_dataframe(table)
        if df is None:
            return []
        
        # Find the column containing entity names
        entity_column = None
        for col in df.columns:
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in column_keywords):
                entity_column = col
                break
        
        if entity_column is None:
            return []
        
        # Find the value column if keywords are provided
        value_column = None
        if value_column_keywords:
            for col in df.columns:
                col_str = str(col).lower()
                if any(keyword in col_str for keyword in value_column_keywords):
                    value_column = col
                    break
        
        # Extract values
        values = []
        for _, row in df.iterrows():
            entity = row[entity_column]
            if pd.isna(entity) or entity == "":
                continue
            
            value_obj = {
                "entity": entity
            }
            
            # Add value if value column is found
            if value_column:
                value = row[value_column]
                if not pd.isna(value) and value != "":
                    # Try to convert to float
                    try:
                        value_obj["value"] = float(str(value).replace(",", "").replace("'", ""))
                    except ValueError:
                        value_obj["value"] = value
            
            # Add all other columns
            for col in df.columns:
                if col != entity_column and col != value_column:
                    col_value = row[col]
                    if not pd.isna(col_value) and col_value != "":
                        value_obj[str(col)] = col_value
            
            values.append(value_obj)
        
        return values

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract tables from financial documents.")
    parser.add_argument("file_path", help="Path to the financial document")
    parser.add_argument("--output-dir", help="Directory to save output files")
    
    args = parser.parse_args()
    
    # Check if the file exists
    if not os.path.exists(args.file_path):
        logger.error(f"Error: File not found: {args.file_path}")
        return 1
    
    # Extract tables
    extractor = EnhancedTableExtractor()
    result = extractor.extract(args.file_path, output_dir=args.output_dir)
    
    # Print summary
    print("\nTable Extraction Summary:")
    print("=======================")
    print(f"Total Tables: {len(result['tables'])}")
    
    for table_type, tables in result["classified_tables"].items():
        print(f"{table_type.capitalize()} Tables: {len(tables)}")
    
    return 0

if __name__ == "__main__":
    main()
