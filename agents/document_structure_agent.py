"""
Document Structure Agent - Identifies document structure, headlines, and sections.
"""
import os
import re
import json
import pdfplumber
from collections import defaultdict

class DocumentStructureAgent:
    """Agent that identifies document structure, headlines, and sections."""
    
    def __init__(self):
        self.sections = []
        self.headlines = []
        self.document_type = None
        self.document_date = None
        self.client_info = {}
    
    def process(self, pdf_path):
        """Process a PDF document to identify its structure."""
        print("Document Structure Agent: Analyzing document structure...")
        
        # Extract text with layout information
        text_by_page = self._extract_text_with_layout(pdf_path)
        
        # Identify document type and date
        self._identify_document_metadata(text_by_page)
        
        # Identify headlines and sections
        self._identify_headlines_and_sections(text_by_page)
        
        # Create document structure map
        structure = {
            'document_type': self.document_type,
            'document_date': self.document_date,
            'client_info': self.client_info,
            'headlines': self.headlines,
            'sections': self.sections
        }
        
        # Save results
        output_dir = 'agent_results'
        os.makedirs(output_dir, exist_ok=True)
        
        with open(os.path.join(output_dir, 'document_structure.json'), 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2)
        
        print(f"Document Structure Agent: Identified {len(self.headlines)} headlines and {len(self.sections)} sections")
        print(f"Document Type: {self.document_type}")
        print(f"Document Date: {self.document_date}")
        
        return structure
    
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
    
    def _identify_document_metadata(self, text_by_page):
        """Identify document type and date."""
        # Look for document type and date in the first few pages
        for page_num in range(1, min(4, len(text_by_page) + 1)):
            if page_num not in text_by_page:
                continue
            
            page_text = text_by_page[page_num]['text']
            
            # Look for document type
            document_type_patterns = [
                r'(?i)valuation',
                r'(?i)portfolio\s+report',
                r'(?i)financial\s+statement',
                r'(?i)investment\s+summary'
            ]
            
            for pattern in document_type_patterns:
                match = re.search(pattern, page_text)
                if match:
                    self.document_type = match.group(0)
                    break
            
            # Look for date
            date_patterns = [
                r'(?i)as\s+of\s+(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})',
                r'(?i)date[:\s]+(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})',
                r'(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, page_text)
                if match:
                    self.document_date = match.group(1)
                    break
            
            # Look for client information
            client_patterns = {
                'name': r'(?i)client\s+name[:\s]+([^\n]+)',
                'number': r'(?i)client\s+number[:\s]+([^\n]+)',
                'account': r'(?i)account[:\s]+([^\n]+)'
            }
            
            for key, pattern in client_patterns.items():
                match = re.search(pattern, page_text)
                if match:
                    self.client_info[key] = match.group(1).strip()
            
            # If we found both document type and date, we can stop
            if self.document_type and self.document_date:
                break
    
    def _identify_headlines_and_sections(self, text_by_page):
        """Identify headlines and sections in the document."""
        # Collect all text elements
        all_elements = []
        for page_num, page_data in text_by_page.items():
            for element in page_data['elements']:
                element['page'] = page_num
                all_elements.append(element)
        
        # Sort elements by size (largest first) to identify potential headlines
        all_elements.sort(key=lambda e: e.get('size', 0), reverse=True)
        
        # Get the most common font size
        sizes = [e.get('size', 0) for e in all_elements if e.get('size', 0) > 0]
        size_counts = defaultdict(int)
        for size in sizes:
            size_counts[size] += 1
        
        # Find the most common size (body text)
        body_size = max(size_counts.items(), key=lambda x: x[1])[0] if size_counts else 0
        
        # Identify headlines (larger than body text)
        headline_elements = [e for e in all_elements if e.get('size', 0) > body_size * 1.2]
        
        # Group headline elements by line
        headline_lines = defaultdict(list)
        for element in headline_elements:
            key = (element['page'], round(element['y0']))
            headline_lines[key].append(element)
        
        # Sort headline lines by page and y-position
        sorted_headline_keys = sorted(headline_lines.keys(), key=lambda k: (k[0], k[1]))
        
        # Extract headlines
        for key in sorted_headline_keys:
            elements = headline_lines[key]
            elements.sort(key=lambda e: e['x0'])  # Sort by x-position
            
            headline_text = ' '.join(e['text'] for e in elements)
            
            # Skip empty or very short headlines
            if len(headline_text.strip()) < 3:
                continue
            
            self.headlines.append({
                'text': headline_text,
                'page': key[0],
                'y_position': key[1],
                'font_size': max(e.get('size', 0) for e in elements)
            })
        
        # Identify sections based on headlines
        if self.headlines:
            current_section = None
            
            for i, headline in enumerate(self.headlines):
                # Skip if this is a sub-headline
                if current_section and headline['font_size'] < current_section['headline']['font_size']:
                    continue
                
                # Create a new section
                section = {
                    'headline': headline,
                    'start_page': headline['page'],
                    'end_page': self.headlines[i+1]['page'] if i+1 < len(self.headlines) else max(text_by_page.keys())
                }
                
                self.sections.append(section)
                current_section = section
        
        # Sort headlines and sections by page and position
        self.headlines.sort(key=lambda h: (h['page'], h['y_position']))
        self.sections.sort(key=lambda s: (s['start_page'], s['headline']['y_position']))

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python document_structure_agent.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    agent = DocumentStructureAgent()
    agent.process(pdf_path)
