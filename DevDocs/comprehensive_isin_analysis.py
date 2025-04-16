"""
Comprehensive ISIN analysis script to extract detailed security information.
"""
import os
import sys
import json
import re
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def extract_security_details(text_file):
    """Extract detailed security information from the text file."""
    print(f"Extracting security details from: {text_file}")

    # Read the text file
    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Dictionary to store security details by ISIN
    securities = {}

    # Extract ISINs
    isin_pattern = r"ISIN:\s+([A-Z0-9]+)"
    isin_matches = re.finditer(isin_pattern, text)

    for match in isin_matches:
        isin = match.group(1)

        # Get the surrounding text (500 characters before and after)
        start_pos = max(0, match.start() - 500)
        end_pos = min(len(text), match.end() + 500)
        surrounding_text = text[start_pos:end_pos]

        # Extract security details
        security = {
            "isin": isin,
            "description": "",
            "type": "",
            "currency": "",
            "nominal_quantity": "",
            "price": "",
            "value": "",
            "weight": "",
            "maturity": "",
            "coupon": "",
            "performance_ytd": "",
            "performance_total": ""
        }

        # Extract description
        desc_pattern = r"([A-Z][A-Z0-9\s\.\,\-\(\)\/\%]+)\s+ISIN:\s+" + re.escape(isin)
        desc_match = re.search(desc_pattern, surrounding_text)
        if desc_match:
            security["description"] = desc_match.group(1).strip()

        # Extract security type
        type_patterns = [
            r"Ordinary Bonds", r"Zero Bonds", r"Structured Bonds",
            r"Other convertible bonds", r"Ordinary Stocks",
            r"Structured products equity"
        ]
        for pattern in type_patterns:
            if re.search(pattern, surrounding_text):
                security["type"] = pattern
                break

        # Extract currency and nominal/quantity
        currency_pattern = r"([A-Z]{3})\s+([\d',]+)"
        currency_match = re.search(currency_pattern, surrounding_text)
        if currency_match:
            security["currency"] = currency_match.group(1)
            security["nominal_quantity"] = currency_match.group(2).replace("'", "").replace(",", "")

        # Extract price
        price_pattern = r"Actual Price.*?[\"']?([\d\.]+)[\"']?"
        price_match = re.search(price_pattern, surrounding_text)
        if price_match:
            security["price"] = price_match.group(1)

        # Extract value
        value_pattern = r"Valuation in price currency.*?[\"']?([\d',]+)[\"']?"
        value_match = re.search(value_pattern, surrounding_text)
        if value_match:
            security["value"] = value_match.group(1).replace("'", "").replace(",", "")

        # Extract weight
        weight_pattern = r"in %.*?[\"']?([\d\.]+)[\"']?%"
        weight_match = re.search(weight_pattern, surrounding_text)
        if weight_match:
            security["weight"] = weight_match.group(1)

        # Extract maturity
        maturity_pattern = r"Maturity:\s+(\d{2}\.\d{2}\.\d{4})"
        maturity_match = re.search(maturity_pattern, surrounding_text)
        if maturity_match:
            security["maturity"] = maturity_match.group(1)

        # Extract coupon
        coupon_pattern = r"Coupon:.*?(\d+\.\d+)%"
        coupon_match = re.search(coupon_pattern, surrounding_text)
        if coupon_match:
            security["coupon"] = coupon_match.group(1)

        # Extract performance YTD
        perf_ytd_pattern = r"Perf YTD.*?[\"']?([\d\.\-]+)[\"']?%"
        perf_ytd_match = re.search(perf_ytd_pattern, surrounding_text)
        if perf_ytd_match:
            security["performance_ytd"] = perf_ytd_match.group(1)

        # Extract performance total
        perf_total_pattern = r"Perf Total.*?[\"']?([\d\.\-]+)[\"']?%"
        perf_total_match = re.search(perf_total_pattern, surrounding_text)
        if perf_total_match:
            security["performance_total"] = perf_total_match.group(1)

        # Store the security details
        securities[isin] = security

    return securities

