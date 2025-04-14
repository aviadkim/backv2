"""
Script to test the data export and document comparison agents.
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
from backend.agents.data_export_agent import DataExportAgent
from backend.agents.document_comparison_agent import DocumentComparisonAgent

def main():
    """Test the data export and document comparison agents."""
    parser = argparse.ArgumentParser(description="Test Data Export and Document Comparison Agents")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--sample-data", default="sample_data.json", help="Path to sample data file")
    parser.add_argument("--export-format", default="json", choices=["json", "csv", "excel", "xml"], help="Export format")
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
        "data_export",
        DataExportAgent
    )

    manager.create_agent(
        "document_comparison",
        DocumentComparisonAgent
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

    # Create a modified version of the sample data for comparison
    modified_data = create_modified_data(sample_data)

    # Test data export agent
    print("\nTesting Data Export Agent...")
    export_result = manager.run_agent(
        "data_export",
        data=sample_data,
        format_type=args.export_format,
        filename=f"test_export.{args.export_format}",
        export_type="raw"
    )

    print(f"Export Status: {export_result.get('status')}")
    print(f"Export Message: {export_result.get('message')}")
    print(f"Export Filepath: {export_result.get('filepath')}")

    # Test portfolio summary export
    print("\nTesting Portfolio Summary Export...")
    portfolio_export_result = manager.run_agent(
        "data_export",
        data=sample_data,
        format_type=args.export_format,
        filename=f"portfolio_summary.{args.export_format}",
        export_type="portfolio_summary"
    )

    print(f"Export Status: {portfolio_export_result.get('status')}")
    print(f"Export Message: {portfolio_export_result.get('message')}")
    print(f"Export Filepath: {portfolio_export_result.get('filepath')}")

    # Test ISIN list export
    print("\nTesting ISIN List Export...")
    isin_export_result = manager.run_agent(
        "data_export",
        data=sample_data,
        format_type=args.export_format,
        filename=f"isin_list.{args.export_format}",
        export_type="isin_list"
    )

    print(f"Export Status: {isin_export_result.get('status')}")
    print(f"Export Message: {isin_export_result.get('message')}")
    print(f"Export Filepath: {isin_export_result.get('filepath')}")

    # Test document comparison agent
    print("\nTesting Document Comparison Agent...")
    comparison_result = manager.run_agent(
        "document_comparison",
        current_doc=modified_data,
        previous_doc=sample_data
    )

    if comparison_result.get('status') == 'success':
        result = comparison_result.get('comparison_result', {})

        print(f"Comparison ID: {result.get('comparison_id')}")
        print(f"Comparison Date: {result.get('comparison_date')}")

        # Print portfolio value changes
        portfolio_comparison = result.get('portfolio_comparison', {})
        if 'total_value_change' in portfolio_comparison:
            print(f"Portfolio Value Change: {portfolio_comparison['total_value_change']:.2f} ({portfolio_comparison.get('total_value_change_percent', 0):.2f}%)")

        # Print new securities
        new_securities = portfolio_comparison.get('new_securities', [])
        if new_securities:
            print(f"\nNew Securities ({len(new_securities)}):")
            for sec in new_securities:
                print(f"  - {sec.get('name', sec.get('security_name', 'Unknown'))} (ISIN: {sec.get('isin', 'N/A')})")

        # Print removed securities
        removed_securities = portfolio_comparison.get('removed_securities', [])
        if removed_securities:
            print(f"\nRemoved Securities ({len(removed_securities)}):")
            for sec in removed_securities:
                print(f"  - {sec.get('name', sec.get('security_name', 'Unknown'))} (ISIN: {sec.get('isin', 'N/A')})")

        # Print security changes
        security_changes = portfolio_comparison.get('security_changes', [])
        if security_changes:
            print(f"\nSecurity Changes ({len(security_changes)}):")
            for change in security_changes:
                print(f"  - {change.get('security_name', 'Unknown')} (ISIN: {change.get('isin', 'N/A')}):")
                for field, field_change in change.get('changes', {}).items():
                    if 'percent_change' in field_change and field_change['percent_change'] is not None:
                        print(f"    * {field}: {field_change['previous']} -> {field_change['current']} ({field_change['percent_change']:.2f}%)")
                    else:
                        print(f"    * {field}: {field_change['previous']} -> {field_change['current']}")

        # Print significant changes
        significant_changes = result.get('summary', {}).get('significant_changes', [])
        if significant_changes:
            print(f"\nSignificant Changes ({len(significant_changes)}):")
            for change in significant_changes:
                print(f"  - [{change.get('type', 'unknown')}] {change.get('description', 'No description')}")
    else:
        print(f"Comparison Error: {comparison_result.get('message')}")

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

    # Create document data
    document_data = {
        "document_id": "doc_123456789",
        "processing_date": "2023-06-16T10:30:00Z",
        "metadata": {
            "text_length": len(extracted_text),
            "language": "english",
            "document_date": ["15", "06", "2023"],
            "document_type": "portfolio_statement",
            "document_text": extracted_text
        },
        "tables": tables_data,
        "financial_data": financial_data,
        "entities": {
            "isin": isin_entities
        },
        "summary": {
            "table_count": len(tables_data),
            "isin_count": len(isin_entities),
            "security_count": len(financial_data["portfolio"]["securities"]),
            "total_portfolio_value": financial_data["portfolio"]["summary"]["total_value"]
        }
    }

    return document_data

def create_modified_data(original_data):
    """Create a modified version of the data for comparison testing."""
    import copy

    # Deep copy the original data
    modified_data = copy.deepcopy(original_data)

    # Change document ID and processing date
    modified_data["document_id"] = "doc_987654321"
    modified_data["processing_date"] = "2023-07-16T10:30:00Z"

    # Update document date if metadata exists
    if "metadata" in modified_data:
        modified_data["metadata"]["document_date"] = ["15", "07", "2023"]

    # Modify financial data
    if "financial_data" in modified_data and "portfolio" in modified_data["financial_data"]:
        portfolio = modified_data["financial_data"]["portfolio"]

        # Increase Apple's price and value
        for security in portfolio["securities"]:
            if security["isin"] == "US0378331005":  # Apple
                security["price"] = 180.50  # Increased price
                security["value"] = security["price"] * security["quantity"]
                security["return"] = 20.1  # Increased return

        # Add a new security
        portfolio["securities"].append({
            "security_name": "NVIDIA Corp.",
            "isin": "US67066G1040",
            "quantity": 25,
            "price": 450.75,
            "value": 11268.75,
            "return": 18.5
        })

        # Remove a security
        portfolio["securities"] = [sec for sec in portfolio["securities"] if sec["isin"] != "US0231351067"]  # Remove Amazon

        # Update summary
        total_value = sum(sec["value"] for sec in portfolio["securities"])
        portfolio["summary"]["total_value"] = total_value
        portfolio["summary"]["total_securities"] = len(portfolio["securities"])

    # Update ISIN entities
    if "entities" in modified_data and "isin" in modified_data["entities"]:
        # Add NVIDIA
        modified_data["entities"]["isin"].append({
            "isin": "US67066G1040",
            "name": "NVIDIA Corp.",
            "type": "stock"
        })

        # Remove Amazon
        modified_data["entities"]["isin"] = [entity for entity in modified_data["entities"]["isin"] if entity["isin"] != "US0231351067"]

    # Update summary
    if "summary" in modified_data:
        modified_data["summary"]["isin_count"] = len(modified_data["entities"]["isin"])
        modified_data["summary"]["security_count"] = len(modified_data["financial_data"]["portfolio"]["securities"])
        modified_data["summary"]["total_portfolio_value"] = modified_data["financial_data"]["portfolio"]["summary"]["total_value"]

    return modified_data

if __name__ == "__main__":
    sys.exit(main())
