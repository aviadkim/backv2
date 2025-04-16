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

def analyze_portfolio(securities_df):
    """Analyze the portfolio based on the securities table."""
    # Calculate total value
    total_value = securities_df["value"].sum()
    
    # Calculate average performance
    avg_ytd = securities_df["performance_ytd"].mean()
    avg_total = securities_df["performance_total"].mean()
    
    analysis = {
        "total_value": float(total_value),
        "total_securities": len(securities_df),
        "asset_allocation": {},
        "currency_allocation": {},
        "maturity_profile": {},
        "performance": {
            "average_ytd": float(avg_ytd),
            "average_total": float(avg_total),
            "best_performers": [],
            "worst_performers": []
        }
    }
    
    # Asset allocation
    # Group by type and sum values
    asset_types = securities_df.groupby("type")["value"].sum()
    
    for asset_type, value in asset_types.items():
        if asset_type and not pd.isna(value) and value > 0:
            analysis["asset_allocation"][asset_type] = {
                "value": float(value),
                "weight": float((value / total_value) * 100)
            }
    
    # Currency allocation
    # Group by currency and sum values
    currencies = securities_df.groupby("currency")["value"].sum()
    
    for currency, value in currencies.items():
        if currency and not pd.isna(value) and value > 0:
            analysis["currency_allocation"][currency] = {
                "value": float(value),
                "weight": float((value / total_value) * 100)
            }
    
    # Maturity profile (for bonds)
    bonds_df = securities_df[securities_df["type"].str.contains("Bonds", na=False)]
    if not bonds_df.empty:
        # Convert maturity to datetime
        bonds_df["maturity_date"] = pd.to_datetime(bonds_df["maturity"], format="%d.%m.%Y", errors='coerce')
        
        # Group by year
        bonds_df["maturity_year"] = bonds_df["maturity_date"].dt.year
        maturity_years = bonds_df.groupby("maturity_year")["value"].sum()
        
        bonds_total = bonds_df["value"].sum()
        if pd.isna(bonds_total) or bonds_total == 0:
            bonds_total = 1  # Avoid division by zero
        
        for year, value in maturity_years.items():
            if pd.notna(year) and pd.notna(value) and value > 0:
                analysis["maturity_profile"][str(int(year))] = {
                    "value": float(value),
                    "weight": float((value / bonds_total) * 100)
                }
    
    # Best and worst performers
    if not securities_df.empty:
        # Filter out rows with NaN performance values
        perf_ytd_df = securities_df.dropna(subset=["performance_ytd"])
        perf_total_df = securities_df.dropna(subset=["performance_total"])
        
        if not perf_ytd_df.empty:
            # YTD performance
            ytd_sorted = perf_ytd_df.sort_values(by="performance_ytd", ascending=False)
            analysis["performance"]["best_performers_ytd"] = ytd_sorted.head(5)[["isin", "description", "performance_ytd"]].to_dict(orient="records")
            analysis["performance"]["worst_performers_ytd"] = ytd_sorted.tail(5)[["isin", "description", "performance_ytd"]].to_dict(orient="records")
        
        if not perf_total_df.empty:
            # Total performance
            total_sorted = perf_total_df.sort_values(by="performance_total", ascending=False)
            analysis["performance"]["best_performers_total"] = total_sorted.head(5)[["isin", "description", "performance_total"]].to_dict(orient="records")
            analysis["performance"]["worst_performers_total"] = total_sorted.tail(5)[["isin", "description", "performance_total"]].to_dict(orient="records")
    
    return analysis

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
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
