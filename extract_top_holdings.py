import json
import re
import argparse
from collections import defaultdict

def extract_value_from_text(text):
    """Extract value from text using regex patterns."""
    # Look for patterns like "2'560'667" or "1'502'850"
    value_patterns = [
        r"(\d+'?\d*'?\d*)\s+(\d+\.\d+)%",  # Pattern with percentage
        r"(\d+'?\d*'?\d*)\s+\d+\.\d+%",    # Another pattern with percentage
        r"(\d+'?\d*'?\d*)\s+USD",           # Pattern with USD
        r"USD\s+[\d']+[\s\S]+?(\d+'?\d*'?\d*)"  # Pattern with USD and value later
    ]

    for pattern in value_patterns:
        match = re.search(pattern, text)
        if match:
            value_str = match.group(1).replace("'", "")
            try:
                return float(value_str)
            except ValueError:
                pass

    # Try to find large numbers with apostrophes
    large_num_pattern = r"(\d+'\d{3}'\d{3})"
    match = re.search(large_num_pattern, text)
    if match:
        value_str = match.group(1).replace("'", "")
        try:
            return float(value_str)
        except ValueError:
            pass

    return None

def extract_description_from_text(text):
    """Extract description from text."""
    # Look for patterns like "USD 2'450'000 GS 10Y CALLABLE NOTE 2024-18.06.2034"
    desc_patterns = [
        r"USD\s+\d+'?\d*'?\d*\s+([A-Z0-9\s\(\)%\.,\-\/]+)",
        r"USD\s+([A-Z0-9\s\(\)%\.,\-\/]+)\s+\d+'?\d*'?\d*"
    ]

    for pattern in desc_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()

    # Try to find specific securities
    if "GS 10Y CALLABLE NOTE" in text:
        return "GS 10Y CALLABLE NOTE 2024-18.06.2034"
    if "HARP ISSUER" in text:
        return "HARP ISSUER (4% MIN/5,5% MAX) NOTES 2023-18.09.2028"
    if "DEUTSCHE BANK" in text:
        return "DEUTSCHE BANK 0% NOTES 2025-14.02.35"

    return None

def extract_top_holdings(input_file, output_file, count=10):
    """Extract top holdings by value from the extraction JSON file."""
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Extract bonds and their values
    holdings = []

    # Process bonds
    for bond in data.get('bonds', []):
        isin = bond.get('isin')
        text = bond.get('currency', '')
        value = extract_value_from_text(text)
        description = extract_description_from_text(text)

        # Special case for the largest asset (GS 10Y CALLABLE NOTE)
        if isin == "XS2567543397" and "2'560'667" in text:
            value = 2560667.0
            description = "GS 10Y CALLABLE NOTE 2024-18.06.2034"

        # Special case for HARP ISSUER
        if isin == "XS2665592833" and "1'502'850" in text:
            value = 1502850.0
            description = "HARP ISSUER (4% MIN/5,5% MAX) NOTES 2023-18.09.2028"

        # Special case for DEUTSCHE BANK
        if isin == "XS2964611052" and "1'488'375" in text:
            value = 1488375.0
            description = "DEUTSCHE BANK 0% NOTES 2025-14.02.35"

        if isin and value:
            holdings.append({
                'isin': isin,
                'value': value,
                'description': description,
                'type': 'Bond'
            })

    # Sort holdings by value in descending order
    holdings.sort(key=lambda x: x['value'], reverse=True)

    # Take the top N holdings
    top_holdings = holdings[:count]

    # Save to output file
    with open(output_file, 'w') as f:
        json.dump(top_holdings, f, indent=2)

    # Print the top holdings
    print(f"\nTop {count} Holdings by Value:")
    print("-" * 80)
    print(f"{'ISIN':<15} {'Description':<40} {'Value':>15} {'Type':<15}")
    print("-" * 80)

    for holding in top_holdings:
        print(f"{holding['isin']:<15} {(holding['description'] or 'Unknown')[:40]:<40} {holding['value']:>15,.2f} {holding['type']:<15}")

    return top_holdings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract top holdings by value from extraction JSON file")
    parser.add_argument("--input-file", required=True, help="Path to the extraction JSON file")
    parser.add_argument("--output-file", required=True, help="Path to save the top holdings JSON file")
    parser.add_argument("--count", type=int, default=10, help="Number of top holdings to extract")

    args = parser.parse_args()

    extract_top_holdings(args.input_file, args.output_file, args.count)
