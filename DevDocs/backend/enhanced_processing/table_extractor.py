"""
Table Extractor Module

This module provides enhanced table extraction capabilities using Camelot.
It extracts tables from financial documents with high accuracy.
"""

import os
import logging
import camelot
import pandas as pd
import pdfplumber
from typing import List, Dict, Any, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TableExtractor:
    """
    Enhanced table extraction using Camelot and pdfplumber.
    Combines multiple extraction methods for optimal results.
    """
    
    def __init__(self, pdf_path: str):
        """
        Initialize the TableExtractor with a PDF file path.
        
        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.tables_lattice = None
        self.tables_stream = None
        self.pdfplumber_tables = None
        self.combined_tables = []
        
        # Verify the PDF file exists
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Initialized TableExtractor for {pdf_path}")
    
    def extract_tables(self, pages: str = 'all') -> List[pd.DataFrame]:
        """
        Extract tables from the PDF using multiple methods and combine results.
        
        Args:
            pages: Page numbers to extract tables from (e.g., '1,3,4' or 'all')
            
        Returns:
            List of pandas DataFrames containing the extracted tables
        """
        logger.info(f"Extracting tables from {self.pdf_path} (pages: {pages})")
        
        # Extract tables using Camelot's lattice method (for bordered tables)
        try:
            self.tables_lattice = camelot.read_pdf(
                self.pdf_path, 
                pages=pages, 
                flavor='lattice',
                suppress_stdout=True
            )
            logger.info(f"Extracted {len(self.tables_lattice)} tables using lattice method")
        except Exception as e:
            logger.error(f"Error extracting tables with lattice method: {e}")
            self.tables_lattice = []
        
        # Extract tables using Camelot's stream method (for borderless tables)
        try:
            self.tables_stream = camelot.read_pdf(
                self.pdf_path, 
                pages=pages, 
                flavor='stream',
                suppress_stdout=True,
                edge_tol=50,  # More tolerant of whitespace
                row_tol=10    # More tolerant of row variations
            )
            logger.info(f"Extracted {len(self.tables_stream)} tables using stream method")
        except Exception as e:
            logger.error(f"Error extracting tables with stream method: {e}")
            self.tables_stream = []
        
        # Extract tables using pdfplumber as a backup
        try:
            self.pdfplumber_tables = self._extract_with_pdfplumber(pages)
            logger.info(f"Extracted {len(self.pdfplumber_tables)} tables using pdfplumber")
        except Exception as e:
            logger.error(f"Error extracting tables with pdfplumber: {e}")
            self.pdfplumber_tables = []
        
        # Combine results based on quality metrics
        self._combine_table_results()
        
        return self.combined_tables
    
    def _extract_with_pdfplumber(self, pages: str) -> List[pd.DataFrame]:
        """
        Extract tables using pdfplumber as a backup method.
        
        Args:
            pages: Page numbers to extract from
            
        Returns:
            List of pandas DataFrames
        """
        tables = []
        
        with pdfplumber.open(self.pdf_path) as pdf:
            # Convert pages string to list of page numbers
            if pages == 'all':
                page_numbers = range(len(pdf.pages))
            else:
                page_numbers = [int(p) - 1 for p in pages.split(',')]  # Convert to 0-based indexing
            
            for i in page_numbers:
                if i < len(pdf.pages):
                    page = pdf.pages[i]
                    for table in page.extract_tables():
                        if table and len(table) > 0:
                            # Convert to pandas DataFrame
                            df = pd.DataFrame(table[1:], columns=table[0])
                            tables.append(df)
        
        return tables
    
    def _combine_table_results(self) -> None:
        """
        Combine table extraction results from different methods based on quality metrics.
        Prioritizes tables with better accuracy and completeness.
        """
        self.combined_tables = []
        
        # Process Camelot lattice tables
        if hasattr(self.tables_lattice, 'n') and self.tables_lattice.n > 0:
            for i in range(self.tables_lattice.n):
                table = self.tables_lattice[i]
                if table.accuracy > 80:  # Only include high-accuracy tables
                    self.combined_tables.append(table.df)
        
        # Process Camelot stream tables, avoiding duplicates
        if hasattr(self.tables_stream, 'n') and self.tables_stream.n > 0:
            for i in range(self.tables_stream.n):
                table = self.tables_stream[i]
                # Check if this table is likely a duplicate of one we already have
                is_duplicate = False
                for existing_table in self.combined_tables:
                    if self._is_similar_table(table.df, existing_table):
                        is_duplicate = True
                        break
                
                if not is_duplicate and table.accuracy > 70:  # Lower threshold for stream
                    self.combined_tables.append(table.df)
        
        # Add pdfplumber tables if they provide additional information
        for plumber_table in self.pdfplumber_tables:
            is_duplicate = False
            for existing_table in self.combined_tables:
                if self._is_similar_table(plumber_table, existing_table):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                self.combined_tables.append(plumber_table)
        
        logger.info(f"Combined results: {len(self.combined_tables)} unique tables")
    
    def _is_similar_table(self, table1: pd.DataFrame, table2: pd.DataFrame, 
                          similarity_threshold: float = 0.7) -> bool:
        """
        Check if two tables are similar based on shape and content.
        
        Args:
            table1: First table
            table2: Second table
            similarity_threshold: Threshold for considering tables similar
            
        Returns:
            Boolean indicating if tables are similar
        """
        # If shapes are very different, tables are not similar
        if abs(table1.shape[0] - table2.shape[0]) > 3 or abs(table1.shape[1] - table2.shape[1]) > 2:
            return False
        
        # If one table is much smaller than the other, they're not similar
        min_rows = min(table1.shape[0], table2.shape[0])
        min_cols = min(table1.shape[1], table2.shape[1])
        
        if min_rows == 0 or min_cols == 0:
            return False
        
        # Compare content of overlapping cells
        match_count = 0
        total_cells = min_rows * min_cols
        
        for i in range(min_rows):
            for j in range(min_cols):
                try:
                    val1 = str(table1.iloc[i, j]).strip()
                    val2 = str(table2.iloc[i, j]).strip()
                    
                    # Check for exact match or significant overlap
                    if val1 == val2 or (len(val1) > 0 and len(val2) > 0 and 
                                        (val1 in val2 or val2 in val1)):
                        match_count += 1
                except (IndexError, KeyError):
                    continue
        
        similarity = match_count / total_cells if total_cells > 0 else 0
        return similarity >= similarity_threshold
    
    def extract_financial_data(self) -> Dict[str, Any]:
        """
        Extract financial data from tables, focusing on securities, ISINs, and values.
        
        Returns:
            Dictionary containing structured financial data
        """
        if not self.combined_tables:
            self.extract_tables()
        
        financial_data = {
            "securities": [],
            "asset_allocation": {},
            "total_value": None,
            "currency": None
        }
        
        # Process each table to extract financial information
        for table in self.combined_tables:
            # Look for tables containing ISINs
            if self._contains_isin(table):
                securities = self._extract_securities_from_table(table)
                financial_data["securities"].extend(securities)
            
            # Look for asset allocation tables
            if self._is_asset_allocation_table(table):
                asset_allocation = self._extract_asset_allocation(table)
                financial_data["asset_allocation"].update(asset_allocation)
            
            # Look for total portfolio value
            total_value, currency = self._extract_total_value(table)
            if total_value and not financial_data["total_value"]:
                financial_data["total_value"] = total_value
                financial_data["currency"] = currency
        
        logger.info(f"Extracted {len(financial_data['securities'])} securities and "
                   f"{len(financial_data['asset_allocation'])} asset classes")
        
        return financial_data
    
    def _contains_isin(self, table: pd.DataFrame) -> bool:
        """
        Check if a table contains ISIN information.
        
        Args:
            table: DataFrame to check
            
        Returns:
            Boolean indicating if the table contains ISINs
        """
        # Convert table to string and check for ISIN pattern or keyword
        table_str = table.to_string().lower()
        return 'isin' in table_str or any(col.lower() == 'isin' for col in table.columns)
    
    def _is_asset_allocation_table(self, table: pd.DataFrame) -> bool:
        """
        Check if a table contains asset allocation information.
        
        Args:
            table: DataFrame to check
            
        Returns:
            Boolean indicating if the table contains asset allocation
        """
        # Look for keywords related to asset allocation
        keywords = ['asset', 'allocation', 'class', 'weight', 'bonds', 'equities', 'liquidity']
        table_str = table.to_string().lower()
        
        return any(keyword in table_str for keyword in keywords)
    
    def _extract_securities_from_table(self, table: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Extract securities information from a table.
        
        Args:
            table: DataFrame containing securities data
            
        Returns:
            List of dictionaries with security information
        """
        securities = []
        
        # Try to identify columns containing ISIN, name, quantity, price, value
        isin_col = self._find_column_by_keywords(table, ['isin'])
        name_col = self._find_column_by_keywords(table, ['name', 'description', 'security'])
        quantity_col = self._find_column_by_keywords(table, ['quantity', 'nominal', 'shares'])
        price_col = self._find_column_by_keywords(table, ['price', 'rate'])
        value_col = self._find_column_by_keywords(table, ['value', 'amount', 'total'])
        currency_col = self._find_column_by_keywords(table, ['currency', 'ccy'])
        asset_class_col = self._find_column_by_keywords(table, ['class', 'type', 'category'])
        
        # If we couldn't identify columns by headers, try to infer from content
        if isin_col is None:
            isin_col = self._find_column_with_isin_pattern(table)
        
        # Process rows if we found at least ISIN or name column
        if isin_col is not None or name_col is not None:
            for idx, row in table.iterrows():
                security = {}
                
                # Extract ISIN if column was found
                if isin_col is not None:
                    isin_value = str(row[isin_col]).strip()
                    # Clean up ISIN value (remove "ISIN:" prefix if present)
                    isin_value = isin_value.replace("ISIN:", "").strip()
                    if self._is_valid_isin(isin_value):
                        security["isin"] = isin_value
                
                # Extract other fields if columns were found
                if name_col is not None:
                    security["name"] = str(row[name_col]).strip()
                
                if quantity_col is not None:
                    try:
                        quantity = self._parse_numeric_value(row[quantity_col])
                        security["quantity"] = quantity
                    except (ValueError, TypeError):
                        pass
                
                if price_col is not None:
                    try:
                        price = self._parse_numeric_value(row[price_col])
                        security["price"] = price
                    except (ValueError, TypeError):
                        pass
                
                if value_col is not None:
                    try:
                        value = self._parse_numeric_value(row[value_col])
                        security["value"] = value
                    except (ValueError, TypeError):
                        pass
                
                if currency_col is not None:
                    security["currency"] = str(row[currency_col]).strip()
                
                if asset_class_col is not None:
                    security["asset_class"] = str(row[asset_class_col]).strip()
                
                # Only add security if we have at least ISIN or name
                if "isin" in security or "name" in security:
                    securities.append(security)
        
        return securities
    
    def _extract_asset_allocation(self, table: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Extract asset allocation information from a table.
        
        Args:
            table: DataFrame containing asset allocation data
            
        Returns:
            Dictionary with asset allocation information
        """
        asset_allocation = {}
        
        # Try to identify columns containing asset class, value, and weight
        class_col = self._find_column_by_keywords(table, ['class', 'category', 'type', 'asset'])
        value_col = self._find_column_by_keywords(table, ['value', 'amount', 'total'])
        weight_col = self._find_column_by_keywords(table, ['weight', '%', 'percent', 'allocation'])
        
        # Process rows if we found at least the class column
        if class_col is not None:
            for idx, row in table.iterrows():
                asset_class = str(row[class_col]).strip()
                
                # Skip empty or header rows
                if not asset_class or asset_class.lower() in ['class', 'asset class', 'category']:
                    continue
                
                asset_info = {}
                
                if value_col is not None:
                    try:
                        value = self._parse_numeric_value(row[value_col])
                        asset_info["value"] = value
                    except (ValueError, TypeError):
                        pass
                
                if weight_col is not None:
                    try:
                        weight = self._parse_numeric_value(row[weight_col])
                        # Convert percentage to decimal if needed
                        if weight > 1 and weight <= 100:
                            weight = weight / 100
                        asset_info["weight"] = weight
                    except (ValueError, TypeError):
                        pass
                
                if asset_info:
                    asset_allocation[asset_class] = asset_info
        
        return asset_allocation
    
    def _extract_total_value(self, table: pd.DataFrame) -> Tuple[Optional[float], Optional[str]]:
        """
        Extract total portfolio value and currency from a table.
        
        Args:
            table: DataFrame to extract from
            
        Returns:
            Tuple of (total_value, currency)
        """
        # Convert table to string for easier searching
        table_str = table.to_string().lower()
        
        # Look for "total" row
        if 'total' in table_str:
            for idx, row in table.iterrows():
                row_str = ' '.join(str(val).lower() for val in row.values)
                
                if 'total' in row_str:
                    # Try to find a numeric value in this row
                    for val in row:
                        try:
                            numeric_val = self._parse_numeric_value(val)
                            if numeric_val > 1000:  # Assume total value is relatively large
                                # Try to find currency
                                currency = None
                                currencies = ['usd', 'eur', 'chf', 'gbp', 'jpy']
                                for curr in currencies:
                                    if curr in row_str:
                                        currency = curr.upper()
                                        break
                                
                                return numeric_val, currency
                        except (ValueError, TypeError):
                            continue
        
        return None, None
    
    def _find_column_by_keywords(self, table: pd.DataFrame, 
                                keywords: List[str]) -> Optional[str]:
        """
        Find a column in a table by looking for keywords in the column names.
        
        Args:
            table: DataFrame to search
            keywords: List of keywords to look for
            
        Returns:
            Column name if found, None otherwise
        """
        # Check if any column name contains any of the keywords
        for col in table.columns:
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in keywords):
                return col
        
        # If not found in column names, check first row (might contain headers)
        if len(table) > 0:
            for col in table.columns:
                if pd.notna(table.iloc[0][col]):
                    cell_val = str(table.iloc[0][col]).lower()
                    if any(keyword in cell_val for keyword in keywords):
                        return col
        
        return None
    
    def _find_column_with_isin_pattern(self, table: pd.DataFrame) -> Optional[str]:
        """
        Find a column containing ISIN patterns (12 characters, starting with 2 letters).
        
        Args:
            table: DataFrame to search
            
        Returns:
            Column name if found, None otherwise
        """
        for col in table.columns:
            # Check a sample of values in the column
            sample_size = min(10, len(table))
            isin_count = 0
            
            for i in range(sample_size):
                if i < len(table) and pd.notna(table.iloc[i][col]):
                    val = str(table.iloc[i][col]).strip()
                    if self._is_valid_isin(val):
                        isin_count += 1
            
            # If more than 30% of sampled values are ISINs, consider this an ISIN column
            if isin_count / sample_size > 0.3:
                return col
        
        return None
    
    def _is_valid_isin(self, value: str) -> bool:
        """
        Check if a string matches the ISIN pattern.
        
        Args:
            value: String to check
            
        Returns:
            Boolean indicating if the string is a valid ISIN
        """
        # Basic ISIN validation: 12 characters, first 2 are letters
        value = value.strip().upper()
        if len(value) == 12 and value[:2].isalpha() and value[2:].isalnum():
            return True
        return False
    
    def _parse_numeric_value(self, value) -> float:
        """
        Parse a numeric value from various formats.
        
        Args:
            value: Value to parse
            
        Returns:
            Parsed numeric value
            
        Raises:
            ValueError: If the value cannot be parsed as a number
        """
        if pd.isna(value):
            raise ValueError("Cannot parse NaN value")
        
        # Convert to string and clean up
        value_str = str(value).strip()
        
        # Remove currency symbols and other non-numeric characters
        for char in ['$', '€', '£', '¥', ',', "'", ' ']:
            value_str = value_str.replace(char, '')
        
        # Handle percentage values
        if '%' in value_str:
            value_str = value_str.replace('%', '')
            return float(value_str)
        
        # Handle special cases like "1.2M" for millions
        if value_str.endswith('M'):
            return float(value_str[:-1]) * 1000000
        if value_str.endswith('K'):
            return float(value_str[:-1]) * 1000
        
        return float(value_str)


# Example usage
if __name__ == "__main__":
    # This will only run when the script is executed directly
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        extractor = TableExtractor(pdf_path)
        tables = extractor.extract_tables()
        
        print(f"Extracted {len(tables)} tables")
        
        financial_data = extractor.extract_financial_data()
        print(f"Extracted {len(financial_data['securities'])} securities")
        print(f"Total value: {financial_data['total_value']} {financial_data['currency']}")
        print(f"Asset allocation: {financial_data['asset_allocation']}")
    else:
        print("Please provide a PDF file path")
