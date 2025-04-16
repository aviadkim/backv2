"""
Direct extraction script for financial documents using pdfplumber.
"""
import os
import json
import re
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
    portfolio_value_patterns = [
        r'Total\s+assets\s*[:\s]+(\d[\d,.\']*)',
        r'Portfolio\s+Total\s*[:\s]+(\d[\d,.\']*)',
        r'Total\s+assets\s*[\|\:]?\s*(\d[\d,.\']*)',
        r'Portfolio\s+Value\s*[\|\:]?\s*(\d[\d,.\']*)',
        r'Total\s+Value\s*[\|\:]?\s*(\d[\d,.\']*)',
        r'Total\s+Portfolio\s+Value\s*[\|\:]?\s*(\d[\d,.\']*)'
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

    return None

def extract_securities(text):
    """Extract securities from text."""
    securities = []

    # Look for ISIN patterns
    isin_pattern = r'([A-Z]{2}[A-Z0-9]{9}[0-9])'
    isin_matches = re.finditer(isin_pattern, text)

    for match in isin_matches:
        isin = match.group(1)

        # Get context around the ISIN (500 characters before and after)
        start_pos = max(0, match.start() - 500)
        end_pos = min(len(text), match.end() + 500)
        context = text[start_pos:end_pos]

        # Try to extract description
        desc_pattern = r'([A-Z][A-Z0-9\s\.\-\(\)]{5,50})'
        desc_match = re.search(desc_pattern, context[:match.start() - start_pos])
        description = desc_match.group(1).strip() if desc_match else "Unknown"

        # Try to extract valuation
        valuation_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)(?:\s*(?:USD|EUR|GBP|CHF|JPY|$|€|£))?'
        valuation_matches = list(re.finditer(valuation_pattern, context[match.end() - start_pos:]))

        valuation = None
        if valuation_matches:
            # Take the first number after the ISIN as potential valuation
            valuation_str = valuation_matches[0].group(1)
            try:
                valuation = float(valuation_str.replace(',', ''))
            except ValueError:
                valuation = None

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

def extract_large_values(text):
    """Extract lines with large monetary values that might be portfolio holdings."""
    # Look for large values (over 10,000) that might be portfolio holdings
    # Pattern for values with apostrophes as thousand separators (e.g., 19'510'599)
    large_value_pattern = r'([A-Z][A-Z0-9\s\.\-\(\)]{5,50}).*?(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)\s*(?:USD|EUR|GBP|CHF|JPY|\$|€|£)?'

    securities = []
    for line in text.split('\n'):
        # Skip short lines
        if len(line.strip()) < 20:
            continue

        # Look for large values
        matches = re.finditer(large_value_pattern, line)
        for match in matches:
            description = match.group(1).strip()
            value_str = match.group(2).strip()

            try:
                value = float(value_str.replace(',', '').replace("'", ''))
                # Only consider values over 10,000 as potential holdings
                if value > 10000:
                    # Try to find an ISIN near this description
                    isin_pattern = r'([A-Z]{2}[A-Z0-9]{9}[0-9])'
                    context_start = max(0, text.find(line) - 500)
                    context_end = min(len(text), text.find(line) + len(line) + 500)
                    context = text[context_start:context_end]

                    isin_match = re.search(isin_pattern, context)
                    isin = isin_match.group(1) if isin_match else None

                    # Create security object
                    security = {
                        "isin": isin,
                        "description": description,
                        "valuation": value
                    }

                    # Check if this security is already in the list
                    if not any((s.get("isin") == isin if isin else s.get("description") == description) for s in securities):
                        securities.append(security)
            except ValueError:
                continue

    return securities

def extract_table_data(text):
    """Extract data that looks like it's in a table format."""
    # Look for lines with multiple numbers that might be table rows
    table_row_pattern = r'([A-Z][A-Z0-9\s\.\-\(\)]{5,50}).*?(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?).*?(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)'
    table_matches = re.finditer(table_row_pattern, text)

    securities = []
    for match in table_matches:
        description = match.group(1).strip()
        # Try to find an ISIN near this description
        isin_pattern = r'([A-Z]{2}[A-Z0-9]{9}[0-9])'
        context_start = max(0, match.start() - 200)
        context_end = min(len(text), match.end() + 200)
        context = text[context_start:context_end]

        isin_match = re.search(isin_pattern, context)
        isin = isin_match.group(1) if isin_match else None

        # Get the valuation (assuming it's the last number in the row)
        valuation_str = match.group(3)
        try:
            valuation = float(valuation_str.replace(',', ''))
        except ValueError:
            valuation = None

        # Create security object
        security = {
            "isin": isin,
            "description": description,
            "valuation": valuation
        }

        # Check if this security is already in the list
        if not any((s.get("isin") == isin if isin else s.get("description") == description) for s in securities):
            securities.append(security)

    return securities

def main():
    """Main function to extract and analyze holdings with direct methods."""
    print("Starting direct extraction on messos.pdf...")

    # Create output directory if it doesn't exist
    os.makedirs("direct_results", exist_ok=True)

    # Extract text from PDF
    pdf_path = "messos.pdf"
    full_text = extract_text_from_pdf(pdf_path)

    # Save the full text
    with open("direct_results/messos_full_text.txt", "w", encoding="utf-8") as f:
        f.write(full_text)

    # Extract portfolio value
    portfolio_value = extract_portfolio_value(full_text)
    print(f"Portfolio value: {portfolio_value}")

    # Extract securities
    securities = extract_securities(full_text)

    # Extract table data
    table_securities = extract_table_data(full_text)

    # Extract large values
    large_value_securities = extract_large_values(full_text)

    # Combine securities
    for sec in table_securities:
        if not any((s.get("isin") == sec.get("isin") if sec.get("isin") else s.get("description") == sec.get("description")) for s in securities):
            securities.append(sec)

    for sec in large_value_securities:
        if not any((s.get("isin") == sec.get("isin") if sec.get("isin") else s.get("description") == sec.get("description")) for s in securities):
            securities.append(sec)

    print(f"Extracted {len(securities)} securities")

    # Calculate total value
    total_value = 0

    # Print securities details
    print("\nSecurities details:")
    print("-" * 80)
    print(f"{'ISIN':<15} {'Description':<40} {'Value':>15}")
    print("-" * 80)

    for security in securities:
        isin = security.get("isin") or "N/A"
        description = security.get("description") or "Unknown"
        valuation = security.get("valuation")

        if valuation is not None:
            total_value += valuation

        valuation_str = f"{valuation:,.2f}" if valuation is not None else "N/A"
        print(f"{isin:<15} {description[:40]:<40} {valuation_str:>15}")

    print("-" * 80)
    print(f"{'Total':<56} {total_value:>15,.2f}")
    portfolio_value = portfolio_value or 0
    print(f"{'Portfolio Value':<56} {portfolio_value:>15,.2f}")
    print(f"{'Difference':<56} {total_value - portfolio_value:>15,.2f}")

    # Calculate percentage of portfolio covered by extracted securities
    if portfolio_value > 0:
        coverage = (total_value / portfolio_value) * 100
        print(f"Coverage: {coverage:.2f}%")

    # Save the detailed holdings information
    with open("direct_results/messos_securities.json", "w", encoding="utf-8") as f:
        json.dump(securities, f, indent=2)

    print("\nDirect extraction completed. Results saved to direct_results directory.")

if __name__ == "__main__":
    main()
