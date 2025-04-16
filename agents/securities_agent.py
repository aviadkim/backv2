"""
Securities Agent - Extracts securities information from financial documents.
"""
import os
import re
import json
import pdfplumber
from collections import defaultdict

class SecuritiesAgent:
    """Agent that extracts securities information."""
    
    def __init__(self):
        self.securities = []
        self.asset_classes = {}
    
    def process(self, pdf_path, document_structure=None, financial_values=None):
        """Process a PDF document to extract securities information."""
        print("Securities Agent: Extracting securities information...")
        
        # Load document structure if provided
        if document_structure:
            self.document_structure = document_structure
        else:
            # Try to load from file
            try:
                with open('agent_results/document_structure.json', 'r', encoding='utf-8') as f:
                    self.document_structure = json.load(f)
            except:
                self.document_structure = None
        
        # Load financial values if provided
        if financial_values:
            self.financial_values = financial_values
        else:
            # Try to load from file
            try:
                with open('agent_results/financial_values.json', 'r', encoding='utf-8') as f:
                    self.financial_values = json.load(f)
            except:
                self.financial_values = None
        
        # Extract text with layout information
        text_by_page = self._extract_text_with_layout(pdf_path)
        
        # Extract tables
        tables = self._extract_tables(pdf_path)
        
        # Extract securities from text
        self._extract_securities_from_text(text_by_page)
        
        # Extract securities from tables
        self._extract_securities_from_tables(tables)
        
        # Merge and deduplicate securities
        self._merge_securities()
        
        # Calculate missing values
        self._calculate_missing_values()
        
        # Categorize securities by asset class
        self._categorize_securities()
        
        # Create securities data
        securities_data = {
            'securities': self.securities,
            'asset_classes': self.asset_classes,
            'total_value': sum(security.get('value', 0) for security in self.securities if security.get('value'))
        }
        
        # Save results
        output_dir = 'agent_results'
        os.makedirs(output_dir, exist_ok=True)
        
        with open(os.path.join(output_dir, 'securities.json'), 'w', encoding='utf-8') as f:
            json.dump(securities_data, f, indent=2)
        
        print(f"Securities Agent: Extracted {len(self.securities)} securities")
        print(f"Total Value: ${securities_data['total_value']:,.2f}")
        print(f"Asset Classes: {', '.join(self.asset_classes.keys())}")
        
        return securities_data
    
    def _extract_text_with_layout(self, pdf_path):
        """Extract text with layout information."""
        text_by_page = {}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text with layout information
                    text_elements = []
                    
                    # Extract words with position and font information
                    words = page.extract_words(
                        keep_blank_chars=True,
                        x_tolerance=3,
                        y_tolerance=3,
                        extra_attrs=['fontname', 'size']
                    )
                    
                    for word in words:
                        text_elements.append({
                            'text': word['text'],
                            'x0': word['x0'],
                            'y0': word['top'],
                            'x1': word['x1'],
                            'y1': word['bottom'],
                            'font': word.get('fontname', ''),
                            'size': word.get('size', 0)
                        })
                    
                    # Sort elements by y-position (top to bottom) and then x-position (left to right)
                    text_elements.sort(key=lambda e: (e['y0'], e['x0']))
                    
                    # Group elements by line
                    lines = []
                    current_line = []
                    current_y = None
                    
                    for element in text_elements:
                        if current_y is None or abs(element['y0'] - current_y) < 5:  # Tolerance for same line
                            current_line.append(element)
                            current_y = element['y0']
                        else:
                            if current_line:
                                lines.append(current_line)
                            current_line = [element]
                            current_y = element['y0']
                    
                    if current_line:
                        lines.append(current_line)
                    
                    text_by_page[page_num] = {
                        'elements': text_elements,
                        'lines': lines,
                        'text': page.extract_text()
                    }
        except Exception as e:
            print(f"Error extracting text with layout: {str(e)}")
        
        return text_by_page
    
    def _extract_tables(self, pdf_path):
        """Extract tables from the PDF."""
        tables_by_page = {}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    tables = page.extract_tables()
                    if tables:
                        tables_by_page[page_num] = tables
        except Exception as e:
            print(f"Error extracting tables: {str(e)}")
        
        return tables_by_page
    
    def _clean_number(self, value_str):
        """Clean a number string by removing quotes and commas."""
        if not value_str:
            return None
        
        # Replace single quotes with nothing (European number format)
        cleaned = str(value_str).replace("'", "")
        
        # Replace commas with nothing (US number format)
        cleaned = cleaned.replace(",", "")
        
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.-]', '', cleaned)
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def _extract_securities_from_text(self, text_by_page):
        """Extract securities from text."""
        # Look for ISIN numbers
        isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
        
        for page_num, page_data in text_by_page.items():
            page_text = page_data['text']
            
            # Find all ISIN numbers
            isin_matches = re.finditer(isin_pattern, page_text)
            
            for match in isin_matches:
                isin = match.group(0)
                
                # Get context around ISIN (200 characters before and after)
                start = max(0, match.start() - 200)
                end = min(len(page_text), match.end() + 200)
                context = page_text[start:end]
                
                # Extract security name (usually before ISIN)
                name = None
                name_match = re.search(r'([A-Za-z0-9\s\.\-\&]+)(?=.*' + isin + ')', context, re.DOTALL)
                if name_match:
                    name = name_match.group(1).strip()
                
                # Extract numeric values
                values = []
                value_pattern = r'(\d{1,3}(?:[,.\']\d{3})*(?:\.\d+)?)'
                value_matches = re.findall(value_pattern, context)
                
                for val_str in value_matches:
                    val = self._clean_number(val_str)
                    if val is not None:
                        values.append(val)
                
                # Try to identify quantity, price, value
                quantity = None
                price = None
                value = None
                
                if values:
                    # Sort by magnitude
                    values.sort()
                    
                    # Look for values in typical ranges
                    # Price is usually around 100 for bonds
                    price_candidates = [v for v in values if 80 <= v <= 120]
                    if price_candidates:
                        price = price_candidates[0]
                        
                        # Value is usually large
                        value_candidates = [v for v in values if v > 10000 and v < 10000000]
                        if value_candidates:
                            value = value_candidates[0]
                            
                            # Calculate quantity
                            if price > 0:
                                quantity = value / price
                
                # Extract maturity date for bonds
                maturity_date = None
                maturity_patterns = [
                    r'(?i)maturity[:\s]+(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})',
                    r'(?i)(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})(?=.*maturity)',
                    r'(?i)(\d{4}-\d{2}-\d{2})'
                ]
                
                for pattern in maturity_patterns:
                    match = re.search(pattern, context)
                    if match:
                        maturity_date = match.group(1)
                        break
                
                # Determine asset class
                asset_class = self._determine_asset_class(context, name)
                
                self.securities.append({
                    'isin': isin,
                    'name': name,
                    'quantity': quantity,
                    'price': price,
                    'value': value,
                    'maturity_date': maturity_date,
                    'asset_class': asset_class,
                    'page': page_num,
                    'source': 'text'
                })
    
    def _extract_securities_from_tables(self, tables_by_page):
        """Extract securities from tables."""
        for page_num, tables in tables_by_page.items():
            for table_idx, table in enumerate(tables):
                # Skip empty tables
                if not table or len(table) <= 1:
                    continue
                
                # Try to identify header row
                header_row = table[0]
                
                # Check if this table contains securities
                has_isin = any('isin' in str(cell).lower() for cell in header_row if cell)
                has_security = any('security' in str(cell).lower() for cell in header_row if cell)
                
                if not (has_isin or has_security):
                    # Check if any row contains an ISIN
                    for row in table[1:]:
                        for cell in row:
                            if cell and re.search(r'[A-Z]{2}[A-Z0-9]{9}[0-9]', str(cell)):
                                has_isin = True
                                break
                        if has_isin:
                            break
                
                if has_isin or has_security:
                    # This table likely contains securities
                    for row_idx, row in enumerate(table[1:], 1):
                        # Skip empty rows
                        if not row or all(not cell for cell in row):
                            continue
                        
                        # Extract ISIN
                        isin = None
                        for cell in row:
                            if cell and re.search(r'[A-Z]{2}[A-Z0-9]{9}[0-9]', str(cell)):
                                isin = re.search(r'[A-Z]{2}[A-Z0-9]{9}[0-9]', str(cell)).group(0)
                                break
                        
                        if not isin:
                            continue
                        
                        # Extract other information
                        name = None
                        quantity = None
                        price = None
                        value = None
                        maturity_date = None
                        
                        # Try to identify columns by header
                        column_indices = {}
                        for col_idx, header in enumerate(header_row):
                            if not header:
                                continue
                            
                            header_lower = str(header).lower()
                            
                            if 'name' in header_lower or 'description' in header_lower or 'security' in header_lower:
                                column_indices['name'] = col_idx
                            elif 'quantity' in header_lower or 'amount' in header_lower:
                                column_indices['quantity'] = col_idx
                            elif 'price' in header_lower or 'rate' in header_lower:
                                column_indices['price'] = col_idx
                            elif 'value' in header_lower or 'total' in header_lower:
                                column_indices['value'] = col_idx
                            elif 'maturity' in header_lower or 'date' in header_lower:
                                column_indices['maturity_date'] = col_idx
                        
                        # Extract values based on column indices
                        for key, col_idx in column_indices.items():
                            if col_idx < len(row) and row[col_idx]:
                                if key == 'name':
                                    name = str(row[col_idx]).strip()
                                elif key in ['quantity', 'price', 'value']:
                                    value_str = str(row[col_idx])
                                    value_num = self._clean_number(value_str)
                                    if value_num is not None:
                                        locals()[key] = value_num
                                elif key == 'maturity_date':
                                    maturity_date = str(row[col_idx]).strip()
                        
                        # If name not found, try to find it in the row
                        if not name:
                            for cell in row:
                                if cell and isinstance(cell, str) and len(cell) > 5 and not re.search(r'[A-Z]{2}[A-Z0-9]{9}[0-9]', cell):
                                    name = cell.strip()
                                    break
                        
                        # Determine asset class
                        asset_class = self._determine_asset_class(' '.join(str(cell) for cell in row if cell), name)
                        
                        self.securities.append({
                            'isin': isin,
                            'name': name,
                            'quantity': quantity,
                            'price': price,
                            'value': value,
                            'maturity_date': maturity_date,
                            'asset_class': asset_class,
                            'page': page_num,
                            'table_idx': table_idx,
                            'row_idx': row_idx,
                            'source': 'table'
                        })
    
    def _determine_asset_class(self, context, name):
        """Determine the asset class of a security."""
        context_lower = context.lower() if context else ''
        name_lower = name.lower() if name else ''
        
        # Check for bonds
        if any(term in context_lower or term in name_lower for term in ['bond', 'note', 'fixed income', 'treasury', 'maturity']):
            return 'Bonds'
        
        # Check for equities
        if any(term in context_lower or term in name_lower for term in ['equity', 'stock', 'share', 'common']):
            return 'Equities'
        
        # Check for structured products
        if any(term in context_lower or term in name_lower for term in ['structured', 'product', 'certificate', 'warrant']):
            return 'Structured Products'
        
        # Check for funds
        if any(term in context_lower or term in name_lower for term in ['fund', 'etf', 'index']):
            return 'Funds'
        
        # Check for cash/liquidity
        if any(term in context_lower or term in name_lower for term in ['cash', 'liquidity', 'deposit']):
            return 'Cash'
        
        # Default to Other
        return 'Other'
    
    def _merge_securities(self):
        """Merge and deduplicate securities."""
        # Group by ISIN
        securities_by_isin = defaultdict(list)
        for security in self.securities:
            securities_by_isin[security['isin']].append(security)
        
        # Merge securities with the same ISIN
        merged_securities = []
        for isin, securities in securities_by_isin.items():
            if len(securities) == 1:
                merged_securities.append(securities[0])
            else:
                # Merge multiple securities
                merged = {
                    'isin': isin,
                    'name': None,
                    'quantity': None,
                    'price': None,
                    'value': None,
                    'maturity_date': None,
                    'asset_class': None,
                    'sources': []
                }
                
                # Collect all non-None values
                for security in securities:
                    for key in ['name', 'quantity', 'price', 'value', 'maturity_date', 'asset_class']:
                        if security.get(key) is not None and merged[key] is None:
                            merged[key] = security[key]
                    
                    # Add source
                    source = security.get('source')
                    if source and source not in merged['sources']:
                        merged['sources'].append(source)
                
                merged_securities.append(merged)
        
        self.securities = merged_securities
    
    def _calculate_missing_values(self):
        """Calculate missing values based on available data."""
        for security in self.securities:
            # If we have quantity and price but no value, calculate value
            if security['quantity'] is not None and security['price'] is not None and security['value'] is None:
                security['value'] = security['quantity'] * security['price']
            
            # If we have quantity and value but no price, calculate price
            elif security['quantity'] is not None and security['value'] is not None and security['price'] is None:
                security['price'] = security['value'] / security['quantity']
            
            # If we have price and value but no quantity, calculate quantity
            elif security['price'] is not None and security['value'] is not None and security['quantity'] is None:
                security['quantity'] = security['value'] / security['price']
    
    def _categorize_securities(self):
        """Categorize securities by asset class."""
        # Group securities by asset class
        for security in self.securities:
            asset_class = security.get('asset_class', 'Other')
            if asset_class not in self.asset_classes:
                self.asset_classes[asset_class] = []
            
            self.asset_classes[asset_class].append(security)
        
        # Calculate total value for each asset class
        for asset_class, securities in self.asset_classes.items():
            total_value = sum(security.get('value', 0) for security in securities if security.get('value'))
            self.asset_classes[asset_class] = {
                'securities': securities,
                'total_value': total_value
            }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python securities_agent.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    agent = SecuritiesAgent()
    agent.process(pdf_path)
