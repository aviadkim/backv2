"""
Script to generate a comprehensive financial report.
"""
import os
import sys
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_securities_data(file_path):
    """Load securities data from CSV file."""
    return pd.read_csv(file_path)

def load_portfolio_analysis(file_path):
    """Load portfolio analysis from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_asset_allocation_chart(portfolio_analysis, output_dir):
    """Generate asset allocation chart."""
    # Extract asset allocation data
    asset_allocation = portfolio_analysis.get("asset_allocation", {})

    if not asset_allocation:
        print("No asset allocation data available.")
        return None

    # Create lists for the pie chart
    labels = []
    values = []

    for asset_type, data in asset_allocation.items():
        if asset_type and data and "value" in data and data["value"]:
            labels.append(asset_type)
            values.append(float(data["value"]))

    if not values or sum(values) == 0:
        print("No valid asset allocation values found.")
        return None

    # Create the pie chart
    plt.figure(figsize=(10, 8))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title('Asset Allocation')

    # Save the chart
    chart_path = output_dir / "asset_allocation_chart.png"
    plt.savefig(chart_path)
    plt.close()

    return chart_path

def generate_maturity_profile_chart(portfolio_analysis, output_dir):
    """Generate maturity profile chart."""
    # Extract maturity profile data
    maturity_profile = portfolio_analysis.get("maturity_profile", {})

    if not maturity_profile:
        print("No maturity profile data available.")
        return None

    # Create lists for the bar chart
    years = []
    values = []

    for year, data in maturity_profile.items():
        if year and data and "value" in data and data["value"]:
            years.append(year)
            values.append(float(data["value"]))

    if not values:
        print("No valid maturity profile values found.")
        return None

    # Create the bar chart
    plt.figure(figsize=(12, 6))
    plt.bar(years, values)
    plt.xlabel('Maturity Year')
    plt.ylabel('Value (USD)')
    plt.title('Maturity Profile')
    plt.xticks(rotation=45)

    # Add value labels on top of each bar
    for i, v in enumerate(values):
        plt.text(i, v + 0.1, f"${v:,.0f}", ha='center')

    plt.tight_layout()

    # Save the chart
    chart_path = output_dir / "maturity_profile_chart.png"
    plt.savefig(chart_path)
    plt.close()

    return chart_path

def generate_performance_chart(securities_df, output_dir):
    """Generate performance chart."""
    # Check if performance columns exist
    if "performance_ytd" not in securities_df.columns or "performance_total" not in securities_df.columns:
        print("Performance columns not found in securities data.")
        return None

    # Convert performance columns to numeric, coercing errors to NaN
    securities_df["performance_ytd"] = pd.to_numeric(securities_df["performance_ytd"], errors="coerce")
    securities_df["performance_total"] = pd.to_numeric(securities_df["performance_total"], errors="coerce")

    # Filter securities with performance data
    perf_df = securities_df.dropna(subset=["performance_ytd"])

    if len(perf_df) == 0:
        print("No valid performance data found.")
        return None

    # Sort by performance_ytd
    perf_df = perf_df.sort_values(by="performance_ytd", ascending=False)

    # Take top 10 and bottom 10 (or fewer if not enough data)
    top_count = min(10, len(perf_df))
    bottom_count = min(10, len(perf_df))

    top_10 = perf_df.head(top_count)
    bottom_10 = perf_df.tail(bottom_count)

    # Create the bar chart for YTD performance
    plt.figure(figsize=(14, 10))

    # Top performers
    plt.subplot(2, 1, 1)
    plt.barh(top_10["isin"], top_10["performance_ytd"], color='green')
    plt.xlabel('YTD Performance (%)')
    plt.title(f'Top {top_count} Performers (YTD)')
    plt.gca().invert_yaxis()  # Invert y-axis to show highest performer at the top

    # Add value labels
    for i, v in enumerate(top_10["performance_ytd"]):
        if not pd.isna(v):
            plt.text(v + 0.1, i, f"{v:.2f}%", va='center')

    # Bottom performers
    plt.subplot(2, 1, 2)
    plt.barh(bottom_10["isin"], bottom_10["performance_ytd"], color='red')
    plt.xlabel('YTD Performance (%)')
    plt.title(f'Bottom {bottom_count} Performers (YTD)')
    plt.gca().invert_yaxis()  # Invert y-axis to show lowest performer at the top

    # Add value labels
    for i, v in enumerate(bottom_10["performance_ytd"]):
        if not pd.isna(v):
            plt.text(v - 0.5, i, f"{v:.2f}%", va='center')

    plt.tight_layout()

    # Save the chart
    chart_path = output_dir / "performance_chart.png"
    plt.savefig(chart_path)
    plt.close()

    return chart_path

def generate_currency_allocation_chart(portfolio_analysis, output_dir):
    """Generate currency allocation chart."""
    # Extract currency allocation data
    currency_allocation = portfolio_analysis.get("currency_allocation", {})

    if not currency_allocation:
        print("No currency allocation data available.")
        return None

    # Create lists for the pie chart
    labels = []
    values = []

    for currency, data in currency_allocation.items():
        if currency and data and "value" in data and data["value"]:
            labels.append(currency)
            values.append(float(data["value"]))

    if not values or sum(values) == 0:
        print("No valid currency allocation values found.")
        return None

    # Create the pie chart
    plt.figure(figsize=(10, 8))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title('Currency Allocation')

    # Save the chart
    chart_path = output_dir / "currency_allocation_chart.png"
    plt.savefig(chart_path)
    plt.close()

    return chart_path

def generate_html_report(securities_df, portfolio_analysis, charts, output_dir):
    """Generate HTML report."""
    # Create the HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Financial Portfolio Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                color: #333;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid #eee;
            }}
            .summary-box {{
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 20px;
                margin-bottom: 30px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .summary-item {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
            }}
            .chart-container {{
                margin-bottom: 40px;
            }}
            .chart {{
                width: 100%;
                max-width: 800px;
                margin: 0 auto;
                display: block;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 30px;
            }}
            th, td {{
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .footer {{
                text-align: center;
                margin-top: 50px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #777;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Financial Portfolio Report</h1>
                <p>Generated on {datetime.now().strftime('%B %d, %Y')}</p>
            </div>

            <div class="summary-box">
                <h2>Portfolio Summary</h2>
                <div class="summary-item">
                    <span>Total Value:</span>
                    <span>${portfolio_analysis["total_value"]:,.2f}</span>
                </div>
                <div class="summary-item">
                    <span>Total Securities:</span>
                    <span>{portfolio_analysis["total_securities"]}</span>
                </div>
                <div class="summary-item">
                    <span>Average YTD Performance:</span>
                    <span>{portfolio_analysis["performance"]["average_ytd"]:.2f}%</span>
                </div>
                <div class="summary-item">
                    <span>Average Total Performance:</span>
                    <span>{portfolio_analysis["performance"]["average_total"]:.2f}%</span>
                </div>
            </div>

            <div class="chart-container">
                <h2>Asset Allocation</h2>
    """

    # Add asset allocation chart
    if "asset_allocation_chart" in charts:
        html_content += f"""
                <img src="{charts['asset_allocation_chart'].name}" alt="Asset Allocation" class="chart">
        """

    html_content += """
            </div>

            <div class="chart-container">
                <h2>Currency Allocation</h2>
    """

    # Add currency allocation chart
    if "currency_allocation_chart" in charts:
        html_content += f"""
                <img src="{charts['currency_allocation_chart'].name}" alt="Currency Allocation" class="chart">
        """

    html_content += """
            </div>

            <div class="chart-container">
                <h2>Maturity Profile</h2>
    """

    # Add maturity profile chart
    if "maturity_profile_chart" in charts:
        html_content += f"""
                <img src="{charts['maturity_profile_chart'].name}" alt="Maturity Profile" class="chart">
        """
    else:
        html_content += """
                <p>No maturity profile data available.</p>
        """

    html_content += """
            </div>

            <div class="chart-container">
                <h2>Performance</h2>
    """

    # Add performance chart
    if "performance_chart" in charts:
        html_content += f"""
                <img src="{charts['performance_chart'].name}" alt="Performance" class="chart">
        """

    html_content += """
            </div>

            <h2>Top 10 Holdings</h2>
            <table>
                <thead>
                    <tr>
                        <th>ISIN</th>
                        <th>Description</th>
                        <th>Type</th>
                        <th>Value (USD)</th>
                        <th>Weight (%)</th>
                        <th>YTD Performance (%)</th>
                    </tr>
                </thead>
                <tbody>
    """

    # Add top 10 holdings
    top_10 = securities_df.sort_values(by="value", ascending=False).head(10)
    for _, security in top_10.iterrows():
        html_content += f"""
                    <tr>
                        <td>{security["isin"]}</td>
                        <td>{security["description"]}</td>
                        <td>{security["type"]}</td>
                        <td>${security["value"]:,.2f}</td>
                        <td>{security["weight"]:.2f}%</td>
                        <td>{security["performance_ytd"]:.2f}%</td>
                    </tr>
        """

    html_content += """
                </tbody>
            </table>

            <h2>Asset Allocation Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Asset Type</th>
                        <th>Value (USD)</th>
                        <th>Weight (%)</th>
                    </tr>
                </thead>
                <tbody>
    """

    # Add asset allocation details
    for asset_type, data in portfolio_analysis["asset_allocation"].items():
        html_content += f"""
                    <tr>
                        <td>{asset_type}</td>
                        <td>${data["value"]:,.2f}</td>
                        <td>{data["weight"]:.2f}%</td>
                    </tr>
        """

    html_content += """
                </tbody>
            </table>

            <div class="footer">
                <p>This report was generated automatically. The information provided is for informational purposes only.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Save the HTML report
    html_path = output_dir / "financial_report.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return html_path

def main():
    """Main function to generate the financial report."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate financial report")
    parser.add_argument("--securities-file", default="./isin_analysis/securities_table.csv", help="Path to the securities CSV file")
    parser.add_argument("--analysis-file", default="./isin_analysis/portfolio_analysis.json", help="Path to the portfolio analysis JSON file")
    parser.add_argument("--output-dir", default="./financial_report", help="Output directory")
    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    # Load securities data
    securities_df = load_securities_data(args.securities_file)

    # Load portfolio analysis
    portfolio_analysis = load_portfolio_analysis(args.analysis_file)

    # Generate charts
    charts = {}

    # Asset allocation chart
    asset_allocation_chart = generate_asset_allocation_chart(portfolio_analysis, output_dir)
    if asset_allocation_chart:
        charts["asset_allocation_chart"] = asset_allocation_chart

    # Maturity profile chart
    maturity_profile_chart = generate_maturity_profile_chart(portfolio_analysis, output_dir)
    if maturity_profile_chart:
        charts["maturity_profile_chart"] = maturity_profile_chart

    # Performance chart
    performance_chart = generate_performance_chart(securities_df, output_dir)
    if performance_chart:
        charts["performance_chart"] = performance_chart

    # Currency allocation chart
    currency_allocation_chart = generate_currency_allocation_chart(portfolio_analysis, output_dir)
    if currency_allocation_chart:
        charts["currency_allocation_chart"] = currency_allocation_chart

    # Generate HTML report
    html_path = generate_html_report(securities_df, portfolio_analysis, charts, output_dir)

    print(f"Financial report generated: {html_path}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
