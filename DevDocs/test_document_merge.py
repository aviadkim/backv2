"""
Test script for the DocumentMergeAgent.
"""
import os
import sys
import json
import argparse
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DevDocs.backend.agents.document_merge_agent import DocumentMergeAgent

def create_sample_documents():
    """Create sample documents for testing."""
    # Create a portfolio statement
    portfolio_statement = {
        "metadata": {
            "document_type": "portfolio_statement",
            "document_date": (datetime.now() - timedelta(days=30)).isoformat()
        },
        "financial_data": {
            "portfolio": {
                "securities": [
                    {
                        "name": "Apple Inc.",
                        "isin": "US0378331005",
                        "type": "stock",
                        "quantity": 100,
                        "price": 150.0,
                        "value": 15000.0,
                        "return": 12.5
                    },
                    {
                        "name": "Microsoft Corp.",
                        "isin": "US5949181045",
                        "type": "stock",
                        "quantity": 50,
                        "price": 300.0,
                        "value": 15000.0,
                        "return": 8.2
                    },
                    {
                        "name": "US Treasury Bond",
                        "isin": "US912810TW33",
                        "type": "bond",
                        "quantity": 10,
                        "price": 1000.0,
                        "value": 10000.0,
                        "return": 3.5
                    }
                ],
                "summary": {
                    "total_value": 40000.0,
                    "total_return": 8.7
                }
            }
        }
    }

    # Create an older portfolio statement
    older_portfolio_statement = {
        "metadata": {
            "document_type": "portfolio_statement",
            "document_date": (datetime.now() - timedelta(days=90)).isoformat()
        },
        "financial_data": {
            "portfolio": {
                "securities": [
                    {
                        "name": "Apple Inc.",
                        "isin": "US0378331005",
                        "type": "stock",
                        "quantity": 80,
                        "price": 140.0,
                        "value": 11200.0,
                        "return": 10.0
                    },
                    {
                        "name": "Microsoft Corp.",
                        "isin": "US5949181045",
                        "type": "stock",
                        "quantity": 50,
                        "price": 280.0,
                        "value": 14000.0,
                        "return": 7.0
                    },
                    {
                        "name": "US Treasury Bond",
                        "isin": "US912810TW33",
                        "type": "bond",
                        "quantity": 10,
                        "price": 980.0,
                        "value": 9800.0,
                        "return": 3.2
                    }
                ],
                "summary": {
                    "total_value": 35000.0,
                    "total_return": 7.5
                }
            }
        }
    }

    # Create a balance sheet
    balance_sheet = {
        "metadata": {
            "document_type": "balance_sheet",
            "document_date": (datetime.now() - timedelta(days=30)).isoformat()
        },
        "financial_data": {
            "balance_sheet": {
                "assets": {
                    "Cash and Cash Equivalents": 50000.0,
                    "Investments": 40000.0,
                    "Real Estate": 300000.0,
                    "Other Assets": 10000.0
                },
                "liabilities": {
                    "Mortgage": 200000.0,
                    "Credit Card Debt": 5000.0,
                    "Other Liabilities": 2000.0
                },
                "equity": {
                    "Net Worth": 193000.0
                },
                "summary": {
                    "total_assets": 400000.0,
                    "total_liabilities": 207000.0,
                    "total_equity": 193000.0
                }
            }
        }
    }

    # Create an income statement
    income_statement = {
        "metadata": {
            "document_type": "income_statement",
            "document_date": (datetime.now() - timedelta(days=30)).isoformat()
        },
        "financial_data": {
            "income_statement": {
                "revenues": {
                    "Salary": 120000.0,
                    "Investment Income": 5000.0,
                    "Other Income": 2000.0
                },
                "expenses": {
                    "Housing": 24000.0,
                    "Transportation": 6000.0,
                    "Food": 12000.0,
                    "Utilities": 4800.0,
                    "Insurance": 3600.0,
                    "Taxes": 30000.0,
                    "Other Expenses": 10000.0
                },
                "profits": {
                    "Net Income": 36600.0
                },
                "summary": {
                    "total_revenue": 127000.0,
                    "total_expenses": 90400.0,
                    "net_profit": 36600.0
                }
            }
        }
    }

    # Create a salary statement
    salary_statement = {
        "metadata": {
            "document_type": "salary_statement",
            "document_date": (datetime.now() - timedelta(days=30)).isoformat()
        },
        "tables": [
            {
                "type": "salary",
                "columns": ["Item", "Amount"],
                "data": [
                    {"Item": "Gross Salary", "Amount": "10000.0"},
                    {"Item": "Income Tax", "Amount": "2000.0"},
                    {"Item": "Social Security", "Amount": "500.0"},
                    {"Item": "Health Insurance", "Amount": "300.0"},
                    {"Item": "Pension", "Amount": "1000.0"},
                    {"Item": "Net Salary", "Amount": "6200.0"}
                ]
            }
        ]
    }

    return [portfolio_statement, older_portfolio_statement, balance_sheet, income_statement, salary_statement]

def test_merge_documents(agent, documents):
    """Test merging documents."""
    print("\n=== Testing Document Merge ===")
    merged_document = agent.merge_documents(documents)
    
    print(f"Merged {len(documents)} documents")
    print(f"Document types: {merged_document['document_types']}")
    print(f"Summary keys: {list(merged_document['summary'].keys())}")
    
    return merged_document

def test_compare_over_time(agent, merged_documents):
    """Test comparing documents over time."""
    print("\n=== Testing Document Comparison Over Time ===")
    comparison = agent.compare_merged_document_over_time(merged_documents)
    
    print(f"Comparison period: {comparison['period_start']} to {comparison['period_end']}")
    print(f"Trend types: {list(comparison['trends'].keys())}")
    print(f"Summary keys: {list(comparison['summary'].keys())}")
    
    return comparison

def test_comprehensive_report(agent, merged_document):
    """Test generating a comprehensive report."""
    print("\n=== Testing Comprehensive Report Generation ===")
    report = agent.generate_comprehensive_report(merged_document)
    
    print(f"Report date: {report['report_date']}")
    print(f"Report type: {report['report_type']}")
    print(f"Data sources: {report['data_sources']}")
    print(f"Report sections: {[k for k in report.keys() if k not in ['report_date', 'report_type', 'data_sources']]}")
    print(f"Recommendation count: {len(report['recommendations'])}")
    
    return report

def main(api_key=None):
    """Main function."""
    print("Testing DocumentMergeAgent...")
    
    # Create the agent
    agent = DocumentMergeAgent()
    
    # Create sample documents
    documents = create_sample_documents()
    print(f"Created {len(documents)} sample documents")
    
    # Test merging documents
    merged_document = test_merge_documents(agent, documents)
    
    # Create another merged document with different date
    older_documents = documents[1:] + [documents[0]]
    older_merged_document = agent.merge_documents(older_documents)
    older_merged_document["merge_date"] = (datetime.now() - timedelta(days=60)).isoformat()
    
    # Test comparing documents over time
    comparison = test_compare_over_time(agent, [older_merged_document, merged_document])
    
    # Test generating a comprehensive report
    report = test_comprehensive_report(agent, merged_document)
    
    print("\nAll tests completed successfully!")
    
    # Save results to files
    with open("merged_document.json", "w") as f:
        json.dump(merged_document, f, indent=2)
    
    with open("comparison.json", "w") as f:
        json.dump(comparison, f, indent=2)
    
    with open("report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\nResults saved to merged_document.json, comparison.json, and report.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the DocumentMergeAgent")
    parser.add_argument("--api-key", help="OpenRouter API key")
    args = parser.parse_args()
    
    main(args.api_key)
