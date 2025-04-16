"""
Analyze portfolio data to extract holdings with value, quantity, and price.
"""
import os
import json
import pandas as pd
import re
import numpy as np
from decimal import Decimal, ROUND_HALF_UP

def load_extracted_data():
    """Load extracted data from the enhanced results."""
    tables_path = os.path.join('enhanced_results', 'extracted_tables_tabula.json')
    financial_data_path = os.path.join('enhanced_results', 'extracted_financial_data.json')
    isins_path = os.path.join('enhanced_results', 'extracted_isins.json')
    
    tables = []
    financial_data = {}
    isins = []
    
    if os.path.exists(tables_path):
        with open(tables_path, 'r', encoding='utf-8') as f:
            tables = json.load(f)
    
    if os.path.exists(financial_data_path):
        with open(financial_data_path, 'r', encoding='utf-8') as f:
            financial_data = json.load(f)
    
    if os.path.exists(isins_path):
        with open(isins_path, 'r', encoding='utf-8') as f:
            isins = json.load(f)
    
    return tables, financial_data, isins

def extract_holdings_from_tables(tables):
    """Extract holdings information from tables."""
    holdings = []
    
    for table_idx, table in enumerate(tables):
        # Convert table to DataFrame
        df = pd.DataFrame(table['data'], columns=table.get('columns', []))
        
        # Clean up column names
        if df.shape[1] >= 5:  # Ensure we have enough columns
            # Try to identify columns based on content
            potential_holdings = []
            
            for i, row in df.iterrows():
                row_values = row.values.tolist()
                
                # Skip header rows or empty rows
                if not row_values or all(pd.isna(val) or val == '' for val in row_values):
                    continue
                
                # Convert row to string for easier processing
                row_str = ' '.join([str(val) for val in row_values if not pd.isna(val) and val != ''])
                
                # Check if this row contains an ISIN
                isin_match = re.search(r'[A-Z]{2}[A-Z0-9]{9}[0-9]', row_str)
                
                if isin_match:
                    isin = isin_match.group(0)
                    
                    # Try to extract quantity, price, and value
                    quantity = None
                    price = None
                    value = None
                    
                    # Look for numeric values that could be quantity, price, or value
                    numeric_values = []
                    for val in row_values:
                        if isinstance(val, (int, float)) and not pd.isna(val):
                            numeric_values.append(val)
                        elif isinstance(val, str):
                            # Try to extract numeric values from strings
                            val_clean = val.replace(',', '').replace('$', '').strip()
                            try:
                                numeric_val = float(val_clean)
                                numeric_values.append(numeric_val)
                            except ValueError:
                                pass
                    
                    # If we have at least 3 numeric values, assume they are quantity, price, and value
                    if len(numeric_values) >= 3:
                        # Sort by magnitude (value is usually the largest)
                        numeric_values.sort()
                        
                        # Assign based on magnitude
                        if len(numeric_values) >= 3:
                            quantity = numeric_values[-3]
                            price = numeric_values[-2]
                            value = numeric_values[-1]
                    
                    # Extract security name
                    name = None
                    for val in row_values:
                        if isinstance(val, str) and len(val) > 5 and not re.match(r'[A-Z]{2}[A-Z0-9]{9}[0-9]', val):
                            name = val
                            break
                    
                    potential_holdings.append({
                        'isin': isin,
                        'name': name,
                        'quantity': quantity,
                        'price': price,
                        'value': value,
                        'table_idx': table_idx,
                        'row_idx': i,
                        'row_data': row_values
                    })
            
            holdings.extend(potential_holdings)
    
    return holdings

def extract_holdings_from_text(financial_data):
    """Extract holdings information from financial data text."""
    holdings = []
    
    # Extract portfolio value
    portfolio_value = None
    for key, value in financial_data.items():
        if 'total' in key.lower() and 'value' in key.lower():
            try:
                portfolio_value = float(value.replace(',', '').replace('$', '').strip())
            except ValueError:
                pass
    
    # Extract individual holdings
    if 'securities' in financial_data:
        securities = financial_data['securities']
        
        for security in securities:
            if isinstance(security, dict):
                holding = {
                    'isin': security.get('isin'),
                    'name': security.get('name'),
                    'quantity': None,
                    'price': None,
                    'value': None
                }
                
                # Try to extract quantity, price, and value
                if 'quantity' in security:
                    try:
                        holding['quantity'] = float(str(security['quantity']).replace(',', ''))
                    except ValueError:
                        pass
                
                if 'price' in security:
                    try:
                        holding['price'] = float(str(security['price']).replace(',', '').replace('$', ''))
                    except ValueError:
                        pass
                
                if 'value' in security:
                    try:
                        holding['value'] = float(str(security['value']).replace(',', '').replace('$', ''))
                    except ValueError:
                        pass
                
                holdings.append(holding)
    
    return holdings, portfolio_value

def merge_holdings(table_holdings, text_holdings):
    """Merge holdings from tables and text."""
    merged_holdings = {}
    
    # First add table holdings
    for holding in table_holdings:
        isin = holding['isin']
        if isin not in merged_holdings:
            merged_holdings[isin] = holding
        else:
            # Update with non-None values
            for key, value in holding.items():
                if value is not None and merged_holdings[isin].get(key) is None:
                    merged_holdings[isin][key] = value
    
    # Then add text holdings
    for holding in text_holdings:
        isin = holding['isin']
        if isin and isin not in merged_holdings:
            merged_holdings[isin] = holding
        elif isin:
            # Update with non-None values
            for key, value in holding.items():
                if value is not None and merged_holdings[isin].get(key) is None:
                    merged_holdings[isin][key] = value
    
    return list(merged_holdings.values())

