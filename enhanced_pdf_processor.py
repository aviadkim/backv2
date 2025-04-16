"""
Enhanced PDF processor for financial documents.
"""
import os
import sys
import json
import re
import cv2
import numpy as np
import pytesseract
from pathlib import Path
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams, LTTextContainer, LTChar, LTLine, LTRect
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from io import StringIO
import tabula
import pandas as pd

def extract_text_with_layout(pdf_path):
    """Extract text with layout information from PDF."""
    print(f"Extracting text with layout from PDF: {pdf_path}")
    
    # Create an output buffer
    output_buffer = StringIO()
    
    # Extract text from the PDF with layout information
    with open(pdf_path, 'rb') as file:
        extract_text_to_fp(file, output_buffer, laparams=LAParams(
            line_margin=0.5,
            char_margin=2.0,
            word_margin=0.1,
            boxes_flow=0.5,
            detect_vertical=True
        ), output_type='text', codec='utf-8')
    
    # Get the extracted text
    text = output_buffer.getvalue()
    
    # Save the extracted text
    output_path = Path(pdf_path).with_suffix('.txt')
    with open(output_path, 'w', encoding='utf-8') as out_file:
        out_file.write(text)
    print(f"Saved extracted text to {output_path}")
    
    return text

def extract_tables_with_tabula(pdf_path):
    """Extract tables from PDF using tabula-py."""
    print(f"Extracting tables from PDF using tabula: {pdf_path}")
    
    try:
        # Extract all tables from the PDF
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
        
        print(f"Extracted {len(tables)} tables")
        
        # Convert tables to JSON
        tables_json = []
        for i, table in enumerate(tables):
            # Clean up the table
            table = table.dropna(how='all')
            table = table.fillna('')
            
            # Convert to dict
            table_dict = table.to_dict(orient='records')
            
            # Add table metadata
            tables_json.append({
                "table_id": i + 1,
                "page": i + 1,  # Approximate page number
                "data": table_dict
            })
        
        # Save the extracted tables
        output_dir = Path("./enhanced_results")
        output_dir.mkdir(exist_ok=True, parents=True)
        tables_path = output_dir / "extracted_tables_tabula.json"
        with open(tables_path, 'w', encoding='utf-8') as f:
            json.dump(tables_json, f, indent=2)
        print(f"Saved extracted tables to {tables_path}")
        
        return tables_json
    except Exception as e:
        print(f"Error extracting tables with tabula: {e}")
        return []

def extract_financial_data(text):
    """Extract financial data from text using regex patterns."""
    print("Extracting financial data from text...")
    
    # Create a dictionary to store the extracted data
    financial_data = {
        "client_info": {},
        "summary": {},
        "asset_allocation": [],
        "securities": []
    }
    
    # Extract client information
    client_pattern = r"(.*?)\s+Valuation\s+as\s+of\s+(\d{2}\.\d{2}\.\d{4})\s+Client\s+Number\s+(\d+)"
    client_match = re.search(client_pattern, text)
    if client_match:
        financial_data["client_info"] = {
            "name": client_match.group(1).strip(),
            "valuation_date": client_match.group(2),
            "client_number": client_match.group(3)
        }
    
    # Extract summary information
    summary_pattern = r"Summary\s+Countervalue USD\s+Weight in %\s+(.*?)Countervalue USD"
    summary_match = re.search(summary_pattern, text, re.DOTALL)
    if summary_match:
        summary_text = summary_match.group(1)
        
        # Extract total value
        total_pattern = r"Total\s+([\d',]+)\s+100\.00%"
        total_match = re.search(total_pattern, summary_text)
        if total_match:
            total_value = total_match.group(1).replace("'", "").replace(",", "")
            financial_data["summary"]["total_value"] = float(total_value)
    
    # Extract securities
    securities_pattern = r"([A-Z]+)\s+([\d',]+)\s+(.*?)\s+ISIN:\s+([A-Z0-9]+).*?(\d+\.\d+)%"
    securities_matches = re.finditer(securities_pattern, text)
    
    for match in securities_matches:
        currency = match.group(1)
        nominal = match.group(2).replace("'", "").replace(",", "")
        description = match.group(3).strip()
        isin = match.group(4)
        weight = match.group(5)
        
        # Look for price and value in the surrounding text
        surrounding_text = text[match.start():match.start() + 500]
        
        # Extract price
        price_pattern = r"(\d+\.\d+)"
        price_matches = re.finditer(price_pattern, surrounding_text)
        prices = [float(m.group(1)) for m in price_matches]
        price = prices[1] if len(prices) > 1 else 0
        
        # Extract value
        value_pattern = r"([\d',]+)\s+(\d+\.\d+)%"
        value_match = re.search(value_pattern, surrounding_text)
        value = value_match.group(1).replace("'", "").replace(",", "") if value_match else "0"
        
        security = {
            "currency": currency,
            "nominal": nominal,
            "description": description,
            "isin": isin,
            "price": price,
            "value": float(value) if value.isdigit() else 0,
            "weight": float(weight)
        }
        
        financial_data["securities"].append(security)
    
    # Save the extracted financial data
    output_dir = Path("./enhanced_results")
    output_dir.mkdir(exist_ok=True, parents=True)
    data_path = output_dir / "extracted_financial_data.json"
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(financial_data, f, indent=2)
    print(f"Saved extracted financial data to {data_path}")
    
    return financial_data

