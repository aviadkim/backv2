"""
Test script for evaluating the DocumentMergeAgent.
"""
import os
import sys
import argparse
import json
import random
from pathlib import Path
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_sample_portfolio_document():
    """Create a sample portfolio document."""
    return {
        "metadata": {
            "document_type": "portfolio_statement",
            "document_date": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
        },
        "tables": [
            {
                "type": "portfolio",
                "data": [
                    {"Security": "Apple Inc.", "ISIN": "US0378331005", "Quantity": 100, "Price": 150.25, "Value": 15025.00},
                    {"Security": "Microsoft Corp.", "ISIN": "US5949181045", "Quantity": 50, "Price": 300.50, "Value": 15025.00},
                    {"Security": "Amazon.com Inc.", "ISIN": "US0231351067", "Quantity": 25, "Price": 130.75, "Value": 3268.75}
                ]
            }
        ],
        "financial_data": {
            "portfolio": {
                "securities": [
                    {"name": "Apple Inc.", "isin": "US0378331005", "quantity": 100, "price": 150.25, "value": 15025.00},
                    {"name": "Microsoft Corp.", "isin": "US5949181045", "quantity": 50, "price": 300.50, "value": 15025.00},
                    {"name": "Amazon.com Inc.", "isin": "US0231351067", "quantity": 25, "price": 130.75, "value": 3268.75}
                ],
                "summary": {
                    "total_value": 33318.75,
                    "total_securities": 3
                }
            }
        }
    }

def create_sample_balance_sheet():
    """Create a sample balance sheet."""
    return {
        "metadata": {
            "document_type": "balance_sheet",
            "document_date": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
        },
        "tables": [
            {
                "type": "balance_sheet",
                "data": [
                    {"Item": "Cash and Cash Equivalents", "Amount": 50000.00},
                    {"Item": "Investments", "Amount": 150000.00},
                    {"Item": "Real Estate", "Amount": 500000.00},
                    {"Item": "Total Assets", "Amount": 700000.00},
                    {"Item": "Credit Card Debt", "Amount": 5000.00},
                    {"Item": "Mortgage", "Amount": 300000.00},
                    {"Item": "Total Liabilities", "Amount": 305000.00},
                    {"Item": "Net Worth", "Amount": 395000.00}
                ]
            }
        ],
        "financial_data": {
            "balance_sheet": {
                "assets": {
                    "cash": 50000.00,
                    "investments": 150000.00,
                    "real_estate": 500000.00
                },
                "liabilities": {
                    "credit_card": 5000.00,
                    "mortgage": 300000.00
                },
                "equity": {
                    "net_worth": 395000.00
                },
                "summary": {
                    "total_assets": 700000.00,
                    "total_liabilities": 305000.00,
                    "total_equity": 395000.00
                }
            }
        }
    }

def create_sample_income_statement():
    """Create a sample income statement."""
    return {
        "metadata": {
            "document_type": "income_statement",
            "document_date": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
        },
        "tables": [
            {
                "type": "income_statement",
                "data": [
                    {"Item": "Salary", "Amount": 120000.00},
                    {"Item": "Investment Income", "Amount": 15000.00},
                    {"Item": "Total Income", "Amount": 135000.00},
                    {"Item": "Housing", "Amount": 36000.00},
                    {"Item": "Transportation", "Amount": 12000.00},
                    {"Item": "Food", "Amount": 9600.00},
                    {"Item": "Other Expenses", "Amount": 24000.00},
                    {"Item": "Total Expenses", "Amount": 81600.00},
                    {"Item": "Net Income", "Amount": 53400.00}
                ]
            }
        ],
        "financial_data": {
            "income_statement": {
                "revenues": {
                    "salary": 120000.00,
                    "investment_income": 15000.00
                },
                "expenses": {
                    "housing": 36000.00,
                    "transportation": 12000.00,
                    "food": 9600.00,
                    "other": 24000.00
                },
                "profits": {
                    "net_income": 53400.00
                },
                "summary": {
                    "total_income": 135000.00,
                    "total_expenses": 81600.00,
                    "net_income": 53400.00
                }
            }
        }
    }

