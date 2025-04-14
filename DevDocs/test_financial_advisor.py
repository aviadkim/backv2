"""
Script to test the financial advisor agent.
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
from backend.agents.financial_advisor_agent import FinancialAdvisorAgent

def main():
    """Test the financial advisor agent."""
    parser = argparse.ArgumentParser(description="Test Financial Advisor Agent")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--sample-data", default="sample_data.json", help="Path to sample data file")
    parser.add_argument("--analysis-type", default="portfolio", choices=["portfolio", "financial_statements", "salary", "investment_suggestion"], help="Type of analysis to perform")
    parser.add_argument("--risk-profile", default="medium", choices=["low", "medium", "high"], help="Risk profile for portfolio analysis")
    parser.add_argument("--investment-amount", type=float, default=100000, help="Investment amount for investment suggestions")
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
    
    # Create agent
    manager.create_agent(
        "financial_advisor",
        FinancialAdvisorAgent
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
    
    # Test financial advisor agent
    print(f"\nTesting Financial Advisor Agent with analysis type: {args.analysis_type}")
    
    result = manager.run_agent(
        "financial_advisor",
        analysis_type=args.analysis_type,
        document_data=sample_data,
        risk_profile=args.risk_profile,
        investment_amount=args.investment_amount
    )
    
    if result.get('status') == 'success':
        print(f"Analysis Date: {result.get('analysis_date')}")
        
        if args.analysis_type == 'portfolio':
            print_portfolio_analysis(result)
        elif args.analysis_type == 'financial_statements':
            print_financial_statements_analysis(result)
        elif args.analysis_type == 'salary':
            print_salary_analysis(result)
        elif args.analysis_type == 'investment_suggestion':
            print_investment_suggestions(result)
    else:
        print(f"Analysis Error: {result.get('message')}")
    
    print("\nTest completed successfully!")
    return 0

def print_portfolio_analysis(result):
    """Print portfolio analysis results."""
    # Basic analysis
    basic_analysis = result.get('basic_analysis', {})
    print("\n=== Basic Portfolio Analysis ===")
    print(f"Total Value: ${basic_analysis.get('total_value', 0):,.2f}")
    print(f"Security Count: {basic_analysis.get('security_count', 0)}")
    
    # Asset allocation
    asset_allocation = result.get('asset_allocation', {})
    current_allocation = asset_allocation.get('current_allocation', {})
    print("\n=== Asset Allocation ===")
    for asset_type, percentage in current_allocation.items():
        print(f"{asset_type.capitalize()}: {percentage:.2f}%")
    
    # Performance
    performance = result.get('performance', {})
    print("\n=== Performance ===")
    if performance.get('average_return') is not None:
        print(f"Average Return: {performance.get('average_return', 0):.2f}%")
    if performance.get('total_return') is not None:
        print(f"Total Return: {performance.get('total_return', 0):.2f}%")
    
    # Risk analysis
    risk_analysis = result.get('risk_analysis', {})
    print("\n=== Risk Analysis ===")
    print(f"Risk Level: {risk_analysis.get('risk_level', 'unknown')}")
    print(f"Risk Profile: {risk_analysis.get('risk_profile', 'unknown')}")
    print(f"Risk Profile Match: {risk_analysis.get('risk_profile_match', False)}")
    
    # Recommendations
    recommendations = result.get('recommendations', [])
    print("\n=== Recommendations ===")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. [{rec.get('priority', 'medium')}] {rec.get('title', '')}")
        print(f"   {rec.get('description', '')}")
        print(f"   Action: {rec.get('action', '')}")
        print()

def print_financial_statements_analysis(result):
    """Print financial statements analysis results."""
    # Balance sheet analysis
    balance_sheet_analysis = result.get('balance_sheet_analysis', {})
    print("\n=== Balance Sheet Analysis ===")
    print(f"Total Assets: ${balance_sheet_analysis.get('total_assets', 0):,.2f}")
    print(f"Total Liabilities: ${balance_sheet_analysis.get('total_liabilities', 0):,.2f}")
    print(f"Total Equity: ${balance_sheet_analysis.get('total_equity', 0):,.2f}")
    
    if balance_sheet_analysis.get('current_ratio') is not None:
        print(f"Current Ratio: {balance_sheet_analysis.get('current_ratio', 0):.2f}")
    if balance_sheet_analysis.get('debt_to_equity') is not None:
        print(f"Debt to Equity: {balance_sheet_analysis.get('debt_to_equity', 0):.2f}")
    
    # Income statement analysis
    income_statement_analysis = result.get('income_statement_analysis', {})
    print("\n=== Income Statement Analysis ===")
    print(f"Total Revenue: ${income_statement_analysis.get('total_revenue', 0):,.2f}")
    print(f"Total Expenses: ${income_statement_analysis.get('total_expenses', 0):,.2f}")
    print(f"Net Profit: ${income_statement_analysis.get('net_profit', 0):,.2f}")
    
    if income_statement_analysis.get('profit_margin') is not None:
        print(f"Profit Margin: {income_statement_analysis.get('profit_margin', 0):.2f}%")
    
    # Financial ratios
    financial_ratios = result.get('financial_ratios', {})
    if financial_ratios:
        print("\n=== Financial Ratios ===")
        
        # Liquidity ratios
        liquidity_ratios = financial_ratios.get('liquidity_ratios', {})
        if liquidity_ratios:
            print("Liquidity Ratios:")
            for name, value in liquidity_ratios.items():
                print(f"  {name}: {value:.2f}")
        
        # Profitability ratios
        profitability_ratios = financial_ratios.get('profitability_ratios', {})
        if profitability_ratios:
            print("Profitability Ratios:")
            for name, value in profitability_ratios.items():
                print(f"  {name}: {value:.2f}%")
        
        # Solvency ratios
        solvency_ratios = financial_ratios.get('solvency_ratios', {})
        if solvency_ratios:
            print("Solvency Ratios:")
            for name, value in solvency_ratios.items():
                print(f"  {name}: {value:.2f}%")

def print_salary_analysis(result):
    """Print salary analysis results."""
    # Basic analysis
    basic_analysis = result.get('basic_analysis', {})
    print("\n=== Basic Salary Analysis ===")
    print(f"Gross Salary: ${basic_analysis.get('gross_salary', 0):,.2f}")
    print(f"Net Salary: ${basic_analysis.get('net_salary', 0):,.2f}")
    print(f"Total Deductions: ${basic_analysis.get('deduction_total', 0):,.2f} ({basic_analysis.get('deduction_percentage', 0):.2f}%)")
    print(f"Total Additions: ${basic_analysis.get('addition_total', 0):,.2f}")
    print(f"Effective Tax Rate: {basic_analysis.get('effective_tax_rate', 0):.2f}%")
    
    # Pension analysis
    pension_analysis = result.get('pension_analysis', {})
    print("\n=== Pension Analysis ===")
    print(f"Pension Contribution: ${pension_analysis.get('pension_contribution', 0):,.2f}")
    print(f"Further Education Contribution: ${pension_analysis.get('further_education_contribution', 0):,.2f}")
    print(f"Total Saving: ${pension_analysis.get('total_saving', 0):,.2f} ({pension_analysis.get('contribution_percentage', 0):.2f}%)")
    print(f"Recommended Contribution: ${pension_analysis.get('recommended_contribution', 0):,.2f}")
    
    # Tax analysis
    tax_analysis = result.get('tax_analysis', {})
    print("\n=== Tax Analysis ===")
    print(f"Income Tax: ${tax_analysis.get('income_tax', 0):,.2f}")
    print(f"Social Security: ${tax_analysis.get('social_security', 0):,.2f}")
    print(f"Health Insurance: ${tax_analysis.get('health_insurance', 0):,.2f}")
    print(f"Total Tax: ${tax_analysis.get('total_tax', 0):,.2f} ({tax_analysis.get('tax_percentage', 0):.2f}%)")
    print(f"Tax Bracket: {tax_analysis.get('tax_bracket', 'unknown')}")
    
    # Recommendations
    recommendations = result.get('recommendations', [])
    print("\n=== Recommendations ===")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. [{rec.get('priority', 'medium')}] {rec.get('title', '')}")
        print(f"   {rec.get('description', '')}")
        print(f"   Action: {rec.get('action', '')}")
        print()

def print_investment_suggestions(result):
    """Print investment suggestions."""
    print(f"\n=== Investment Suggestions (${result.get('investment_amount', 0):,.2f}) ===")
    print(f"Risk Profile: {result.get('risk_profile', 'medium')}")
    
    # Target allocation
    target_allocation = result.get('target_allocation', {})
    print("\n=== Target Allocation ===")
    for asset_type, percentage in target_allocation.items():
        print(f"{asset_type.capitalize()}: {percentage:.2f}%")
    
    # Suggestions
    suggestions = result.get('suggestions', [])
    print("\n=== Specific Suggestions ===")
    for i, suggestion in enumerate(suggestions, 1):
        if suggestion.get('type') == 'asset_type':
            print(f"{i}. {suggestion.get('title', '')}")
            print(f"   Description: {suggestion.get('description', '')}")
            print(f"   Allocation: ${suggestion.get('allocation_amount', 0):,.2f} ({suggestion.get('allocation_percentage', 0):.2f}%)")
            print("   Specific Suggestions:")
            for j, specific in enumerate(suggestion.get('specific_suggestions', []), 1):
                print(f"     {j}. {specific}")
            print()
        elif suggestion.get('type') == 'general':
            print(f"{i}. {suggestion.get('title', '')}")
            print(f"   Description: {suggestion.get('description', '')}")
            print("   General Advice:")
            for j, specific in enumerate(suggestion.get('specific_suggestions', []), 1):
                print(f"     {j}. {specific}")
            print()

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
    
    # Sample balance sheet data
    balance_sheet_data = pd.DataFrame({
        "Item": ["Cash and Cash Equivalents", "Accounts Receivable", "Inventory", "Property, Plant and Equipment", 
                "Total Assets", "Accounts Payable", "Short-term Debt", "Long-term Debt", "Total Liabilities", 
                "Common Stock", "Retained Earnings", "Total Equity"],
        "Value": [50000, 75000, 125000, 350000, 600000, 45000, 30000, 200000, 275000, 100000, 225000, 325000]
    })
    
    balance_sheet_table = {
        "id": "table_2",
        "type": "balance_sheet",
        "data": balance_sheet_data.to_dict(orient="records"),
        "columns": balance_sheet_data.columns.tolist(),
        "row_count": len(balance_sheet_data),
        "column_count": len(balance_sheet_data.columns)
    }
    
    # Sample income statement data
    income_statement_data = pd.DataFrame({
        "Item": ["Revenue", "Cost of Goods Sold", "Gross Profit", "Operating Expenses", "Operating Income", 
                "Interest Expense", "Income Before Tax", "Income Tax", "Net Income"],
        "Value": [500000, 300000, 200000, 120000, 80000, 15000, 65000, 15000, 50000]
    })
    
    income_statement_table = {
        "id": "table_3",
        "type": "income_statement",
        "data": income_statement_data.to_dict(orient="records"),
        "columns": income_statement_data.columns.tolist(),
        "row_count": len(income_statement_data),
        "column_count": len(income_statement_data.columns)
    }
    
    # Sample salary data
    salary_data = pd.DataFrame({
        "Item": ["Gross Salary", "Income Tax", "Social Security", "Health Insurance", "Pension", "Net Salary"],
        "Value": [10000, 2000, 700, 300, 500, 6500]
    })
    
    salary_table = {
        "id": "table_4",
        "type": "salary",
        "data": salary_data.to_dict(orient="records"),
        "columns": salary_data.columns.tolist(),
        "row_count": len(salary_data),
        "column_count": len(salary_data.columns)
    }
    
    # Add all tables
    tables_data.extend([balance_sheet_table, income_statement_table, salary_table])
    
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
        "summary": {
            "table_count": len(tables_data),
            "security_count": len(financial_data["portfolio"]["securities"]),
            "total_portfolio_value": financial_data["portfolio"]["summary"]["total_value"]
        }
    }
    
    return document_data

if __name__ == "__main__":
    sys.exit(main())
