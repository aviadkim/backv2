"""
Grid Analyzer Module

This module provides grid-based analysis for financial documents using Unstructured.
It analyzes the spatial relationships between elements to improve data extraction accuracy.
"""

import os
import logging
from typing import List, Dict, Any, Tuple, Optional
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import (
    Element, Text, Title, NarrativeText, ListItem, Table, TableCell
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GridAnalyzer:
    """
    Grid-based analysis for financial documents using Unstructured.
    Analyzes spatial relationships between elements to improve extraction accuracy.
    """
    
    def __init__(self, pdf_path: str):
        """
        Initialize the GridAnalyzer with a PDF file path.
        
        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.elements = []
        self.tables = []
        self.text_elements = []
        self.grid_data = {}
        
        # Verify the PDF file exists
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Initialized GridAnalyzer for {pdf_path}")
    
    def analyze(self, include_ocr: bool = True) -> Dict[str, Any]:
        """
        Analyze the PDF document using grid-based analysis.
        
        Args:
            include_ocr: Whether to use OCR for text extraction
            
        Returns:
            Dictionary containing structured data from the document
        """
        logger.info(f"Analyzing {self.pdf_path} with grid-based analysis")
        
        # Extract elements with spatial information
        self.elements = partition_pdf(
            self.pdf_path,
            include_metadata=True,
            include_page_breaks=True,
            include_image_data=False,
            ocr_languages=['eng', 'heb'] if include_ocr else None,
            extract_images_in_pdf=False,
            infer_table_structure=True,
            strategy="hi_res"
        )
        
        logger.info(f"Extracted {len(self.elements)} elements from the document")
        
        # Separate elements by type
        self._categorize_elements()
        
        # Analyze spatial relationships
        self._analyze_spatial_relationships()
        
        # Extract financial data
        financial_data = self._extract_financial_data()
        
        return financial_data
    
    def _categorize_elements(self) -> None:
        """
        Categorize elements by type (tables, text, etc.).
        """
        self.tables = []
        self.text_elements = []
        
        for element in self.elements:
            if isinstance(element, Table):
                self.tables.append(element)
            elif isinstance(element, (Text, Title, NarrativeText, ListItem)):
                self.text_elements.append(element)
        
        logger.info(f"Categorized elements: {len(self.tables)} tables, {len(self.text_elements)} text elements")
    
    def _analyze_spatial_relationships(self) -> None:
        """
        Analyze spatial relationships between elements.
        Creates a grid representation of the document.
        """
        # Group elements by page
        pages = {}
        for element in self.elements:
            metadata = getattr(element, 'metadata', {})
            page_number = metadata.get('page_number', 0)
            
            if page_number not in pages:
                pages[page_number] = []
            
            pages[page_number].append(element)
        
        # Analyze each page
        for page_number, page_elements in pages.items():
            # Create grid for this page
            grid = self._create_page_grid(page_elements)
            self.grid_data[page_number] = grid
        
        logger.info(f"Analyzed spatial relationships for {len(pages)} pages")
    
    def _create_page_grid(self, elements: List[Element]) -> Dict[str, Any]:
        """
        Create a grid representation of a page.
        
        Args:
            elements: List of elements on the page
            
        Returns:
            Dictionary containing grid data
        """
        grid = {
            'elements': [],
            'rows': [],
            'columns': [],
            'cells': {}
        }
        
        # Extract coordinates for each element
        for element in elements:
            metadata = getattr(element, 'metadata', {})
            coordinates = metadata.get('coordinates', {})
            
            if coordinates:
                # Extract bounding box
                x0 = coordinates.get('x0', 0)
                y0 = coordinates.get('y0', 0)
                x1 = coordinates.get('x1', 0)
                y1 = coordinates.get('y1', 0)
                
                # Add element with its coordinates
                grid['elements'].append({
                    'element': element,
                    'x0': x0,
                    'y0': y0,
                    'x1': x1,
                    'y1': y1,
                    'text': str(element)
                })
        
        # Sort elements by y-coordinate (top to bottom)
        grid['elements'].sort(key=lambda e: e['y0'])
        
        # Identify rows based on y-coordinates
        current_row = []
        current_y = None
        row_tolerance = 5  # Pixels tolerance for considering elements in the same row
        
        for element in grid['elements']:
            if current_y is None:
                # First element
                current_row.append(element)
                current_y = element['y0']
            elif abs(element['y0'] - current_y) <= row_tolerance:
                # Same row
                current_row.append(element)
            else:
                # New row
                if current_row:
                    # Sort elements in the row by x-coordinate (left to right)
                    current_row.sort(key=lambda e: e['x0'])
                    grid['rows'].append(current_row)
                
                # Start new row
                current_row = [element]
                current_y = element['y0']
        
        # Add the last row
        if current_row:
            current_row.sort(key=lambda e: e['x0'])
            grid['rows'].append(current_row)
        
        # Identify columns based on x-coordinates
        x_positions = []
        for element in grid['elements']:
            x_positions.append(element['x0'])
            x_positions.append(element['x1'])
        
        # Find distinct column boundaries
        x_positions = sorted(set(x_positions))
        column_boundaries = []
        
        # Merge close x-positions
        column_tolerance = 10  # Pixels tolerance for considering positions as the same column
        current_x = None
        
        for x in x_positions:
            if current_x is None:
                current_x = x
            elif x - current_x <= column_tolerance:
                # Same column, update to the rightmost position
                current_x = x
            else:
                # New column
                column_boundaries.append(current_x)
                current_x = x
        
        # Add the last column boundary
        if current_x is not None:
            column_boundaries.append(current_x)
        
        grid['columns'] = column_boundaries
        
        # Create cells based on row and column intersections
        for row_idx, row in enumerate(grid['rows']):
            for element in row:
                # Find which columns this element spans
                start_col = None
                end_col = None
                
                for col_idx, col_x in enumerate(column_boundaries):
                    if start_col is None and abs(element['x0'] - col_x) <= column_tolerance:
                        start_col = col_idx
                    
                    if start_col is not None and end_col is None and abs(element['x1'] - col_x) <= column_tolerance:
                        end_col = col_idx
                
                if start_col is not None:
                    # If end_col wasn't found, assume it spans only one column
                    if end_col is None:
                        end_col = start_col
                    
                    # Create cell
                    cell_key = f"{row_idx}_{start_col}_{end_col}"
                    grid['cells'][cell_key] = {
                        'element': element,
                        'row': row_idx,
                        'col_start': start_col,
                        'col_end': end_col,
                        'text': element['text']
                    }
        
        return grid
    
    def _extract_financial_data(self) -> Dict[str, Any]:
        """
        Extract financial data using grid-based analysis.
        
        Returns:
            Dictionary containing structured financial data
        """
        financial_data = {
            "securities": [],
            "asset_allocation": {},
            "total_value": None,
            "currency": None
        }
        
        # Extract securities from tables
        for table in self.tables:
            securities = self._extract_securities_from_table(table)
            financial_data["securities"].extend(securities)
        
        # Extract asset allocation from grid data
        asset_allocation = self._extract_asset_allocation_from_grid()
        financial_data["asset_allocation"].update(asset_allocation)
        
        # Extract total value from text elements
        total_value, currency = self._extract_total_value_from_text()
        if total_value:
            financial_data["total_value"] = total_value
            financial_data["currency"] = currency
        
        # Extract ISINs from text elements
        isins = self._extract_isins_from_text()
        
        # Match ISINs with securities
        self._match_isins_with_securities(financial_data["securities"], isins)
        
        logger.info(f"Extracted {len(financial_data['securities'])} securities and "
                   f"{len(financial_data['asset_allocation'])} asset classes")
        
        return financial_data
    
    def _extract_securities_from_table(self, table: Table) -> List[Dict[str, Any]]:
        """
        Extract securities information from a table.
        
        Args:
            table: Table element
            
        Returns:
            List of dictionaries with security information
        """
        securities = []
        
        # Get table data
        table_data = table.metadata.get('text_as_html', '')
        
        # Skip if table is empty
        if not table_data:
            return securities
        
        # Parse table data
        rows = []
        header_row = []
        
        # Extract rows from HTML table
        import re
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(table_data, 'html.parser')
        table_element = soup.find('table')
        
        if table_element:
            # Extract header row
            thead = table_element.find('thead')
            if thead:
                header_row = [th.get_text().strip() for th in thead.find_all('th')]
            
            # Extract data rows
            tbody = table_element.find('tbody')
            if tbody:
                for tr in tbody.find_all('tr'):
                    row = [td.get_text().strip() for td in tr.find_all('td')]
                    rows.append(row)
        
        # If no header row was found, use the first row as header
        if not header_row and rows:
            header_row = rows[0]
            rows = rows[1:]
        
        # Find columns for security information
        isin_col = self._find_column_index(header_row, ['isin'])
        name_col = self._find_column_index(header_row, ['name', 'description', 'security'])
        quantity_col = self._find_column_index(header_row, ['quantity', 'nominal', 'shares'])
        price_col = self._find_column_index(header_row, ['price', 'rate'])
        value_col = self._find_column_index(header_row, ['value', 'amount', 'total'])
        currency_col = self._find_column_index(header_row, ['currency', 'ccy'])
        asset_class_col = self._find_column_index(header_row, ['class', 'type', 'category'])
        
        # Process rows
        for row in rows:
            # Skip if row is too short
            if len(row) < max(filter(None, [isin_col, name_col, quantity_col, price_col, value_col, currency_col, asset_class_col]), default=0) + 1:
                continue
            
            security = {}
            
            # Extract ISIN if column was found
            if isin_col is not None and isin_col < len(row):
                isin_value = row[isin_col].strip()
                # Clean up ISIN value (remove "ISIN:" prefix if present)
                isin_value = isin_value.replace("ISIN:", "").strip()
                if self._is_valid_isin(isin_value):
                    security["isin"] = isin_value
            
            # Extract other fields if columns were found
            if name_col is not None and name_col < len(row):
                security["name"] = row[name_col].strip()
            
            if quantity_col is not None and quantity_col < len(row):
                try:
                    quantity = self._parse_numeric_value(row[quantity_col])
                    security["quantity"] = quantity
                except (ValueError, TypeError):
                    pass
            
            if price_col is not None and price_col < len(row):
                try:
                    price = self._parse_numeric_value(row[price_col])
                    security["price"] = price
                except (ValueError, TypeError):
                    pass
            
            if value_col is not None and value_col < len(row):
                try:
                    value = self._parse_numeric_value(row[value_col])
                    security["value"] = value
                except (ValueError, TypeError):
                    pass
            
            if currency_col is not None and currency_col < len(row):
                security["currency"] = row[currency_col].strip()
            
            if asset_class_col is not None and asset_class_col < len(row):
                security["asset_class"] = row[asset_class_col].strip()
            
            # Only add security if we have at least ISIN or name
            if "isin" in security or "name" in security:
                securities.append(security)
        
        return securities
    
    def _extract_asset_allocation_from_grid(self) -> Dict[str, Dict[str, float]]:
        """
        Extract asset allocation information from grid data.
        
        Returns:
            Dictionary with asset allocation information
        """
        asset_allocation = {}
        
        # Look for asset allocation patterns in grid data
        asset_class_keywords = ['liquidity', 'bonds', 'equities', 'structured products', 'other assets']
        
        for page_number, grid in self.grid_data.items():
            for row_idx, row in enumerate(grid['rows']):
                # Check if this row contains asset allocation information
                row_text = ' '.join(element['text'].lower() for element in row)
                
                if any(keyword in row_text for keyword in asset_class_keywords):
                    # This row might contain asset allocation information
                    for element in row:
                        element_text = element['text'].lower()
                        
                        # Check if this element contains an asset class
                        for keyword in asset_class_keywords:
                            if keyword in element_text:
                                # Found an asset class, look for value and weight
                                asset_class = keyword.title()
                                value = None
                                weight = None
                                
                                # Look for value and weight in the same row
                                for value_element in row:
                                    if value_element != element:
                                        # Try to parse as numeric value
                                        try:
                                            numeric_value = self._parse_numeric_value(value_element['text'])
                                            
                                            # Determine if this is value or weight
                                            if '%' in value_element['text']:
                                                weight = numeric_value / 100 if numeric_value > 1 else numeric_value
                                            elif numeric_value > 1000:
                                                value = numeric_value
                                        except (ValueError, TypeError):
                                            pass
                                
                                # If not found in the same row, look in adjacent cells
                                if value is None or weight is None:
                                    # Look in the next column
                                    next_col_key = f"{row_idx}_{element['col'] + 1}"
                                    if next_col_key in grid['cells']:
                                        next_cell = grid['cells'][next_col_key]
                                        try:
                                            numeric_value = self._parse_numeric_value(next_cell['text'])
                                            if value is None and numeric_value > 1000:
                                                value = numeric_value
                                        except (ValueError, TypeError):
                                            pass
                                    
                                    # Look in the next row, same column
                                    next_row_key = f"{row_idx + 1}_{element['col']}"
                                    if next_row_key in grid['cells']:
                                        next_cell = grid['cells'][next_row_key]
                                        try:
                                            numeric_value = self._parse_numeric_value(next_cell['text'])
                                            if weight is None and '%' in next_cell['text']:
                                                weight = numeric_value / 100 if numeric_value > 1 else numeric_value
                                        except (ValueError, TypeError):
                                            pass
                                
                                # Add to asset allocation if we found value or weight
                                if value is not None or weight is not None:
                                    asset_allocation[asset_class] = {}
                                    if value is not None:
                                        asset_allocation[asset_class]['value'] = value
                                    if weight is not None:
                                        asset_allocation[asset_class]['weight'] = weight
        
        return asset_allocation
    
    def _extract_total_value_from_text(self) -> Tuple[Optional[float], Optional[str]]:
        """
        Extract total portfolio value and currency from text elements.
        
        Returns:
            Tuple of (total_value, currency)
        """
        # Look for "total" in text elements
        for element in self.text_elements:
            element_text = str(element).lower()
            
            if 'total' in element_text and any(currency in element_text for currency in ['usd', 'eur', 'chf', 'gbp']):
                # This element might contain the total value
                # Extract numeric value
                import re
                
                # Look for currency
                currency = None
                for curr in ['usd', 'eur', 'chf', 'gbp']:
                    if curr in element_text:
                        currency = curr.upper()
                        break
                
                # Look for numeric value
                numeric_matches = re.findall(r'[\d,\'\.]+', element_text)
                for match in numeric_matches:
                    try:
                        value = self._parse_numeric_value(match)
                        if value > 10000:  # Assume total value is relatively large
                            return value, currency
                    except (ValueError, TypeError):
                        continue
        
        return None, None
    
    def _extract_isins_from_text(self) -> List[Dict[str, Any]]:
        """
        Extract ISINs and associated information from text elements.
        
        Returns:
            List of dictionaries with ISIN information
        """
        isins = []
        
        # Regular expression for ISIN pattern
        import re
        isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
        
        # Look for ISINs in text elements
        for element in self.text_elements:
            element_text = str(element)
            
            # Find all ISINs in this element
            matches = re.findall(isin_pattern, element_text)
            
            for isin in matches:
                # Extract context around the ISIN
                isin_index = element_text.find(isin)
                context_start = max(0, isin_index - 50)
                context_end = min(len(element_text), isin_index + 50)
                context = element_text[context_start:context_end]
                
                # Extract metadata
                metadata = getattr(element, 'metadata', {})
                page_number = metadata.get('page_number', 0)
                
                # Add to ISINs list
                isins.append({
                    'isin': isin,
                    'context': context,
                    'page': page_number,
                    'element': element
                })
        
        return isins
    
    def _match_isins_with_securities(self, securities: List[Dict[str, Any]], 
                                    isins: List[Dict[str, Any]]) -> None:
        """
        Match extracted ISINs with securities and update securities information.
        
        Args:
            securities: List of securities
            isins: List of ISINs with context
        """
        # Create a map of ISINs to securities
        isin_to_security = {}
        for security in securities:
            if 'isin' in security:
                isin_to_security[security['isin']] = security
        
        # Process each ISIN
        for isin_info in isins:
            isin = isin_info['isin']
            context = isin_info['context']
            
            # If this ISIN is already in securities, update with additional information
            if isin in isin_to_security:
                security = isin_to_security[isin]
                
                # Try to extract additional information from context
                if 'name' not in security or not security['name']:
                    # Try to extract name from context
                    name = self._extract_name_from_context(context, isin)
                    if name:
                        security['name'] = name
                
                if 'asset_class' not in security:
                    # Try to extract asset class from context
                    asset_class = self._extract_asset_class_from_context(context)
                    if asset_class:
                        security['asset_class'] = asset_class
            else:
                # This is a new ISIN, create a new security
                new_security = {
                    'isin': isin
                }
                
                # Try to extract information from context
                name = self._extract_name_from_context(context, isin)
                if name:
                    new_security['name'] = name
                
                asset_class = self._extract_asset_class_from_context(context)
                if asset_class:
                    new_security['asset_class'] = asset_class
                
                # Add to securities list
                securities.append(new_security)
                isin_to_security[isin] = new_security
    
    def _extract_name_from_context(self, context: str, isin: str) -> Optional[str]:
        """
        Extract security name from context around an ISIN.
        
        Args:
            context: Text context around the ISIN
            isin: ISIN code
            
        Returns:
            Security name if found, None otherwise
        """
        # Remove the ISIN from context
        context = context.replace(isin, '')
        
        # Look for patterns like "Name: XYZ" or "XYZ ISIN:"
        import re
        
        # Pattern 1: After "Name:" or similar
        name_pattern1 = r'(?:name|description|security)\s*:\s*([^,\n]+)'
        match = re.search(name_pattern1, context, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Pattern 2: Before "ISIN:" or similar
        name_pattern2 = r'([^,\n]+)\s+(?:isin|valorn)'
        match = re.search(name_pattern2, context, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Pattern 3: All caps words (common for security names)
        name_pattern3 = r'([A-Z][A-Z\s]+(?:\d+(?:\.\d+)?%?)?)'
        match = re.search(name_pattern3, context)
        if match:
            return match.group(1).strip()
        
        return None
    
    def _extract_asset_class_from_context(self, context: str) -> Optional[str]:
        """
        Extract asset class from context.
        
        Args:
            context: Text context
            
        Returns:
            Asset class if found, None otherwise
        """
        # Look for common asset class keywords
        asset_classes = {
            'Bonds': ['bond', 'fixed income', 'treasury', 'note'],
            'Equities': ['equity', 'stock', 'share'],
            'Structured products': ['structured', 'product', 'certificate'],
            'Liquidity': ['cash', 'liquidity', 'money market'],
            'Other assets': ['other', 'alternative', 'hedge', 'private equity']
        }
        
        context_lower = context.lower()
        
        for asset_class, keywords in asset_classes.items():
            if any(keyword in context_lower for keyword in keywords):
                return asset_class
        
        return None
    
    def _find_column_index(self, header_row: List[str], keywords: List[str]) -> Optional[int]:
        """
        Find column index in a header row by looking for keywords.
        
        Args:
            header_row: List of header cell texts
            keywords: List of keywords to look for
            
        Returns:
            Column index if found, None otherwise
        """
        for i, header in enumerate(header_row):
            header_lower = header.lower()
            if any(keyword in header_lower for keyword in keywords):
                return i
        
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
        if not value:
            raise ValueError("Empty value")
        
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
        analyzer = GridAnalyzer(pdf_path)
        financial_data = analyzer.analyze()
        
        print(f"Extracted {len(financial_data['securities'])} securities")
        print(f"Total value: {financial_data['total_value']} {financial_data['currency']}")
        print(f"Asset allocation: {financial_data['asset_allocation']}")
    else:
        print("Please provide a PDF file path")
