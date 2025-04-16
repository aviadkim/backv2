"""
Bank Report Agent - Generates bank-like financial reports.
"""
import os
import json
from datetime import datetime

class BankReportAgent:
    """Agent that generates bank-like financial reports."""

    def __init__(self):
        self.document_structure = None
        self.financial_values = None
        self.securities = None
        self.validation_results = None

    def process(self, document_structure=None, financial_values=None, securities=None, validation_results=None):
        """Generate a bank-like financial report."""
        print("Bank Report Agent: Generating bank-like financial report...")

        # Load document structure if provided
        if document_structure:
            self.document_structure = document_structure
        else:
            # Try to load from file
            try:
                with open('agent_results/document_structure.json', 'r', encoding='utf-8') as f:
                    self.document_structure = json.load(f)
            except:
                self.document_structure = None

        # Load financial values if provided
        if financial_values:
            self.financial_values = financial_values
        else:
            # Try to load from file
            try:
                with open('agent_results/financial_values.json', 'r', encoding='utf-8') as f:
                    self.financial_values = json.load(f)
            except:
                self.financial_values = None

        # Load securities if provided
        if securities:
            self.securities = securities
        else:
            # Try to load from file
            try:
                with open('agent_results/securities.json', 'r', encoding='utf-8') as f:
                    self.securities = json.load(f)
            except:
                self.securities = None

        # Load validation results if provided
        if validation_results:
            self.validation_results = validation_results
        else:
            # Try to load from file
            try:
                with open('agent_results/validation_results.json', 'r', encoding='utf-8') as f:
                    self.validation_results = json.load(f)
            except:
                self.validation_results = None

        # Generate HTML report
        html_report = self._generate_html_report()

        # Save report
        output_dir = 'agent_results'
        os.makedirs(output_dir, exist_ok=True)

        report_path = os.path.join(output_dir, 'bank_financial_report.html')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_report)

        print(f"Bank Report Agent: Financial report generated at {report_path}")

        return report_path

    def _generate_html_report(self):
        """Generate HTML report."""
        # Get portfolio value
        portfolio_value = None
        if self.validation_results and 'validated_portfolio_value' in self.validation_results:
            portfolio_value = self.validation_results['validated_portfolio_value']
        elif self.financial_values and 'portfolio_value' in self.financial_values:
            portfolio_value = self.financial_values['portfolio_value']

        # Get securities total
        securities_total = None
        if self.validation_results and 'validated_securities_total' in self.validation_results:
            securities_total = self.validation_results['validated_securities_total']
        elif self.securities and 'total_value' in self.securities:
            securities_total = self.securities['total_value']

        # Get confidence scores
        confidence_scores = {}
        if self.validation_results and 'confidence_scores' in self.validation_results:
            confidence_scores = self.validation_results['confidence_scores']

        # Get document metadata
        document_type = None
        document_date = None
        client_info = {}
        if self.document_structure:
            document_type = self.document_structure.get('document_type')
            document_date = self.document_structure.get('document_date')
            client_info = self.document_structure.get('client_info', {})

        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Investment Portfolio Statement</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap');

                :root {{
                    --primary-color: #003366;
                    --secondary-color: #0066cc;
                    --accent-color: #ff9900;
                    --light-gray: #f5f5f5;
                    --medium-gray: #e0e0e0;
                    --dark-gray: #333333;
                    --success-color: #28a745;
                    --warning-color: #ffc107;
                    --danger-color: #dc3545;
                }}

                body {{
                    font-family: 'Open Sans', Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    color: var(--dark-gray);
                    background-color: #f9f9f9;
                }}

                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: white;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
                }}

                .header {{
                    background-color: var(--primary-color);
                    color: white;
                    padding: 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}

                .logo {{
                    font-size: 24px;
                    font-weight: 700;
                }}

                .document-info {{
                    text-align: right;
                }}

                h1, h2, h3, h4 {{
                    color: var(--primary-color);
                    margin-top: 30px;
                }}

                .summary-box {{
                    background-color: var(--light-gray);
                    border-left: 5px solid var(--primary-color);
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}

                .value {{
                    font-size: 24px;
                    font-weight: 700;
                    color: var(--primary-color);
                }}

                .warning {{
                    color: var(--danger-color);
                }}

                .chart-container {{
                    margin: 30px 0;
                }}

                .chart {{
                    width: 100%;
                    height: 30px;
                    background-color: var(--medium-gray);
                    border-radius: 15px;
                    overflow: hidden;
                    margin-bottom: 15px;
                }}

                .chart-segment {{
                    height: 100%;
                    float: left;
                    text-align: center;
                    color: white;
                    font-weight: 600;
                    line-height: 30px;
                    font-size: 14px;
                }}

                .chart-legend {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px;
                    margin-top: 10px;
                }}

                .legend-item {{
                    display: flex;
                    align-items: center;
                    margin-right: 15px;
                }}

                .legend-color {{
                    width: 15px;
                    height: 15px;
                    border-radius: 3px;
                    margin-right: 5px;
                }}

                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}

                th {{
                    background-color: var(--primary-color);
                    color: white;
                    padding: 12px 15px;
                    text-align: left;
                }}

                td {{
                    padding: 10px 15px;
                    border-bottom: 1px solid var(--medium-gray);
                }}

                tr:nth-child(even) {{
                    background-color: var(--light-gray);
                }}

                tr:hover {{
                    background-color: rgba(0, 102, 204, 0.1);
                }}

                .footer {{
                    margin-top: 50px;
                    padding: 20px;
                    background-color: var(--primary-color);
                    color: white;
                    text-align: center;
                    font-size: 14px;
                }}

                .disclaimer {{
                    font-size: 12px;
                    color: #666;
                    margin-top: 30px;
                    padding: 15px;
                    border: 1px solid var(--medium-gray);
                    border-radius: 5px;
                }}

                .performance-indicator {{
                    display: inline-block;
                    width: 10px;
                    height: 10px;
                    border-radius: 50%;
                    margin-right: 5px;
                }}

                .positive {{
                    background-color: var(--success-color);
                }}

                .negative {{
                    background-color: var(--danger-color);
                }}

                .neutral {{
                    background-color: var(--warning-color);
                }}

                @media print {{
                    body {{
                        background-color: white;
                    }}

                    .container {{
                        box-shadow: none;
                        padding: 0;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">GLOBAL INVESTMENT BANK</div>
                    <div class="document-info">
                        <div>Investment Portfolio Statement</div>
                        <div>{document_date or 'Statement Date: ' + datetime.now().strftime('%d.%m.%Y')}</div>
                    </div>
                </div>

                <div class="summary-box">
                    <h2>Portfolio Summary</h2>
                    <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                        <div style="flex: 1; min-width: 200px;">
                            <div style="margin-bottom: 15px;">
                                <div style="font-size: 14px; color: #666;">Total Portfolio Value</div>
                                <div class="value">${'{:,.2f}'.format(portfolio_value) if portfolio_value is not None else '0.00'}</div>
                            </div>
                            <div>
                                <div style="font-size: 14px; color: #666;">Number of Securities</div>
                                <div style="font-size: 18px; font-weight: 600;">{len(self.securities.get('securities', [])) if self.securities and 'securities' in self.securities else 0}</div>
                            </div>
                        </div>
                        <div style="flex: 1; min-width: 200px;">
                            <div style="margin-bottom: 15px;">
                                <div style="font-size: 14px; color: #666;">Account Number</div>
                                <div style="font-size: 18px; font-weight: 600;">{client_info.get('account', '12345-678')}</div>
                            </div>
                            <div>
                                <div style="font-size: 14px; color: #666;">Client Name</div>
                                <div style="font-size: 18px; font-weight: 600;">{client_info.get('name', 'Valued Client')}</div>
                            </div>
                        </div>
                    </div>
                </div>
        """

        # Add asset allocation
        if self.securities and 'asset_classes' in self.securities:
            html_content += """
                <h2>Asset Allocation</h2>
                <div class="chart-container">
                    <div class="chart">
            """

            # Define colors for asset classes
            colors = {
                'Bonds': '#0066cc',
                'Equities': '#28a745',
                'Structured Products': '#fd7e14',
                'Funds': '#6f42c1',
                'Cash': '#17a2b8',
                'Other': '#6c757d'
            }

            # Calculate total value
            total_value = sum(data['total_value'] for data in self.securities['asset_classes'].values())

            # Add chart segments
            for asset_class, data in self.securities['asset_classes'].items():
                if total_value > 0:
                    percentage = (data['total_value'] / total_value) * 100
                    color = colors.get(asset_class, '#6c757d')

                    html_content += f"""
                    <div class="chart-segment" style="width: {percentage}%; background-color: {color};">
                        {percentage:.1f}%
                    </div>
                    """

            html_content += """
                    </div>
                    <div class="chart-legend">
            """

            # Add legend
            for asset_class, data in self.securities['asset_classes'].items():
                if total_value > 0:
                    percentage = (data['total_value'] / total_value) * 100
                    color = colors.get(asset_class, '#6c757d')

                    html_content += f"""
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: {color};"></div>
                        <div>{asset_class}: {percentage:.1f}%</div>
                    </div>
                    """

            html_content += """
                    </div>
                </div>

                <table>
                    <tr>
                        <th>Asset Class</th>
                        <th>Value</th>
                        <th>Allocation</th>
                    </tr>
            """

            # Add asset allocation rows
            for asset_class, data in self.securities['asset_classes'].items():
                value = data['total_value']
                percentage = (value / total_value) * 100 if total_value > 0 else 0

                html_content += f"""
                    <tr>
                        <td>{asset_class}</td>
                        <td>${value:,.2f}</td>
                        <td>{percentage:.2f}%</td>
                    </tr>
                """

            html_content += f"""
                    <tr style="font-weight: bold;">
                        <td>Total</td>
                        <td>${total_value:,.2f}</td>
                        <td>100.00%</td>
                    </tr>
                </table>
            """

        # Add securities by asset class
        if self.securities and 'asset_classes' in self.securities:
            for asset_class, data in self.securities['asset_classes'].items():
                securities = data['securities']

                if securities:
                    html_content += f"""
                <h2>{asset_class} Holdings</h2>
                <table>
                    <tr>
                        <th>Security</th>
                        <th>ISIN</th>
                        <th>Quantity</th>
                        <th>Price</th>
                        <th>Value</th>
                        <th>% of Portfolio</th>
                    </tr>
                    """

                    # Sort by value
                    securities.sort(key=lambda x: x.get('value', 0) if x.get('value') else 0, reverse=True)

                    for security in securities:
                        isin = security.get('isin', 'N/A')
                        name = security.get('name', 'N/A')
                        quantity = security.get('quantity')
                        price = security.get('price')
                        value = security.get('value', 0)

                        portfolio_percentage = (value / portfolio_value) * 100 if portfolio_value and portfolio_value > 0 and value is not None else 0

                        quantity_str = f"{quantity:,.2f}" if quantity else 'N/A'
                        price_str = f"${price:,.2f}" if price else 'N/A'

                        html_content += f"""
                    <tr>
                        <td>{name}</td>
                        <td>{isin}</td>
                        <td>{quantity_str}</td>
                        <td>{price_str}</td>
                        <td>${'{:,.2f}'.format(value) if value is not None else '0.00'}</td>
                        <td>{portfolio_percentage:.2f}%</td>
                    </tr>
                        """

                    html_content += """
                </table>
                    """

        # Add disclaimer and footer
        html_content += """
                <div class="disclaimer">
                    <strong>Important Information:</strong> Past performance is not a reliable indicator of future results. The value of investments and the income from them can go down as well as up and investors may not get back the amount originally invested. This statement is for informational purposes only and does not constitute investment advice. Please consult with a financial advisor before making investment decisions.
                </div>

                <div class="footer">
                    <div>Global Investment Bank</div>
                    <div>123 Financial Street, New York, NY 10001</div>
                    <div>Tel: +1 (555) 123-4567 | Email: info@globalinvestmentbank.com</div>
                    <div>© 2025 Global Investment Bank. All rights reserved.</div>
                </div>
            </div>
        </body>
        </html>
        """

        return html_content

if __name__ == "__main__":
    agent = BankReportAgent()
    agent.process()
