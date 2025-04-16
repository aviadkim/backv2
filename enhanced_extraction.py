"""
Enhanced extraction script for financial documents using OCR with Poppler.
"""
import os
import json
import re
from multi_document_processor import MultiDocumentProcessor

def extract_securities_from_text(text):
    """Extract securities from text using pattern matching."""
    securities = []
    
    # Look for ISIN patterns
    isin_pattern = r'([A-Z]{2}[A-Z0-9]{9}[0-9])'
    isin_matches = re.finditer(isin_pattern, text)
    
    for match in isin_matches:
        isin = match.group(1)
        
        # Get context around the ISIN (500 characters before and after)
        start_pos = max(0, match.start() - 500)
        end_pos = min(len(text), match.end() + 500)
        context = text[start_pos:end_pos]
        
        # Try to extract description
        desc_pattern = r'([A-Z][A-Z0-9\s\.\-\(\)]{5,50})'
        desc_match = re.search(desc_pattern, context[:match.start() - start_pos])
        description = desc_match.group(1).strip() if desc_match else "Unknown"
        
        # Try to extract valuation
        valuation_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)(?:\s*(?:USD|EUR|GBP|CHF|JPY|$|€|£))?'
        valuation_matches = list(re.finditer(valuation_pattern, context[match.end() - start_pos:]))
        
        valuation = None
        if valuation_matches:
            # Take the first number after the ISIN as potential valuation
            valuation_str = valuation_matches[0].group(1)
            try:
                valuation = float(valuation_str.replace(',', ''))
            except ValueError:
                valuation = None
        
        # Create security object
        security = {
            "isin": isin,
            "description": description,
            "valuation": valuation
        }
        
        # Check if this security is already in the list
        if not any(s["isin"] == isin for s in securities):
            securities.append(security)
    
    return securities

def main():
    """Main function to extract and analyze holdings with enhanced methods."""
    print("Starting enhanced extraction on messos.pdf...")
    
    # Create output directory if it doesn't exist
    os.makedirs("enhanced_results", exist_ok=True)
    
    # Set up environment for Poppler
    poppler_path = os.path.join(os.getcwd(), "poppler", "Library", "bin")
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + poppler_path
    
    # Process the PDF file using MultiDocumentProcessor with OCR
    processor = MultiDocumentProcessor(use_ocr=True, ocr_lang="en")
    processor.add_document("messos.pdf", force_ocr=True)
    doc_id = "messos.pdf"
    result = processor.get_document_data(doc_id)
    
    # Save the raw extraction results
    with open("enhanced_results/messos_extraction.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    
    # Get the full text from the document
    full_text = result.get("full_text", "")
    
    # Save the full text
    with open("enhanced_results/messos_full_text.txt", "w", encoding="utf-8") as f:
        f.write(full_text)
    
    # Extract securities from the full text
    securities = extract_securities_from_text(full_text)
    
    # Combine with any securities from the processor
    bonds = result.get("bonds", [])
    for bond in bonds:
        isin = bond.get("isin")
        if isin and not any(s["isin"] == isin for s in securities):
            securities.append(bond)
    
    print(f"Client: {result.get('client_info', {})}")
    print(f"Document date: {result.get('document_date')}")
    print(f"Portfolio value: {result.get('portfolio_value')}")
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
        
        valuation_str = f"{valuation:,.2f}" if valuation is not None else "N/A"
        print(f"{isin:<15} {description[:40]:<40} {valuation_str:>15}")
    
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
    with open("enhanced_results/messos_securities.json", "w", encoding="utf-8") as f:
        json.dump(securities, f, indent=2)
    
    print("\nEnhanced extraction completed. Results saved to enhanced_results directory.")

if __name__ == "__main__":
    main()