def extract_isins(text):
    """Extract ISINs from text."""
    print("Extracting ISINs from text...")
    
    # ISIN pattern: 2 letters followed by 10 digits/letters
    isin_pattern = r"\b([A-Z]{2}[A-Z0-9]{10})\b"
    isins = re.findall(isin_pattern, text)
    
    # Remove duplicates
    isins = list(set(isins))
    
    print(f"Extracted {len(isins)} unique ISINs")
    
    # Save the extracted ISINs
    output_dir = Path("./enhanced_results")
    output_dir.mkdir(exist_ok=True, parents=True)
    isins_path = output_dir / "extracted_isins.json"
    with open(isins_path, 'w', encoding='utf-8') as f:
        json.dump(isins, f, indent=2)
    print(f"Saved extracted ISINs to {isins_path}")
    
    return isins

def process_pdf(pdf_path, api_key=None):
    """Process a financial PDF document."""
    print(f"Processing PDF: {pdf_path}")
    
    # Create output directory
    output_dir = Path("./enhanced_results")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Extract text with layout
    text = extract_text_with_layout(pdf_path)
    
    # Extract tables with tabula
    tables = extract_tables_with_tabula(pdf_path)
    
    # Extract financial data
    financial_data = extract_financial_data(text)
    
    # Extract ISINs
    isins = extract_isins(text)
    
    # Create a comprehensive financial document
    document = {
        "metadata": {
            "document_type": "portfolio_statement",
            "document_date": financial_data["client_info"].get("valuation_date", ""),
            "client_name": financial_data["client_info"].get("name", ""),
            "client_number": financial_data["client_info"].get("client_number", ""),
            "valuation_currency": "USD"
        },
        "tables": tables,
        "financial_data": {
            "portfolio": {
                "securities": [],
                "summary": {
                    "total_value": financial_data["summary"].get("total_value", 0),
                    "total_securities": len(financial_data["securities"])
                }
            },
            "isins": isins
        }
    }
    
    # Add securities
    for security in financial_data["securities"]:
        document["financial_data"]["portfolio"]["securities"].append({
            "type": "security",
            "isin": security["isin"],
            "description": security["description"],
            "currency": security["currency"],
            "nominal": security["nominal"],
            "price": security["price"],
            "value": security["value"],
            "weight": security["weight"]
        })
    
    # Save the comprehensive document
    document_path = output_dir / "comprehensive_document.json"
    with open(document_path, 'w', encoding='utf-8') as f:
        json.dump(document, f, indent=2)
    print(f"Saved comprehensive document to {document_path}")
    
    # If API key is provided, use it to process the document with AI agents
    if api_key:
        try:
            # Add the parent directory to the path so we can import the backend modules
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Import the agents
            from DevDocs.backend.agents.document_merge_agent import DocumentMergeAgent
            from DevDocs.backend.agents.financial_data_analyzer_agent import FinancialDataAnalyzerAgent
            
            print("\nProcessing with AI agents...")
            
            # Create the agents
            merge_agent = DocumentMergeAgent()
            analyzer_agent = FinancialDataAnalyzerAgent(api_key=api_key)
            
            # Merge the document
            merged_document = merge_agent.merge_documents([document])
            
            # Save the merged document
            merged_path = output_dir / "merged_document.json"
            with open(merged_path, 'w', encoding='utf-8') as f:
                json.dump(merged_document, f, indent=2)
            print(f"Saved merged document to {merged_path}")
            
            # Analyze the document
            analysis = analyzer_agent.process({
                "document": merged_document,
                "analysis_type": "comprehensive"
            })
            
            # Save the analysis
            analysis_path = output_dir / "financial_analysis.json"
            with open(analysis_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2)
            print(f"Saved financial analysis to {analysis_path}")
            
            return {
                "document": document,
                "merged_document": merged_document,
                "analysis": analysis
            }
        except Exception as e:
            print(f"Error processing with AI agents: {e}")
    
    return {
        "document": document
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process a financial PDF document")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--api-key", help="OpenRouter API key")
    args = parser.parse_args()
    
    process_pdf(args.pdf_path, args.api_key)
