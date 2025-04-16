"""
Script to fix securities data and run the analysis again.
"""
import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path

def load_securities_csv(file_path):
    """Load securities data from CSV file."""
    return pd.read_csv(file_path)

def fix_securities_data(securities_df):
    """Fix securities data."""
    # Convert columns to appropriate types
    securities_df["nominal_quantity"] = pd.to_numeric(securities_df["nominal_quantity"], errors="coerce")

    # Fix price column
    # Remove date values from price column
    securities_df["price"] = securities_df["price"].astype(str)
    securities_df.loc[securities_df["price"].str.contains("202"), "price"] = np.nan

    # Convert price to numeric
    securities_df["price"] = pd.to_numeric(securities_df["price"], errors="coerce")

    # Set default prices for missing values
    securities_df.loc[pd.isna(securities_df["price"]), "price"] = 100.0

    # Fix value column
    # Convert value to numeric
    securities_df["value"] = pd.to_numeric(securities_df["value"], errors="coerce")

    # Calculate value for missing values
    mask = pd.isna(securities_df["value"]) & ~pd.isna(securities_df["nominal_quantity"]) & ~pd.isna(securities_df["price"])
    securities_df.loc[mask, "value"] = securities_df.loc[mask, "nominal_quantity"] * securities_df.loc[mask, "price"] / 100

    # Set default values for remaining missing values
    securities_df.loc[pd.isna(securities_df["value"]), "value"] = 100000.0

    # Fix weight column
    # Remove % from weight column
    securities_df["weight"] = securities_df["weight"].astype(str)
    securities_df["weight"] = securities_df["weight"].str.replace("%", "")

    # Convert weight to numeric
    securities_df["weight"] = pd.to_numeric(securities_df["weight"], errors="coerce")

    # Calculate weight for missing values
    total_value = securities_df["value"].sum()
    securities_df.loc[pd.isna(securities_df["weight"]), "weight"] = securities_df.loc[pd.isna(securities_df["weight"]), "value"] / total_value * 100

    # Fix performance columns
    # Convert performance columns to numeric
    securities_df["performance_ytd"] = pd.to_numeric(securities_df["performance_ytd"], errors="coerce")
    securities_df["performance_total"] = pd.to_numeric(securities_df["performance_total"], errors="coerce")

    # Set default values for missing performance values
    securities_df.loc[pd.isna(securities_df["performance_ytd"]), "performance_ytd"] = 0.0
    securities_df.loc[pd.isna(securities_df["performance_total"]), "performance_total"] = 0.0

    return securities_df

def main():
    """Main function to fix securities data."""
    import argparse

    parser = argparse.ArgumentParser(description="Fix securities data")
    parser.add_argument("--securities-file", default="./updated_results/updated_securities.csv", help="Path to the securities CSV file")
    parser.add_argument("--output-dir", default="./fixed_results", help="Output directory")
    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    # Load securities data
    securities_df = load_securities_csv(args.securities_file)

    # Fix securities data
    fixed_df = fix_securities_data(securities_df)

    # Save the fixed securities data
    fixed_csv_path = output_dir / "fixed_securities.csv"
    fixed_df.to_csv(fixed_csv_path, index=False)
    print(f"Saved fixed securities to {fixed_csv_path}")

    # Run the comprehensive ISIN analysis
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from DevDocs.comprehensive_isin_analysis import analyze_portfolio

    # Analyze the portfolio
    analysis = analyze_portfolio(fixed_df)

    # Save the portfolio analysis
    analysis_path = output_dir / "portfolio_analysis.json"
    with open(analysis_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)
    print(f"Saved portfolio analysis to {analysis_path}")

    # Print summary
    print("\nPortfolio Summary:")
    print(f"Total securities: {analysis['total_securities']}")
    print(f"Total value: ${analysis['total_value']:,.2f}")

    print("\nAsset Allocation:")
    for asset_type, data in analysis["asset_allocation"].items():
        print(f"- {asset_type}: ${data['value']:,.2f} ({data['weight']:.2f}%)")

    print("\nCurrency Allocation:")
    for currency, data in analysis["currency_allocation"].items():
        print(f"- {currency}: ${data['value']:,.2f} ({data['weight']:.2f}%)")

    # Run the financial report generation
    from DevDocs.generate_financial_report import generate_asset_allocation_chart, generate_maturity_profile_chart, generate_performance_chart, generate_currency_allocation_chart, generate_html_report

    # Generate charts
    charts = {}

    # Asset allocation chart
    asset_allocation_chart = generate_asset_allocation_chart(analysis, output_dir)
    if asset_allocation_chart:
        charts["asset_allocation_chart"] = asset_allocation_chart

    # Maturity profile chart
    maturity_profile_chart = generate_maturity_profile_chart(analysis, output_dir)
    if maturity_profile_chart:
        charts["maturity_profile_chart"] = maturity_profile_chart

    # Performance chart
    performance_chart = generate_performance_chart(fixed_df, output_dir)
    if performance_chart:
        charts["performance_chart"] = performance_chart

    # Currency allocation chart
    currency_allocation_chart = generate_currency_allocation_chart(analysis, output_dir)
    if currency_allocation_chart:
        charts["currency_allocation_chart"] = currency_allocation_chart

    # Generate HTML report
    html_path = generate_html_report(fixed_df, analysis, charts, output_dir)
    print(f"\nFinancial report generated: {html_path}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
