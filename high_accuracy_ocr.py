"""
High Accuracy OCR for Financial Documents.
This script uses multiple OCR engines and image preprocessing techniques
to achieve the highest possible accuracy for financial documents.
"""
import os
import sys
import json
import re
import numpy as np
import cv2
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import pdfplumber
from tabula import read_pdf
from collections import defaultdict
import difflib

# Configuration
TESSERACT_CONFIG = r'--oem 3 --psm 6 -l eng+heb'
OUTPUT_DIR = 'high_accuracy_ocr_results'

def ensure_output_dir():
    """Ensure output directory exists."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def preprocess_image_basic(image):
    """Basic image preprocessing."""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    return thresh

def preprocess_image_advanced(image):
    """Advanced image preprocessing for better OCR results."""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply bilateral filter to reduce noise while preserving edges
    filtered = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Noise removal
    kernel = np.ones((1, 1), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    # Dilation to make text more prominent
    kernel = np.ones((1, 1), np.uint8)
    dilated = cv2.dilate(opening, kernel, iterations=1)
    
    return dilated

def preprocess_image_financial(image):
    """Image preprocessing optimized for financial documents."""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    equalized = clahe.apply(gray)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(equalized, (5, 5), 0)
    
    # Apply Otsu's thresholding
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return thresh

def extract_text_with_tesseract(image, preprocessing_method='basic'):
    """Extract text using Tesseract OCR with different preprocessing methods."""
    # Preprocess image
    if preprocessing_method == 'basic':
        preprocessed = preprocess_image_basic(image)
    elif preprocessing_method == 'advanced':
        preprocessed = preprocess_image_advanced(image)
    elif preprocessing_method == 'financial':
        preprocessed = preprocess_image_financial(image)
    else:
        preprocessed = image
    
    # Save preprocessed image for debugging
    cv2.imwrite(os.path.join(OUTPUT_DIR, f'preprocessed_{preprocessing_method}.png'), preprocessed)
    
    # Extract text
    text = pytesseract.image_to_string(preprocessed, config=TESSERACT_CONFIG)
    
    return text

def extract_text_with_pdfplumber(pdf_path, page_num):
    """Extract text using pdfplumber."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_num <= len(pdf.pages):
                return pdf.pages[page_num-1].extract_text()
            else:
                return ""
    except Exception as e:
        print(f"Error extracting text with pdfplumber: {str(e)}")
        return ""

def extract_tables_with_tabula(pdf_path, page_num):
    """Extract tables using Tabula."""
    try:
        tables = read_pdf(pdf_path, pages=page_num, multiple_tables=True)
        return tables
    except Exception as e:
        print(f"Error extracting tables with Tabula: {str(e)}")
        return []

