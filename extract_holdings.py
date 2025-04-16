"""
Extract holdings data from the PDF text.
"""
import os
import re
import json
import pandas as pd

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

def extract_holdings():
    """Extract holdings data from the PDF text."""
    # Try to read the extracted text
    try:
        with open('messos.txt', 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading text file: {str(e)}")
        return

    print(f"Extracted text length: {len(text)} characters")

    # Find the portfolio value
    portfolio_value_pattern = r"19'510'599"
    if re.search(portfolio_value_pattern, text):
        portfolio_value = 19510599
        print(f"Found portfolio value: ${portfolio_value:,}")
    else:
        portfolio_value = None
        print("Portfolio value not found in text")

    # Extract asset allocation
    print("\nExtracting asset allocation...")

    asset_allocation = {}

    # Look for asset allocation section
    asset_allocation_pattern = r"Asset Allocation.*?(?=Currency allocation|$)"
    asset_allocation_match = re.search(asset_allocation_pattern, text, re.DOTALL | re.IGNORECASE)

    if asset_allocation_match:
        asset_section = asset_allocation_match.group(0)

        # Extract asset categories and values
        categories = [
            "Liquidity", "Bonds", "Equities", "Mixed funds",
            "Structured products", "Metal accounts and precious metals",
            "Real Estate", "Other assets"
        ]

        for category in categories:
            # Look for the category and associated value
            category_pattern = f"{category}.*?(\\d+'\\d+(?:'\\d+)?)"
            category_match = re.search(category_pattern, asset_section, re.DOTALL)

            if category_match:
                value_str = category_match.group(1)
                value = clean_number(value_str)

                if value:
                    asset_allocation[category] = value

    # Print asset allocation
    if asset_allocation:
        print("\nAsset Allocation:")
        total = sum(asset_allocation.values())

        for category, value in asset_allocation.items():
            percentage = value / total * 100 if total > 0 else 0
            print(f"{category}: ${value:,.2f} ({percentage:.2f}%)")

    # Extract holdings data
    print("\nExtracting holdings data...")

    # Extract securities directly by looking for ISIN patterns
    holdings = []

    # Look for ISIN numbers in the entire text
    isin_pattern = r'ISIN:\s*([A-Z]{2}[A-Z0-9]{9}[0-9])'
    isin_matches = re.findall(isin_pattern, text)

    print(f"Found {len(isin_matches)} ISIN numbers")

    for isin in isin_matches:
        # Find context around this ISIN (larger context to capture more information)
        context_pattern = r'.{0,500}ISIN:\s*' + isin + r'.{0,500}'
        context_matches = re.findall(context_pattern, text, re.DOTALL)

        if context_matches:
            context = context_matches[0]

            # Extract security name (usually the line before ISIN)
            name = None
            lines = context.split('\n')
            for i, line in enumerate(lines):
                if f"ISIN: {isin}" in line and i > 0:
                    name = lines[i-1].strip()
                    break

            # If name not found, try a different approach
            if not name:
                for line in lines:
                    if len(line) > 10 and not re.search(r'ISIN|Valorn', line):
                        name = line.strip()
                        break

            # Look for numeric values in the context
            value_pattern = r"(\d+'?\d*(?:'?\d*)?)"
            value_matches = re.findall(value_pattern, context)

            numeric_values = []
            for val_match in value_matches:
                numeric_value = clean_number(val_match)
                if numeric_value and numeric_value > 0:
                    numeric_values.append(numeric_value)

            # Determine asset class
            asset_class = "Unknown"
            if "Bonds" in context or "Bond" in context:
                asset_class = "Bonds"
            elif "Equities" in context or "Equity" in context:
                asset_class = "Equities"
            elif "Structured products" in context or "Structured product" in context:
                asset_class = "Structured products"
            elif "Liquidity" in context:
                asset_class = "Liquidity"
            elif "Other assets" in context:
                asset_class = "Other assets"

            # Look for specific patterns in the context
            quantity = None
            price = None
            value = None

            # Sort numeric values by magnitude
            numeric_values.sort()

            # Look for specific patterns that indicate value
            value_candidates = []
            for i, line in enumerate(lines):
                # Look for percentage patterns which often appear next to values
                if re.search(r'\d+\.\d+%', line) and i > 0:
                    # Check the previous line for a numeric value
                    prev_line = lines[i-1].strip()
                    prev_values = re.findall(value_pattern, prev_line)

                    for val_match in prev_values:
                        val = clean_number(val_match)
                        if val and val > 10000:  # Values are usually large
                            value_candidates.append(val)

            # If we found value candidates, use the largest one
            if value_candidates:
                value = max(value_candidates)
            elif numeric_values and len(numeric_values) >= 1:
                # If no specific value candidates, use the largest numeric value
                large_values = [v for v in numeric_values if v > 10000]
                if large_values:
                    value = max(large_values)

            # Look for price (usually around 100 for bonds)
            price_candidates = [v for v in numeric_values if 80 <= v <= 120]
            if price_candidates:
                price = price_candidates[-1]  # Use the largest price candidate

            # If we have value and price, calculate quantity
            if value and price and price > 0:
                calculated_quantity = value / price

                # Look for a numeric value close to the calculated quantity
                quantity_candidates = [v for v in numeric_values if v != price and abs(v - calculated_quantity) / calculated_quantity < 0.1]
                if quantity_candidates:
                    quantity = min(quantity_candidates, key=lambda x: abs(x - calculated_quantity))
                else:
                    # If no close match, just use the calculated quantity
                    quantity = calculated_quantity

            holdings.append({
                'isin': isin,
                'name': name,
                'quantity': quantity,
                'price': price,
                'value': value,
                'asset_class': asset_class,
                'context': context.strip()
            })

    # Remove duplicates based on ISIN
    unique_holdings = {}
    for holding in holdings:
        isin = holding['isin']
        if isin not in unique_holdings or (holding['value'] is not None and unique_holdings[isin]['value'] is None):
            unique_holdings[isin] = holding

    holdings = list(unique_holdings.values())

    # Calculate missing values
    for holding in holdings:
        if holding['quantity'] and holding['price'] and not holding['value']:
            holding['value'] = holding['quantity'] * holding['price']
        elif holding['quantity'] and holding['value'] and not holding['price']:
            holding['price'] = holding['value'] / holding['quantity']
        elif holding['price'] and holding['value'] and not holding['quantity']:
            holding['quantity'] = holding['value'] / holding['price']

    # Calculate total value
    total_value = sum(holding['value'] for holding in holdings if holding['value'] is not None)

    print(f"Found {len(holdings)} unique securities")
    print(f"Calculated total value: ${total_value:,.2f}")

    if portfolio_value:
        discrepancy = portfolio_value - total_value
        print(f"Discrepancy from reported value: ${discrepancy:,.2f} ({discrepancy/portfolio_value*100:.2f}%)")

    # Create a DataFrame for better display
    df = pd.DataFrame(holdings)

    # Reorder and select columns
    columns = ['isin', 'name', 'quantity', 'price', 'value', 'asset_class']
    if not df.empty and all(col in df.columns for col in columns):
        df = df[columns]

    # Save results
    output_dir = 'holdings_data'
    os.makedirs(output_dir, exist_ok=True)

    # Save to CSV
    df.to_csv(os.path.join(output_dir, 'holdings.csv'), index=False)

    # Save to JSON
    with open(os.path.join(output_dir, 'holdings.json'), 'w', encoding='utf-8') as f:
        json.dump(holdings, f, indent=2)

    # Save summary
    summary = {
        'total_securities': len(holdings),
        'calculated_total_value': total_value,
        'reported_portfolio_value': portfolio_value,
        'discrepancy': portfolio_value - total_value if portfolio_value else None,
        'discrepancy_percentage': (portfolio_value - total_value) / portfolio_value * 100 if portfolio_value else None,
        'asset_allocation': asset_allocation
    }

    with open(os.path.join(output_dir, 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults saved to {output_dir} directory")

    return holdings, portfolio_value, asset_allocation

def main():
    """Main function."""
    extract_holdings()

    return 0

if __name__ == "__main__":
    main()
