"""
Analyze Messos PDF with direct API call to OpenRouter

This script uses a direct API call to OpenRouter to analyze the extracted data from the Messos PDF
and provide a comprehensive understanding of the document.
"""
import os
import json
import sys
import argparse
from pathlib import Path
import requests

def analyze_with_openrouter(extracted_data_path, securities_path, api_key, output_path="openrouter_analysis.json"):
    """
    Analyze the extracted data with OpenRouter API.
    
    Args:
        extracted_data_path: Path to the extracted data JSON file
        securities_path: Path to the securities JSON file
        api_key: OpenRouter API key
        output_path: Output path for the analysis
    
    Returns:
        Dictionary with analysis results
    """
    # Load extracted data
    with open(extracted_data_path, "r", encoding="utf-8") as f:
        extracted_data = json.load(f)
    
    # Load securities data
    with open(securities_path, "r", encoding="utf-8") as f:
        securities_data = json.load(f)
    
    # Create prompt
    prompt = f"""
    You are a financial document analysis expert. I need you to analyze the following financial document data and provide a comprehensive understanding of the document.
    
    EXTRACTED DATA:
    {json.dumps(extracted_data, indent=2)}
    
    SECURITIES DATA:
    {json.dumps(securities_data, indent=2)}
    
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
    print("Calling OpenRouter API...")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/aviadkim/backv2",
        "X-Title": "Financial Document Analysis",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "anthropic/claude-3-opus",
        "messages": [
            {"role": "system", "content": "You are a financial document analysis expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 4000
    }
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    
    # Get response
    response_json = response.json()
    analysis = response_json["choices"][0]["message"]["content"]
    
    # Parse JSON response
    try:
        analysis_json = json.loads(analysis)
    except json.JSONDecodeError:
        print("Error parsing JSON response. Saving raw response.")
        analysis_json = {"raw_response": analysis}
    
    # Save analysis
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis_json, f, indent=2)
    
    print(f"Analysis saved to {output_path}")
    
    return analysis_json

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Analyze Messos PDF with OpenRouter API")
    parser.add_argument("--extracted-data", default="test_output/messos_extraction.json", help="Path to the extracted data JSON file")
    parser.add_argument("--securities", default="test_output/securities.json", help="Path to the securities JSON file")
    parser.add_argument("--api-key", required=True, help="OpenRouter API key")
    parser.add_argument("--output", default="openrouter_analysis.json", help="Output path for the analysis")
    args = parser.parse_args()
    
    analyze_with_openrouter(args.extracted_data, args.securities, args.api_key, args.output)

if __name__ == "__main__":
    main()
