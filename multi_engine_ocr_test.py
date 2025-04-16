"""
Multi-engine OCR test for financial documents.
This script tests multiple OCR approaches and compares their results.
"""
import os
import sys
import json
import re
import pandas as pd
import numpy as np
from PIL import Image
import cv2
import pytesseract
from pdf2image import convert_from_path
import pdfplumber
from tabula import read_pdf
import matplotlib.pyplot as plt
from collections import defaultdict

# Configuration
TESSERACT_CONFIG = r'--oem 3 --psm 6 -l eng+heb'
OUTPUT_DIR = 'ocr_test_results'

def ensure_output_dir():
    """Ensure output directory exists."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def preprocess_image(image):
    """Preprocess image for better OCR results."""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Noise removal
    kernel = np.ones((1, 1), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    return opening

def extract_text_tesseract(image):
    """Extract text using Tesseract OCR."""
    preprocessed = preprocess_image(image)
    text = pytesseract.image_to_string(preprocessed, config=TESSERACT_CONFIG)
    return text

def extract_text_tesseract_with_boxes(image):
    """Extract text with bounding boxes using Tesseract OCR."""
    preprocessed = preprocess_image(image)
    data = pytesseract.image_to_data(preprocessed, config=TESSERACT_CONFIG, output_type=pytesseract.Output.DICT)
    
    # Create a list of dictionaries with text and position
    results = []
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 60 and data['text'][i].strip():  # Filter by confidence and non-empty text
            results.append({
                'text': data['text'][i],
                'x': data['left'][i],
                'y': data['top'][i],
                'width': data['width'][i],
                'height': data['height'][i],
                'conf': data['conf'][i]
            })
    
    return results

def extract_tables_tesseract(image):
    """Extract tables using Tesseract OCR."""
    preprocessed = preprocess_image(image)
    tables = pytesseract.image_to_data(preprocessed, config=TESSERACT_CONFIG, output_type=pytesseract.Output.DATAFRAME)
    return tables

def extract_tables_tabula(pdf_path, page):
    """Extract tables using Tabula."""
    try:
        tables = read_pdf(pdf_path, pages=page, multiple_tables=True)
        return tables
    except Exception as e:
        print(f"Error extracting tables with Tabula: {str(e)}")
        return []

def extract_text_pdfplumber(pdf_path, page):
    """Extract text using pdfplumber."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page <= len(pdf.pages):
                return pdf.pages[page-1].extract_text()
            else:
                return ""
    except Exception as e:
        print(f"Error extracting text with pdfplumber: {str(e)}")
        return ""

