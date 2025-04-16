"""
Create a comprehensive financial report from extracted data.
"""
import os
import json
import sys
import re
from datetime import datetime

def load_data():
    """Load extracted data."""
    securities = []
    portfolio_value = None
    
    # Try to load from portfolio_data_simple
    try:
        with open('portfolio_data_simple/securities.json', 'r', encoding='utf-8') as f:
            securities = json.load(f)
        
        with open('portfolio_data_simple/summary.json', 'r', encoding='utf-8') as f:
            summary = json.load(f)
            portfolio_value = summary.get('portfolio_value')
    except Exception as e:
        print(f"Error loading data: {str(e)}")
    
    return securities, portfolio_value

def clean_securities(securities):
    """Clean and validate securities data."""
    cleaned = []
    
    for security in securities:
        # Skip securities with no value
        if not security.get('value'):
            continue
        
        # Clean up name
        name = security.get('name', '')
        if name:
            # Remove newlines and extra spaces
            name = re.sub(r'\s+', ' ', name).strip()
            
            # Limit length
            if len(name) > 50:
                name = name[:47] + '...'
            
            security['name'] = name
        
        cleaned.append(security)
    
    return cleaned

def categorize_securities(securities):
    """Categorize securities by type."""
    categories = {
        'Bonds': [],
        'Equities': [],
        'Structured Products': [],
        'Other': []
    }
    
    for security in securities:
        name = security.get('name', '').lower()
        isin = security.get('isin', '')
        
        if 'bond' in name or 'note' in name:
            categories['Bonds'].append(security)
        elif 'equity' in name or 'stock' in name or 'share' in name:
            categories['Equities'].append(security)
        elif 'structured' in name or 'product' in name or 'certificate' in name:
            categories['Structured Products'].append(security)
        else:
            categories['Other'].append(security)
    
    return categories

def calculate_asset_allocation(categories):
    """Calculate asset allocation."""
    allocation = {}
    total = 0
    
    for category, securities in categories.items():
        category_value = sum(security.get('value', 0) for security in securities)
        allocation[category] = category_value
        total += category_value
    
    # Calculate percentages
    percentages = {}
    for category, value in allocation.items():
        percentages[category] = (value / total * 100) if total > 0 else 0
    
    return {
        'values': allocation,
        'percentages': percentages,
        'total': total
    }

def create_html_report(securities, portfolio_value, categories, asset_allocation):
    """Create HTML report."""
    # Create output directory
    output_dir = 'comprehensive_report'
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate total from securities
    total_from_securities = sum(security.get('value', 0) for security in securities)
    
    # Calculate discrepancy
    discrepancy = 0
    discrepancy_pct = 0
    if portfolio_value and total_from_securities:
        discrepancy = portfolio_value - total_from_securities
        discrepancy_pct = (discrepancy / portfolio_value) * 100
    
    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Comprehensive Financial Report</title>
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
            .warning {{
                color: #dc3545;
            }}
            .chart {{
                width: 100%;
                height: 20px;
                background-color: #e9ecef;
                margin-bottom: 10px;
                border-radius: 5px;
                overflow: hidden;
            }}
            .chart-segment {{
                height: 100%;
                float: left;
                text-align: center;
                color: white;
                font-weight: bold;
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
            <h1>Comprehensive Financial Report</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="summary-box">
                <h2>Portfolio Summary</h2>
                <p>Portfolio Value: <span class="value">${portfolio_value:,.2f}</span></p>
                <p>Total from Securities: <span class="value">${total_from_securities:,.2f}</span></p>
                <p>Discrepancy: <span class="{('warning' if abs(discrepancy_pct) > 5 else 'value')}">${discrepancy:,.2f} ({discrepancy_pct:.2f}%)</span></p>
                <p>Number of Securities: <span class="value">{len(securities)}</span></p>
            </div>
            
            <h2>Asset Allocation</h2>
            <div class="chart">
    """
    
    # Add chart segments
    colors = {
        'Bonds': '#007bff',
        'Equities': '#28a745',
        'Structured Products': '#fd7e14',
        'Other': '#6c757d'
    }
    
    for category, percentage in asset_allocation['percentages'].items():
        if percentage > 0:
            html_content += f"""
                <div class="chart-segment" style="width: {percentage}%; background-color: {colors.get(category, '#6c757d')};">
                    {percentage:.1f}%
                </div>
            """
    
    html_content += """
            </div>
            <table>
                <tr>
                    <th>Asset Class</th>
                    <th>Value</th>
                    <th>Percentage</th>
                </tr>
    """
    
    # Add asset allocation rows
    for category, value in asset_allocation['values'].items():
        percentage = asset_allocation['percentages'].get(category, 0)
        html_content += f"""
                <tr>
                    <td>{category}</td>
                    <td>${value:,.2f}</td>
                    <td>{percentage:.2f}%</td>
                </tr>
        """
    
    html_content += f"""
                <tr style="font-weight: bold;">
                    <td>Total</td>
                    <td>${asset_allocation['total']:,.2f}</td>
                    <td>100.00%</td>
                </tr>
            </table>
    """
    
    # Add securities by category
    for category, category_securities in categories.items():
        if category_securities:
            html_content += f"""
            <h2>{category}</h2>
            <table>
                <tr>
                    <th>ISIN</th>
                    <th>Name</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Value</th>
                    <th>% of Portfolio</th>
                </tr>
            """
            
            # Sort by value
            category_securities.sort(key=lambda x: x.get('value', 0), reverse=True)
            
            for security in category_securities:
                isin = security.get('isin', 'N/A')
                name = security.get('name', 'N/A')
                quantity = security.get('quantity')
                price = security.get('price')
                value = security.get('value', 0)
                
                percentage = (value / total_from_securities * 100) if total_from_securities > 0 else 0
                
                quantity_str = f"{quantity:,.2f}" if quantity else 'N/A'
                price_str = f"${price:,.2f}" if price else 'N/A'
                
                html_content += f"""
                <tr>
                    <td>{isin}</td>
                    <td>{name}</td>
                    <td>{quantity_str}</td>
                    <td>{price_str}</td>
                    <td>${value:,.2f}</td>
                    <td>{percentage:.2f}%</td>
                </tr>
                """
            
            html_content += """
            </table>
            """
    
    html_content += """
            <div class="footer">
                <p>This report is for informational purposes only. Please consult with a financial advisor before making investment decisions.</p>
                <p>Generated using high-accuracy financial document processing.</p>
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

def main():
    """Main function."""
    print("Creating comprehensive financial report...")
    
    # Load data
    securities, portfolio_value = load_data()
    
    if not securities:
        print("No securities data found")
        return 1
    
    if not portfolio_value:
        print("No portfolio value found")
        return 1
    
    # Clean securities
    securities = clean_securities(securities)
    print(f"Cleaned {len(securities)} securities")
    
    # Categorize securities
    categories = categorize_securities(securities)
    print(f"Categorized securities: {', '.join(f'{k}: {len(v)}' for k, v in categories.items())}")
    
    # Calculate asset allocation
    asset_allocation = calculate_asset_allocation(categories)
    print("Calculated asset allocation")
    
    # Create HTML report
    report_path = create_html_report(securities, portfolio_value, categories, asset_allocation)
    
    print(f"\nComprehensive report created: {report_path}")
    print(f"Open the report in your browser: file://{os.path.abspath(report_path)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
