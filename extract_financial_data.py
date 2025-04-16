"""
Extract financial data from PDF without relying on external APIs.
"""
import os
import re
import json
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_text_with_pdfplumber(pdf_path: str) -> str:
    """Extract text from PDF using pdfplumber."""
    try:
        import pdfplumber
        logger.info(f"Extracting text from {pdf_path} using pdfplumber")
        
        with pdfplumber.open(pdf_path) as pdf:
            logger.info(f"PDF has {len(pdf.pages)} pages")
            
            full_text = ""
            for i, page in enumerate(pdf.pages):
                logger.info(f"Processing page {i+1}/{len(pdf.pages)}")
                text = page.extract_text() or ""
                full_text += f"\n\n--- Page {i+1} ---\n\n{text}"
            
            return full_text
    except Exception as e:
        logger.error(f"Error extracting text with pdfplumber: {e}")
        return ""

def extract_tables_with_pdfplumber(pdf_path: str) -> List[Dict[str, Any]]:
    """Extract tables from PDF using pdfplumber."""
    try:
        import pdfplumber
        logger.info(f"Extracting tables from {pdf_path} using pdfplumber")
        
        tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_tables = page.extract_tables()
                for j, table_data in enumerate(page_tables):
                    tables.append({
                        "page": i + 1,
                        "table_number": j + 1,
                        "data": table_data
                    })
            
            logger.info(f"Extracted {len(tables)} tables")
            return tables
    except Exception as e:
        logger.error(f"Error extracting tables with pdfplumber: {e}")
        return []

def extract_tables_with_camelot(pdf_path: str) -> List[Dict[str, Any]]:
    """Extract tables from PDF using camelot."""
    try:
        import camelot
        logger.info(f"Extracting tables from {pdf_path} using camelot")
        
        tables = []
        
        # Try lattice mode first (for tables with borders)
        lattice_tables = camelot.read_pdf(pdf_path, pages="all", flavor="lattice")
        
        # Then try stream mode (for tables without borders)
        stream_tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")
        
        # Process lattice tables
        for i, table in enumerate(lattice_tables):
            tables.append({
                "page": table.page,
                "extraction_method": "camelot_lattice",
                "table_number": i + 1,
                "data": table.data,
                "headers": table.data[0] if len(table.data) > 0 else [],
                "rows": table.data[1:] if len(table.data) > 1 else [],
                "accuracy": table.accuracy
            })
        
        # Process stream tables
        for i, table in enumerate(stream_tables):
            tables.append({
                "page": table.page,
                "extraction_method": "camelot_stream",
                "table_number": i + 1,
                "data": table.data,
                "headers": table.data[0] if len(table.data) > 0 else [],
                "rows": table.data[1:] if len(table.data) > 1 else [],
                "accuracy": table.accuracy
            })
        
        logger.info(f"Extracted {len(tables)} tables")
        return tables
    except Exception as e:
        logger.error(f"Error extracting tables with camelot: {e}")
        return []

