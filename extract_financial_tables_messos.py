"""
Script to extract financial tables from the Messos PDF text.
"""
import os
import sys
import json
import re
from pathlib import Path

def extract_asset_allocation_table(text):
    """Extract the asset allocation table from the text."""
    # Look for the Asset Allocation section
    asset_allocation_pattern = r"Asset Allocation\s+Countervalue USD\s+Weight\s+(.*?)Total assets"
    match = re.search(asset_allocation_pattern, text, re.DOTALL)
    
    if not match:
        return None
    
    table_text = match.group(1)
    
    # Parse the table rows
    rows = []
    
    # Define patterns for different asset types
    patterns = [
        r"Liquidity\s+([\d',]+)\s+([\d.]+)%",
        r"Cash accounts\s+([\d',]+)\s+([\d.]+)%",
        r"Bonds\s+([\d',]+)\s+([\d.]+)%",
        r"Bonds\s+([\d',]+)\s+([\d.]+)%",
        r"Bond funds / certificates\s+([\d',]+)\s+([\d.]+)%",
        r"Equities\s+([\d',]+)\s+([\d.]+)%",
        r"Equities\s+([\d',]+)\s+([\d.]+)%",
        r"Equity funds/certificates\s+([\d',]+)\s+([\d.]+)%",
        r"Structured products\s+([\d',]+)\s+([\d.]+)%",
        r"Structured products \(Bonds\)\s+([\d',]+)\s+([\d.]+)%",
        r"Structured products \(Equities\)\s+([\d',]+)\s+([\d.]+)%",
        r"Other assets\s+([\d',]+)\s+([\d.]+)%",
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, table_text)
        for match in matches:
            asset_type = match.group(0).split()[0]
            if len(match.group(0).split()) > 1:
                asset_type = " ".join(match.group(0).split()[:-2])
            value = match.group(1).replace("'", "").replace(",", "")
            weight = match.group(2)
            
            rows.append({
                "Asset Type": asset_type,
                "Value (USD)": value,
                "Weight (%)": weight
            })
    
    return rows

def extract_summary_table(text):
    """Extract the summary table from the text."""
    # Look for the Summary section
    summary_pattern = r"Summary\s+Countervalue USD\s+Weight in %\s+(.*?)Countervalue USD"
    match = re.search(summary_pattern, text, re.DOTALL)
    
    if not match:
        return None
    
    table_text = match.group(1)
    
    # Parse the table rows
    rows = []
    
    # Define patterns for different asset types
    patterns = [
        r"Liquidity\s+([\d',]+)\s+([\d.]+)%",
        r"Bonds\s+([\d',]+)\s+([\d.]+)%",
        r"Equities\s+([\d',]+)\s+([\d.]+)%",
        r"Mixed funds\s+([\d',]+)\s+([\d.]+)%",
        r"Structured products\s+([\d',]+)\s+([\d.]+)%",
        r"Precious metals\s+([\d',]+)\s+([\d.]+)%",
        r"Real Estate\s+([\d',]+)\s+([\d.]+)%",
        r"Other assets\s+([\d',]+)\s+([\d.]+)%",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, table_text)
        if match:
            asset_type = match.group(0).split()[0]
            if len(match.group(0).split()) > 1:
                asset_type = " ".join(match.group(0).split()[:-2])
            value = match.group(1).replace("'", "").replace(",", "")
            weight = match.group(2)
            
            rows.append({
                "Asset Type": asset_type,
                "Value (USD)": value,
                "Weight (%)": weight
            })
    
    return rows

def extract_bonds_table(text):
    """Extract the bonds table from the text."""
    # Look for the Bonds section
    bonds_pattern = r"Bonds\s+Bonds, Bond funds, Convertible bonds, Interest options\s+(.*?)Total Bonds"
    match = re.search(bonds_pattern, text, re.DOTALL)
    
    if not match:
        return None
    
    table_text = match.group(1)
    
    # Parse the table rows
    rows = []
    
    # Define pattern for bond entries
    bond_pattern = r"([A-Z]+)\s+([\d',]+)\s+(.*?)\s+ISIN: ([A-Z0-9]+)"
    matches = re.finditer(bond_pattern, table_text)
    
    for match in matches:
        currency = match.group(1)
        nominal = match.group(2).replace("'", "").replace(",", "")
        description = match.group(3).strip()
        isin = match.group(4)
        
        # Try to extract price and value
        price_pattern = r"(\d+\.\d+)%"
        price_match = re.search(price_pattern, table_text[match.end():match.end()+200])
        price = price_match.group(1) if price_match else "N/A"
        
        value_pattern = r"([\d',]+)\s+(\d+\.\d+)%"
        value_match = re.search(value_pattern, table_text[match.end():match.end()+200])
        value = value_match.group(1).replace("'", "").replace(",", "") if value_match else "N/A"
        weight = value_match.group(2) if value_match else "N/A"
        
        rows.append({
            "Currency": currency,
            "Nominal": nominal,
            "Description": description,
            "ISIN": isin,
            "Price": price,
            "Value (USD)": value,
            "Weight (%)": weight
        })
    
    return rows

