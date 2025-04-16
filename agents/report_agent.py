"""
Report Agent - Generates comprehensive financial reports.
"""
import os
import json
from datetime import datetime

class ReportAgent:
    """Agent that generates comprehensive financial reports."""

    def __init__(self):
        self.document_structure = None
        self.financial_values = None
        self.securities = None
        self.validation_results = None

    def process(self, document_structure=None, financial_values=None, securities=None, validation_results=None):
        """Generate a comprehensive financial report."""
        print("Report Agent: Generating financial report...")

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

        report_path = os.path.join(output_dir, 'financial_report.html')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_report)

        print(f"Report Agent: Financial report generated at {report_path}")

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
                .warning {{
                    color: #dc3545;
                }}
                .confidence {{
                    display: inline-block;
                    width: 100px;
                    height: 10px;
                    background-color: #e9ecef;
                    border-radius: 5px;
                    margin-left: 10px;
                    position: relative;
                }}
                .confidence-level {{
                    height: 100%;
                    background-color: #28a745;
                    border-radius: 5px;
                    position: absolute;
                    top: 0;
                    left: 0;
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
                <h1>Financial Portfolio Report</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """

        # Add document metadata
        html_content += """
                <div class="summary-box">
                    <h2>Document Information</h2>
        """

        if document_type:
            html_content += f"""
                    <p>Document Type: {document_type}</p>
            """

        if document_date:
            html_content += f"""
                    <p>Document Date: {document_date}</p>
            """

        if client_info:
            html_content += """
                    <h3>Client Information</h3>
            """

            for key, value in client_info.items():
                html_content += f"""
                    <p>{key.capitalize()}: {value}</p>
                """

        html_content += """
                </div>
        """

        # Add portfolio summary
        html_content += """
                <div class="summary-box">
                    <h2>Portfolio Summary</h2>
        """

        if portfolio_value:
            confidence = confidence_scores.get('portfolio_value', 0.5) * 100
            html_content += f"""
                    <p>Portfolio Value: <span class="value">${portfolio_value:,.2f}</span>
                        <span class="confidence">
                            <span class="confidence-level" style="width: {confidence}%;"></span>
                        </span>
                    </p>
            """

        if securities_total:
            confidence = confidence_scores.get('securities', 0.5) * 100
            html_content += f"""
                    <p>Securities Total: <span class="value">${securities_total:,.2f}</span>
                        <span class="confidence">
                            <span class="confidence-level" style="width: {confidence}%;"></span>
                        </span>
                    </p>
            """

        if portfolio_value and securities_total:
            discrepancy = portfolio_value - securities_total
            discrepancy_pct = (discrepancy / portfolio_value) * 100 if portfolio_value else 0

            html_content += f"""
                    <p>Discrepancy: <span class="{('warning' if abs(discrepancy_pct) > 5 else 'value')}">${discrepancy:,.2f} ({discrepancy_pct:.2f}%)</span></p>
            """

        if self.securities and 'securities' in self.securities:
            html_content += f"""
                    <p>Number of Securities: <span class="value">{len(self.securities['securities'])}</span></p>
            """

        html_content += """
                </div>
        """

        # Add asset allocation
        if self.securities and 'asset_classes' in self.securities:
            html_content += """
                <h2>Asset Allocation</h2>
                <div class="chart">
            """

            # Define colors for asset classes
            colors = {
                'Bonds': '#007bff',
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
                <table>
                    <tr>
                        <th>Asset Class</th>
                        <th>Value</th>
                        <th>Percentage</th>
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
                <h2>{asset_class}</h2>
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
                    securities.sort(key=lambda x: x.get('value', 0) if x.get('value') else 0, reverse=True)

                    for security in securities:
                        isin = security.get('isin', 'N/A')
                        name = security.get('name', 'N/A')
                        quantity = security.get('quantity')
                        price = security.get('price')
                        value = security.get('value', 0) or 0

                        portfolio_percentage = (value / portfolio_value) * 100 if portfolio_value and portfolio_value > 0 and value is not None else 0

                        quantity_str = f"{quantity:,.2f}" if quantity else 'N/A'
                        price_str = f"${price:,.2f}" if price else 'N/A'

                        html_content += f"""
                    <tr>
                        <td>{isin}</td>
                        <td>{name}</td>
                        <td>{quantity_str}</td>
                        <td>{price_str}</td>
                        <td>${value:,.2f}</td>
                        <td>{portfolio_percentage:.2f}%</td>
                    </tr>
                        """

                    html_content += """
                </table>
                    """

        # Add validation issues
        if self.validation_results and 'issues' in self.validation_results and self.validation_results['issues']:
            html_content += """
                <h2>Validation Issues</h2>
                <table>
                    <tr>
                        <th>Type</th>
                        <th>Description</th>
                    </tr>
            """

            for issue in self.validation_results['issues']:
                html_content += f"""
                    <tr>
                        <td>{issue['type']}</td>
                        <td>{issue['description']}</td>
                    </tr>
                """

            html_content += """
                </table>
            """

        # Add footer
        html_content += """
                <div class="footer">
                    <p>This report is for informational purposes only. Please consult with a financial advisor before making investment decisions.</p>
                    <p>Generated using multi-agent financial document processing.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html_content

if __name__ == "__main__":
    agent = ReportAgent()
    agent.process()
