"""
Format the comprehensive analysis into a more readable format.
"""
import json
import sys

def format_analysis(input_path, output_path):
    """Format the analysis into a more readable format."""
    # Load the analysis
    with open(input_path, "r", encoding="utf-8") as f:
        analysis = json.load(f)
    
    # Extract the raw response
    raw_response = analysis.get("raw_response", "")
    
    # Try to parse the JSON from the raw response
    try:
        # Find the JSON part in the raw response
        json_start = raw_response.find("{")
        json_end = raw_response.rfind("}")
        
        if json_start >= 0 and json_end >= 0:
            json_str = raw_response[json_start:json_end+1]
            parsed_analysis = json.loads(json_str)
            
            # Format the analysis
            formatted_analysis = {
                "client_info": parsed_analysis.get("client_info", {}),
                "document_date": parsed_analysis.get("document_date", ""),
                "portfolio_value": parsed_analysis.get("portfolio_value", 0),
                "securities_count": parsed_analysis.get("securities_count", 0),
                "asset_allocation": parsed_analysis.get("asset_allocation", {}),
                "structured_products": parsed_analysis.get("structured_products", {}),
                "top_holdings": parsed_analysis.get("top_holdings", []),
                "analysis": parsed_analysis.get("analysis", {})
            }
            
            # Save the formatted analysis
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(formatted_analysis, f, indent=2)
            
            print(f"Formatted analysis saved to {output_path}")
            return formatted_analysis
        else:
            print("Could not find JSON in raw response")
            return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python format_analysis.py <input_path> <output_path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    format_analysis(input_path, output_path)
