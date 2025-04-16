"""
Extract holdings data from the PDF text with improved value extraction.
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
            
            # Extract quantity, price, and value using a more targeted approach
            quantity = None
            price = None
            value = None
            
            # Look for patterns that indicate value
            # Values are often followed by a percentage (weight in portfolio)
            value_pattern = r"(\d+'?\d*(?:'?\d*)?)\s*\n\s*(\d+\.\d+%)"
            value_matches = re.findall(value_pattern, context)
            
            if value_matches:
                for val_str, pct in value_matches:
                    val = clean_number(val_str)
                    if val and val > 1000 and val < 10000000:  # Reasonable range for security values
                        value = val
                        break
            
            # If no value found, look for large numbers
            if not value:
                # Look for numeric values in the context
                value_pattern = r"(\d+'?\d*(?:'?\d*)?)"
                value_matches = re.findall(value_pattern, context)
                
                numeric_values = []
                for val_match in value_matches:
                    numeric_value = clean_number(val_match)
                    if numeric_value and numeric_value > 0:
                        numeric_values.append(numeric_value)
                
                # Filter for reasonable values (not too small, not too large)
                reasonable_values = [v for v in numeric_values if 1000 < v < 10000000]
                if reasonable_values:
                    value = max(reasonable_values)
            
            # Look for price (usually around 100 for bonds)
            price_pattern = r"(\d+\.\d+)"
            price_matches = re.findall(price_pattern, context)
            
            price_candidates = []
            for price_str in price_matches:
                price_val = float(price_str)
                if 80 <= price_val <= 120:  # Typical bond price range
                    price_candidates.append(price_val)
            
            if price_candidates:
                price = price_candidates[0]
            
            # If we have value and price, calculate quantity
            if value and price and price > 0:
                quantity = value / price
            
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
    output_dir = 'holdings_data_fixed'
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
