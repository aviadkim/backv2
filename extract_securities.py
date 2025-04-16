"""
Script to extract securities from messos.pdf.
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

def extract_securities_from_bonds_section(text):
    """Extract securities from the Bonds section."""
    securities = []

    # Find the Bonds section
    bonds_start = text.find("Bonds")
    if bonds_start == -1:
        return securities

    # Find the end of the Bonds section
    bonds_end = text.find("Equities", bonds_start)
    if bonds_end == -1:
        bonds_end = len(text)

    bonds_text = text[bonds_start:bonds_end]

    # Look for ISIN patterns in the Bonds section
    isin_pattern = r'ISIN:?\s*([A-Z]{2}[A-Z0-9]{9}[0-9])'
    isin_matches = re.finditer(isin_pattern, bonds_text)

    for match in isin_matches:
        isin = match.group(1)

        # Get context around the ISIN (500 characters before and after)
        context_start = max(0, match.start() - 500)
        context_end = min(len(bonds_text), match.end() + 500)
        context = bonds_text[context_start:context_end]

        # Try to extract description
        desc_pattern = r'([A-Z][A-Z0-9\s\.\-\(\)]{5,50})'
        desc_match = re.search(desc_pattern, context[:match.start() - context_start])
        description = desc_match.group(1).strip() if desc_match else "Unknown"

        # Try to extract valuation
        valuation_pattern = r'(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)'

        # Look for valuation in the context after the ISIN
        after_isin = context[match.end() - context_start:]
        valuation_matches = list(re.finditer(valuation_pattern, after_isin))

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

        # If no large value found, look for specific patterns
        if valuation is None:
            # Look for "Valuation in price currency" followed by a number
            valuation_pattern = r'Valuation\s+in\s+price\s+currency.*?(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)'
            valuation_match = re.search(valuation_pattern, after_isin)
            if valuation_match:
                val_str = valuation_match.group(1)
                try:
                    valuation = float(val_str.replace(',', '').replace("'", ''))
                except ValueError:
                    valuation = None

        # Create security object
        security = {
            "isin": isin,
            "description": description,
            "valuation": valuation,
            "section": "Bonds"
        }

        # Check if this security is already in the list
        if not any(s["isin"] == isin for s in securities):
            securities.append(security)

    return securities

def extract_securities_from_structured_products_section(text):
    """Extract securities from the Structured Products section."""
    securities = []

    # Find the Structured Products section
    structured_start = text.find("Structured products")
    if structured_start == -1:
        return securities

    # Find the end of the Structured Products section
    structured_end = text.find("Other assets", structured_start)
    if structured_end == -1:
        structured_end = len(text)

    structured_text = text[structured_start:structured_end]

    # Look for ISIN patterns in the Structured Products section
    isin_pattern = r'ISIN:?\s*([A-Z]{2}[A-Z0-9]{9}[0-9])'
    isin_matches = re.finditer(isin_pattern, structured_text)

    for match in isin_matches:
        isin = match.group(1)

        # Get context around the ISIN (500 characters before and after)
        context_start = max(0, match.start() - 500)
        context_end = min(len(structured_text), match.end() + 500)
        context = structured_text[context_start:context_end]

        # Try to extract description
        desc_pattern = r'([A-Z][A-Z0-9\s\.\-\(\)]{5,50})'
        desc_match = re.search(desc_pattern, context[:match.start() - context_start])
        description = desc_match.group(1).strip() if desc_match else "Unknown"

        # Try to extract valuation
        valuation_pattern = r'(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)'

        # Look for valuation in the context after the ISIN
        after_isin = context[match.end() - context_start:]
        valuation_matches = list(re.finditer(valuation_pattern, after_isin))

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

        # If no large value found, look for specific patterns
        if valuation is None:
            # Look for "Valuation in price currency" followed by a number
            valuation_pattern = r'Valuation\s+in\s+price\s+currency.*?(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)'
            valuation_match = re.search(valuation_pattern, after_isin)
            if valuation_match:
                val_str = valuation_match.group(1)
                try:
                    valuation = float(val_str.replace(',', '').replace("'", ''))
                except ValueError:
                    valuation = None

        # Create security object
        security = {
            "isin": isin,
            "description": description,
            "valuation": valuation,
            "section": "Structured Products"
        }

        # Check if this security is already in the list
        if not any(s["isin"] == isin for s in securities):
            securities.append(security)

    return securities

def extract_securities_from_equities_section(text):
    """Extract securities from the Equities section."""
    securities = []

    # Find the Equities section
    equities_start = text.find("Equities")
    if equities_start == -1:
        return securities

    # Find the end of the Equities section
    equities_end = text.find("Structured products", equities_start)
    if equities_end == -1:
        equities_end = len(text)

    equities_text = text[equities_start:equities_end]

    # Look for ISIN patterns in the Equities section
    isin_pattern = r'ISIN:?\s*([A-Z]{2}[A-Z0-9]{9}[0-9])'
    isin_matches = re.finditer(isin_pattern, equities_text)

    for match in isin_matches:
        isin = match.group(1)

        # Get context around the ISIN (500 characters before and after)
        context_start = max(0, match.start() - 500)
        context_end = min(len(equities_text), match.end() + 500)
        context = equities_text[context_start:context_end]

        # Try to extract description
        desc_pattern = r'([A-Z][A-Z0-9\s\.\-\(\)]{5,50})'
        desc_match = re.search(desc_pattern, context[:match.start() - context_start])
        description = desc_match.group(1).strip() if desc_match else "Unknown"

        # Try to extract valuation
        valuation_pattern = r'(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)'

        # Look for valuation in the context after the ISIN
        after_isin = context[match.end() - context_start:]
        valuation_matches = list(re.finditer(valuation_pattern, after_isin))

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

        # If no large value found, look for specific patterns
        if valuation is None:
            # Look for "Valuation in price currency" followed by a number
            valuation_pattern = r'Valuation\s+in\s+price\s+currency.*?(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)'
            valuation_match = re.search(valuation_pattern, after_isin)
            if valuation_match:
                val_str = valuation_match.group(1)
                try:
                    valuation = float(val_str.replace(',', '').replace("'", ''))
                except ValueError:
                    valuation = None

        # Create security object
        security = {
            "isin": isin,
            "description": description,
            "valuation": valuation,
            "section": "Equities"
        }

        # Check if this security is already in the list
        if not any(s["isin"] == isin for s in securities):
            securities.append(security)

    return securities

def extract_securities_from_full_text(text):
    """Extract securities from the full text."""
    securities = []

    # Look for ISIN patterns in the full text
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

        # Look for valuation in the context after the ISIN
        after_isin = context[match.end() - context_start:]
        valuation_matches = list(re.finditer(valuation_pattern, after_isin))

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

        # Determine section based on context
        section = "Unknown"
        if "Bonds" in context or "Bond" in context:
            section = "Bonds"
        elif "Equities" in context or "Equity" in context:
            section = "Equities"
        elif "Structured products" in context or "Structured product" in context:
            section = "Structured Products"

        # Create security object
        security = {
            "isin": isin,
            "description": description,
            "valuation": valuation,
            "section": section
        }

        # Check if this security is already in the list
        if not any(s["isin"] == isin for s in securities):
            securities.append(security)

    return securities

def main():
    """Main function."""
    print("Starting securities extraction on messos.pdf...")

    # Create output directory if it doesn't exist
    os.makedirs("securities_results", exist_ok=True)

    # Extract text from PDF
    pdf_path = "messos.pdf"
    full_text = extract_text_from_pdf(pdf_path)

    # Save the full text
    with open("securities_results/messos_full_text.txt", "w", encoding="utf-8") as f:
        f.write(full_text)

    # Extract portfolio value
    portfolio_value = extract_portfolio_value(full_text)
    print(f"Portfolio value: {portfolio_value}")

    # Extract securities from the full text
    securities = extract_securities_from_full_text(full_text)

    # Count securities by section
    bonds_count = sum(1 for s in securities if s["section"] == "Bonds")
    equities_count = sum(1 for s in securities if s["section"] == "Equities")
    structured_count = sum(1 for s in securities if s["section"] == "Structured Products")
    unknown_count = sum(1 for s in securities if s["section"] == "Unknown")

    print(f"Extracted {len(securities)} securities:")
    print(f"  - Bonds: {bonds_count}")
    print(f"  - Equities: {equities_count}")
    print(f"  - Structured Products: {structured_count}")
    print(f"  - Unknown: {unknown_count}")

    # Calculate total securities value
    total_value = 0
    securities_with_value = 0

    # Print securities details
    print("\nSecurities details:")
    print("-" * 100)
    print(f"{'ISIN':<15} {'Description':<40} {'Section':<20} {'Value':>15}")
    print("-" * 100)

    for security in securities:
        isin = security.get("isin") or "N/A"
        description = security.get("description") or "Unknown"
        section = security.get("section") or "Unknown"
        valuation = security.get("valuation")

        if valuation is not None:
            total_value += valuation
            securities_with_value += 1

        valuation_str = f"{valuation:,.2f}" if valuation is not None else "N/A"
        print(f"{isin:<15} {description[:40]:<40} {section:<20} {valuation_str:>15}")

    print("-" * 100)
    print(f"{'Total':<76} {total_value:>15,.2f}")
    print(f"{'Portfolio Value':<76} {portfolio_value:>15,.2f}")
    print(f"{'Difference':<76} {total_value - portfolio_value:>15,.2f}")

    # Calculate percentage of portfolio covered by extracted securities
    if portfolio_value > 0:
        coverage = (total_value / portfolio_value) * 100
        print(f"Coverage: {coverage:.2f}%")

    if len(securities) > 0:
        print(f"\nSecurities with value: {securities_with_value} out of {len(securities)} ({securities_with_value / len(securities) * 100:.2f}%)")
    else:
        print("\nNo securities found.")

    # Save the detailed securities information
    with open("securities_results/messos_securities.json", "w", encoding="utf-8") as f:
        json.dump(securities, f, indent=2)

    print("\nSecurities extraction completed. Results saved to securities_results directory.")

if __name__ == "__main__":
    main()