def extract_equities_table(text):
    """Extract the equities table from the text."""
    # Look for the Equities section
    equities_pattern = r"Equities\s+Equities, Equity funds, Options on equities/indices\s+(.*?)Total Equities"
    match = re.search(equities_pattern, text, re.DOTALL)
    
    if not match:
        return None
    
    table_text = match.group(1)
    
    # Parse the table rows
    rows = []
    
    # Define pattern for equity entries
    equity_pattern = r"([A-Z]+)\s+([\d',]+)\s+(.*?)\s+ISIN: ([A-Z0-9]+)"
    matches = re.finditer(equity_pattern, table_text)
    
    for match in matches:
        currency = match.group(1)
        quantity = match.group(2).replace("'", "").replace(",", "")
        description = match.group(3).strip()
        isin = match.group(4)
        
        # Try to extract price and value
        price_pattern = r"(\d+\.\d+)"
        price_match = re.search(price_pattern, table_text[match.end():match.end()+200])
        price = price_match.group(1) if price_match else "N/A"
        
        value_pattern = r"([\d',]+)\s+(\d+\.\d+)%"
        value_match = re.search(value_pattern, table_text[match.end():match.end()+200])
        value = value_match.group(1).replace("'", "").replace(",", "") if value_match else "N/A"
        weight = value_match.group(2) if value_match else "N/A"
        
        rows.append({
            "Currency": currency,
            "Quantity": quantity,
            "Description": description,
            "ISIN": isin,
            "Price": price,
            "Value (USD)": value,
            "Weight (%)": weight
        })
    
    return rows

def extract_structured_products_table(text):
    """Extract the structured products table from the text."""
    # Look for the Structured products section
    structured_pattern = r"Structured products\s+Structured products \(Bonds\)\s+(.*?)Total Structured products"
    match = re.search(structured_pattern, text, re.DOTALL)
    
    if not match:
        return None
    
    table_text = match.group(1)
    
    # Parse the table rows
    rows = []
    
    # Define pattern for structured product entries
    product_pattern = r"([A-Z]+)\s+([\d',]+)\s+(.*?)\s+ISIN: ([A-Z0-9]+)"
    matches = re.finditer(product_pattern, table_text)
    
    for match in matches:
        currency = match.group(1)
        nominal = match.group(2).replace("'", "").replace(",", "")
        description = match.group(3).strip()
        isin = match.group(4)
        
        # Try to extract price and value
        price_pattern = r"(\d+\.\d+)%"
        price_match = re.search(price_pattern, table_text[match.end():match.end()+200])
        price = price_match.group(1) if price_match else "N/A"
        
        value_pattern = r"([\d',]+)\s+(\d+\.\d+)%"
        value_match = re.search(value_pattern, table_text[match.end():match.end()+200])
        value = value_match.group(1).replace("'", "").replace(",", "") if value_match else "N/A"
        weight = value_match.group(2) if value_match else "N/A"
        
        rows.append({
            "Currency": currency,
            "Nominal": nominal,
            "Description": description,
            "ISIN": isin,
            "Price": price,
            "Value (USD)": value,
            "Weight (%)": weight
        })
    
    return rows

def extract_tables_from_text(text_file):
    """Extract financial tables from the text file."""
    # Read the text file
    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Extract tables
    tables = {
        "summary": extract_summary_table(text),
        "asset_allocation": extract_asset_allocation_table(text),
        "bonds": extract_bonds_table(text),
        "equities": extract_equities_table(text),
        "structured_products": extract_structured_products_table(text)
    }
    
    # Create output directory
    output_dir = Path("./messos_results")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Save the extracted tables
    tables_path = output_dir / "extracted_tables.json"
    with open(tables_path, "w", encoding="utf-8") as f:
        json.dump(tables, f, indent=2)
    
    print(f"Saved extracted tables to {tables_path}")
    
    # Print summary of extracted tables
    print("\nExtracted Tables Summary:")
    for table_name, table_data in tables.items():
        if table_data:
            print(f"- {table_name.capitalize()}: {len(table_data)} rows")
        else:
            print(f"- {table_name.capitalize()}: No data extracted")
    
    return tables

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_financial_tables_messos.py <text_file>")
        sys.exit(1)
    
    text_file = sys.argv[1]
    extract_tables_from_text(text_file)
