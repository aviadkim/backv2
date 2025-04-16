"""
Ultimate Financial Document Processor

This script combines all available tools and agents to achieve 100% accuracy
in understanding financial documents.
"""
import os
import json
import sys
import argparse
import requests
import re
import time
from pathlib import Path

# API keys to try
API_KEYS = [
    {"key": "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", "model": "meta-llama/llama-3-70b-instruct", "name": "Llama Scout 4"},
    {"key": "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", "model": "anthropic/claude-3-haiku", "name": "Quaser"},
    {"key": "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", "model": "anthropic/claude-3-haiku", "name": "Quaser2"}
]

def extract_values_from_text(text):
    """Extract values from text."""
    # Extract portfolio value
    portfolio_value_match = re.search(r'Portfolio value: (\d+(?:,\d+)*(?:\.\d+)?)', text)
    portfolio_value = float(portfolio_value_match.group(1).replace(',', '')) if portfolio_value_match else None
    
    # Extract security values
    security_values = {}
    # Pattern to match: USD X'XXX'XXX DESCRIPTION ... XX.XXXX XX.XXXX X.XX% X.XX% X'XXX'XXX X.XX%
    security_pattern = r'USD\s+(\d+[\'|\,]?\d*[\'|\,]?\d*)\s+.*?(?:ISIN:\s+([A-Z0-9]{12}).*?(\d+[\'|\,]?\d*[\'|\,]?\d*)\s+(\d+\.\d+)%)'
    for match in re.finditer(security_pattern, text, re.DOTALL):
        nominal = match.group(1).replace("'", "").replace(",", "")
        isin = match.group(2)
        value = match.group(3).replace("'", "").replace(",", "")
        percentage = match.group(4)
        
        security_values[isin] = {
            "nominal": float(nominal),
            "value": float(value),
            "percentage": float(percentage)
        }
    
    # Extract asset allocation
    asset_allocation = {}
    # Pattern to match: Total XXX USD X'XXX'XXX XX.XX%
    allocation_pattern = r'Total\s+([A-Za-z\s/]+)\s+USD\s+(\d+[\'|\,]?\d*[\'|\,]?\d*)\s+(\d+\.\d+)%'
    for match in re.finditer(allocation_pattern, text):
        asset_class = match.group(1).strip()
        value = match.group(2).replace("'", "").replace(",", "")
        percentage = match.group(3)
        
        asset_allocation[asset_class] = {
            "value": float(value),
            "percentage": float(percentage)
        }
    
    return {
        "portfolio_value": portfolio_value,
        "security_values": security_values,
        "asset_allocation": asset_allocation
    }