def extract_portfolio_value(text: str) -> Optional[float]:
    """Extract portfolio value from text using regex patterns."""
    logger.info("Extracting portfolio value from text")
    
    # Define patterns to match portfolio value
    patterns = [
        r'Portfolio\s+Total\s+(\d[\d,.\']*)',
        r'Total\s+assets\s+(\d[\d,.\']*)',
        r'Portfolio\s+Total\s*[:\s]+(\d[\d,.\']*)',
        r'Total\s+assets\s*[:\s]+(\d[\d,.\']*)',
        r'Portfolio\s+Value\s*[:\s]+(\d[\d,.\']*)',
        r'Total\s+Value\s*[:\s]+(\d[\d,.\']*)',
        r'Total\s+Portfolio\s+Value\s*[:\s]+(\d[\d,.\']*)'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            value_str = match.group(1).strip()
            value_str = value_str.replace("'", "").replace(",", "")
            try:
                value = float(value_str)
                logger.info(f"Found portfolio value: {value}")
                return value
            except ValueError:
                continue
    
    # If no match found with patterns, look for specific lines
    lines = text.split('\n')
    for line in lines:
        if "Portfolio Total" in line:
            # Try to extract a number from this line
            number_match = re.search(r'(\d[\d,.\']*)', line)
            if number_match:
                value_str = number_match.group(1).strip()
                value_str = value_str.replace("'", "").replace(",", "")
                try:
                    value = float(value_str)
                    logger.info(f"Found portfolio value: {value}")
                    return value
                except ValueError:
                    continue
    
    logger.warning("No portfolio value found")
    return None

def extract_asset_allocation(text: str) -> List[Dict[str, Any]]:
    """Extract asset allocation from text."""
    logger.info("Extracting asset allocation from text")
    
    asset_allocations = []
    
    # Look for the Asset Allocation section
    asset_allocation_start = text.find("Asset Allocation")
    if asset_allocation_start == -1:
        logger.warning("No Asset Allocation section found")
        return asset_allocations
    
    # Find the end of the Asset Allocation section
    asset_allocation_end = text.find("Total assets", asset_allocation_start)
    if asset_allocation_end == -1:
        asset_allocation_end = len(text)
    
    asset_allocation_text = text[asset_allocation_start:asset_allocation_end]
    
    # Extract asset classes and their values
    asset_class_pattern = r'([A-Za-z\s]+)\s+(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)\s+(\d{1,3}(?:\.\d{1,2})?)%'
    asset_class_matches = re.finditer(asset_class_pattern, asset_allocation_text)
    
    for match in asset_class_matches:
        asset_class = match.group(1).strip()
        value_str = match.group(2).strip()
        percentage_str = match.group(3).strip()
        
        try:
            value = float(value_str.replace(',', '').replace("'", ''))
            percentage = float(percentage_str)
            
            asset_allocations.append({
                "asset_class": asset_class,
                "value": value,
                "percentage": percentage
            })
            
            logger.info(f"Found asset allocation: {asset_class} - {value} ({percentage}%)")
        except ValueError:
            continue
    
    # If no asset allocations found with the pattern, try to extract from tables
    if not asset_allocations:
        logger.info("Trying to extract asset allocation from tables")
        
        # Look for lines with asset class and percentage
        lines = asset_allocation_text.split('\n')
        for line in lines:
            # Skip short lines
            if len(line.strip()) < 10:
                continue
            
            # Look for lines with asset class and percentage
            asset_class_match = re.search(r'([A-Za-z\s]+)\s+(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)\s+(\d{1,3}(?:\.\d{1,2})?)%', line)
            if asset_class_match:
                asset_class = asset_class_match.group(1).strip()
                value_str = asset_class_match.group(2).strip()
                percentage_str = asset_class_match.group(3).strip()
                
                try:
                    value = float(value_str.replace(',', '').replace("'", ''))
                    percentage = float(percentage_str)
                    
                    asset_allocations.append({
                        "asset_class": asset_class,
                        "value": value,
                        "percentage": percentage
                    })
                    
                    logger.info(f"Found asset allocation: {asset_class} - {value} ({percentage}%)")
                except ValueError:
                    continue
    
    return asset_allocations

def extract_securities(text: str) -> List[Dict[str, Any]]:
    """Extract securities from text."""
    logger.info("Extracting securities from text")
    
    securities = []
    
    # Look for ISIN patterns
    isin_pattern = r'ISIN:\s*([A-Z]{2}[A-Z0-9]{9}[0-9])'
    isin_matches = re.finditer(isin_pattern, text)
    
    for match in isin_matches:
        isin = match.group(1)
        
        # Get context around the ISIN (500 characters before and after)
        context_start = max(0, match.start() - 500)
        context_end = min(len(text), match.end() + 500)
        context = text[context_start:context_end]
        
        # Try to extract description
        desc_pattern = r'([A-Z][A-Z0-9\s\.\-\(\)]{5,50})'
        desc_match = re.search(desc_pattern, context[:match.start() - context_start])
        description = desc_match.group(1).strip() if desc_match else "Unknown"
        
        # Try to extract valuation
        valuation_pattern = r'(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)'
        valuation_matches = list(re.finditer(valuation_pattern, context[match.end() - context_start:]))
        
        valuation = None
        if valuation_matches:
            # Look for large values that might be valuations
            for val_match in valuation_matches:
                val_str = val_match.group(1)
                try:
                    val = float(val_str.replace(',', '').replace("'", ''))
                    if val > 10000:  # Likely a valuation
                        valuation = val
                        break
                except ValueError:
                    continue
        
        # Try to determine security type
        security_type = "Unknown"
        if "Bond" in context or "bond" in context:
            security_type = "Bond"
        elif "Equity" in context or "equity" in context or "Stock" in context or "stock" in context:
            security_type = "Equity"
        elif "Structured" in context or "structured" in context:
            security_type = "Structured Product"
        elif "Fund" in context or "fund" in context:
            security_type = "Fund"
        
        # Create security object
        security = {
            "isin": isin,
            "description": description,
            "security_type": security_type,
            "valuation": valuation
        }
        
        # Check if this security is already in the list
        if not any(s["isin"] == isin for s in securities):
            securities.append(security)
            logger.info(f"Found security: {isin} - {description} - {valuation}")
    
    return securities

def extract_risk_profile(text: str) -> Optional[str]:
    """Extract risk profile from text."""
    logger.info("Extracting risk profile from text")
    
    # Define patterns to match risk profile
    patterns = [
        r'Risk\s+Profile\s*[:\s]+([A-Za-z\-]+)',
        r'Risk\s+profile\s*[:\s]+([A-Za-z\-]+)',
        r'Risk\s+Profile\s*//([A-Za-z\-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            risk_profile = match.group(1).strip()
            logger.info(f"Found risk profile: {risk_profile}")
            return risk_profile
    
    logger.warning("No risk profile found")
    return None

def extract_currency(text: str) -> Optional[str]:
    """Extract currency from text."""
    logger.info("Extracting currency from text")
    
    # Define patterns to match currency
    patterns = [
        r'Valuation\s+currency\s*[:\s]+([A-Z]{3})',
        r'Valuation\s+currency\s*//([A-Z]{3})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            currency = match.group(1).strip()
            logger.info(f"Found currency: {currency}")
            return currency
    
    logger.warning("No currency found")
    return None

def process_document(pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """Process a document and extract financial data."""
    logger.info(f"Processing document: {pdf_path}")
    
    # Create output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Extract text
    text = extract_text_with_pdfplumber(pdf_path)
    
    # Extract tables
    pdfplumber_tables = extract_tables_with_pdfplumber(pdf_path)
    camelot_tables = extract_tables_with_camelot(pdf_path)
    
    # Extract financial data
    portfolio_value = extract_portfolio_value(text)
    asset_allocation = extract_asset_allocation(text)
    securities = extract_securities(text)
    risk_profile = extract_risk_profile(text)
    currency = extract_currency(text)
    
    # Calculate total securities value
    total_securities_value = sum(s["valuation"] for s in securities if s["valuation"] is not None)
    
    # Calculate coverage
    coverage = (total_securities_value / portfolio_value) * 100 if portfolio_value and portfolio_value > 0 else 0
    
    # Create result
    result = {
        "document_info": {
            "filename": os.path.basename(pdf_path),
            "risk_profile": risk_profile,
            "currency": currency
        },
        "portfolio_value": portfolio_value,
        "asset_allocation": asset_allocation,
        "securities": {
            "count": len(securities),
            "total_value": total_securities_value,
            "coverage": coverage,
            "items": securities
        },
        "extraction_stats": {
            "text_length": len(text),
            "pdfplumber_tables": len(pdfplumber_tables),
            "camelot_tables": len(camelot_tables)
        }
    }
    
    # Save results if output directory is specified
    if output_dir:
        # Save text
        with open(os.path.join(output_dir, "text.txt"), "w", encoding="utf-8") as f:
            f.write(text)
        
        # Save result
        with open(os.path.join(output_dir, "result.json"), "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
    
    logger.info(f"Document processing completed: {pdf_path}")
    return result

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract financial data from PDF")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output-dir", help="Directory to save extracted data")
    
    args = parser.parse_args()
    
    # Process document
    result = process_document(args.pdf_path, args.output_dir)
    
    # Print summary
    print("\n" + "=" * 80)
    print("FINANCIAL DATA EXTRACTION SUMMARY")
    print("=" * 80)
    
    print(f"\nDocument: {result['document_info']['filename']}")
    print(f"Risk Profile: {result['document_info']['risk_profile']}")
    print(f"Currency: {result['document_info']['currency']}")
    
    print(f"\nPortfolio Value: ${result['portfolio_value']:,.2f}" if result['portfolio_value'] else "\nPortfolio Value: Not found")
    
    print(f"\nAsset Allocation:")
    for allocation in result['asset_allocation']:
        print(f"- {allocation['asset_class']}: ${allocation['value']:,.2f} ({allocation['percentage']}%)")
    
    print(f"\nSecurities: {result['securities']['count']}")
    print(f"Total Securities Value: ${result['securities']['total_value']:,.2f}")
    print(f"Coverage: {result['securities']['coverage']:.2f}%")
    
    print("\nTop 5 Securities:")
    # Sort securities by valuation (descending)
    top_securities = sorted(
        [s for s in result['securities']['items'] if s['valuation'] is not None],
        key=lambda s: s['valuation'],
        reverse=True
    )[:5]
    
    for i, security in enumerate(top_securities):
        print(f"{i+1}. {security['description']} ({security['isin']}): ${security['valuation']:,.2f}")
    
    print("\nExtraction Statistics:")
    print(f"- Text Length: {result['extraction_stats']['text_length']} characters")
    print(f"- PDFPlumber Tables: {result['extraction_stats']['pdfplumber_tables']}")
    print(f"- Camelot Tables: {result['extraction_stats']['camelot_tables']}")
    
    print("\nResults saved to:", args.output_dir if args.output_dir else "Not saved")

if __name__ == "__main__":
    main()
