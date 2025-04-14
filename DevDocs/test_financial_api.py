"""
Script to test the financial agents API.
"""
import os
import sys
import argparse
import requests
import json
import base64
from pathlib import Path
import pandas as pd

def main():
    """Test the financial agents API."""
    parser = argparse.ArgumentParser(description="Test Financial Agents API")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--host", default="localhost", help="API host")
    parser.add_argument("--port", type=int, default=8000, help="API port")
    parser.add_argument("--image", help="Path to an image file for table detection")
    parser.add_argument("--csv", help="Path to a CSV file for data analysis")
    args = parser.parse_args()
    
    # Get API key from arguments or environment
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OpenRouter API key is required. Provide it with --api-key or set OPENROUTER_API_KEY environment variable.")
        return 1
    
    # Set the API key in the environment
    os.environ["OPENROUTER_API_KEY"] = api_key
    
    # Set up the API URL
    api_url = f"http://{args.host}:{args.port}"
    
    # Check the API health
    print("Checking API health...")
    try:
        response = requests.get(f"{api_url}/api/financial/health")
        response.raise_for_status()
        print(f"API health: {response.json()}")
    except Exception as e:
        print(f"Error checking API health: {e}")
        print("Make sure the API server is running.")
        return 1
    
    # Test table detection if an image is provided
    if args.image:
        print(f"\nTesting table detection with image: {args.image}")
        
        # Check if the file exists
        if not os.path.exists(args.image):
            print(f"Error: Image file not found: {args.image}")
            return 1
        
        try:
            # Read the image file and convert to base64
            with open(args.image, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
            
            # Send the request
            response = requests.post(
                f"{api_url}/api/financial/detect-tables",
                json={"image_base64": image_data, "lang": "heb+eng"}
            )
            response.raise_for_status()
            
            # Print the response
            result = response.json()
            print(f"Detected {result['num_tables']} tables")
            
            # Analyze each table
            for i, table in enumerate(result['tables']):
                print(f"\nTable {i+1} ({table['region'].get('table_type', 'unknown')}):")
                
                # Analyze the table data
                analysis_response = requests.post(
                    f"{api_url}/api/financial/analyze-data",
                    json={
                        "table_data": table['data'],
                        "table_type": table['region'].get('table_type', 'unknown')
                    }
                )
                analysis_response.raise_for_status()
                
                # Print the analysis
                analysis = analysis_response.json()
                print(f"Analysis: {analysis['table_type']}")
                
                if 'summary' in analysis:
                    print("Summary:")
                    for key, value in analysis['summary'].items():
                        print(f"  {key}: {value}")
        
        except Exception as e:
            print(f"Error testing table detection: {e}")
            return 1
    
    # Test data analysis if a CSV file is provided
    elif args.csv:
        print(f"\nTesting data analysis with CSV: {args.csv}")
        
        # Check if the file exists
        if not os.path.exists(args.csv):
            print(f"Error: CSV file not found: {args.csv}")
            return 1
        
        try:
            # Read the CSV file
            df = pd.read_csv(args.csv)
            
            # Convert DataFrame to dict for JSON serialization
            table_data = df.to_dict(orient="records")
            
            # Send the request
            response = requests.post(
                f"{api_url}/api/financial/analyze-data",
                json={"table_data": table_data}
            )
            response.raise_for_status()
            
            # Print the response
            analysis = response.json()
            print(f"Analysis: {analysis['table_type']}")
            
            if 'summary' in analysis:
                print("Summary:")
                for key, value in analysis['summary'].items():
                    print(f"  {key}: {value}")
        
        except Exception as e:
            print(f"Error testing data analysis: {e}")
            return 1
    
    # If no input is provided, run a simple test with sample data
    else:
        print("\nRunning test with sample data...")
        
        try:
            # Create sample portfolio data
            sample_data = [
                {"Security": "Stock A", "ISIN": "IL0001", "Quantity": 100, "Price": 10.5, "Value": 1050, "Type": "Stocks"},
                {"Security": "Stock B", "ISIN": "IL0002", "Quantity": 200, "Price": 20.5, "Value": 4100, "Type": "Stocks"},
                {"Security": "Stock C", "ISIN": "IL0003", "Quantity": 300, "Price": 30.5, "Value": 9150, "Type": "Bonds"}
            ]
            
            # Send the request
            response = requests.post(
                f"{api_url}/api/financial/analyze-data",
                json={"table_data": sample_data, "table_type": "portfolio"}
            )
            response.raise_for_status()
            
            # Print the response
            analysis = response.json()
            print(f"Analysis: {analysis['table_type']}")
            
            if 'summary' in analysis:
                print("Summary:")
                for key, value in analysis['summary'].items():
                    print(f"  {key}: {value}")
            
            if 'securities' in analysis:
                print("\nSecurities:")
                for i, security in enumerate(analysis['securities']):
                    print(f"  Security {i+1}:")
                    for key, value in security.items():
                        print(f"    {key}: {value}")
        
        except Exception as e:
            print(f"Error testing with sample data: {e}")
            return 1
    
    print("\nAll tests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