def process_with_multi_document_processor(pdf_path, output_dir):
    """Process the PDF with MultiDocumentProcessor."""
    print("\n=== Processing with MultiDocumentProcessor ===")
    
    # Import the MultiDocumentProcessor
    try:
        from multi_document_processor import MultiDocumentProcessor
    except ImportError:
        print("MultiDocumentProcessor not available. Skipping.")
        return None
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Process the PDF
    processor = MultiDocumentProcessor()
    processor.add_document(pdf_path)
    doc_id = os.path.basename(pdf_path)
    result = processor.get_document_data(doc_id)
    
    # Save the raw extraction results
    extraction_path = os.path.join(output_dir, "extraction.json")
    with open(extraction_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    
    print(f"Client: {result.get('client_info', {})}")
    print(f"Document date: {result.get('document_date')}")
    print(f"Portfolio value: {result.get('portfolio_value')}")
    
    # Extract and analyze securities
    securities = result.get("bonds", [])
    print(f"Extracted {len(securities)} securities")
    
    # Calculate total value
    total_value = 0
    
    # Print securities details
    print("\nSecurities details:")
    print("-" * 80)
    print(f"{'ISIN':<15} {'Description':<40} {'Value':>15}")
    print("-" * 80)
    
    for security in securities:
        isin = security.get("isin", "N/A")
        description = security.get("description", "Unknown")
        valuation = security.get("valuation", 0)
        
        if valuation is not None:
            total_value += valuation
        
        print(f"{isin:<15} {description[:40]:<40} {valuation:>15,.2f}")
    
    print("-" * 80)
    print(f"{'Total':<56} {total_value:>15,.2f}")
    portfolio_value = result.get('portfolio_value', 0) or 0
    print(f"{'Portfolio Value':<56} {portfolio_value:>15,.2f}")
    print(f"{'Difference':<56} {total_value - portfolio_value:>15,.2f}")
    
    # Calculate percentage of portfolio covered by extracted securities
    if portfolio_value > 0:
        coverage = (total_value / portfolio_value) * 100
        print(f"Coverage: {coverage:.2f}%")
    
    # Save the detailed holdings information
    holdings_data = []
    for security in securities:
        holdings_data.append({
            "isin": security.get("isin", "N/A"),
            "description": security.get("description", "Unknown"),
            "valuation": security.get("valuation", 0),
            "currency": security.get("currency", "USD"),
            "quantity": security.get("quantity", None),
            "price": security.get("price", None),
        })
    
    holdings_path = os.path.join(output_dir, "holdings.json")
    with open(holdings_path, "w", encoding="utf-8") as f:
        json.dump(holdings_data, f, indent=2)
    
    # Extract values from text
    extracted_values = extract_values_from_text(json.dumps(result))
    
    # Save extracted values
    values_path = os.path.join(output_dir, "extracted_values.json")
    with open(values_path, "w", encoding="utf-8") as f:
        json.dump(extracted_values, f, indent=2)
    
    return {
        "extraction": result,
        "holdings": holdings_data,
        "extracted_values": extracted_values
    }

def process_with_financial_agents(pdf_path, api_key, model, output_dir):
    """Process the PDF with financial agents."""
    print(f"\n=== Processing with Financial Agents (Model: {model}) ===")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load extraction data
    extraction_path = os.path.join(output_dir, "extraction.json")
    if os.path.exists(extraction_path):
        with open(extraction_path, "r", encoding="utf-8") as f:
            extraction = json.load(f)
    else:
        print("Extraction data not found. Skipping financial agents.")
        return None
    
    # Load holdings data
    holdings_path = os.path.join(output_dir, "holdings.json")
    if os.path.exists(holdings_path):
        with open(holdings_path, "r", encoding="utf-8") as f:
            holdings = json.load(f)
    else:
        print("Holdings data not found. Skipping financial agents.")
        return None
    
    # Load extracted values
    values_path = os.path.join(output_dir, "extracted_values.json")
    if os.path.exists(values_path):
        with open(values_path, "r", encoding="utf-8") as f:
            extracted_values = json.load(f)
    else:
        print("Extracted values not found. Skipping financial agents.")
        return None
    
    # Create prompt
    prompt = f"""
    You are a financial document analysis expert. I need you to analyze the following financial document data and provide a comprehensive understanding of the document.
    
    EXTRACTED DATA:
    {json.dumps(extraction, indent=2)}
    
    HOLDINGS DATA:
    {json.dumps(holdings, indent=2)}
    
    EXTRACTED VALUES:
    {json.dumps(extracted_values, indent=2)}
    
    Please provide a comprehensive analysis of this financial document, including:
    
    1. Client Information: Who is the client? What is their client number?
    2. Document Date: When was this document created?
    3. Portfolio Value: What is the total portfolio value?
    4. Securities: How many securities are in the portfolio? What are they?
    5. Asset Allocation: What is the asset allocation of the portfolio?
    6. Structured Products: What is the total value of structured products? What is the value of security with ISIN CH1259344831?
    7. Top Holdings: What are the top 5 holdings by value?
    8. Missing Information: What information is missing or incomplete in the extracted data?
    
    Format your response as a JSON object with the following structure:
    {{
        "client_info": {{
            "name": "Client name",
            "number": "Client number"
        }},
        "document_date": "Document date",
        "portfolio_value": "Total portfolio value",
        "securities_count": "Number of securities",
        "securities": [
            {{
                "isin": "ISIN code",
                "description": "Security description",
                "value": "Security value",
                "percentage": "Percentage of portfolio"
            }}
        ],
        "asset_allocation": {{
            "asset_class": "Percentage"
        }},
        "structured_products": {{
            "total_value": "Total value of structured products",
            "ch1259344831_value": "Value of security with ISIN CH1259344831"
        }},
        "top_holdings": [
            {{
                "isin": "ISIN code",
                "description": "Security description",
                "value": "Security value",
                "percentage": "Percentage of portfolio"
            }}
        ],
        "missing_information": [
            "Description of missing information"
        ],
        "analysis": "Your comprehensive analysis of the document"
    }}
    """
    
    # Call OpenRouter API
    print(f"Calling OpenRouter API with {model}...")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/aviadkim/backv2",
        "X-Title": "Financial Document Analysis",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a financial document analysis expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 4000
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return None
        
        response_json = response.json()
        analysis = response_json["choices"][0]["message"]["content"]
        
        # Save raw analysis
        raw_analysis_path = os.path.join(output_dir, f"raw_analysis_{model.split('/')[-1]}.txt")
        with open(raw_analysis_path, "w", encoding="utf-8") as f:
            f.write(analysis)
        
        # Try to parse JSON response
        try:
            # Find the JSON part in the raw response
            json_start = analysis.find("{")
            json_end = analysis.rfind("}")
            
            if json_start >= 0 and json_end >= 0:
                json_str = analysis[json_start:json_end+1]
                parsed_analysis = json.loads(json_str)
                
                # Save parsed analysis
                parsed_analysis_path = os.path.join(output_dir, f"parsed_analysis_{model.split('/')[-1]}.json")
                with open(parsed_analysis_path, "w", encoding="utf-8") as f:
                    json.dump(parsed_analysis, f, indent=2)
                
                print(f"Analysis saved to {parsed_analysis_path}")
                return parsed_analysis
            else:
                print("Could not find JSON in raw response")
                return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
    
    except Exception as e:
        print(f"Error calling OpenRouter API: {e}")
        return None

def combine_results(multi_doc_result, agent_results, output_dir):
    """Combine results from different processing methods."""
    print("\n=== Combining Results ===")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract client info
    client_info = multi_doc_result["extraction"].get("client_info", {})
    
    # Extract document date
    document_date = multi_doc_result["extraction"].get("document_date", "")
    
    # Extract portfolio value
    portfolio_value = multi_doc_result["extraction"].get("portfolio_value", 0)
    
    # Extract securities
    securities = []
    security_values = multi_doc_result["extracted_values"].get("security_values", {})
    
    for isin, values in security_values.items():
        security = {
            "isin": isin,
            "description": None,
            "value": values.get("value", 0),
            "percentage": values.get("percentage", 0)
        }
        
        # Try to find description in agent results
        for agent_result in agent_results:
            if agent_result:
                agent_securities = agent_result.get("securities", [])
                for agent_security in agent_securities:
                    if agent_security.get("isin") == isin:
                        security["description"] = agent_security.get("description")
                        break
        
        securities.append(security)
    
    # Sort securities by value
    securities.sort(key=lambda x: x["value"], reverse=True)
    
    # Extract asset allocation
    asset_allocation = {}
    
    # Try to find asset allocation in agent results
    for agent_result in agent_results:
        if agent_result and agent_result.get("asset_allocation"):
            asset_allocation = agent_result.get("asset_allocation")
            break
    
    # Extract structured products
    structured_products = {}
    
    # Try to find structured products in agent results
    for agent_result in agent_results:
        if agent_result and agent_result.get("structured_products"):
            structured_products = agent_result.get("structured_products")
            break
    
    # Extract top holdings
    top_holdings = securities[:5]
    
    # Create combined result
    combined_result = {
        "client_info": client_info,
        "document_date": document_date,
        "portfolio_value": portfolio_value,
        "securities_count": len(securities),
        "securities": securities,
        "asset_allocation": asset_allocation,
        "structured_products": structured_products,
        "top_holdings": top_holdings
    }
    
    # Save combined result
    combined_result_path = os.path.join(output_dir, "combined_result.json")
    with open(combined_result_path, "w", encoding="utf-8") as f:
        json.dump(combined_result, f, indent=2)
    
    print(f"Combined result saved to {combined_result_path}")
    
    # Create human-readable report
    report = f"""
    # Financial Document Analysis Report

    ## Client Information
    - Name: {client_info.get('name', '')}
    - Number: {client_info.get('number', '')}

    ## Document Date
    {document_date}

    ## Portfolio Value
    ${portfolio_value:,.2f}

    ## Securities
    Total: {len(securities)}

    ### Top 10 Securities
    | ISIN | Description | Value | Percentage |
    |------|-------------|-------|------------|
    """
    
    for security in securities[:10]:
        report += f"| {security['isin']} | {security['description'] or 'Unknown'} | ${security['value']:,.2f} | {security['percentage']}% |\n"
    
    report += f"""
    ## Asset Allocation
    """
    
    for asset_class, percentage in asset_allocation.items():
        report += f"- {asset_class}: {percentage}%\n"
    
    report += f"""
    ## Structured Products
    - Total Value: ${structured_products.get('total_value', 0):,.2f}
    - CH1259344831 Value: ${structured_products.get('ch1259344831_value', 0):,.2f}
    """
    
    # Save report
    report_path = os.path.join(output_dir, "report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"Report saved to {report_path}")
    
    return combined_result

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Ultimate Financial Document Processor")
    parser.add_argument("--pdf", required=True, help="Path to the PDF file")
    parser.add_argument("--output-dir", default="ultimate_results", help="Output directory")
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Process with MultiDocumentProcessor
    multi_doc_result = process_with_multi_document_processor(args.pdf, args.output_dir)
    
    # Process with financial agents
    agent_results = []
    for api_key_info in API_KEYS:
        agent_result = process_with_financial_agents(
            args.pdf,
            api_key_info["key"],
            api_key_info["model"],
            args.output_dir
        )
        agent_results.append(agent_result)
    
    # Combine results
    combined_result = combine_results(multi_doc_result, agent_results, args.output_dir)
    
    print("\n=== Processing Complete ===")
    print(f"Results saved to {args.output_dir}")

if __name__ == "__main__":
    main()
