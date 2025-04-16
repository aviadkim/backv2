"""
Test script to extract ISINs from the Messos PDF.
"""
import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_isin_extractor(text_file):
    """Test ISINExtractorAgent on the Messos PDF text."""
    try:
        from DevDocs.backend.agents.isin_extractor_agent import ISINExtractorAgent
        
        print("\n=== Testing ISINExtractorAgent on Messos PDF ===\n")
        
        # Read the text file
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Create the agent
        agent = ISINExtractorAgent()
        
        # Process the text
        result = agent.process({"text": text, "validate": True, "with_metadata": True})
        
        print(f"Processed text")
        if "isins" in result:
            print(f"Extracted {len(result['isins'])} ISINs:")
            
            # Print the extracted ISINs
            for isin in result["isins"]:
                if isinstance(isin, dict) and "isin" in isin:
                    print(f"- {isin['isin']}")
                    if "metadata" in isin:
                        print(f"  Metadata: {isin['metadata']}")
                else:
                    print(f"- {isin}")
            
            # Save the extracted ISINs
            output_dir = Path("./messos_results")
            output_dir.mkdir(exist_ok=True, parents=True)
            isins_path = output_dir / "extracted_isins.json"
            with open(isins_path, "w", encoding="utf-8") as f:
                json.dump(result["isins"], f, indent=2)
            print(f"Saved extracted ISINs to {isins_path}")
        
        return result
    except Exception as e:
        print(f"Error testing ISINExtractorAgent: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_isin_extraction_messos.py <text_file>")
        sys.exit(1)
    
    text_file = sys.argv[1]
    test_isin_extractor(text_file)
