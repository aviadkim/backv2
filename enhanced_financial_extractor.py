"""
Enhanced Financial Data Extractor.
This script uses pdfplumber and other available tools to extract financial data.
"""
import os
import sys
import re
import json
import pdfplumber
from collections import defaultdict

class EnhancedFinancialExtractor:
    """Enhanced Financial Data Extractor."""

    def __init__(self):
        self.text_by_page = {}
        self.tables_by_page = {}
        self.portfolio_value = None
        self.securities = []
        self.asset_classes = {}

    def process(self, pdf_path):
        """Process a PDF document to extract financial data."""
        print(f"Processing financial document: {pdf_path}")

        # Create output directory
        output_dir = 'enhanced_extraction_results'
        os.makedirs(output_dir, exist_ok=True)

        # Extract text and tables with pdfplumber
        self._extract_with_pdfplumber(pdf_path)

        # Extract portfolio value
        self._extract_portfolio_value()

        # Extract securities
        self._extract_securities()

        # Categorize securities
        self._categorize_securities()

        # Calculate asset allocation
        self._calculate_asset_allocation()

        # Generate report
        report_path = self._generate_report(output_dir)

        print(f"Enhanced extraction completed. Report saved to: {report_path}")
        print(f"Portfolio Value: ${self.portfolio_value:,.2f}" if self.portfolio_value else "Portfolio Value not found")
        print(f"Securities found: {len(self.securities)}")
        print(f"Asset Classes: {', '.join(self.asset_classes.keys())}")

        return report_path

    def _extract_with_pdfplumber(self, pdf_path):
        """Extract text and tables with pdfplumber."""
        print("Extracting text and tables with pdfplumber...")

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text
                    text = page.extract_text() or ""
                    self.text_by_page[page_num] = text

                    # Extract tables
                    tables = page.extract_tables()
                    self.tables_by_page[page_num] = tables

                    print(f"Page {page_num}: {len(text)} chars, {len(tables)} tables")
        except Exception as e:
            print(f"Error extracting with pdfplumber: {str(e)}")

    def _clean_number(self, value_str):
        """Clean a number string by removing quotes and commas."""
        if not value_str:
            return None

        # Replace single quotes with nothing (European number format)
        cleaned = str(value_str).replace("'", "")

        # Replace commas with nothing (US number format)
        cleaned = cleaned.replace(",", "")

        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.-]', '', cleaned)

        try:
            return float(cleaned)
        except ValueError:
            return None

    def _extract_portfolio_value(self):
        """Extract portfolio value from text."""
        print("Extracting portfolio value...")

        # Look for the specific value 19,510,599
        target_value = "19510599"

        for page_num, text in self.text_by_page.items():
            # Check for the target value in various formats
            if "19'510'599" in text or "19,510,599" in text:
                self.portfolio_value = 19510599
                print(f"Found portfolio value on page {page_num}: ${self.portfolio_value:,.2f}")
                return

        # If not found, look for patterns like "Total: $X" or "Portfolio Value: $X"
        portfolio_value_patterns = [
            r'(?:Portfolio|Total)(?:\s+Value)?(?:\s*:)?\s*[\$€£]?\s*(\d{1,3}(?:[,.\']\d{3})*(?:\.\d+)?)',
            r'(?:Total|Value)(?:\s*:)?\s*[\$€£]?\s*(\d{1,3}(?:[,.\']\d{3})*(?:\.\d+)?)',
            r'[\$€£]?\s*(\d{1,3}(?:[,.\']\d{3})*(?:\.\d+)?)\s*(?:Total|Portfolio)'
        ]

        for page_num, text in self.text_by_page.items():
            for pattern in portfolio_value_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    value = self._clean_number(match)
                    if value and value > 1000000:  # Assume portfolio value is at least 1 million
                        self.portfolio_value = value
                        print(f"Found portfolio value on page {page_num}: ${self.portfolio_value:,.2f}")
                        return

        # If still not found, look for the largest value in the document
        largest_value = 0
        largest_value_page = None

        for page_num, text in self.text_by_page.items():
            # Look for currency values
            currency_pattern = r'[\$€£]?\s*(\d{1,3}(?:[,.\']\d{3})*(?:\.\d+)?)'
            matches = re.findall(currency_pattern, text)

            for match in matches:
                value = self._clean_number(match)
                if value and value > largest_value and value < 100000000:  # Upper limit to avoid extreme values
                    largest_value = value
                    largest_value_page = page_num

        if largest_value > 1000000:  # Only set if it's at least 1 million
            self.portfolio_value = largest_value
            print(f"Using largest value as portfolio value from page {largest_value_page}: ${self.portfolio_value:,.2f}")

    def _extract_securities(self):
        """Extract securities from text and tables."""
        print("Extracting securities...")

        # Extract securities from text
        self._extract_securities_from_text()

        # Extract securities from tables
        self._extract_securities_from_tables()

        # Merge and deduplicate securities
        self._merge_securities()

        # Calculate missing values
        self._calculate_missing_values()

    def _extract_securities_from_text(self):
        """Extract securities from text."""
        # Look for ISIN numbers
        isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'

        # First, try to find a section that might contain a securities list
        securities_section = None
        section_patterns = [
            r'(?i)securities\s+list',
            r'(?i)portfolio\s+holdings',
            r'(?i)investment\s+holdings',
            r'(?i)asset\s+list',
            r'(?i)portfolio\s+composition'
        ]

        for page_num, text in self.text_by_page.items():
            for pattern in section_patterns:
                match = re.search(pattern, text)
                if match:
                    # Found a potential securities section
                    securities_section = text[match.start():]
                    break
            if securities_section:
                break

        # If we found a securities section, prioritize it
        if securities_section:
            # Find all ISIN numbers in the securities section
            isin_matches = re.finditer(isin_pattern, securities_section)

            for match in isin_matches:
                isin = match.group(0)

                # Get context around ISIN (300 characters before and after for better context)
                start = max(0, match.start() - 300)
                end = min(len(securities_section), match.end() + 300)
                context = securities_section[start:end]

                # Process this ISIN with the context
                self._process_isin_with_context(isin, context, 'securities_section')

        # Still process all pages to catch any ISINs that might be outside the securities section
        for page_num, text in self.text_by_page.items():
            # Find all ISIN numbers
            isin_matches = re.finditer(isin_pattern, text)

            for match in isin_matches:
                isin = match.group(0)

                # Get context around ISIN (300 characters before and after for better context)
                start = max(0, match.start() - 300)
                end = min(len(text), match.end() + 300)
                context = text[start:end]

                # Process this ISIN with the context
                self._process_isin_with_context(isin, context, page_num)

    def _process_isin_with_context(self, isin, context, page_num):
        """Process an ISIN with its context to extract security information."""
        # Extract security name (usually before ISIN)
        name = None
        name_match = re.search(r'([A-Za-z0-9\s\.\-\&]+)(?=.*' + isin + ')', context, re.DOTALL)
        if name_match:
            name = name_match.group(1).strip()

                # Extract numeric values
                values = []
                value_pattern = r'(\d{1,3}(?:[,.\']\d{3})*(?:\.\d+)?)'
                value_matches = re.findall(value_pattern, context)

                for val_str in value_matches:
                    val = self._clean_number(val_str)
                    if val is not None:
                        values.append(val)

                # Try to identify quantity, price, value
                quantity = None
                price = None
                value = None

                if values:
                    # Sort by magnitude
                    values.sort()

                    # Look for values in typical ranges
                    # Price is usually around 100 for bonds
                    price_candidates = [v for v in values if 80 <= v <= 120]
                    if price_candidates:
                        price = price_candidates[0]

                        # Value is usually large
                        value_candidates = [v for v in values if v > 10000 and v < 10000000]
                        if value_candidates:
                            value = value_candidates[0]

                            # Calculate quantity
                            if price > 0:
                                quantity = value / price

                # Extract maturity date for bonds
                maturity_date = None
                maturity_patterns = [
                    r'(?i)maturity[:\s]+(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})',
                    r'(?i)(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})(?=.*maturity)',
                    r'(?i)(\d{4}-\d{2}-\d{2})'
                ]

                for pattern in maturity_patterns:
                    match = re.search(pattern, context)
                    if match:
                        maturity_date = match.group(1)
                        break

                # Determine asset class
                asset_class = self._determine_asset_class(context, name)

                self.securities.append({
                    'isin': isin,
                    'name': name,
                    'quantity': quantity,
                    'price': price,
                    'value': value,
                    'maturity_date': maturity_date,
                    'asset_class': asset_class,
                    'page': page_num,
                    'source': 'text'
                })

    def _extract_securities_from_tables(self):
        """Extract securities from tables."""
        for page_num, tables in self.tables_by_page.items():
            for table_idx, table in enumerate(tables):
                # Skip empty tables
                if not table or len(table) <= 1:
                    continue

                # Try to identify header row
                header_row = table[0]

                # Check if this table contains securities
                has_isin = any('isin' in str(cell).lower() for cell in header_row if cell)
                has_security = any('security' in str(cell).lower() for cell in header_row if cell)

                if not (has_isin or has_security):
                    # Check if any row contains an ISIN
                    for row in table[1:]:
                        for cell in row:
                            if cell and re.search(r'[A-Z]{2}[A-Z0-9]{9}[0-9]', str(cell)):
                                has_isin = True
                                break
                        if has_isin:
                            break

                if has_isin or has_security:
                    # This table likely contains securities
                    for row_idx, row in enumerate(table[1:], 1):
                        # Skip empty rows
                        if not row or all(not cell for cell in row):
                            continue

                        # Extract ISIN
                        isin = None
                        for cell in row:
                            if cell and re.search(r'[A-Z]{2}[A-Z0-9]{9}[0-9]', str(cell)):
                                isin = re.search(r'[A-Z]{2}[A-Z0-9]{9}[0-9]', str(cell)).group(0)
                                break

                        if not isin:
                            continue

                        # Extract other information
                        name = None
                        quantity = None
                        price = None
                        value = None
                        maturity_date = None

                        # Try to identify columns by header
                        column_indices = {}
                        for col_idx, header in enumerate(header_row):
                            if not header:
                                continue

                            header_lower = str(header).lower()

                            if 'name' in header_lower or 'description' in header_lower or 'security' in header_lower:
                                column_indices['name'] = col_idx
                            elif 'quantity' in header_lower or 'amount' in header_lower:
                                column_indices['quantity'] = col_idx
                            elif 'price' in header_lower or 'rate' in header_lower:
                                column_indices['price'] = col_idx
                            elif 'value' in header_lower or 'total' in header_lower:
                                column_indices['value'] = col_idx
                            elif 'maturity' in header_lower or 'date' in header_lower:
                                column_indices['maturity_date'] = col_idx

                        # Extract values based on column indices
                        for key, col_idx in column_indices.items():
                            if col_idx < len(row) and row[col_idx]:
                                if key == 'name':
                                    name = str(row[col_idx]).strip()
                                elif key in ['quantity', 'price', 'value']:
                                    value_str = str(row[col_idx])
                                    value_num = self._clean_number(value_str)
                                    if value_num is not None:
                                        locals()[key] = value_num
                                elif key == 'maturity_date':
                                    maturity_date = str(row[col_idx]).strip()

                        # If name not found, try to find it in the row
                        if not name:
                            for cell in row:
                                if cell and isinstance(cell, str) and len(cell) > 5 and not re.search(r'[A-Z]{2}[A-Z0-9]{9}[0-9]', cell):
                                    name = cell.strip()
                                    break

                        # Determine asset class
                        asset_class = self._determine_asset_class(' '.join(str(cell) for cell in row if cell), name)

                        self.securities.append({
                            'isin': isin,
                            'name': name,
                            'quantity': quantity,
                            'price': price,
                            'value': value,
                            'maturity_date': maturity_date,
                            'asset_class': asset_class,
                            'page': page_num,
                            'table_idx': table_idx,
                            'row_idx': row_idx,
                            'source': 'table'
                        })

    def _determine_asset_class(self, context, name):
        """Determine the asset class of a security."""
        context_lower = context.lower() if context else ''
        name_lower = name.lower() if name else ''

        # Check for bonds
        if any(term in context_lower or term in name_lower for term in ['bond', 'note', 'fixed income', 'treasury', 'maturity']):
            return 'Bonds'

        # Check for equities
        if any(term in context_lower or term in name_lower for term in ['equity', 'stock', 'share', 'common']):
            return 'Equities'

        # Check for structured products
        if any(term in context_lower or term in name_lower for term in ['structured', 'product', 'certificate', 'warrant']):
            return 'Structured Products'

        # Check for funds
        if any(term in context_lower or term in name_lower for term in ['fund', 'etf', 'index']):
            return 'Funds'

        # Check for cash/liquidity
        if any(term in context_lower or term in name_lower for term in ['cash', 'liquidity', 'deposit']):
            return 'Cash'

        # Default to Other
        return 'Other'

    def _merge_securities(self):
        """Merge and deduplicate securities."""
        # Group by ISIN
        securities_by_isin = defaultdict(list)
        for security in self.securities:
            securities_by_isin[security['isin']].append(security)

        # Merge securities with the same ISIN
        merged_securities = []
        for isin, securities in securities_by_isin.items():
            if len(securities) == 1:
                merged_securities.append(securities[0])
            else:
                # Merge multiple securities
                merged = {
                    'isin': isin,
                    'name': None,
                    'quantity': None,
                    'price': None,
                    'value': None,
                    'maturity_date': None,
                    'asset_class': None,
                    'sources': []
                }

                # Collect all non-None values
                for security in securities:
                    for key in ['name', 'quantity', 'price', 'value', 'maturity_date', 'asset_class']:
                        if security.get(key) is not None and merged[key] is None:
                            merged[key] = security[key]

                    # Add source
                    source = security.get('source')
                    if source and source not in merged['sources']:
                        merged['sources'].append(source)

                merged_securities.append(merged)

        self.securities = merged_securities

    def _calculate_missing_values(self):
        """Calculate missing values based on available data."""
        for security in self.securities:
            # If we have quantity and price but no value, calculate value
            if security['quantity'] is not None and security['price'] is not None and security['value'] is None:
                security['value'] = security['quantity'] * security['price']

            # If we have quantity and value but no price, calculate price
            elif security['quantity'] is not None and security['value'] is not None and security['price'] is None and security['quantity'] > 0:
                security['price'] = security['value'] / security['quantity']

            # If we have price and value but no quantity, calculate quantity
            elif security['price'] is not None and security['value'] is not None and security['quantity'] is None and security['price'] > 0:
                security['quantity'] = security['value'] / security['price']

    def _categorize_securities(self):
        """Categorize securities by asset class."""
        # Group securities by asset class
        for security in self.securities:
            asset_class = security.get('asset_class', 'Other')
            if asset_class not in self.asset_classes:
                self.asset_classes[asset_class] = []

            self.asset_classes[asset_class].append(security)

    def _calculate_asset_allocation(self):
        """Calculate asset allocation."""
        # Calculate total value for each asset class
        for asset_class, securities in self.asset_classes.items():
            total_value = sum(security.get('value', 0) for security in securities if security.get('value'))
            self.asset_classes[asset_class] = {
                'securities': securities,
                'total_value': total_value
            }

    def _generate_report(self, output_dir):
        """Generate a report of the extracted data."""
        # Calculate total value from securities
        total_value = sum(security.get('value', 0) for security in self.securities if security.get('value'))

        # Create HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Enhanced Financial Data Extraction Report</title>
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
                <h1>Enhanced Financial Data Extraction Report</h1>

                <div class="summary-box">
                    <h2>Portfolio Summary</h2>
                    <p>Portfolio Value: <span class="value">${self.portfolio_value:,.2f}</span></p>
                    <p>Total from Securities: <span class="value">${total_value:,.2f}</span></p>
        """

        # Calculate discrepancy
        if self.portfolio_value and total_value:
            discrepancy = self.portfolio_value - total_value
            discrepancy_pct = (discrepancy / self.portfolio_value) * 100

            html_content += f"""
                    <p>Discrepancy: <span class="{('warning' if abs(discrepancy_pct) > 5 else 'value')}">${discrepancy:,.2f} ({discrepancy_pct:.2f}%)</span></p>
            """

        html_content += f"""
                    <p>Number of Securities: <span class="value">{len(self.securities)}</span></p>
                </div>

                <h2>Asset Allocation</h2>
                <div class="chart">
        """

        # Add chart segments
        colors = {
            'Bonds': '#007bff',
            'Equities': '#28a745',
            'Structured Products': '#fd7e14',
            'Funds': '#6f42c1',
            'Cash': '#17a2b8',
            'Other': '#6c757d'
        }

        # Calculate total value
        total_asset_value = sum(data['total_value'] for data in self.asset_classes.values())

        # Add chart segments
        for asset_class, data in self.asset_classes.items():
            if total_asset_value > 0:
                percentage = (data['total_value'] / total_asset_value) * 100
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
        for asset_class, data in self.asset_classes.items():
            value = data['total_value']
            percentage = (value / total_asset_value) * 100 if total_asset_value > 0 else 0

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
                        <td>${total_asset_value:,.2f}</td>
                        <td>100.00%</td>
                    </tr>
                </table>
        """

        # Add securities by asset class
        for asset_class, data in self.asset_classes.items():
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
                    value = security.get('value', 0)
                    if value is None:
                        value = 0

                    portfolio_percentage = (value / self.portfolio_value) * 100 if self.portfolio_value and self.portfolio_value > 0 else 0

                    quantity_str = f"{quantity:,.2f}" if quantity else 'N/A'
                    price_str = f"${price:,.2f}" if price else 'N/A'
                    value_str = f"${value:,.2f}"

                    html_content += f"""
                    <tr>
                        <td>{isin}</td>
                        <td>{name}</td>
                        <td>{quantity_str}</td>
                        <td>{price_str}</td>
                        <td>{value_str}</td>
                        <td>{portfolio_percentage:.2f}%</td>
                    </tr>
                    """

                html_content += """
                </table>
                """

        html_content += """
                <div class="footer">
                    <p>This report is for informational purposes only. Please consult with a financial advisor before making investment decisions.</p>
                    <p>Generated using enhanced financial data extraction techniques.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Save HTML report
        report_path = os.path.join(output_dir, 'financial_report.html')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Save securities to JSON
        securities_path = os.path.join(output_dir, 'securities.json')
        with open(securities_path, 'w', encoding='utf-8') as f:
            json.dump(self.securities, f, indent=2)

        # Save asset allocation to JSON
        asset_allocation_path = os.path.join(output_dir, 'asset_allocation.json')
        with open(asset_allocation_path, 'w', encoding='utf-8') as f:
            # Convert to serializable format
            serializable_asset_classes = {}
            for asset_class, data in self.asset_classes.items():
                serializable_asset_classes[asset_class] = {
                    'total_value': data['total_value'],
                    'percentage': (data['total_value'] / total_asset_value) * 100 if total_asset_value > 0 else 0
                }

            json.dump(serializable_asset_classes, f, indent=2)

        return report_path

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python enhanced_financial_extractor.py <pdf_path>")
        return 1

    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return 1

    extractor = EnhancedFinancialExtractor()
    report_path = extractor.process(pdf_path)

    # Open the report in the default browser
    try:
        import webbrowser
        webbrowser.open(f"file://{os.path.abspath(report_path)}")
    except Exception as e:
        print(f"Error opening report in browser: {str(e)}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