def calculate_missing_values(holdings):
    """Calculate missing values based on available data."""
    for holding in holdings:
        # If we have quantity and price but no value, calculate value
        if holding['quantity'] is not None and holding['price'] is not None and holding['value'] is None:
            holding['value'] = holding['quantity'] * holding['price']
        
        # If we have quantity and value but no price, calculate price
        elif holding['quantity'] is not None and holding['value'] is not None and holding['price'] is None:
            holding['price'] = holding['value'] / holding['quantity']
        
        # If we have price and value but no quantity, calculate quantity
        elif holding['price'] is not None and holding['value'] is not None and holding['quantity'] is None:
            holding['quantity'] = holding['value'] / holding['price']
    
    return holdings

def clean_holdings(holdings):
    """Clean holdings data."""
    cleaned_holdings = []
    
    for holding in holdings:
        # Skip holdings with no value
        if holding['value'] is None:
            continue
        
        # Clean up values
        if holding['value'] is not None:
            # Round to 2 decimal places
            holding['value'] = round(float(holding['value']), 2)
        
        if holding['price'] is not None:
            # Round to 4 decimal places
            holding['price'] = round(float(holding['price']), 4)
        
        if holding['quantity'] is not None:
            # Round to whole number if close to integer
            quantity = float(holding['quantity'])
            if abs(quantity - round(quantity)) < 0.01:
                holding['quantity'] = int(round(quantity))
            else:
                holding['quantity'] = round(quantity, 2)
        
        cleaned_holdings.append(holding)
    
    return cleaned_holdings

def analyze_portfolio():
    """Analyze the portfolio and calculate the total value."""
    # Load extracted data
    tables, financial_data, isins = load_extracted_data()
    
    # Extract holdings from tables
    table_holdings = extract_holdings_from_tables(tables)
    
    # Extract holdings from text
    text_holdings, portfolio_value_from_text = extract_holdings_from_text(financial_data)
    
    # Merge holdings
    merged_holdings = merge_holdings(table_holdings, text_holdings)
    
    # Calculate missing values
    holdings_with_calculated_values = calculate_missing_values(merged_holdings)
    
    # Clean holdings
    cleaned_holdings = clean_holdings(holdings_with_calculated_values)
    
    # Calculate total portfolio value
    total_value = sum(holding['value'] for holding in cleaned_holdings if holding['value'] is not None)
    
    # Create a DataFrame for better display
    df = pd.DataFrame(cleaned_holdings)
    
    # Reorder columns
    if not df.empty:
        column_order = ['isin', 'name', 'quantity', 'price', 'value']
        df = df[column_order]
    
    return df, total_value, portfolio_value_from_text

def main():
    """Main function."""
    print("Analyzing portfolio data...")
    
    # Analyze portfolio
    holdings_df, calculated_total, reported_total = analyze_portfolio()
    
    # Print results
    print("\nExtracted Holdings:")
    print(holdings_df)
    
    print(f"\nCalculated Total Portfolio Value: ${calculated_total:,.2f}")
    if reported_total:
        print(f"Reported Total Portfolio Value: ${reported_total:,.2f}")
        
        # Calculate discrepancy
        discrepancy = reported_total - calculated_total
        print(f"Discrepancy: ${discrepancy:,.2f} ({discrepancy/reported_total*100:.2f}%)")
    
    # Save results to CSV
    output_dir = 'portfolio_analysis'
    os.makedirs(output_dir, exist_ok=True)
    
    holdings_df.to_csv(os.path.join(output_dir, 'holdings.csv'), index=False)
    
    # Save summary to JSON
    summary = {
        'calculated_total': calculated_total,
        'reported_total': reported_total,
        'holdings_count': len(holdings_df),
        'discrepancy': reported_total - calculated_total if reported_total else None,
        'discrepancy_percentage': (reported_total - calculated_total) / reported_total * 100 if reported_total else None
    }
    
    with open(os.path.join(output_dir, 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nResults saved to {output_dir} directory")
    
    # Try to extract the correct total from the text
    try:
        with open('messos.txt', 'r', encoding='utf-8') as f:
            text = f.read()
            
            # Look for patterns like "Total: $19,510,599" or similar
            total_patterns = [
                r'Total\s*:?\s*\$?\s*([\d,]+\.?\d*)',
                r'Total\s*Value\s*:?\s*\$?\s*([\d,]+\.?\d*)',
                r'Portfolio\s*Value\s*:?\s*\$?\s*([\d,]+\.?\d*)',
                r'Total\s*Portfolio\s*:?\s*\$?\s*([\d,]+\.?\d*)',
                r'Total\s*Portfolio\s*Value\s*:?\s*\$?\s*([\d,]+\.?\d*)',
                r'Value\s*:?\s*\$?\s*([\d,]+\.?\d*)',
                r'\$\s*([\d,]+\.?\d*)\s*Total',
                r'\$\s*([\d,]+\.?\d*)'
            ]
            
            potential_totals = []
            for pattern in total_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    try:
                        value = float(match.replace(',', ''))
                        if value > 1000000:  # Only consider values over 1 million
                            potential_totals.append(value)
                    except ValueError:
                        pass
            
            if potential_totals:
                # Sort by value (descending)
                potential_totals.sort(reverse=True)
                print("\nPotential portfolio totals found in text:")
                for i, total in enumerate(potential_totals[:5]):
                    print(f"{i+1}. ${total:,.2f}")
    except Exception as e:
        print(f"Error analyzing text file: {str(e)}")
    
    return 0

if __name__ == "__main__":
    main()
