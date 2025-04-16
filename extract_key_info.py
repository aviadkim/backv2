"""
Extract key information from the comprehensive analysis.
"""
import json
import re
import sys

def extract_key_info(input_path, output_path):
    """Extract key information from the analysis."""
    # Load the analysis
    with open(input_path, "r", encoding="utf-8") as f:
        analysis = json.load(f)
    
    # Extract the raw response
    raw_response = analysis.get("raw_response", "")
    
    # Extract client info
    client_name_match = re.search(r'"client_info":\s*{\s*"name":\s*"([^"]+)"', raw_response)
    client_number_match = re.search(r'"number":\s*"([^"]+)"', raw_response)
    
    client_info = {
        "name": client_name_match.group(1) if client_name_match else "",
        "number": client_number_match.group(1) if client_number_match else ""
    }
    
    # Extract document date
    document_date_match = re.search(r'"document_date":\s*"([^"]+)"', raw_response)
    document_date = document_date_match.group(1) if document_date_match else ""
    
    # Extract portfolio value
    portfolio_value_match = re.search(r'"portfolio_value":\s*([\d\.]+)', raw_response)
    portfolio_value = float(portfolio_value_match.group(1)) if portfolio_value_match else 0
    
    # Extract securities count
    securities_count_match = re.search(r'"securities_count":\s*(\d+)', raw_response)
    securities_count = int(securities_count_match.group(1)) if securities_count_match else 0
    
    # Extract asset allocation
    asset_allocation = {}
    asset_allocation_matches = re.finditer(r'"([^"]+)":\s*([\d\.]+)', raw_response[raw_response.find('"asset_allocation"'):raw_response.find('"structured_products"')])
    for match in asset_allocation_matches:
        if match.group(1) != "asset_allocation":
            asset_allocation[match.group(1)] = float(match.group(2))
    
    # Extract structured products
    structured_products_total_match = re.search(r'"total_value":\s*([\d\.]+)', raw_response)
    structured_products_ch1259344831_match = re.search(r'"ch1259344831_value":\s*([\d\.]+)', raw_response)
    
    structured_products = {
        "total_value": float(structured_products_total_match.group(1)) if structured_products_total_match else 0,
        "ch1259344831_value": float(structured_products_ch1259344831_match.group(1)) if structured_products_ch1259344831_match else 0
    }
    
    # Extract top holdings
    top_holdings = []
    top_holdings_section = raw_response[raw_response.find('"top_holdings"'):raw_response.find('"missing_information"')]
    top_holdings_matches = re.finditer(r'"isin":\s*"([^"]+)"[^}]*"value":\s*([\d\.]+)[^}]*"percentage":\s*([\d\.]+)', top_holdings_section)
    
    for match in top_holdings_matches:
        top_holdings.append({
            "isin": match.group(1),
            "value": float(match.group(2)),
            "percentage": float(match.group(3))
        })
    
    # Extract analysis
    analysis_section = raw_response[raw_response.find('"analysis"'):].strip()
    analysis_text = analysis_section[analysis_section.find('{') + 1:analysis_section.rfind('}')]
    
    # Format the key information
    key_info = {
        "client_info": client_info,
        "document_date": document_date,
        "portfolio_value": portfolio_value,
        "securities_count": securities_count,
        "asset_allocation": asset_allocation,
        "structured_products": structured_products,
        "top_holdings": top_holdings,
        "analysis_summary": analysis_text.strip()
    }
    
    # Save the key information
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(key_info, f, indent=2)
    
    print(f"Key information saved to {output_path}")
    return key_info

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_key_info.py <input_path> <output_path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    extract_key_info(input_path, output_path)
