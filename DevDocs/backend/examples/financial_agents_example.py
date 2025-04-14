"""
Example of how to use the financial agents.
"""
import os
import sys
import argparse
import cv2
import pandas as pd
from pathlib import Path

# Add the parent directory to the path so we can import the agents
sys.path.append(str(Path(__file__).parent.parent))

from agents.agent_manager import AgentManager
from agents.financial_table_detector_agent import FinancialTableDetectorAgent
from agents.financial_data_analyzer_agent import FinancialDataAnalyzerAgent

def main():
    """Example of how to use the financial agents."""
    parser = argparse.ArgumentParser(description="Financial Agents Example")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--image", help="Path to an image file containing financial tables")
    parser.add_argument("--csv", help="Path to a CSV file containing financial data")
    args = parser.parse_args()

    # Get API key from arguments or environment
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Warning: OpenRouter API key is not provided. Some features may not work properly.")

    # Create agent manager
    manager = AgentManager(api_key=api_key)

    # Create agents
    manager.create_agent(
        "table_detector",
        FinancialTableDetectorAgent
    )

    manager.create_agent(
        "data_analyzer",
        FinancialDataAnalyzerAgent
    )

    # Process an image if provided
    if args.image:
        print(f"Processing image: {args.image}")

        # Check if the file exists
        if not os.path.exists(args.image):
            print(f"Error: Image file not found: {args.image}")
            return 1

        # Detect tables
        try:
            result = manager.run_agent(
                "table_detector",
                image_path=args.image
            )

            print(f"Detected {result['num_tables']} tables")

            # Analyze each table
            for i, table in enumerate(result['tables']):
                print(f"\nTable {i+1} ({table['region'].get('table_type', 'unknown')}):")

                # Analyze the table data
                analysis = manager.run_agent(
                    "data_analyzer",
                    table_data=table['data'],
                    table_type=table['region'].get('table_type', 'unknown')
                )

                # Print the analysis
                print(f"Analysis: {analysis['table_type']}")

                if 'summary' in analysis:
                    print("Summary:")
                    for key, value in analysis['summary'].items():
                        print(f"  {key}: {value}")

        except Exception as e:
            print(f"Error processing image: {e}")
            return 1

    # Process a CSV file if provided
    elif args.csv:
        print(f"Processing CSV: {args.csv}")

        # Check if the file exists
        if not os.path.exists(args.csv):
            print(f"Error: CSV file not found: {args.csv}")
            return 1

        try:
            # Load the CSV file
            df = pd.read_csv(args.csv)

            # Analyze the data
            analysis = manager.run_agent(
                "data_analyzer",
                table_data=df
            )

            # Print the analysis
            print(f"Analysis: {analysis['table_type']}")

            if 'summary' in analysis:
                print("Summary:")
                for key, value in analysis['summary'].items():
                    print(f"  {key}: {value}")

        except Exception as e:
            print(f"Error processing CSV: {e}")
            return 1

    # If no input is provided, show an example with a sample DataFrame
    else:
        print("No input provided. Running with a sample DataFrame.")

        # Create a sample portfolio table
        portfolio_df = pd.DataFrame({
            'Security': ['Stock A', 'Stock B', 'Stock C'],
            'ISIN': ['IL0001', 'IL0002', 'IL0003'],
            'Quantity': [100, 200, 300],
            'Price': [10.5, 20.5, 30.5],
            'Value': [1050, 4100, 9150],
            'Type': ['Stocks', 'Stocks', 'Bonds']
        })

        # Analyze the data
        analysis = manager.run_agent(
            "data_analyzer",
            table_data=portfolio_df
        )

        # Print the analysis
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

    print("\nExample completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
