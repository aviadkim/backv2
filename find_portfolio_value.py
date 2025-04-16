"""
Find the portfolio value in the extracted text.
"""
import os
import re
import json

def find_portfolio_value():
    """Find the portfolio value in the extracted text."""
    # Try to read the extracted text
    try:
        with open('messos.txt', 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading text file: {str(e)}")
        return
    
    print(f"Extracted text length: {len(text)} characters")
    
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
                    potential_totals.append((value, pattern))
            except ValueError:
                pass
    
    if potential_totals:
        # Sort by value (descending)
        potential_totals.sort(key=lambda x: x[0], reverse=True)
        print("\nPotential portfolio totals found in text:")
        for i, (total, pattern) in enumerate(potential_totals[:10]):
            print(f"{i+1}. ${total:,.2f} (matched pattern: {pattern})")
            
            # Find the context around this value
            value_str = f"{total:,.0f}".replace(',', ',?')
            context_pattern = r'.{0,50}' + value_str + r'.{0,50}'
            context_matches = re.findall(context_pattern, text)
            
            if context_matches:
                print(f"   Context: {context_matches[0].strip()}")
    else:
        print("No potential portfolio totals found in text")
    
    # Look for specific values
    target_value = 19510599
    target_str = f"{target_value:,}".replace(',', ',?')
    target_pattern = r'.{0,50}' + target_str + r'.{0,50}'
    target_matches = re.findall(target_pattern, text)
    
    if target_matches:
        print(f"\nFound target value ${target_value:,} in text:")
        for i, match in enumerate(target_matches):
            print(f"{i+1}. {match.strip()}")
    else:
        print(f"\nTarget value ${target_value:,} not found in text")
    
    # Look for securities with values
    print("\nLooking for securities with values...")
    
    # ISIN pattern
    isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
    isin_matches = re.findall(isin_pattern, text)
    
    securities = []
    for isin in isin_matches:
        # Find context around this ISIN
        context_pattern = r'.{0,100}' + isin + r'.{0,100}'
        context_matches = re.findall(context_pattern, text)
        
        if context_matches:
            context = context_matches[0]
            
            # Look for values in the context
            value_pattern = r'\$?\s*([\d,]+\.?\d*)'
            value_matches = re.findall(value_pattern, context)
            
            values = []
            for val_match in value_matches:
                try:
                    value = float(val_match.replace(',', ''))
                    if value > 100:  # Only consider values over 100
                        values.append(value)
                except ValueError:
                    pass
            
            if values:
                securities.append({
                    'isin': isin,
                    'context': context.strip(),
                    'values': values
                })
    
    if securities:
        print(f"Found {len(securities)} securities with values")
        
        # Calculate total of the largest values
        total = sum(max(sec['values']) for sec in securities if sec['values'])
        print(f"Sum of largest values: ${total:,.2f}")
        
        # Save to JSON
        output_dir = 'text_analysis'
        os.makedirs(output_dir, exist_ok=True)
        
        with open(os.path.join(output_dir, 'securities.json'), 'w', encoding='utf-8') as f:
            json.dump(securities, f, indent=2)
        
        print(f"Securities saved to {os.path.join(output_dir, 'securities.json')}")
    else:
        print("No securities with values found")
    
    # Save a sample of the text
    output_dir = 'text_analysis'
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, 'text_sample.txt'), 'w', encoding='utf-8') as f:
        f.write(text[:10000])  # Save first 10000 characters
    
    print(f"Text sample saved to {os.path.join(output_dir, 'text_sample.txt')}")

def main():
    """Main function."""
    find_portfolio_value()
    
    return 0

if __name__ == "__main__":
    main()
