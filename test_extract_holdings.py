"""
Test script to extract holdings from messos.pdf and analyze the results.
"""
import os
import json
import argparse
import requests
from multi_document_processor import MultiDocumentProcessor

def analyze_with_openrouter(result, api_key):
    """Analyze the extracted data with OpenRouter API."""
    if not api_key:
        print("No API key provided. Skipping OpenRouter analysis.")
        return None

    print("\nAnalyzing with OpenRouter API...")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/aviadkim/backv2",
        "X-Title": "Financial Document Analysis",
        "Content-Type": "application/json"
    }

    prompt = f"""
    You are a financial document analysis expert. I need you to analyze the following financial document data and provide a comprehensive understanding of the document.

    EXTRACTED DATA:
    {json.dumps(result, indent=2)}

    Please provide a comprehensive analysis of this financial document, including:

    1. Client Information: Who is the client? What is their client number?
    2. Document Date: When was this document created?
    3. Portfolio Value: What is the total portfolio value?
    4. Securities: How many securities are in the portfolio? What are they?
    5. Asset Allocation: What is the asset allocation of the portfolio?
    6. Structured Products: What is the total value of structured products? What is the value of security with ISIN CH1259344831?
    7. Top Holdings: What are the top 5 holdings by value?
    8. Missing Information: What information is missing or incomplete in the extracted data?

    Your analysis should be detailed and comprehensive, explaining what you can determine from the data and what might be missing.
    """

    data = {
        "model": "anthropic/claude-3-opus",
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

        # Save analysis
        with open("test_output/openrouter_analysis.txt", "w", encoding="utf-8") as f:
            f.write(analysis)

        print("Analysis saved to test_output/openrouter_analysis.txt")
        return analysis

    except Exception as e:
        print(f"Error calling OpenRouter API: {e}")
        return None

def main():
    """Main function to extract and analyze holdings."""
    parser = argparse.ArgumentParser(description="Extract and analyze holdings from messos.pdf")
    parser.add_argument("--api-key", help="OpenRouter API key")
    args = parser.parse_args()

    print("Starting extraction test on messos.pdf...")

    # Create output directory if it doesn't exist
    os.makedirs("test_output", exist_ok=True)

    # Process the PDF file using MultiDocumentProcessor
    processor = MultiDocumentProcessor()
    processor.add_document("messos.pdf")
    doc_id = "messos.pdf"
    result = processor.get_document_data(doc_id)

    # Save the raw extraction results
    with open("test_output/messos_extraction.json", "w", encoding="utf-8") as f:
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

    with open("test_output/messos_holdings.json", "w", encoding="utf-8") as f:
        json.dump(holdings_data, f, indent=2)

    # Analyze with OpenRouter API if API key is provided
    if args.api_key:
        print("\nAnalyzing with OpenRouter API...")
        analysis = analyze_with_openrouter(result, args.api_key)
        if analysis:
            print("\nOpenRouter Analysis:")
            print("-" * 80)
            print(analysis[:1000] + "..." if len(analysis) > 1000 else analysis)
            print("-" * 80)

    print("\nExtraction test completed. Results saved to test_output directory.")

if __name__ == "__main__":
    main()
