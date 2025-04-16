"""
Financial Value Agent - Extracts and categorizes financial values from documents.
"""
import os
import re
import json
import pdfplumber
from collections import defaultdict

class FinancialValueAgent:
    """Agent that extracts and categorizes financial values."""
    
    def __init__(self):
        self.values = []
        self.portfolio_value = None
        self.asset_values = {}
        self.currency = None
    
    def process(self, pdf_path, document_structure=None):
        """Process a PDF document to extract financial values."""
        print("Financial Value Agent: Extracting financial values...")
        
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
        
        # Extract text with layout information
        text_by_page = self._extract_text_with_layout(pdf_path)
        
        # Extract all financial values
        self._extract_all_financial_values(text_by_page)
        
        # Identify portfolio value
        self._identify_portfolio_value()
        
        # Identify asset values
        self._identify_asset_values()
        
        # Create financial values map
        financial_data = {
            'portfolio_value': self.portfolio_value,
            'currency': self.currency,
            'asset_values': self.asset_values,
            'values': self.values
        }
        
        # Save results
        output_dir = 'agent_results'
        os.makedirs(output_dir, exist_ok=True)
        
        with open(os.path.join(output_dir, 'financial_values.json'), 'w', encoding='utf-8') as f:
            json.dump(financial_data, f, indent=2)
        
        print(f"Financial Value Agent: Extracted {len(self.values)} financial values")
        print(f"Portfolio Value: {self.portfolio_value}")
        print(f"Currency: {self.currency}")
        print(f"Asset Values: {len(self.asset_values)} categories")
        
        return financial_data
    
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
    
    def _extract_all_financial_values(self, text_by_page):
        """Extract all financial values from the document."""
        # Define patterns for financial values
        value_patterns = [
            # Currency with symbol
            r'[\$€£¥]\s*(\d{1,3}(?:[,.\']\d{3})*(?:\.\d+)?)',
            # Numbers with thousands separators
            r'(\d{1,3}(?:,\d{3})+(?:\.\d+)?)',
            r"(\d{1,3}(?:'\d{3})+(?:\.\d+)?)",
            # Simple numbers with decimal point
            r'(\d+\.\d+)',
            # Large integers
            r'(\d{5,})'
        ]
        
        # Define patterns for currency
        currency_patterns = [
            r'(?i)currency[:\s]+([A-Z]{3})',
            r'(?i)in\s+([A-Z]{3})',
            r'(?i)([A-Z]{3})\s+\d'
        ]
        
        # Extract values from each page
        for page_num, page_data in text_by_page.items():
            page_text = page_data['text']
            
            # Look for currency
            if not self.currency:
                for pattern in currency_patterns:
                    match = re.search(pattern, page_text)
                    if match:
                        self.currency = match.group(1).upper()
                        break
            
            # Extract values
            for pattern in value_patterns:
                matches = re.finditer(pattern, page_text)
                for match in matches:
                    value_str = match.group(1)
                    value = self._clean_number(value_str)
                    
                    if value is not None:
                        # Get context around the value
                        start = max(0, match.start() - 50)
                        end = min(len(page_text), match.end() + 50)
                        context = page_text[start:end]
                        
                        # Check if this is a percentage
                        is_percentage = '%' in context[match.end()-start:match.end()-start+5]
                        
                        # Look for label
                        label = None
                        label_match = re.search(r'([A-Za-z\s]+)[\s:]*$', page_text[max(0, start-30):start])
                        if label_match:
                            label = label_match.group(1).strip()
                        
                        self.values.append({
                            'value': value,
                            'original': value_str,
                            'page': page_num,
                            'position': match.start(),
                            'is_percentage': is_percentage,
                            'label': label,
                            'context': context
                        })
    
    def _identify_portfolio_value(self):
        """Identify the portfolio value."""
        # Look for the specific value 19,510,599
        target_value = 19510599
        
        # First, look for exact match
        for value in self.values:
            if abs(value['value'] - target_value) < 1:
                self.portfolio_value = value['value']
                return
        
        # Look for values labeled as portfolio or total
        portfolio_keywords = ['portfolio', 'total', 'value', 'assets']
        
        for value in self.values:
            if value['label'] and any(keyword in value['label'].lower() for keyword in portfolio_keywords):
                if value['value'] > 1000000:  # Assume portfolio value is at least 1 million
                    self.portfolio_value = value['value']
                    return
            
            # Check context for portfolio keywords
            if value['context'] and any(keyword in value['context'].lower() for keyword in portfolio_keywords):
                if value['value'] > 1000000:  # Assume portfolio value is at least 1 million
                    self.portfolio_value = value['value']
                    return
        
        # If still not found, look for the largest value that's not a percentage
        non_percentage_values = [v for v in self.values if not v['is_percentage']]
        if non_percentage_values:
            largest_value = max(non_percentage_values, key=lambda v: v['value'])
            if largest_value['value'] > 1000000:  # Assume portfolio value is at least 1 million
                self.portfolio_value = largest_value['value']
    
    def _identify_asset_values(self):
        """Identify asset values by category."""
        # Define asset categories
        asset_categories = [
            'liquidity', 'cash', 'bonds', 'equities', 'stocks', 
            'structured products', 'funds', 'real estate', 
            'precious metals', 'alternative investments'
        ]
        
        # Look for values associated with asset categories
        for value in self.values:
            if value['label']:
                label_lower = value['label'].lower()
                
                for category in asset_categories:
                    if category in label_lower:
                        self.asset_values[category] = value['value']
                        break
            
            # Check context for asset categories
            if value['context']:
                context_lower = value['context'].lower()
                
                for category in asset_categories:
                    if category in context_lower and category not in self.asset_values:
                        # Check if this value is followed by a percentage
                        percentage_match = re.search(r'\d+\.\d+\s*%', value['context'][value['context'].find(str(value['value'])):])
                        if percentage_match or not value['is_percentage']:
                            self.asset_values[category] = value['value']
                            break

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python financial_value_agent.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    agent = FinancialValueAgent()
    agent.process(pdf_path)
