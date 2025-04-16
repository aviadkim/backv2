"""
Extract portfolio data from the PDF text.
"""
import os
import re
import json
import pandas as pd

def extract_portfolio_data():
    """Extract portfolio data from the PDF text."""
    # Try to read the extracted text
    try:
        with open('messos.txt', 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading text file: {str(e)}")
        return
    
    print(f"Extracted text length: {len(text)} characters")
    
    # Look for the portfolio value
    portfolio_value = None
    
    # Try to find the specific value 19,510,599
    target_value = "19,510,599"
    if target_value in text:
        portfolio_value = 19510599
        print(f"Found target portfolio value: ${portfolio_value:,}")
        
        # Find the context
        context_pattern = r'.{0,50}19,510,599.{0,50}'
        context_matches = re.findall(context_pattern, text)
        
        if context_matches:
            print(f"Context: {context_matches[0].strip()}")
    else:
        print(f"Target value {target_value} not found in text")
    
    # Extract securities data
    print("\nExtracting securities data...")
    
    # Look for sections that might contain securities data
    securities_sections = []
    
    # Common section headers
    section_headers = [
        "Securities", "Portfolio", "Holdings", "Assets", "Investments",
        "Bonds", "Stocks", "Equities", "Fixed Income", "Securities Portfolio"
    ]
    
    for header in section_headers:
        pattern = f"{header}.*?(?=\\n\\n|$)"
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        securities_sections.extend(matches)
    
    # Extract ISIN numbers and associated data
    securities = []
    isin_pattern = r'([A-Z]{2}[A-Z0-9]{9}[0-9])'
    
    for section in securities_sections:
        isin_matches = re.findall(isin_pattern, section)
        
        for isin in isin_matches:
            # Find context around this ISIN
            context_pattern = r'.{0,200}' + isin + r'.{0,200}'
            context_matches = re.findall(context_pattern, section)
            
            if context_matches:
                context = context_matches[0]
                
                # Extract potential quantity, price, and value
                quantity = None
                price = None
                value = None
                
                # Look for numeric values
                value_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'
                value_matches = re.findall(value_pattern, context)
                
                numeric_values = []
                for val_match in value_matches:
                    try:
                        numeric_value = float(val_match.replace(',', ''))
                        numeric_values.append(numeric_value)
                    except ValueError:
                        pass
                
                # Sort by magnitude
                numeric_values.sort()
                
                # Assign based on magnitude (value is usually the largest)
                if len(numeric_values) >= 3:
                    quantity = numeric_values[-3]
                    price = numeric_values[-2]
                    value = numeric_values[-1]
                elif len(numeric_values) == 2:
                    price = numeric_values[0]
                    value = numeric_values[1]
                elif len(numeric_values) == 1:
                    value = numeric_values[0]
                
                # Extract security name
                name = None
                name_pattern = r'([A-Za-z0-9\s\.\-\&]+)(?=\s+' + isin + ')'
                name_matches = re.findall(name_pattern, context)
                
                if name_matches:
                    name = name_matches[0].strip()
                
                securities.append({
                    'isin': isin,
                    'name': name,
                    'quantity': quantity,
                    'price': price,
                    'value': value,
                    'context': context.strip()
                })
    
    # Remove duplicates based on ISIN
    unique_securities = {}
    for security in securities:
        isin = security['isin']
        if isin not in unique_securities or (security['value'] is not None and unique_securities[isin]['value'] is None):
            unique_securities[isin] = security
    
    securities = list(unique_securities.values())
    
    # Calculate total value
    total_value = sum(security['value'] for security in securities if security['value'] is not None)
    
    print(f"Found {len(securities)} unique securities")
    print(f"Calculated total value: ${total_value:,.2f}")
    
    if portfolio_value:
        discrepancy = portfolio_value - total_value
        print(f"Discrepancy from reported value: ${discrepancy:,.2f} ({discrepancy/portfolio_value*100:.2f}%)")
    
    # Create a DataFrame for better display
    df = pd.DataFrame(securities)
    
    # Reorder and select columns
    columns = ['isin', 'name', 'quantity', 'price', 'value']
    if not df.empty:
        df = df[columns]
    
    # Save results
    output_dir = 'portfolio_data'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save to CSV
    df.to_csv(os.path.join(output_dir, 'securities.csv'), index=False)
    
    # Save to JSON
    with open(os.path.join(output_dir, 'securities.json'), 'w', encoding='utf-8') as f:
        json.dump(securities, f, indent=2)
    
    # Save summary
    summary = {
        'total_securities': len(securities),
        'calculated_total_value': total_value,
        'reported_portfolio_value': portfolio_value,
        'discrepancy': portfolio_value - total_value if portfolio_value else None,
        'discrepancy_percentage': (portfolio_value - total_value) / portfolio_value * 100 if portfolio_value else None
    }
    
    with open(os.path.join(output_dir, 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nResults saved to {output_dir} directory")
    
    # Try a different approach - look for lines with dollar amounts
    print("\nLooking for lines with dollar amounts...")
    
    dollar_pattern = r'.*\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?).*'
    dollar_matches = re.findall(dollar_pattern, text)
    
    dollar_values = []
    for match in dollar_matches:
        try:
            value = float(match.replace(',', ''))
            if value > 10000:  # Only consider values over 10,000
                dollar_values.append(value)
        except ValueError:
            pass
    
    # Sort by value (descending)
    dollar_values.sort(reverse=True)
    
    print(f"Found {len(dollar_values)} dollar values over $10,000")
    print("\nTop 10 dollar values:")
    for i, value in enumerate(dollar_values[:10]):
        print(f"{i+1}. ${value:,.2f}")
    
    # Look for the specific value 19,510,599
    if 19510599 in dollar_values:
        print("\nFound the exact portfolio value $19,510,599 in dollar values")
    
    # Try to find values that sum to approximately 19,510,599
    target_sum = 19510599
    tolerance = 0.05  # 5% tolerance
    
    # Try combinations of the top values
    top_values = dollar_values[:20]  # Use top 20 values
    
    best_combination = None
    best_diff = float('inf')
    
    # Try single values
    for val in top_values:
        diff = abs(val - target_sum)
        if diff < best_diff:
            best_diff = diff
            best_combination = [val]
    
    # Try pairs of values
    for i, val1 in enumerate(top_values):
        for val2 in top_values[i+1:]:
            total = val1 + val2
            diff = abs(total - target_sum)
            if diff < best_diff:
                best_diff = diff
                best_combination = [val1, val2]
    
    # Check if we found a good match
    if best_combination and best_diff / target_sum <= tolerance:
        total = sum(best_combination)
        print(f"\nFound combination that sums to approximately ${target_sum:,.2f}:")
        for i, val in enumerate(best_combination):
            print(f"{i+1}. ${val:,.2f}")
        print(f"Total: ${total:,.2f}")
        print(f"Difference: ${best_diff:,.2f} ({best_diff/target_sum*100:.2f}%)")
    
    return securities, portfolio_value

def main():
    """Main function."""
    extract_portfolio_data()
    
    return 0

if __name__ == "__main__":
    main()
