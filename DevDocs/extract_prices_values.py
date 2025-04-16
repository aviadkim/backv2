"""
Script to extract prices and values from the tables.
"""
import os
import sys
import json
import pandas as pd
from pathlib import Path

def load_tables(file_path):
    """Load tables from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_securities_from_tables(tables):
    """Extract securities from tables."""
    securities = []
    
    # Process each table
    for table in tables:
        # Skip tables that don't have the right structure
        if "data" not in table:
            continue
        
        # Check if this is a securities table
        is_securities_table = False
        for row in table["data"]:
            if "Currency Nominal/" in row and "Description" in row and "Actual Price" in row:
                is_securities_table = True
                break
        
        if not is_securities_table:
            continue
        
        # Process the securities table
        current_security = None
        
        for i, row in enumerate(table["data"]):
            # Skip header rows
            if i < 2:
                continue
            
            # Check if this is a new security
            if "Currency Nominal/" in row and row["Currency Nominal/"] and "USD" in row["Currency Nominal/"]:
                # Save the previous security
                if current_security:
                    securities.append(current_security)
                
                # Extract nominal/quantity
                nominal_parts = row["Currency Nominal/"].split()
                currency = nominal_parts[0] if len(nominal_parts) > 0 else ""
                nominal = nominal_parts[1] if len(nominal_parts) > 1 else ""
                
                # Create a new security
                current_security = {
                    "currency": currency,
                    "nominal": nominal.replace("'", "").replace(",", ""),
                    "description": row.get("Description", ""),
                    "price": "",
                    "value": "",
                    "weight": "",
                    "isin": ""
                }
            
            # Check if this is an ISIN row
            elif current_security and "Description" in row and row["Description"] and "ISIN:" in row["Description"]:
                # Extract ISIN
                isin_parts = row["Description"].split("ISIN:")
                if len(isin_parts) > 1:
                    isin_parts = isin_parts[1].strip().split()
                    if len(isin_parts) > 0:
                        current_security["isin"] = isin_parts[0]
            
            # Check if this is a price row
            elif current_security and "Actual Price" in row and row["Actual Price"] and row["Actual Price"] != "Price Date":
                current_security["price"] = row["Actual Price"].replace("'", "").replace(",", "")
            
            # Check if this is a value row
            elif current_security and "Valuation in price currency" in row and row["Valuation in price currency"] and "USD" not in row["Valuation in price currency"]:
                current_security["value"] = row["Valuation in price currency"].replace("'", "").replace(",", "")
            
            # Check if this is a weight row
            elif current_security and "in %" in row and row["in %"] and row["in %"] != "of assets":
                current_security["weight"] = row["in %"]
        
        # Save the last security
        if current_security:
            securities.append(current_security)
    
    return securities

def update_securities_csv(securities, csv_file):
    """Update securities CSV file with prices and values."""
    # Load the CSV file
    df = pd.read_csv(csv_file)
    
    # Create a dictionary of securities by ISIN
    securities_dict = {s["isin"]: s for s in securities if s["isin"]}
    
    # Update the DataFrame
    for i, row in df.iterrows():
        isin = row["isin"]
        if isin in securities_dict:
            # Update price
            if securities_dict[isin]["price"]:
                df.at[i, "price"] = securities_dict[isin]["price"]
            
            # Update value
            if securities_dict[isin]["value"]:
                df.at[i, "value"] = securities_dict[isin]["value"]
            
            # Update weight
            if securities_dict[isin]["weight"]:
                df.at[i, "weight"] = securities_dict[isin]["weight"]
    
    # Save the updated DataFrame
    df.to_csv(csv_file, index=False)
    
    return df

def main():
    """Main function to extract prices and values."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract prices and values from tables")
    parser.add_argument("--tables-file", default="./enhanced_results/extracted_tables_tabula.json", help="Path to the tables JSON file")
    parser.add_argument("--securities-file", default="./test_results/isin_analysis/securities_table.csv", help="Path to the securities CSV file")
    parser.add_argument("--output-dir", default="./updated_results", help="Output directory")
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Load tables
    tables = load_tables(args.tables_file)
    
    # Extract securities
    securities = extract_securities_from_tables(tables)
    
    # Save the extracted securities
    securities_path = output_dir / "extracted_securities.json"
    with open(securities_path, "w", encoding="utf-8") as f:
        json.dump(securities, f, indent=2)
    print(f"Saved extracted securities to {securities_path}")
    
    # Update securities CSV
    updated_df = update_securities_csv(securities, args.securities_file)
    
    # Save the updated securities CSV
    updated_csv_path = output_dir / "updated_securities.csv"
    updated_df.to_csv(updated_csv_path, index=False)
    print(f"Saved updated securities to {updated_csv_path}")
    
    # Print summary
    print("\nExtracted Securities Summary:")
    print(f"Total securities extracted: {len(securities)}")
    print(f"Securities with ISIN: {sum(1 for s in securities if s['isin'])}")
    print(f"Securities with price: {sum(1 for s in securities if s['price'])}")
    print(f"Securities with value: {sum(1 for s in securities if s['value'])}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
