"""
Script to test the document integration and query engine agents.
"""
import os
import sys
import argparse
import json
from pathlib import Path
import pandas as pd

# Add the parent directory to the path so we can import the agents
sys.path.append(str(Path(__file__).parent))

from backend.agents.agent_manager import AgentManager
from backend.agents.document_integration_agent import DocumentIntegrationAgent
from backend.agents.query_engine_agent import QueryEngineAgent
from backend.agents.notification_agent import NotificationAgent

def main():
    """Test the document integration and query engine agents."""
    parser = argparse.ArgumentParser(description="Test Document Integration and Query Engine Agents")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--sample-data", default="sample_data.json", help="Path to sample data file")
    parser.add_argument("--query", help="Query to test with the query engine")
    args = parser.parse_args()
    
    # Get API key from arguments or environment
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OpenRouter API key is required. Provide it with --api-key or set OPENROUTER_API_KEY environment variable.")
        return 1
    
    # Set the API key in the environment
    os.environ["OPENROUTER_API_KEY"] = api_key
    
    # Create agent manager
    manager = AgentManager(api_key=api_key)
    
    # Create agents
    manager.create_agent(
        "document_integration",
        DocumentIntegrationAgent
    )
    
    manager.create_agent(
        "query_engine",
        QueryEngineAgent
    )
    
    manager.create_agent(
        "notification",
        NotificationAgent
    )
    
    # Load sample data or create it if it doesn't exist
    sample_data_path = args.sample_data
    if os.path.exists(sample_data_path):
        with open(sample_data_path, 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
        print(f"Loaded sample data from {sample_data_path}")
    else:
        # Create sample data
        sample_data = create_sample_data()
        
        # Save sample data
        with open(sample_data_path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        print(f"Created and saved sample data to {sample_data_path}")
    
    # Test document integration agent
    print("\nTesting Document Integration Agent...")
    integration_result = manager.run_agent(
        "document_integration",
        extracted_text=sample_data["extracted_text"],
        tables_data=sample_data["tables_data"],
        financial_data=sample_data["financial_data"],
        isin_entities=sample_data["isin_entities"]
    )
    
    integrated_data = integration_result.get("integrated_data", {})
    print(f"Document ID: {integrated_data.get('document_id')}")
    print(f"Document Type: {integrated_data.get('metadata', {}).get('document_type')}")
    print(f"Number of Tables: {len(integrated_data.get('tables', []))}")
    print(f"Number of ISIN Entities: {len(integrated_data.get('entities', {}).get('isin', []))}")
    
    # Test query engine agent
    if args.query:
        print(f"\nTesting Query Engine Agent with query: '{args.query}'")
        query_result = manager.run_agent(
            "query_engine",
            query=args.query,
            document_data=integrated_data
        )
        
        print(f"Query Type: {query_result.get('query_type')}")
        print(f"Answer: {query_result.get('answer')}")
    else:
        # Test with some sample queries
        sample_queries = [
            "What is the total value of the portfolio?",
            "What securities are in the portfolio?",
            "What is the document date?",
            "Show me information about the balance sheet"
        ]
        
        for query in sample_queries:
            print(f"\nTesting Query Engine Agent with query: '{query}'")
            query_result = manager.run_agent(
                "query_engine",
                query=query,
                document_data=integrated_data
            )
            
            print(f"Query Type: {query_result.get('query_type')}")
            print(f"Answer: {query_result.get('answer')}")
    
    # Test notification agent
    print("\nTesting Notification Agent...")
    notification_result = manager.run_agent(
        "notification",
        document_data=integrated_data,
        user_settings={
            "portfolio_value_threshold": 1000000,
            "security_return_threshold": 5.0,
            "watched_securities": ["US0378331005"]  # Apple Inc.
        }
    )
    
    notifications = notification_result.get("notifications", [])
    print(f"Generated {len(notifications)} notifications:")
    for i, notification in enumerate(notifications):
        print(f"{i+1}. {notification.get('title')}: {notification.get('message')}")
    
    print("\nAll tests completed successfully!")
    return 0

def create_sample_data():
    """Create sample data for testing."""
    # Sample extracted text
    extracted_text = """
    Portfolio Statement
    Date: 15/06/2023
    
    This document contains information about your investment portfolio.
    The portfolio includes stocks, bonds, and other securities.
    
    Total Portfolio Value: $1,250,000.00
    """
    
    # Sample table data
    table_data = pd.DataFrame({
        "Security": ["Apple Inc.", "Microsoft Corp.", "Amazon.com Inc.", "Tesla Inc.", "Alphabet Inc."],
        "ISIN": ["US0378331005", "US5949181045", "US0231351067", "US88160R1014", "US02079K1079"],
        "Quantity": [100, 50, 20, 30, 15],
        "Price": [150.25, 300.50, 3200.75, 700.50, 2500.25],
        "Value": [15025.00, 15025.00, 64015.00, 21015.00, 37503.75],
        "Return": [12.5, 8.3, -2.1, 15.7, 5.2]
    })
    
    tables_data = [{
        "id": "table_1",
        "type": "portfolio",
        "data": table_data.to_dict(orient="records"),
        "columns": table_data.columns.tolist(),
        "row_count": len(table_data),
        "column_count": len(table_data.columns)
    }]
    
    # Sample financial data
    financial_data = {
        "portfolio": {
            "securities": [
                {
                    "security_name": "Apple Inc.",
                    "isin": "US0378331005",
                    "quantity": 100,
                    "price": 150.25,
                    "value": 15025.00,
                    "return": 12.5
                },
                {
                    "security_name": "Microsoft Corp.",
                    "isin": "US5949181045",
                    "quantity": 50,
                    "price": 300.50,
                    "value": 15025.00,
                    "return": 8.3
                },
                {
                    "security_name": "Amazon.com Inc.",
                    "isin": "US0231351067",
                    "quantity": 20,
                    "price": 3200.75,
                    "value": 64015.00,
                    "return": -2.1
                },
                {
                    "security_name": "Tesla Inc.",
                    "isin": "US88160R1014",
                    "quantity": 30,
                    "price": 700.50,
                    "value": 21015.00,
                    "return": 15.7
                },
                {
                    "security_name": "Alphabet Inc.",
                    "isin": "US02079K1079",
                    "quantity": 15,
                    "price": 2500.25,
                    "value": 37503.75,
                    "return": 5.2
                }
            ],
            "summary": {
                "total_value": 152583.75,
                "total_securities": 5,
                "type_distribution": {
                    "Stocks": 100.0,
                    "Bonds": 0.0,
                    "Cash": 0.0,
                    "Other": 0.0
                }
            }
        }
    }
    
    # Sample ISIN entities
    isin_entities = [
        {
            "isin": "US0378331005",
            "name": "Apple Inc.",
            "type": "stock"
        },
        {
            "isin": "US5949181045",
            "name": "Microsoft Corp.",
            "type": "stock"
        },
        {
            "isin": "US0231351067",
            "name": "Amazon.com Inc.",
            "type": "stock"
        },
        {
            "isin": "US88160R1014",
            "name": "Tesla Inc.",
            "type": "stock"
        },
        {
            "isin": "US02079K1079",
            "name": "Alphabet Inc.",
            "type": "stock"
        }
    ]
    
    return {
        "extracted_text": extracted_text,
        "tables_data": tables_data,
        "financial_data": financial_data,
        "isin_entities": isin_entities
    }

if __name__ == "__main__":
    sys.exit(main())