def create_sample_salary_statement():
    """Create a sample salary statement."""
    return {
        "metadata": {
            "document_type": "salary_statement",
            "document_date": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
        },
        "tables": [
            {
                "type": "salary",
                "data": [
                    {"Item": "Gross Salary", "Amount": 10000.00},
                    {"Item": "Income Tax", "Amount": 2500.00},
                    {"Item": "Social Security", "Amount": 800.00},
                    {"Item": "Health Insurance", "Amount": 400.00},
                    {"Item": "Net Salary", "Amount": 6300.00}
                ]
            }
        ],
        "financial_data": {
            "salary": {
                "gross_salary": 10000.00,
                "deductions": {
                    "income_tax": 2500.00,
                    "social_security": 800.00,
                    "health_insurance": 400.00
                },
                "net_salary": 6300.00
            }
        }
    }

def validate_document_merge_result(actual, expected):
    """Validate DocumentMergeAgent results."""
    # Check document types
    if "document_types" in expected:
        if "document_types" not in actual:
            print("Missing document_types in result")
            return False

        # Check if all expected document types are present
        for doc_type in expected["document_types"]:
            if doc_type not in actual["document_types"]:
                print(f"Missing document type: {doc_type}")
                return False

    # Check period start/end for comparison
    if "period_start" in expected and expected["period_start"]:
        if "period_start" not in actual or not actual["period_start"]:
            print("Missing period_start in result")
            return False

    if "period_end" in expected and expected["period_end"]:
        if "period_end" not in actual or not actual["period_end"]:
            print("Missing period_end in result")
            return False

    # Check trend types
    if "trend_types" in expected:
        if "trend_types" not in actual:
            print("Missing trend_types in result")
            return False

        # Check if all expected trend types are present
        for trend_type in expected["trend_types"]:
            if trend_type not in actual["trend_types"]:
                print(f"Missing trend type: {trend_type}")
                return False

    # Check report type
    if "report_type" in expected:
        if "report_type" not in actual:
            print("Missing report_type in result")
            return False

        if actual["report_type"] != expected["report_type"]:
            print(f"Report type mismatch: expected {expected['report_type']}, got {actual['report_type']}")
            return False

    # Check data sources
    if "data_sources" in expected:
        if "data_sources" not in actual:
            print("Missing data_sources in result")
            return False

        # Check if all expected data sources are present
        for source in expected["data_sources"]:
            if source not in actual["data_sources"]:
                print(f"Missing data source: {source}")
                return False

    return True

