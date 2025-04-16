"""
Script to extract asset allocation from messos.pdf.
"""
import os
import re
import json
import pdfplumber

def extract_text_from_pdf(pdf_path):
    """Extract text directly from PDF using pdfplumber."""
    full_text = ""
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"Processing page {i+1}/{len(pdf.pages)}")
            text = page.extract_text()
            if text:
                full_text += text + "\n\n"
    
    return full_text

def extract_portfolio_value(text):
    """Extract portfolio value from text."""
    # Look for specific patterns in the text
    portfolio_value_patterns = [
        r'Portfolio\s+Total\s+(\d[\d,.\']*)',
        r'Total\s+assets\s+(\d[\d,.\']*)',
        r'Portfolio\s+Total\s*[:\s]+(\d[\d,.\']*)',
        r'Total\s+assets\s*[:\s]+(\d[\d,.\']*)',
        r'Portfolio\s+Value\s*[:\s]+(\d[\d,.\']*)',
        r'Total\s+Value\s*[:\s]+(\d[\d,.\']*)',
        r'Total\s+Portfolio\s+Value\s*[:\s]+(\d[\d,.\']*)'
    ]
    
    for pattern in portfolio_value_patterns:
        match = re.search(pattern, text)
        if match:
            value_str = match.group(1).strip()
            value_str = value_str.replace("'", "").replace(",", "")
            try:
                return float(value_str)
            except ValueError:
                continue
    
    # If no match found, look for specific lines
    lines = text.split('\n')
    for line in lines:
        if "Portfolio Total" in line:
            # Try to extract a number from this line
            number_match = re.search(r'(\d[\d,.\']*)', line)
            if number_match:
                value_str = number_match.group(1).strip()
                value_str = value_str.replace("'", "").replace(",", "")
                try:
                    return float(value_str)
                except ValueError:
                    continue
    
    return None

def extract_asset_allocation(text):
    """Extract asset allocation from text."""
    asset_allocation = {}
    
    # Look for the Asset Allocation section
    asset_allocation_start = text.find("Asset Allocation")
    if asset_allocation_start == -1:
        return asset_allocation
    
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
            
            asset_allocation[asset_class] = {
                "value": value,
                "percentage": percentage
            }
        except ValueError:
            continue
    
    return asset_allocation

def extract_securities(text):
    """Extract securities from text."""
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
        
        # Create security object
        security = {
            "isin": isin,
            "description": description,
            "valuation": valuation
        }
        
        # Check if this security is already in the list
        if not any(s["isin"] == isin for s in securities):
            securities.append(security)
    
    return securities

def main():
    """Main function."""
    print("Starting asset allocation extraction on messos.pdf...")
    
    # Create output directory if it doesn't exist
    os.makedirs("asset_allocation_results", exist_ok=True)
    
    # Extract text from PDF
    pdf_path = "messos.pdf"
    full_text = extract_text_from_pdf(pdf_path)
    
    # Save the full text
    with open("asset_allocation_results/messos_full_text.txt", "w", encoding="utf-8") as f:
        f.write(full_text)
    
    # Extract portfolio value
    portfolio_value = extract_portfolio_value(full_text)
    print(f"Portfolio value: {portfolio_value}")
    
    # Extract asset allocation
    asset_allocation = extract_asset_allocation(full_text)
    print(f"Extracted {len(asset_allocation)} asset classes")
    
    # Print asset allocation details
    print("\nAsset Allocation:")
    print("-" * 80)
    print(f"{'Asset Class':<30} {'Value':>15} {'Percentage':>15}")
    print("-" * 80)
    
    total_value = 0
    for asset_class, data in asset_allocation.items():
        value = data.get("value", 0)
        percentage = data.get("percentage", 0)
        
        total_value += value
        
        print(f"{asset_class:<30} {value:>15,.2f} {percentage:>15.2f}%")
    
    print("-" * 80)
    print(f"{'Total':<30} {total_value:>15,.2f}")
    print(f"{'Portfolio Value':<30} {portfolio_value:>15,.2f}")
    print(f"{'Difference':<30} {total_value - portfolio_value:>15,.2f}")
    
    # Calculate percentage of portfolio covered by extracted asset classes
    if portfolio_value > 0:
        coverage = (total_value / portfolio_value) * 100
        print(f"Coverage: {coverage:.2f}%")
    
    # Extract securities
    securities = extract_securities(full_text)
    print(f"\nExtracted {len(securities)} securities")
    
    # Calculate total securities value
    securities_value = 0
    for security in securities:
        valuation = security.get("valuation")
        if valuation is not None:
            securities_value += valuation
    
    print(f"Total securities value: ${securities_value:,.2f}")
    print(f"Securities coverage: {(securities_value / portfolio_value * 100) if portfolio_value > 0 else 0:.2f}%")
    
    # Save the detailed asset allocation information
    with open("asset_allocation_results/messos_asset_allocation.json", "w", encoding="utf-8") as f:
        json.dump(asset_allocation, f, indent=2)
    
    # Save the detailed securities information
    with open("asset_allocation_results/messos_securities.json", "w", encoding="utf-8") as f:
        json.dump(securities, f, indent=2)
    
    print("\nAsset allocation extraction completed. Results saved to asset_allocation_results directory.")

if __name__ == "__main__":
    main()
