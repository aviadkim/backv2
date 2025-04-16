"""
Create a comprehensive financial report from the extracted data.
"""
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def load_holdings():
    """Load holdings data from the fixed holdings file."""
    try:
        holdings_path = os.path.join('holdings_data_fixed', 'holdings.csv')
        if os.path.exists(holdings_path):
            return pd.read_csv(holdings_path)
        else:
            print(f"Holdings file not found: {holdings_path}")
            return None
    except Exception as e:
        print(f"Error loading holdings: {str(e)}")
        return None

def load_summary():
    """Load summary data from the fixed summary file."""
    try:
        summary_path = os.path.join('holdings_data_fixed', 'summary.json')
        if os.path.exists(summary_path):
            with open(summary_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"Summary file not found: {summary_path}")
            return None
    except Exception as e:
        print(f"Error loading summary: {str(e)}")
        return None

def calculate_asset_allocation(holdings):
    """Calculate asset allocation from holdings."""
    if holdings is None or holdings.empty:
        return {}

    # Group by asset class and sum values
    asset_allocation = holdings.groupby('asset_class')['value'].sum().to_dict()

    # Calculate percentages
    total = sum(asset_allocation.values())
    asset_allocation_pct = {k: v / total * 100 for k, v in asset_allocation.items()}

    return {
        'values': asset_allocation,
        'percentages': asset_allocation_pct
    }

def create_asset_allocation_chart(asset_allocation, output_dir):
    """Create asset allocation chart."""
    if not asset_allocation or 'percentages' not in asset_allocation:
        return

    # Create figure
    plt.figure(figsize=(10, 6))

    # Create pie chart
    labels = asset_allocation['percentages'].keys()
    sizes = asset_allocation['percentages'].values()

    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title('Asset Allocation')

    # Save chart
    chart_path = os.path.join(output_dir, 'asset_allocation.png')
    plt.savefig(chart_path)
    plt.close()

    return chart_path

def create_top_holdings_chart(holdings, output_dir, top_n=10):
    """Create top holdings chart."""
    if holdings is None or holdings.empty:
        return

    # Sort by value and take top N
    top_holdings = holdings.sort_values('value', ascending=False).head(top_n)

    # Create figure
    plt.figure(figsize=(12, 6))

    # Create bar chart
    bars = plt.bar(top_holdings['name'], top_holdings['value'])

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:,.0f}',
                ha='center', va='bottom', rotation=0)

    plt.xticks(rotation=45, ha='right')
    plt.title(f'Top {top_n} Holdings')
    plt.ylabel('Value (USD)')
    plt.tight_layout()

    # Save chart
    chart_path = os.path.join(output_dir, 'top_holdings.png')
    plt.savefig(chart_path)
    plt.close()

    return chart_path

def create_html_report(holdings, summary, asset_allocation, output_dir):
    """Create HTML report."""
    if holdings is None or holdings.empty:
        return

    # Calculate total portfolio value
    total_value = holdings['value'].sum()

    # Get reported portfolio value
    reported_value = summary.get('reported_portfolio_value', 0) if summary else 0

    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Financial Portfolio Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                color: #333;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            .summary-box {{
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 20px;
            }}
            .value {{
                font-size: 24px;
                font-weight: bold;
                color: #28a745;
            }}
            .chart-container {{
                margin: 20px 0;
                text-align: center;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px 15px;
                border-bottom: 1px solid #ddd;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                font-size: 12px;
                color: #6c757d;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Financial Portfolio Report</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <div class="summary-box">
                <h2>Portfolio Summary</h2>
                <p>Total Portfolio Value: <span class="value">${total_value:,.2f}</span></p>
                <p>Reported Portfolio Value: <span class="value">${reported_value:,.2f}</span></p>
                <p>Number of Securities: <span class="value">{len(holdings)}</span></p>
            </div>

            <h2>Asset Allocation</h2>
            <div class="chart-container">
                <img src="asset_allocation.png" alt="Asset Allocation" style="max-width: 100%;">
            </div>

            <h2>Top 10 Holdings</h2>
            <div class="chart-container">
                <img src="top_holdings.png" alt="Top 10 Holdings" style="max-width: 100%;">
            </div>

            <h2>Holdings Details</h2>
            <table>
                <tr>
                    <th>Security Name</th>
                    <th>ISIN</th>
                    <th>Asset Class</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Value</th>
                    <th>% of Portfolio</th>
                </tr>
    """

    # Add rows for each holding
    for _, row in holdings.sort_values('value', ascending=False).iterrows():
        name = row.get('name', 'N/A')
        isin = row.get('isin', 'N/A')
        asset_class = row.get('asset_class', 'N/A')
        quantity = row.get('quantity', 0)
        price = row.get('price', 0)
        value = row.get('value', 0)
        pct = value / total_value * 100 if total_value > 0 else 0

        # Format quantity and price with conditional logic
        if pd.isna(quantity) or quantity == 0:
            quantity_str = 'N/A'
        else:
            quantity_str = f"{quantity:,.2f}"

        if pd.isna(price) or price == 0:
            price_str = 'N/A'
        else:
            price_str = f"${price:,.2f}"

        html_content += f"""
                <tr>
                    <td>{name}</td>
                    <td>{isin}</td>
                    <td>{asset_class}</td>
                    <td>{quantity_str}</td>
                    <td>{price_str}</td>
                    <td>${value:,.2f}</td>
                    <td>{pct:.2f}%</td>
                </tr>
        """

    # Close the table and HTML
    html_content += """
            </table>

            <div class="footer">
                <p>This report is for informational purposes only. Please consult with a financial advisor before making investment decisions.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Save HTML report
    report_path = os.path.join(output_dir, 'financial_report.html')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return report_path

def create_financial_report():
    """Create a comprehensive financial report."""
    print("Creating financial report...")

    # Load data
    holdings = load_holdings()
    summary = load_summary()

    if holdings is None:
        print("Cannot create report without holdings data")
        return

    # Create output directory
    output_dir = 'financial_report'
    os.makedirs(output_dir, exist_ok=True)

    # Calculate asset allocation
    asset_allocation = calculate_asset_allocation(holdings)

    # Create charts
    create_asset_allocation_chart(asset_allocation, output_dir)
    create_top_holdings_chart(holdings, output_dir)

    # Create HTML report
    report_path = create_html_report(holdings, summary, asset_allocation, output_dir)

    print(f"Financial report created: {report_path}")

    return report_path

def main():
    """Main function."""
    report_path = create_financial_report()

    if report_path:
        print(f"\nOpen the report in your browser: file://{os.path.abspath(report_path)}")

    return 0

if __name__ == "__main__":
    main()