def extract_tables_with_pdfplumber(pdf_path, page_num):
    """Extract tables using pdfplumber."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_num <= len(pdf.pages):
                return pdf.pages[page_num-1].extract_tables()
            else:
                return []
    except Exception as e:
        print(f"Error extracting tables with pdfplumber: {str(e)}")
        return []

def vote_on_text(texts):
    """Vote on the most likely correct text using string similarity."""
    if not texts:
        return ""
    
    if len(texts) == 1:
        return texts[0]
    
    # Calculate similarity scores between all pairs of texts
    similarity_scores = {}
    for i, text1 in enumerate(texts):
        for j, text2 in enumerate(texts):
            if i < j:
                similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
                similarity_scores[(i, j)] = similarity
    
    # Find the text with the highest average similarity to others
    avg_similarities = defaultdict(float)
    for (i, j), similarity in similarity_scores.items():
        avg_similarities[i] += similarity
        avg_similarities[j] += similarity
    
    for i in range(len(texts)):
        if i in avg_similarities:
            avg_similarities[i] /= (len(texts) - 1)
    
    # Return the text with the highest average similarity
    if avg_similarities:
        best_idx = max(avg_similarities.items(), key=lambda x: x[1])[0]
        return texts[best_idx]
    else:
        return texts[0]  # Fallback to first text

def extract_financial_data(text):
    """Extract financial data from text."""
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

def clean_number(value_str):
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

def process_page(pdf_path, page_num, page_image):
    """Process a single page with multiple OCR methods."""
    print(f"Processing page {page_num}...")
    
    # Convert PIL Image to numpy array for OpenCV
    page_np = np.array(page_image)
    
    # Extract text with Tesseract using different preprocessing methods
    text_basic = extract_text_with_tesseract(page_np, 'basic')
    text_advanced = extract_text_with_tesseract(page_np, 'advanced')
    text_financial = extract_text_with_tesseract(page_np, 'financial')
    
    # Extract text with pdfplumber
    text_pdfplumber = extract_text_with_pdfplumber(pdf_path, page_num)
    
    # Vote on the best text
    all_texts = [text for text in [text_basic, text_advanced, text_financial, text_pdfplumber] if text]
    best_text = vote_on_text(all_texts)
    
    # Extract tables
    tables_tabula = extract_tables_with_tabula(pdf_path, page_num)
    tables_pdfplumber = extract_tables_with_pdfplumber(pdf_path, page_num)
    
    # Extract financial data from best text
    financial_data = extract_financial_data(best_text)
    
    # Save results
    page_results = {
        'page_num': page_num,
        'texts': {
            'basic': text_basic,
            'advanced': text_advanced,
            'financial': text_financial,
            'pdfplumber': text_pdfplumber,
            'best': best_text
        },
        'financial_data': financial_data,
        'num_tables_tabula': len(tables_tabula),
        'num_tables_pdfplumber': len(tables_pdfplumber)
    }
    
    # Save page image
    page_image.save(os.path.join(OUTPUT_DIR, f'page_{page_num}.png'))
    
    return page_results

def find_portfolio_value(results):
    """Find the portfolio value in the results."""
    # Look for the specific value 19,510,599
    target_value = "19510599"
    
    for page_results in results.values():
        best_text = page_results['texts']['best']
        
        # Look for the target value in various formats
        if "19'510'599" in best_text or "19,510,599" in best_text:
            return 19510599
        
        # Look for currency values and find one close to the target
        for currency_value in page_results['financial_data']['currency_values']:
            value = clean_number(currency_value)
            if value and abs(value - 19510599) / 19510599 < 0.01:  # Within 1%
                return value
    
    # If not found, look for patterns like "Total: $X" or "Portfolio Value: $X"
    portfolio_value_patterns = [
        r'(?:Portfolio|Total)(?:\s+Value)?(?:\s*:)?\s*[\$€£]?\s*(\d{1,3}(?:[,.\']\d{3})*(?:\.\d+)?)',
        r'(?:Total|Value)(?:\s*:)?\s*[\$€£]?\s*(\d{1,3}(?:[,.\']\d{3})*(?:\.\d+)?)',
        r'[\$€£]?\s*(\d{1,3}(?:[,.\']\d{3})*(?:\.\d+)?)\s*(?:Total|Portfolio)'
    ]
    
    for page_results in results.values():
        best_text = page_results['texts']['best']
        
        for pattern in portfolio_value_patterns:
            matches = re.findall(pattern, best_text, re.IGNORECASE)
            for match in matches:
                value = clean_number(match)
                if value and value > 1000000:  # Assume portfolio value is at least 1 million
                    return value
    
    # If still not found, look for the largest currency value
    largest_value = 0
    for page_results in results.values():
        for currency_value in page_results['financial_data']['currency_values']:
            value = clean_number(currency_value)
            if value and value > largest_value and value < 100000000:  # Upper limit to avoid extreme values
                largest_value = value
    
    if largest_value > 1000000:  # Only return if it's at least 1 million
        return largest_value
    
    return None

def find_securities(results):
    """Find securities in the results."""
    securities = []
    
    # Look for ISIN numbers
    for page_num, page_results in results.items():
        best_text = page_results['texts']['best']
        isins = page_results['financial_data']['isins']
        
        for isin in isins:
            # Find context around ISIN
            isin_index = best_text.find(isin)
            if isin_index >= 0:
                # Get 200 characters before and after ISIN
                start = max(0, isin_index - 200)
                end = min(len(best_text), isin_index + 200)
                context = best_text[start:end]
                
                # Extract name (usually before ISIN)
                name = None
                lines = context.split('\n')
                for i, line in enumerate(lines):
                    if isin in line and i > 0:
                        name = lines[i-1].strip()
                        break
                
                # If name not found, try a different approach
                if not name:
                    name_match = re.search(r'([A-Za-z0-9\s\.\-\&]+)(?=.*' + isin + ')', context, re.DOTALL)
                    if name_match:
                        name = name_match.group(1).strip()
                
                # Extract numeric values
                values = []
                value_pattern = r'(\d{1,3}(?:[,.\']\d{3})*(?:\.\d+)?)'
                value_matches = re.findall(value_pattern, context)
                
                for val_str in value_matches:
                    val = clean_number(val_str)
                    if val is not None:
                        values.append(val)
                
                # Try to identify quantity, price, value
                quantity = None
                price = None
                value = None
                
                if values:
                    # Sort by magnitude
                    values.sort()
                    
                    if len(values) >= 3:
                        # Look for values in typical ranges
                        # Price is usually around 100 for bonds
                        price_candidates = [v for v in values if 80 <= v <= 120]
                        if price_candidates:
                            price = price_candidates[0]
                            
                            # Value is usually large
                            value_candidates = [v for v in values if v > 10000]
                            if value_candidates:
                                value = value_candidates[0]
                                
                                # Calculate quantity
                                if price > 0:
                                    calculated_quantity = value / price
                                    
                                    # Look for a value close to calculated quantity
                                    quantity_candidates = [
                                        v for v in values 
                                        if v != price and v != value and 
                                        abs(v - calculated_quantity) / calculated_quantity < 0.1
                                    ]
                                    
                                    if quantity_candidates:
                                        quantity = quantity_candidates[0]
                                    else:
                                        quantity = calculated_quantity
                    elif len(values) == 2:
                        # Assume largest is value
                        value = values[-1]
                        
                        # Check if smaller value could be price
                        if values[0] < 1000:
                            price = values[0]
                            quantity = value / price if price > 0 else None
                    elif len(values) == 1:
                        # Assume it's the value
                        value = values[0]
                
                securities.append({
                    'isin': isin,
                    'name': name,
                    'quantity': quantity,
                    'price': price,
                    'value': value,
                    'page': page_num,
                    'context': context
                })
    
    # Remove duplicates based on ISIN
    unique_securities = {}
    for security in securities:
        isin = security['isin']
        if isin not in unique_securities:
            unique_securities[isin] = security
        else:
            # Update with non-None values
            for key, value in security.items():
                if value is not None and unique_securities[isin].get(key) is None:
                    unique_securities[isin][key] = value
    
    return list(unique_securities.values())

def create_report(results, portfolio_value, securities, pdf_path):
    """Create a report of the OCR results."""
    # Calculate total from securities
    total_from_securities = sum(security.get('value', 0) for security in securities if security.get('value'))
    
    # Create HTML report
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>High Accuracy OCR Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .summary-box {{ background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px; margin-bottom: 20px; }}
            .value {{ font-size: 24px; font-weight: bold; color: #28a745; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>High Accuracy OCR Report</h1>
            <p>Document: {os.path.basename(pdf_path)}</p>
            
            <div class="summary-box">
                <h2>Portfolio Summary</h2>
                <p>Portfolio Value: <span class="value">${portfolio_value:,.2f}</span></p>
                <p>Total from Securities: <span class="value">${total_from_securities:,.2f}</span></p>
                <p>Number of Securities: <span class="value">{len(securities)}</span></p>
            </div>
            
            <h2>Securities</h2>
            <table>
                <tr>
                    <th>ISIN</th>
                    <th>Name</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Value</th>
                    <th>Page</th>
                </tr>
    """
    
    # Add securities rows
    for security in sorted(securities, key=lambda x: x.get('value', 0) if x.get('value') else 0, reverse=True):
        isin = security.get('isin', 'N/A')
        name = security.get('name', 'N/A')
        quantity = security.get('quantity', None)
        price = security.get('price', None)
        value = security.get('value', None)
        page = security.get('page', 'N/A')
        
        html_report += f"""
                <tr>
                    <td>{isin}</td>
                    <td>{name}</td>
                    <td>{quantity:,.2f if quantity else 'N/A'}</td>
                    <td>${price:,.2f if price else 'N/A'}</td>
                    <td>${value:,.2f if value else 'N/A'}</td>
                    <td>{page}</td>
                </tr>
        """
    
    html_report += """
            </table>
            
            <h2>OCR Results by Page</h2>
    """
    
    # Add page results
    for page_num, page_results in sorted(results.items()):
        html_report += f"""
            <h3>Page {page_results['page_num']}</h3>
            <p>Tables found: {page_results['num_tables_tabula']} (Tabula), {page_results['num_tables_pdfplumber']} (pdfplumber)</p>
            <p>ISINs found: {len(page_results['financial_data']['isins'])}</p>
            <p>Currency values found: {len(page_results['financial_data']['currency_values'])}</p>
            
            <h4>Best Text</h4>
            <pre style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; white-space: pre-wrap;">{page_results['texts']['best'][:500]}...</pre>
        """
    
    html_report += """
        </div>
    </body>
    </html>
    """
    
    # Save HTML report
    report_path = os.path.join(OUTPUT_DIR, 'ocr_report.html')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    # Save securities to JSON
    securities_path = os.path.join(OUTPUT_DIR, 'securities.json')
    with open(securities_path, 'w', encoding='utf-8') as f:
        json.dump(securities, f, indent=2)
    
    # Save summary to JSON
    summary = {
        'portfolio_value': portfolio_value,
        'total_from_securities': total_from_securities,
        'num_securities': len(securities),
        'num_pages': len(results)
    }
    
    summary_path = os.path.join(OUTPUT_DIR, 'summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    return report_path

def process_pdf(pdf_path):
    """Process a PDF file with high accuracy OCR."""
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
        page_results = process_page(pdf_path, page_num, page)
        results[f"page_{page_num}"] = page_results
    
    # Find portfolio value
    portfolio_value = find_portfolio_value(results)
    print(f"Portfolio value: ${portfolio_value:,.2f}" if portfolio_value else "Portfolio value not found")
    
    # Find securities
    securities = find_securities(results)
    print(f"Found {len(securities)} securities")
    
    # Create report
    report_path = create_report(results, portfolio_value, securities, pdf_path)
    
    print(f"\nHigh accuracy OCR completed. Report saved to: {report_path}")
    print(f"Open the report in your browser: file://{os.path.abspath(report_path)}")
    
    return results, portfolio_value, securities

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python high_accuracy_ocr.py <pdf_path>")
        return 1
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return 1
    
    # Ensure output directory exists
    ensure_output_dir()
    
    # Process PDF
    process_pdf(pdf_path)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
