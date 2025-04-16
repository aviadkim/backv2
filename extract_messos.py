"""
Extract and validate data from messos.pdf using improved extraction techniques.
"""
import os
import sys
import logging
import json
import re
from typing import Dict, List, Any, Optional
from collections import defaultdict

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
            
            logger.info(f"Extracted {len(tables)} tables with pdfplumber")
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
        
        logger.info(f"Extracted {len(tables)} tables with camelot")
        return tables
    except Exception as e:
        logger.error(f"Error extracting tables with camelot: {e}")
        return []

def extract_securities(text: str, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract securities from text and tables."""
    logger.info("Extracting securities")
    
    securities = []
    
    # Extract securities from text
    isin_pattern = r'ISIN:?\s*([A-Z]{2}[A-Z0-9]{9}[0-9])'
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
        security_obj = {
            "isin": isin,
            "description": description,
            "security_type": security_type,
            "valuation": valuation,
            "source": "text"
        }
        
        # Check if this security is already in the list
        if not any(s["isin"] == isin for s in securities):
            securities.append(security_obj)
    
    # Extract securities from tables
    for table in tables:
        # Skip tables without data
        if not table.get("data"):
            continue
        
        # Check if table contains securities
        for row in table.get("data", []):
            # Skip empty rows
            if not row or all(not cell for cell in row):
                continue
            
            # Look for ISIN in the row
            isin = None
            for cell in row:
                if not cell:
                    continue
                
                # Check if cell contains ISIN
                isin_match = re.search(r'([A-Z]{2}[A-Z0-9]{9}[0-9])', str(cell))
                if isin_match:
                    isin = isin_match.group(1)
                    break
            
            if not isin:
                continue
            
            # Extract other information from the row
            description = "Unknown"
            security_type = "Unknown"
            valuation = None
            
            for cell in row:
                if not cell:
                    continue
                
                # Try to extract description
                if len(str(cell)) > 10 and not description or description == "Unknown":
                    description = str(cell)
                
                # Try to extract security type
                cell_lower = str(cell).lower()
                if "bond" in cell_lower and security_type == "Unknown":
                    security_type = "Bond"
                elif "equity" in cell_lower or "stock" in cell_lower and security_type == "Unknown":
                    security_type = "Equity"
                elif "structured" in cell_lower and security_type == "Unknown":
                    security_type = "Structured Product"
                elif "fund" in cell_lower and security_type == "Unknown":
                    security_type = "Fund"
                
                # Try to extract valuation
                if not valuation:
                    val_match = re.search(r'(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)', str(cell))
                    if val_match:
                        val_str = val_match.group(1)
                        try:
                            val = float(val_str.replace(',', '').replace("'", ''))
                            if val > 10000:  # Likely a valuation
                                valuation = val
                        except ValueError:
                            continue
            
            # Create security object
            security_obj = {
                "isin": isin,
                "description": description,
                "security_type": security_type,
                "valuation": valuation,
                "source": "table",
                "extraction_method": table.get("extraction_method"),
                "table_number": table.get("table_number"),
                "page": table.get("page")
            }
            
            # Check if this security is already in the list
            existing_security = next((s for s in securities if s["isin"] == isin), None)
            if existing_security:
                # Update existing security with table information if it's more complete
                if existing_security["description"] == "Unknown" and description != "Unknown":
                    existing_security["description"] = description
                
                if existing_security["security_type"] == "Unknown" and security_type != "Unknown":
                    existing_security["security_type"] = security_type
                
                if existing_security["valuation"] is None and valuation is not None:
                    existing_security["valuation"] = valuation
                    existing_security["source"] = f"{existing_security['source']}, table"
            else:
                securities.append(security_obj)
    
    logger.info(f"Found {len(securities)} securities")
    return securities

def extract_portfolio_value(text: str, tables: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract portfolio value from text and tables."""
    logger.info("Extracting portfolio value")
    
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
    
    # Search for portfolio value in text
    text_values = []
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            value_str = match.group(1).strip()
            value_str = value_str.replace("'", "").replace(",", "")
            try:
                value = float(value_str)
                text_values.append({
                    "value": value,
                    "source": "text",
                    "pattern": pattern,
                    "match": match.group(0)
                })
            except ValueError:
                continue
    
    # Search for portfolio value in tables
    table_values = []
    for table in tables:
        # Skip tables without data
        if not table.get("data"):
            continue
        
        # Check if table contains portfolio value
        for row in table.get("data", []):
            for i, cell in enumerate(row):
                if not cell:
                    continue
                
                # Check if cell contains portfolio value keywords
                if any(keyword in str(cell).lower() for keyword in ["portfolio total", "total assets", "portfolio value", "total value"]):
                    # Look for value in the same row
                    for j, value_cell in enumerate(row):
                        if j == i:
                            continue
                        
                        if not value_cell:
                            continue
                        
                        # Try to extract value
                        value_str = str(value_cell).strip()
                        value_str = re.sub(r'[^\d.]', '', value_str)
                        
                        try:
                            value = float(value_str)
                            if value > 1000:  # Minimum threshold for portfolio value
                                table_values.append({
                                    "value": value,
                                    "source": "table",
                                    "extraction_method": table.get("extraction_method"),
                                    "table_number": table.get("table_number"),
                                    "page": table.get("page")
                                })
                        except ValueError:
                            continue
    
    # Combine values from text and tables
    all_values = text_values + table_values
    
    if not all_values:
        logger.warning("No portfolio value found")
        return {"value": None, "confidence": 0, "sources": []}
    
    # Group values by value
    value_groups = defaultdict(list)
    for value_info in all_values:
        value_groups[value_info["value"]].append(value_info)
    
    # Find the most common value
    most_common_value = max(value_groups.items(), key=lambda x: len(x[1]))
    value = most_common_value[0]
    sources = most_common_value[1]
    confidence = len(sources) / len(all_values)
    
    logger.info(f"Found portfolio value: {value} (confidence: {confidence:.2f})")
    
    return {
        "value": value,
        "confidence": confidence,
        "sources": sources
    }

def extract_asset_allocation(text: str, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract asset allocation from text and tables."""
    logger.info("Extracting asset allocation")
    
    asset_allocations = []
    
    # Look for the Asset Allocation section
    asset_allocation_start = text.find("Asset Allocation")
    if asset_allocation_start == -1:
        logger.warning("No Asset Allocation section found in text")
    else:
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
                    "percentage": percentage,
                    "source": "text"
                })
                
                logger.info(f"Found asset allocation in text: {asset_class} - {value} ({percentage}%)")
            except ValueError:
                continue
    
    # Extract asset allocation from tables
    for table in tables:
        # Skip tables without data
        if not table.get("data"):
            continue
        
        # Check if table contains asset allocation
        is_asset_allocation_table = False
        for row in table.get("data", []):
            # Skip empty rows
            if not row or all(not cell for cell in row):
                continue
            
            # Check if row contains asset allocation keywords
            row_str = " ".join(str(cell) for cell in row if cell)
            if "asset allocation" in row_str.lower() or "asset class" in row_str.lower():
                is_asset_allocation_table = True
                break
        
        if not is_asset_allocation_table:
            continue
        
        # Extract asset allocation from table
        for row in table.get("data", []):
            # Skip empty rows
            if not row or all(not cell for cell in row):
                continue
            
            # Skip header rows
            row_str = " ".join(str(cell) for cell in row if cell)
            if "asset allocation" in row_str.lower() or "asset class" in row_str.lower():
                continue
            
            # Extract asset class, value, and percentage
            asset_class = None
            value = None
            percentage = None
            
            for i, cell in enumerate(row):
                if not cell:
                    continue
                
                cell_str = str(cell).strip()
                
                # Try to extract asset class
                if i == 0 and not asset_class:
                    asset_class = cell_str
                
                # Try to extract value
                if not value:
                    val_match = re.search(r'(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)', cell_str)
                    if val_match:
                        val_str = val_match.group(1)
                        try:
                            val = float(val_str.replace(',', '').replace("'", ''))
                            if val > 1000:  # Minimum threshold for asset value
                                value = val
                        except ValueError:
                            continue
                
                # Try to extract percentage
                if not percentage:
                    pct_match = re.search(r'(\d{1,3}(?:\.\d{1,2})?)%', cell_str)
                    if pct_match:
                        pct_str = pct_match.group(1)
                        try:
                            percentage = float(pct_str)
                        except ValueError:
                            continue
            
            if asset_class and (value or percentage):
                # Create asset allocation object
                asset_allocation = {
                    "asset_class": asset_class,
                    "value": value,
                    "percentage": percentage,
                    "source": "table",
                    "extraction_method": table.get("extraction_method"),
                    "table_number": table.get("table_number"),
                    "page": table.get("page")
                }
                
                # Check if this asset class is already in the list
                existing_allocation = next((a for a in asset_allocations if a["asset_class"] == asset_class), None)
                if existing_allocation:
                    # Update existing allocation with table information if it's more complete
                    if existing_allocation["value"] is None and value is not None:
                        existing_allocation["value"] = value
                    
                    if existing_allocation["percentage"] is None and percentage is not None:
                        existing_allocation["percentage"] = percentage
                    
                    existing_allocation["source"] = f"{existing_allocation['source']}, table"
                else:
                    asset_allocations.append(asset_allocation)
                    logger.info(f"Found asset allocation in table: {asset_class} - {value} ({percentage}%)")
    
    # Validate asset allocations
    if asset_allocations:
        # Check if percentages sum to approximately 100%
        total_percentage = sum(a["percentage"] for a in asset_allocations if a["percentage"] is not None)
        if abs(total_percentage - 100) > 5:
            logger.warning(f"Asset allocation percentages sum to {total_percentage}%, which is not close to 100%")
        
        # Check if values sum to approximately the portfolio value
        total_value = sum(a["value"] for a in asset_allocations if a["value"] is not None)
        logger.info(f"Asset allocation total value: {total_value}")
    
    return asset_allocations

def validate_extraction(portfolio_value: Dict[str, Any], securities: List[Dict[str, Any]], asset_allocations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate extraction results."""
    logger.info("Validating extraction results")
    
    validation_results = {
        "portfolio_value": {
            "valid": True,
            "issues": []
        },
        "securities": {
            "valid": True,
            "issues": []
        },
        "asset_allocation": {
            "valid": True,
            "issues": []
        },
        "overall": {
            "valid": True,
            "issues": []
        }
    }
    
    # Validate portfolio value
    if not portfolio_value or portfolio_value.get("value") is None:
        validation_results["portfolio_value"]["valid"] = False
        validation_results["portfolio_value"]["issues"].append("Portfolio value not found")
    elif portfolio_value["value"] <= 0:
        validation_results["portfolio_value"]["valid"] = False
        validation_results["portfolio_value"]["issues"].append(f"Portfolio value is not positive: {portfolio_value['value']}")
    
    # Validate securities
    if not securities:
        validation_results["securities"]["valid"] = False
        validation_results["securities"]["issues"].append("No securities found")
    else:
        # Check for duplicate ISINs
        isin_counts = defaultdict(int)
        for security in securities:
            isin = security.get("isin")
            if isin:
                isin_counts[isin] += 1
        
        duplicates = [isin for isin, count in isin_counts.items() if count > 1]
        if duplicates:
            validation_results["securities"]["valid"] = False
            validation_results["securities"]["issues"].append(f"Duplicate ISINs found: {duplicates}")
        
        # Check if securities have required fields
        for i, security in enumerate(securities):
            if not security.get("isin"):
                validation_results["securities"]["valid"] = False
                validation_results["securities"]["issues"].append(f"Security at index {i} has no ISIN")
            
            if not security.get("description") or security.get("description") == "Unknown":
                validation_results["securities"]["issues"].append(f"Security {security.get('isin', f'at index {i}')} has no description")
            
            if not security.get("security_type") or security.get("security_type") == "Unknown":
                validation_results["securities"]["issues"].append(f"Security {security.get('isin', f'at index {i}')} has no security type")
            
            if security.get("valuation") is None:
                validation_results["securities"]["issues"].append(f"Security {security.get('isin', f'at index {i}')} has no valuation")
    
    # Validate asset allocation
    if not asset_allocations:
        validation_results["asset_allocation"]["valid"] = False
        validation_results["asset_allocation"]["issues"].append("Asset allocation not found")
    else:
        # Check if percentages sum to approximately 100%
        total_percentage = sum(a.get("percentage", 0) or 0 for a in asset_allocations)
        if abs(total_percentage - 100) > 5:
            validation_results["asset_allocation"]["valid"] = False
            validation_results["asset_allocation"]["issues"].append(f"Asset allocation percentages sum to {total_percentage:.2f}%, which is not close to 100%")
    
    # Cross-validate portfolio value, securities, and asset allocation
    if portfolio_value and portfolio_value.get("value") and securities:
        # Calculate total securities value
        total_securities_value = sum(s.get("valuation", 0) or 0 for s in securities)
        
        # Calculate relative difference
        if total_securities_value > 0 and portfolio_value["value"] > 0:
            relative_diff = abs(total_securities_value - portfolio_value["value"]) / portfolio_value["value"]
            tolerance = 0.05  # 5% tolerance
            
            if relative_diff > tolerance:
                validation_results["overall"]["valid"] = False
                validation_results["overall"]["issues"].append(f"Sum of securities ({total_securities_value:.2f}) does not match portfolio value ({portfolio_value['value']:.2f}), difference: {relative_diff:.2%}")
    
    if portfolio_value and portfolio_value.get("value") and asset_allocations:
        # Calculate total asset allocation value
        total_asset_allocation_value = sum(a.get("value", 0) or 0 for a in asset_allocations)
        
        # Calculate relative difference
        if total_asset_allocation_value > 0 and portfolio_value["value"] > 0:
            relative_diff = abs(total_asset_allocation_value - portfolio_value["value"]) / portfolio_value["value"]
            tolerance = 0.05  # 5% tolerance
            
            if relative_diff > tolerance:
                validation_results["overall"]["valid"] = False
                validation_results["overall"]["issues"].append(f"Sum of asset allocations ({total_asset_allocation_value:.2f}) does not match portfolio value ({portfolio_value['value']:.2f}), difference: {relative_diff:.2%}")
    
    # Check if any validation failed
    for key, result in validation_results.items():
        if key == "overall":
            continue
        
        if not result["valid"]:
            validation_results["overall"]["valid"] = False
            validation_results["overall"]["issues"].extend(result["issues"])
    
    logger.info(f"Validation completed: {'valid' if validation_results['overall']['valid'] else 'invalid'}")
    return validation_results

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract and validate data from messos.pdf")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output-dir", help="Directory to save extracted data")
    
    args = parser.parse_args()
    
    # Create output directory if specified
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
    
    # Extract text
    text = extract_text_with_pdfplumber(args.pdf_path)
    
    # Extract tables
    pdfplumber_tables = extract_tables_with_pdfplumber(args.pdf_path)
    camelot_tables = extract_tables_with_camelot(args.pdf_path)
    
    # Combine tables
    tables = pdfplumber_tables + camelot_tables
    
    # Extract portfolio value
    portfolio_value = extract_portfolio_value(text, tables)
    
    # Extract securities
    securities = extract_securities(text, tables)
    
    # Extract asset allocation
    asset_allocations = extract_asset_allocation(text, tables)
    
    # Validate extraction
    validation_results = validate_extraction(portfolio_value, securities, asset_allocations)
    
    # Create result
    result = {
        "portfolio_value": portfolio_value,
        "securities": securities,
        "asset_allocation": asset_allocations,
        "validation": validation_results
    }
    
    # Save results if output directory is specified
    if args.output_dir:
        # Save text
        with open(os.path.join(args.output_dir, "text.txt"), "w", encoding="utf-8") as f:
            f.write(text)
        
        # Save result
        with open(os.path.join(args.output_dir, "result.json"), "w", encoding="utf-8") as f:
            # Convert result to JSON-serializable format
            json_result = json.dumps(result, indent=2, default=str)
            f.write(json_result)
    
    # Print summary
    print("\n" + "=" * 80)
    print("FINANCIAL DATA EXTRACTION SUMMARY")
    print("=" * 80)
    
    print(f"\nPortfolio Value: ${portfolio_value['value']:,.2f}" if portfolio_value['value'] else "\nPortfolio Value: Not found")
    print(f"Confidence: {portfolio_value['confidence']:.2f}")
    
    print(f"\nSecurities: {len(securities)}")
    total_securities_value = sum(s.get("valuation", 0) or 0 for s in securities)
    print(f"Total Securities Value: ${total_securities_value:,.2f}")
    
    if portfolio_value['value']:
        coverage = (total_securities_value / portfolio_value['value']) * 100
        print(f"Coverage: {coverage:.2f}%")
    
    print("\nAsset Allocation:")
    for allocation in asset_allocations:
        print(f"- {allocation['asset_class']}: ${allocation['value']:,.2f} ({allocation['percentage']}%)")
    
    print("\nTop 10 Securities:")
    # Sort securities by valuation (descending)
    top_securities = sorted(
        [s for s in securities if s.get('valuation') is not None],
        key=lambda s: s.get('valuation', 0),
        reverse=True
    )[:10]
    
    for i, security in enumerate(top_securities):
        print(f"{i+1}. {security.get('description', 'Unknown')} ({security.get('isin', 'Unknown')}): ${security.get('valuation', 0):,.2f}")
    
    print("\nValidation Results:")
    print(f"Overall Valid: {validation_results['overall']['valid']}")
    if validation_results['overall']['issues']:
        print("Issues:")
        for issue in validation_results['overall']['issues']:
            print(f"- {issue}")
    
    print("\nResults saved to:", args.output_dir if args.output_dir else "Not saved")

if __name__ == "__main__":
    main()