def test_document_merge_agent():
    """Test the DocumentMergeAgent."""
    from DevDocs.backend.agents.document_merge_agent import DocumentMergeAgent

    # Create the agent
    agent = DocumentMergeAgent()

    # Create sample documents
    portfolio_doc = create_sample_portfolio_document()
    balance_sheet = create_sample_balance_sheet()
    income_statement = create_sample_income_statement()
    salary_statement = create_sample_salary_statement()

    # Create test cases
    test_cases = [
        {
            "description": "Merge portfolio and balance sheet",
            "input": {
                "documents": [portfolio_doc, balance_sheet]
            },
            "expected": {
                "document_types": ["portfolio_statement", "balance_sheet"]
            }
        },
        {
            "description": "Merge all document types",
            "input": {
                "documents": [portfolio_doc, balance_sheet, income_statement, salary_statement]
            },
            "expected": {
                "document_types": ["portfolio_statement", "balance_sheet", "income_statement", "salary_statement"]
            }
        },
        {
            "description": "Compare documents over time",
            "input": {
                "merged_documents": [
                    {
                        "merge_date": (datetime.now() - timedelta(days=60)).isoformat(),
                        "document_types": ["portfolio_statement", "balance_sheet"],
                        "merged_data": {
                            "portfolio": {
                                "securities": [
                                    {"name": "Apple Inc.", "isin": "US0378331005", "quantity": 80, "price": 140.25, "value": 11220.00},
                                    {"name": "Microsoft Corp.", "isin": "US5949181045", "quantity": 40, "price": 280.50, "value": 11220.00}
                                ],
                                "summary": {
                                    "total_value": 22440.00,
                                    "total_securities": 2
                                }
                            },
                            "balance_sheet": {
                                "assets": {
                                    "cash": 40000.00,
                                    "investments": 120000.00,
                                    "real_estate": 450000.00
                                },
                                "liabilities": {
                                    "credit_card": 6000.00,
                                    "mortgage": 320000.00
                                },
                                "equity": {
                                    "net_worth": 284000.00
                                },
                                "summary": {
                                    "total_assets": 610000.00,
                                    "total_liabilities": 326000.00,
                                    "total_equity": 284000.00
                                }
                            }
                        }
                    },
                    {
                        "merge_date": datetime.now().isoformat(),
                        "document_types": ["portfolio_statement", "balance_sheet"],
                        "merged_data": {
                            "portfolio": {
                                "securities": [
                                    {"name": "Apple Inc.", "isin": "US0378331005", "quantity": 100, "price": 150.25, "value": 15025.00},
                                    {"name": "Microsoft Corp.", "isin": "US5949181045", "quantity": 50, "price": 300.50, "value": 15025.00},
                                    {"name": "Amazon.com Inc.", "isin": "US0231351067", "quantity": 25, "price": 130.75, "value": 3268.75}
                                ],
                                "summary": {
                                    "total_value": 33318.75,
                                    "total_securities": 3
                                }
                            },
                            "balance_sheet": {
                                "assets": {
                                    "cash": 50000.00,
                                    "investments": 150000.00,
                                    "real_estate": 500000.00
                                },
                                "liabilities": {
                                    "credit_card": 5000.00,
                                    "mortgage": 300000.00
                                },
                                "equity": {
                                    "net_worth": 395000.00
                                },
                                "summary": {
                                    "total_assets": 700000.00,
                                    "total_liabilities": 305000.00,
                                    "total_equity": 395000.00
                                }
                            }
                        }
                    }
                ]
            },
            "expected": {
                "period_start": True,
                "period_end": True,
                "trend_types": ["portfolio", "balance_sheet"]
            }
        },
        {
            "description": "Generate comprehensive report",
            "input": {
                "merged_document": {
                    "merge_date": datetime.now().isoformat(),
                    "document_types": ["portfolio_statement", "balance_sheet", "income_statement", "salary_statement"],
                    "merged_data": {
                        "portfolio": {
                            "securities": [
                                {"name": "Apple Inc.", "isin": "US0378331005", "quantity": 100, "price": 150.25, "value": 15025.00},
                                {"name": "Microsoft Corp.", "isin": "US5949181045", "quantity": 50, "price": 300.50, "value": 15025.00},
                                {"name": "Amazon.com Inc.", "isin": "US0231351067", "quantity": 25, "price": 130.75, "value": 3268.75}
                            ],
                            "summary": {
                                "total_value": 33318.75,
                                "total_securities": 3
                            }
                        },
                        "balance_sheet": {
                            "assets": {
                                "cash": 50000.00,
                                "investments": 150000.00,
                                "real_estate": 500000.00
                            },
                            "liabilities": {
                                "credit_card": 5000.00,
                                "mortgage": 300000.00
                            },
                            "equity": {
                                "net_worth": 395000.00
                            },
                            "summary": {
                                "total_assets": 700000.00,
                                "total_liabilities": 305000.00,
                                "total_equity": 395000.00
                            }
                        },
                        "income_statement": {
                            "revenues": {
                                "salary": 120000.00,
                                "investment_income": 15000.00
                            },
                            "expenses": {
                                "housing": 36000.00,
                                "transportation": 12000.00,
                                "food": 9600.00,
                                "other": 24000.00
                            },
                            "profits": {
                                "net_income": 53400.00
                            },
                            "summary": {
                                "total_income": 135000.00,
                                "total_expenses": 81600.00,
                                "net_income": 53400.00
                            }
                        },
                        "salary": {
                            "salary_slips": [
                                {
                                    "date": (datetime.now() - timedelta(days=30)).isoformat(),
                                    "gross_salary": 10000.00,
                                    "deductions": {
                                        "income_tax": 2500.00,
                                        "social_security": 800.00,
                                        "health_insurance": 400.00
                                    },
                                    "net_salary": 6300.00
                                }
                            ],
                            "summary": {
                                "average_gross": 10000.00,
                                "average_net": 6300.00,
                                "total_gross": 10000.00,
                                "total_net": 6300.00
                            }
                        }
                    }
                }
            },
            "expected": {
                "report_type": "comprehensive_financial_report",
                "data_sources": ["portfolio_statement", "balance_sheet", "income_statement", "salary_statement"]
            }
        }
    ]

    # Custom evaluation for DocumentMergeAgent since it doesn't use the process method
    print(f"\n=== Evaluating DocumentMergeAgent ===\n")

    results = {
        "agent_name": "DocumentMergeAgent",
        "test_date": datetime.now().isoformat(),
        "total_tests": len(test_cases),
        "passed_tests": 0,
        "failed_tests": 0,
        "test_results": []
    }

    for i, test_case in enumerate(test_cases):
        print(f"Test {i+1}/{len(test_cases)}: {test_case.get('description', 'No description')}")

        try:
            start_time = datetime.now()

            # Call the appropriate method based on the test case
            if "documents" in test_case["input"]:
                result = agent.merge_documents(test_case["input"]["documents"])
            elif "merged_documents" in test_case["input"]:
                result = agent.compare_documents_over_time(test_case["input"]["merged_documents"])
            elif "merged_document" in test_case["input"]:
                result = agent.generate_comprehensive_report(test_case["input"]["merged_document"])
            else:
                raise ValueError("Unknown test case type")

            end_time = datetime.now()

            # Validate the result
            passed = validate_document_merge_result(result, test_case.get("expected", {}))

            # Record the result
            test_result = {
                "test_id": i + 1,
                "description": test_case.get("description", "No description"),
                "passed": passed,
                "execution_time": (end_time - start_time).total_seconds(),
                "input": test_case.get("input", {}),
                "expected": test_case.get("expected", {}),
                "actual": result
            }

            # Update counters
            if passed:
                results["passed_tests"] += 1
                print("Test passed")
            else:
                results["failed_tests"] += 1
                print("X Test failed")

            results["test_results"].append(test_result)

        except Exception as e:
            print(f"X Test failed with exception: {str(e)}")

            # Record the error
            test_result = {
                "test_id": i + 1,
                "description": test_case.get("description", "No description"),
                "passed": False,
                "execution_time": 0,
                "input": test_case.get("input", {}),
                "expected": test_case.get("expected", {}),
                "actual": {"error": str(e)}
            }

            results["failed_tests"] += 1
            results["test_results"].append(test_result)

    # Calculate success rate
    results["success_rate"] = (results["passed_tests"] / results["total_tests"]) * 100 if results["total_tests"] > 0 else 0

    # Print summary
    print(f"\nSummary for DocumentMergeAgent:")
    print(f"Total tests: {results['total_tests']}")
    print(f"Passed tests: {results['passed_tests']}")
    print(f"Failed tests: {results['failed_tests']}")
    print(f"Success rate: {results['success_rate']:.2f}%")

    # Save results
    output_dir = Path("./evaluation_results")
    output_dir.mkdir(exist_ok=True, parents=True)
    filename = "documentmergeagent_evaluation.json"
    file_path = output_dir / filename

    # Save the results
    with open(file_path, 'w', encoding='utf-8') as f:
        # Clean the results for JSON serialization
        clean_results = {}
        for k, v in results.items():
            if k == "test_results":
                clean_results[k] = []
                for tr in v:
                    clean_tr = {}
                    for trk, trv in tr.items():
                        if trk not in ["actual", "input", "expected"]:
                            clean_tr[trk] = trv
                        else:
                            clean_tr[trk] = str(trv)
                    clean_results[k].append(clean_tr)
            else:
                clean_results[k] = v

        json.dump(clean_results, f, indent=2)

    print(f"Results saved to {file_path}")

    return results

if __name__ == "__main__":
    test_document_merge_agent()
