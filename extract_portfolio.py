"""
Script to extract portfolio value and holdings from messos.pdf.
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

def extract_holdings(text):
    """Extract holdings from text."""
    holdings = []
    
    # Look for sections that might contain holdings
    sections = [
        "Bonds",
        "Equities",
        "Structured products",
        "Other assets"
    ]
    
    for section in sections:
        section_start = text.find(section)
        if section_start == -1:
            continue
        
        # Find the end of the section (next section or end of text)
        section_end = len(text)
        for next_section in sections:
            if next_section != section:
                next_section_start = text.find(next_section, section_start + len(section))
                if next_section_start != -1 and next_section_start < section_end:
                    section_end = next_section_start
        
        section_text = text[section_start:section_end]
        
        # Look for ISIN patterns in the section
        isin_pattern = r'ISIN:\s*([A-Z]{2}[A-Z0-9]{9}[0-9])'
        isin_matches = re.finditer(isin_pattern, section_text)
        
        for match in isin_matches:
            isin = match.group(1)
            
            # Get context around the ISIN (200 characters before and after)
            context_start = max(0, match.start() - 200)
            context_end = min(len(section_text), match.end() + 200)
            context = section_text[context_start:context_end]
            
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
            
            # Create holding object
            holding = {
                "isin": isin,
                "description": description,
                "valuation": valuation,
                "section": section
            }
            
            # Check if this holding is already in the list
            if not any(h["isin"] == isin for h in holdings):
                holdings.append(holding)
    
    # Look for large values in the text that might be asset class totals
    asset_class_pattern = r'((?:Bonds|Equities|Structured products|Other assets)(?:\s+\([^)]*\))?)\s+(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)'
    asset_class_matches = re.finditer(asset_class_pattern, text)
    
    for match in asset_class_matches:
        asset_class = match.group(1).strip()
        value_str = match.group(2).strip()
        
        try:
            value = float(value_str.replace(',', '').replace("'", ''))
            if value > 10000:  # Likely an asset class total
                holding = {
                    "isin": None,
                    "description": f"Total {asset_class}",
                    "valuation": value,
                    "section": "Asset Class Totals"
                }
                holdings.append(holding)
        except ValueError:
            continue
    
    return holdings

def main():
    """Main function."""
    print("Starting portfolio extraction on messos.pdf...")
    
    # Create output directory if it doesn't exist
    os.makedirs("portfolio_results", exist_ok=True)
    
    # Extract text from PDF
    pdf_path = "messos.pdf"
    full_text = extract_text_from_pdf(pdf_path)
    
    # Save the full text
    with open("portfolio_results/messos_full_text.txt", "w", encoding="utf-8") as f:
        f.write(full_text)
    
    # Extract portfolio value
    portfolio_value = extract_portfolio_value(full_text)
    print(f"Portfolio value: {portfolio_value}")
    
    # Extract holdings
    holdings = extract_holdings(full_text)
    print(f"Extracted {len(holdings)} holdings")
    
    # Calculate total value
    total_value = 0
    
    # Print holdings details
    print("\nHoldings details:")
    print("-" * 80)
    print(f"{'ISIN':<15} {'Description':<40} {'Value':>15}")
    print("-" * 80)
    
    for holding in holdings:
        isin = holding.get("isin") or "N/A"
        description = holding.get("description") or "Unknown"
        valuation = holding.get("valuation")
        
        if valuation is not None:
            total_value += valuation
        
        valuation_str = f"{valuation:,.2f}" if valuation is not None else "N/A"
        print(f"{isin:<15} {description[:40]:<40} {valuation_str:>15}")
    
    print("-" * 80)
    print(f"{'Total':<56} {total_value:>15,.2f}")
    portfolio_value = portfolio_value or 0
    print(f"{'Portfolio Value':<56} {portfolio_value:>15,.2f}")
    print(f"{'Difference':<56} {total_value - portfolio_value:>15,.2f}")
    
    # Calculate percentage of portfolio covered by extracted holdings
    if portfolio_value > 0:
        coverage = (total_value / portfolio_value) * 100
        print(f"Coverage: {coverage:.2f}%")
    
    # Save the detailed holdings information
    with open("portfolio_results/messos_holdings.json", "w", encoding="utf-8") as f:
        json.dump(holdings, f, indent=2)
    
    print("\nPortfolio extraction completed. Results saved to portfolio_results directory.")

if __name__ == "__main__":
    main()