def create_securities_table(securities):
    """Create a structured table of securities."""
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(securities, orient='index')

    # Reorder columns
    columns = [
        "isin", "description", "type", "currency", "nominal_quantity",
        "price", "value", "weight", "maturity", "coupon",
        "performance_ytd", "performance_total"
    ]
    df = df[columns]

    # Convert numeric columns
    numeric_columns = ["price", "value", "weight", "coupon", "performance_ytd", "performance_total"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Sort by value (descending)
    df = df.sort_values(by="value", ascending=False)

    return df

def analyze_portfolio(securities_df):
    """Analyze the portfolio based on the securities table."""
    # Convert value column to numeric, coercing errors to NaN
    securities_df["value"] = pd.to_numeric(securities_df["value"], errors="coerce")

    # Calculate total value, handling NaN values
    total_value = securities_df["value"].sum()
    if pd.isna(total_value):
        total_value = 0

    # Convert performance columns to numeric
    securities_df["performance_ytd"] = pd.to_numeric(securities_df["performance_ytd"], errors="coerce")
    securities_df["performance_total"] = pd.to_numeric(securities_df["performance_total"], errors="coerce")

    # Calculate average performance, handling NaN values
    avg_ytd = securities_df["performance_ytd"].mean()
    avg_total = securities_df["performance_total"].mean()

    if pd.isna(avg_ytd):
        avg_ytd = 0
    if pd.isna(avg_total):
        avg_total = 0

    analysis = {
        "total_value": total_value,
        "total_securities": len(securities_df),
        "asset_allocation": {},
        "currency_allocation": {},
        "maturity_profile": {},
        "performance": {
            "average_ytd": avg_ytd,
            "average_total": avg_total,
            "best_performers": [],
            "worst_performers": []
        }
    }

    # Asset allocation
    if total_value > 0:
        # Filter out rows with NaN values
        valid_df = securities_df.dropna(subset=["type", "value"])

        # Group by type and sum values
        asset_types = valid_df.groupby("type")["value"].sum()

        for asset_type, value in asset_types.items():
            if asset_type and not pd.isna(value) and value > 0:
                analysis["asset_allocation"][asset_type] = {
                    "value": float(value),
                    "weight": (float(value) / total_value) * 100
                }

    # Currency allocation
    if total_value > 0:
        # Filter out rows with NaN values
        valid_df = securities_df.dropna(subset=["currency", "value"])

        # Group by currency and sum values
        currencies = valid_df.groupby("currency")["value"].sum()

        for currency, value in currencies.items():
            if currency and not pd.isna(value) and value > 0:
                analysis["currency_allocation"][currency] = {
                    "value": float(value),
                    "weight": (float(value) / total_value) * 100
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
                    "weight": (float(value) / bonds_total) * 100
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
    """Main function to run the comprehensive ISIN analysis."""
    import argparse

    parser = argparse.ArgumentParser(description="Comprehensive ISIN analysis")
    parser.add_argument("--text-file", default="messos.txt", help="Path to the text file")
    parser.add_argument("--output-dir", default="./isin_analysis", help="Output directory")
    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    # Extract security details
    securities = extract_security_details(args.text_file)

    # Save the raw security details
    securities_path = output_dir / "securities_details.json"
    with open(securities_path, "w", encoding="utf-8") as f:
        json.dump(securities, f, indent=2)
    print(f"Saved security details to {securities_path}")

    # Create securities table
    securities_df = create_securities_table(securities)

    # Save the securities table as CSV
    csv_path = output_dir / "securities_table.csv"
    securities_df.to_csv(csv_path, index=False)
    print(f"Saved securities table to {csv_path}")

    # Save the securities table as Excel
    excel_path = output_dir / "securities_table.xlsx"
    securities_df.to_excel(excel_path, index=False)
    print(f"Saved securities table to {excel_path}")

    # Analyze the portfolio
    analysis = analyze_portfolio(securities_df)

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

    print("\nMaturity Profile:")
    for year, data in analysis["maturity_profile"].items():
        print(f"- {year}: ${data['value']:,.2f} ({data['weight']:.2f}%)")

    print("\nPerformance:")
    print(f"Average YTD: {analysis['performance']['average_ytd']:.2f}%")
    print(f"Average Total: {analysis['performance']['average_total']:.2f}%")

    return 0

if __name__ == "__main__":
    sys.exit(main())
