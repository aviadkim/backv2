"""
Examine extracted tables from the PDF.
"""
import os
import json
import pandas as pd
import re

def load_tables():
    """Load extracted tables from the enhanced results."""
    tables_path = os.path.join('enhanced_results', 'extracted_tables_tabula.json')
    
    if os.path.exists(tables_path):
        with open(tables_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return []

def examine_tables():
    """Examine the extracted tables."""
    tables = load_tables()
    
    print(f"Found {len(tables)} tables in the PDF")
    
    # Create a directory for table outputs
    output_dir = 'table_analysis'
    os.makedirs(output_dir, exist_ok=True)
    
    # Examine each table
    for i, table in enumerate(tables):
        print(f"\nTable {i+1}:")
        
        # Convert to DataFrame
        df = pd.DataFrame(table['data'], columns=table.get('columns', []))
        
        # Print table info
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        
        # Print first few rows
        print("\nSample data:")
        print(df.head())
        
        # Save to CSV
        csv_path = os.path.join(output_dir, f'table_{i+1}.csv')
        df.to_csv(csv_path, index=False)
        print(f"Saved to {csv_path}")
        
        # Look for potential portfolio values
        potential_values = []
        for col in df.columns:
            for val in df[col]:
                if isinstance(val, str):
                    # Look for currency values
                    matches = re.findall(r'\$?\s*([\d,]+\.?\d*)', val)
                    for match in matches:
                        try:
                            value = float(match.replace(',', ''))
                            if value > 1000000:  # Only consider values over 1 million
                                potential_values.append(value)
                        except ValueError:
                            pass
        
        if potential_values:
            print("\nPotential portfolio values found in this table:")
            for val in sorted(potential_values, reverse=True)[:5]:
                print(f"${val:,.2f}")
    
    # Look for tables with ISIN numbers
    print("\nSearching for tables with ISIN numbers...")
    for i, table in enumerate(tables):
        df = pd.DataFrame(table['data'], columns=table.get('columns', []))
        
        # Convert all values to strings for searching
        df_str = df.astype(str)
        
        # Look for ISIN pattern
        isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
        has_isin = False
        
        for col in df_str.columns:
            for val in df_str[col]:
                if re.search(isin_pattern, val):
                    has_isin = True
                    break
            if has_isin:
                break
        
        if has_isin:
            print(f"Table {i+1} contains ISIN numbers")
            
            # Save this table with a special name
            csv_path = os.path.join(output_dir, f'securities_table_{i+1}.csv')
            df.to_csv(csv_path, index=False)
            print(f"Saved to {csv_path}")
    
    # Look for the total portfolio value
    print("\nSearching for total portfolio value...")
    for i, table in enumerate(tables):
        df = pd.DataFrame(table['data'], columns=table.get('columns', []))
        
        # Convert all values to strings for searching
        df_str = df.astype(str)
        
        # Look for "total" or "portfolio value" text
        total_pattern = r'(?i)total|portfolio\s*value'
        has_total = False
        
        for col in df_str.columns:
            for val in df_str[col]:
                if re.search(total_pattern, val):
                    has_total = True
                    print(f"Found potential total in Table {i+1}, value: {val}")
                    
                    # Look for a value in the same row
                    row_idx = df_str[df_str[col] == val].index[0]
                    row = df.iloc[row_idx]
                    
                    for col_val in row:
                        if isinstance(col_val, str):
                            matches = re.findall(r'\$?\s*([\d,]+\.?\d*)', col_val)
                            for match in matches:
                                try:
                                    value = float(match.replace(',', ''))
                                    if value > 1000000:  # Only consider values over 1 million
                                        print(f"Potential portfolio value: ${value:,.2f}")
                                except ValueError:
                                    pass

def main():
    """Main function."""
    examine_tables()
    
    return 0

if __name__ == "__main__":
    main()