def extract_tables_pdfplumber(pdf_path, page):
    """Extract tables using pdfplumber."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page <= len(pdf.pages):
                return pdf.pages[page-1].extract_tables()
            else:
                return []
    except Exception as e:
        print(f"Error extracting tables with pdfplumber: {str(e)}")
        return []

def find_financial_data(text):
    """Find financial data in text."""
    # Look for currency values
    currency_pattern = r'[\$€£¥]?\s*(\d{1,3}(?:[,.]\d{3})*(?:\.\d+)?)'
    currency_matches = re.findall(currency_pattern, text)
    
    # Look for percentages
    percentage_pattern = r'(\d+(?:\.\d+)?)\s*%'
    percentage_matches = re.findall(percentage_pattern, text)
    
    # Look for dates
    date_pattern = r'\d{1,2}[./-]\d{1,2}[./-]\d{2,4}'
    date_matches = re.findall(date_pattern, text)
    
    # Look for ISIN numbers
    isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
    isin_matches = re.findall(isin_pattern, text)
    
    return {
        'currency_values': currency_matches,
        'percentages': percentage_matches,
        'dates': date_matches,
        'isins': isin_matches
    }

def extract_structured_data(text):
    """Extract structured data from text."""
    # Look for key-value pairs
    kv_pattern = r'([A-Za-z\s]+):\s*(.+?)(?=\n|$)'
    kv_matches = re.findall(kv_pattern, text)
    
    # Convert to dictionary
    kv_dict = {k.strip(): v.strip() for k, v in kv_matches}
    
    return kv_dict

def compare_ocr_results(results):
    """Compare OCR results from different engines."""
    # Count occurrences of each value
    value_counts = defaultdict(int)
    
    for engine, data in results.items():
        if 'financial_data' in data:
            for value_type, values in data['financial_data'].items():
                for value in values:
                    value_counts[f"{value_type}:{value}"] += 1
    
    # Find values with high agreement
    high_agreement = {k: v for k, v in value_counts.items() if v > 1}
    
    return {
        'value_counts': dict(value_counts),
        'high_agreement': high_agreement
    }

def process_pdf(pdf_path):
    """Process a PDF file with multiple OCR engines."""
    print(f"Processing PDF: {pdf_path}")
    
    # Convert PDF to images
    try:
        pages = convert_from_path(pdf_path)
    except Exception as e:
        print(f"Error converting PDF to images: {str(e)}")
        return None
    
    results = {}
    
    # Process each page
    for i, page in enumerate(pages):
        page_num = i + 1
        print(f"Processing page {page_num}...")
        
        # Convert PIL Image to numpy array for OpenCV
        page_np = np.array(page)
        
        # Extract text with Tesseract
        tesseract_text = extract_text_tesseract(page_np)
        tesseract_boxes = extract_text_tesseract_with_boxes(page_np)
        
        # Extract text with pdfplumber
        pdfplumber_text = extract_text_pdfplumber(pdf_path, page_num)
        
        # Extract tables with Tabula
        tabula_tables = extract_tables_tabula(pdf_path, page_num)
        
        # Extract tables with pdfplumber
        pdfplumber_tables = extract_tables_pdfplumber(pdf_path, page_num)
        
        # Find financial data in text
        tesseract_financial = find_financial_data(tesseract_text)
        pdfplumber_financial = find_financial_data(pdfplumber_text)
        
        # Extract structured data
        tesseract_structured = extract_structured_data(tesseract_text)
        pdfplumber_structured = extract_structured_data(pdfplumber_text)
        
        # Store results
        page_results = {
            'tesseract': {
                'text': tesseract_text,
                'boxes': tesseract_boxes,
                'financial_data': tesseract_financial,
                'structured_data': tesseract_structured
            },
            'pdfplumber': {
                'text': pdfplumber_text,
                'tables': pdfplumber_tables,
                'financial_data': pdfplumber_financial,
                'structured_data': pdfplumber_structured
            },
            'tabula': {
                'tables': [t.to_dict() for t in tabula_tables]
            }
        }
        
        # Compare results
        comparison = compare_ocr_results(page_results)
        page_results['comparison'] = comparison
        
        results[f"page_{page_num}"] = page_results
        
        # Save page image for reference
        page.save(os.path.join(OUTPUT_DIR, f"page_{page_num}.png"))
    
    return results

def analyze_financial_data(results):
    """Analyze financial data from OCR results."""
    # Collect all financial data
    all_financial_data = {
        'currency_values': [],
        'percentages': [],
        'dates': [],
        'isins': []
    }
    
    for page_key, page_data in results.items():
        for engine, engine_data in page_data.items():
            if engine != 'comparison' and 'financial_data' in engine_data:
                for data_type, values in engine_data['financial_data'].items():
                    all_financial_data[data_type].extend(values)
    
    # Remove duplicates
    for data_type in all_financial_data:
        all_financial_data[data_type] = list(set(all_financial_data[data_type]))
    
    # Sort currency values by magnitude
    try:
        all_financial_data['currency_values'] = sorted(
            [float(v.replace(',', '')) for v in all_financial_data['currency_values'] if v],
            reverse=True
        )
    except Exception:
        pass
    
    return all_financial_data

def create_report(results, financial_data, pdf_path):
    """Create a report of OCR results."""
    report = {
        'pdf_path': pdf_path,
        'num_pages': len([k for k in results.keys() if k.startswith('page_')]),
        'financial_data': financial_data,
        'engines_used': ['tesseract', 'pdfplumber', 'tabula'],
        'potential_portfolio_value': None
    }
    
    # Look for potential portfolio value
    if financial_data['currency_values']:
        # Filter for values in a reasonable range for portfolio value
        potential_values = [v for v in financial_data['currency_values'] if v > 1000000 and v < 100000000]
        if potential_values:
            report['potential_portfolio_value'] = potential_values[0]
    
    # Count ISINs
    report['num_isins'] = len(financial_data['isins'])
    
    # Generate HTML report
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Financial Document OCR Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .section {{ margin-bottom: 30px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            .highlight {{ background-color: #ffffcc; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Financial Document OCR Report</h1>
            <p>Document: {os.path.basename(pdf_path)}</p>
            <p>Pages: {report['num_pages']}</p>
            
            <div class="section">
                <h2>Portfolio Summary</h2>
                <p>Potential Portfolio Value: ${report['potential_portfolio_value']:,.2f}</p>
                <p>Number of Securities (ISINs): {report['num_isins']}</p>
            </div>
            
            <div class="section">
                <h2>Top Financial Values</h2>
                <table>
                    <tr>
                        <th>Value</th>
                        <th>Potential Meaning</th>
                    </tr>
    """
    
    # Add top financial values
    for i, value in enumerate(financial_data['currency_values'][:10]):
        meaning = "Unknown"
        if i == 0 and value > 1000000:
            meaning = "Portfolio Value"
        elif 1000 < value < 1000000:
            meaning = "Security Value"
        
        html_report += f"""
                    <tr>
                        <td>${value:,.2f}</td>
                        <td>{meaning}</td>
                    </tr>
        """
    
    html_report += """
                </table>
            </div>
            
            <div class="section">
                <h2>Securities (ISINs)</h2>
                <table>
                    <tr>
                        <th>ISIN</th>
                    </tr>
    """
    
    # Add ISINs
    for isin in financial_data['isins']:
        html_report += f"""
                    <tr>
                        <td>{isin}</td>
                    </tr>
        """
    
    html_report += """
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Save HTML report
    report_path = os.path.join(OUTPUT_DIR, 'ocr_report.html')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    # Save JSON results
    json_path = os.path.join(OUTPUT_DIR, 'ocr_results.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        # Convert non-serializable objects to strings
        serializable_results = {}
        for page_key, page_data in results.items():
            serializable_results[page_key] = {}
            for engine_key, engine_data in page_data.items():
                if engine_key == 'comparison':
                    serializable_results[page_key][engine_key] = engine_data
                else:
                    serializable_results[page_key][engine_key] = {}
                    for data_key, data_value in engine_data.items():
                        if data_key == 'tables' and engine_key == 'tabula':
                            serializable_results[page_key][engine_key][data_key] = "Tables extracted (not shown in JSON)"
                        elif data_key == 'tables' and engine_key == 'pdfplumber':
                            serializable_results[page_key][engine_key][data_key] = f"{len(data_value)} tables extracted"
                        else:
                            serializable_results[page_key][engine_key][data_key] = data_value
        
        json.dump(serializable_results, f, indent=2)
    
    return report_path

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python multi_engine_ocr_test.py <pdf_path>")
        return 1
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return 1
    
    # Ensure output directory exists
    ensure_output_dir()
    
    # Process PDF
    results = process_pdf(pdf_path)
    if results is None:
        return 1
    
    # Analyze financial data
    financial_data = analyze_financial_data(results)
    
    # Create report
    report_path = create_report(results, financial_data, pdf_path)
    
    print(f"\nOCR test completed. Report saved to: {report_path}")
    print(f"Open the report in your browser: file://{os.path.abspath(report_path)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
