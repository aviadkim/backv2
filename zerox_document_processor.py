"""
ZeroX Document Processor - Uses ZeroX to extract structured data from financial documents.
"""
import os
import re
import json
import pandas as pd
from typing import Optional, Union, Iterable, Dict, List, Any
import tempfile

try:
    from pyzerox import Zerox
    ZEROX_AVAILABLE = True
except ImportError:
    ZEROX_AVAILABLE = False
    print("ZeroX not available. Install with: pip install py-zerox")

class ZeroXDocumentProcessor:
    """Agent that uses ZeroX to process financial documents."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the ZeroX document processor.
        
        Args:
            api_key: OpenAI API key or other provider API key
            model: Model to use for processing (default: gpt-4o-mini)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.zerox = None
        self.markdown_content = ""
        self.extracted_data = {
            "bonds": [],
            "asset_allocation": {},
            "portfolio_value": None,
            "client_info": {},
            "document_date": None
        }
        
        if ZEROX_AVAILABLE and self.api_key:
            self._initialize_zerox()
    
    def _initialize_zerox(self):
        """Initialize the ZeroX processor."""
        try:
            # Set the API key in the environment if not already set
            if self.api_key and "OPENAI_API_KEY" not in os.environ:
                os.environ["OPENAI_API_KEY"] = self.api_key
            
            # Initialize ZeroX
            self.zerox = Zerox()
            print("ZeroX initialized successfully.")
        except Exception as e:
            print(f"Error initializing ZeroX: {str(e)}")
            self.zerox = None
    
    def process_document(self, file_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a financial document using ZeroX.
        
        Args:
            file_path: Path to the document file
            output_dir: Directory to save output files (default: None)
        
        Returns:
            Dict containing extracted data
        """
        if not ZEROX_AVAILABLE:
            print("ZeroX is not available. Please install with: pip install py-zerox")
            return self.extracted_data
        
        if not self.zerox:
            self._initialize_zerox()
            if not self.zerox:
                print("Failed to initialize ZeroX.")
                return self.extracted_data
        
        print(f"Processing document: {file_path}")
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Process the document with ZeroX
        try:
            # Custom system prompt to guide the extraction
            custom_system_prompt = """
            You are a financial document analysis expert. Your task is to extract structured information from financial documents.
            
            Focus on extracting:
            1. Client information (name, client number)
            2. Document date
            3. Portfolio value
            4. Bonds and securities (with ISIN, description, currency, nominal/quantity, price, valuation)
            5. Asset allocation (asset classes and their values/percentages)
            
            Preserve all tables exactly as they appear in the document. Maintain the exact numbers, formatting, and layout.
            For financial tables, ensure all columns are properly aligned and all numeric values are preserved exactly.
            
            When you encounter tables with financial data:
            - Preserve all numeric values exactly as they appear
            - Maintain column headers and row labels
            - Keep all currency symbols, percentages, and decimal places
            
            After processing the document, summarize the key financial information you've extracted.
            """
            
            # Process the document
            output = self.zerox.process(
                file_path=file_path,
                model=self.model,
                output_dir=output_dir,
                custom_system_prompt=custom_system_prompt,
                maintain_format=True,
                cleanup=True,
                concurrency=10
            )
            
            # Store the markdown content
            self.markdown_content = ""
            for page in output.pages:
                self.markdown_content += page.content + "\n\n"
            
            # Save the markdown content if output_dir is specified
            if output_dir:
                markdown_path = os.path.join(output_dir, "document.md")
                with open(markdown_path, "w", encoding="utf-8") as f:
                    f.write(self.markdown_content)
                print(f"Markdown content saved to: {markdown_path}")
            
            # Extract structured data from the markdown content
            self._extract_structured_data()
            
            # Save the extracted data if output_dir is specified
            if output_dir:
                json_path = os.path.join(output_dir, "extracted_data.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(self.extracted_data, f, indent=2)
                print(f"Extracted data saved to: {json_path}")
            
            print("Document processing completed successfully.")
            return self.extracted_data
            
        except Exception as e:
            print(f"Error processing document with ZeroX: {str(e)}")
            return self.extracted_data
    
    def _extract_structured_data(self):
        """Extract structured data from the markdown content."""
        if not self.markdown_content:
            return
        
        # Extract client information
        self._extract_client_info()
        
        # Extract document date
        self._extract_document_date()
        
        # Extract portfolio value
        self._extract_portfolio_value()
        
        # Extract bonds
        self._extract_bonds()
        
        # Extract asset allocation
        self._extract_asset_allocation()
    
    def _extract_client_info(self):
        """Extract client information from the markdown content."""
        # Look for client name
        client_match = re.search(r'([A-Z\s]+LTD\.)', self.markdown_content)
        if client_match:
            self.extracted_data["client_info"]["name"] = client_match.group(1).strip()
        
        # Look for client number
        client_num_match = re.search(r'Client\s+Number[:\s]+(\d+)', self.markdown_content)
        if client_num_match:
            self.extracted_data["client_info"]["number"] = client_num_match.group(1).strip()
    
    def _extract_document_date(self):
        """Extract document date from the markdown content."""
        date_match = re.search(r'Valuation\s+as\s+of\s+(\d{2}\.\d{2}\.\d{4})', self.markdown_content)
        if date_match:
            self.extracted_data["document_date"] = date_match.group(1).strip()
    
    def _extract_portfolio_value(self):
        """Extract portfolio value from the markdown content."""
        # Look for portfolio value in tables
        portfolio_value_patterns = [
            r'Total\s+assets\s*\|\s*(\d[\d,.\']*)',
            r'Portfolio\s+Total\s*\|\s*(\d[\d,.\']*)',
            r'Total\s+assets\s*[\|\:]?\s*(\d[\d,.\']*)',
            r'Portfolio\s+Value\s*[\|\:]?\s*(\d[\d,.\']*)'
        ]
        
        for pattern in portfolio_value_patterns:
            match = re.search(pattern, self.markdown_content)
            if match:
                value_str = match.group(1).strip()
                value = self._clean_number(value_str)
                if value:
                    self.extracted_data["portfolio_value"] = value
                    break
    
    def _extract_bonds(self):
        """Extract bonds from the markdown content."""
        # Look for bond tables
        # This is a simplified approach - in a real implementation, we would use more sophisticated
        # table parsing to extract structured data from markdown tables
        
        # Find tables with bond-related headers
        bond_table_patterns = [
            r'(\|\s*Currency\s*\|\s*Nominal.*\|\s*Description.*\|.*\|\s*Valuation.*\|)',
            r'(\|\s*ISIN\s*\|\s*Description.*\|.*\|\s*Value.*\|)'
        ]
        
        for pattern in bond_table_patterns:
            match = re.search(pattern, self.markdown_content, re.MULTILINE)
            if match:
                # Found a bond table, extract the entire table
                table_start = match.start()
                
                # Find the end of the table (empty line or end of content)
                table_end = self.markdown_content.find("\n\n", table_start)
                if table_end == -1:
                    table_end = len(self.markdown_content)
                
                table_content = self.markdown_content[table_start:table_end]
                
                # Parse the table rows
                rows = table_content.strip().split("\n")
                
                # Skip the header row and separator row
                data_rows = rows[2:] if len(rows) > 2 else []
                
                for row in data_rows:
                    # Split the row by pipe character and clean up cells
                    cells = [cell.strip() for cell in row.split("|")]
                    cells = [cell for cell in cells if cell]  # Remove empty cells
                    
                    if len(cells) >= 4:  # Ensure we have enough cells
                        bond = {}
                        
                        # Map cells to bond properties based on the table structure
                        # This is a simplified approach and would need to be adapted to the actual table structure
                        if len(cells) >= 5:
                            bond["currency"] = cells[0]
                            bond["nominal"] = self._clean_number(cells[1])
                            bond["description"] = cells[2]
                            
                            # Try to extract ISIN from description
                            isin_match = re.search(r'ISIN:\s*([A-Z0-9]+)', cells[2])
                            if isin_match:
                                bond["isin"] = isin_match.group(1).strip()
                            
                            # Extract valuation (usually one of the last cells)
                            for i in range(3, len(cells)):
                                value = self._clean_number(cells[i])
                                if value and value > 1000:  # Assume valuation is a larger number
                                    bond["valuation"] = value
                                    break
                        
                        # Only add bonds with at least description and valuation
                        if "description" in bond and "valuation" in bond:
                            self.extracted_data["bonds"].append(bond)
    
    def _extract_asset_allocation(self):
        """Extract asset allocation from the markdown content."""
        # Look for asset allocation table
        asset_table_pattern = r'Asset\s+Allocation\s*\|.*\|\s*Weight'
        match = re.search(asset_table_pattern, self.markdown_content)
        
        if match:
            # Found an asset allocation table, extract the entire table
            table_start = match.start()
            
            # Find the end of the table (empty line or end of content)
            table_end = self.markdown_content.find("\n\n", table_start)
            if table_end == -1:
                table_end = len(self.markdown_content)
            
            table_content = self.markdown_content[table_start:table_end]
            
            # Parse the table rows
            rows = table_content.strip().split("\n")
            
            # Skip the header row and separator row
            data_rows = rows[2:] if len(rows) > 2 else []
            
            current_asset_class = None
            
            for row in rows:
                # Split the row by pipe character and clean up cells
                cells = [cell.strip() for cell in row.split("|")]
                cells = [cell for cell in cells if cell]  # Remove empty cells
                
                if len(cells) >= 3:  # Ensure we have enough cells
                    asset_name = cells[0]
                    
                    # Check if this is a main asset class (usually starts with uppercase)
                    if asset_name and asset_name[0].isupper():
                        current_asset_class = asset_name
                        
                        # Extract value and percentage
                        value = self._clean_number(cells[1])
                        percentage = self._clean_number(cells[2])
                        
                        if value is not None:
                            self.extracted_data["asset_allocation"][current_asset_class] = {
                                "value": value,
                                "percentage": percentage,
                                "sub_classes": {}
                            }
                    
                    # Check if this is a sub-asset class
                    elif current_asset_class and asset_name:
                        # This is a sub-asset class
                        sub_class = asset_name
                        
                        # Extract value and percentage
                        value = self._clean_number(cells[1])
                        percentage = self._clean_number(cells[2])
                        
                        if value is not None and current_asset_class in self.extracted_data["asset_allocation"]:
                            self.extracted_data["asset_allocation"][current_asset_class]["sub_classes"][sub_class] = {
                                "value": value,
                                "percentage": percentage
                            }
    
    def _clean_number(self, value_str):
        """Clean a number string by removing quotes and commas."""
        if not value_str:
            return None
        
        # Replace single quotes with nothing (European number format)
        cleaned = str(value_str).replace("'", "")
        
        # Replace commas with nothing (US number format)
        cleaned = cleaned.replace(",", "")
        
        # Remove any non-numeric characters except decimal point and negative sign
        cleaned = re.sub(r'[^\d.-]', '', cleaned)
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def generate_financial_report(self, output_dir: Optional[str] = None) -> str:
        """
        Generate a financial report based on the extracted data.
        
        Args:
            output_dir: Directory to save the report (default: None)
        
        Returns:
            Path to the generated report
        """
        if not self.extracted_data["bonds"] and not self.extracted_data["asset_allocation"]:
            print("No data available to generate a report.")
            return ""
        
        # Create HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Financial Report</title>
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
                <h1>Financial Report</h1>
        """
        
        # Add client information
        if self.extracted_data["client_info"]:
            client_name = self.extracted_data["client_info"].get("name", "Unknown")
            client_number = self.extracted_data["client_info"].get("number", "Unknown")
            
            html_content += f"""
                <div class="summary-box">
                    <h2>Client Information</h2>
                    <p>Client: <span class="value">{client_name}</span></p>
                    <p>Client Number: <span class="value">{client_number}</span></p>
            """
            
            if self.extracted_data["document_date"]:
                html_content += f"""
                    <p>Document Date: <span class="value">{self.extracted_data["document_date"]}</span></p>
                """
            
            html_content += f"""
                </div>
            """
        
        # Add portfolio summary
        if self.extracted_data["portfolio_value"]:
            html_content += f"""
                <div class="summary-box">
                    <h2>Portfolio Summary</h2>
                    <p>Portfolio Value: <span class="value">${self.extracted_data["portfolio_value"]:,.2f}</span></p>
                </div>
            """
        
        # Add asset allocation
        if self.extracted_data["asset_allocation"]:
            html_content += f"""
                <h2>Asset Allocation</h2>
            """
            
            # Add chart
            html_content += f"""
                <div class="chart">
            """
            
            # Define colors for asset classes
            colors = {
                "Liquidity": "#17a2b8",
                "Bonds": "#007bff",
                "Equities": "#28a745",
                "Mixed funds": "#6f42c1",
                "Structured products": "#fd7e14",
                "Metal accounts and precious metals": "#dc3545",
                "Real Estate": "#6c757d",
                "Other assets": "#20c997"
            }
            
            # Add chart segments
            for asset_class, data in self.extracted_data["asset_allocation"].items():
                percentage = data.get("percentage", 0)
                color = colors.get(asset_class, "#6c757d")
                
                if percentage > 0:
                    html_content += f"""
                        <div class="chart-segment" style="width: {percentage}%; background-color: {color};">
                            {percentage:.1f}%
                        </div>
                    """
            
            html_content += f"""
                </div>
                
                <table>
                    <tr>
                        <th>Asset Class</th>
                        <th>Value</th>
                        <th>Percentage</th>
                    </tr>
            """
            
            # Add asset classes
            for asset_class, data in self.extracted_data["asset_allocation"].items():
                value = data.get("value", 0)
                percentage = data.get("percentage", 0)
                
                html_content += f"""
                    <tr>
                        <td>{asset_class}</td>
                        <td>${value:,.2f}</td>
                        <td>{percentage:.2f}%</td>
                    </tr>
                """
                
                # Add sub-classes
                sub_classes = data.get("sub_classes", {})
                for sub_class, sub_data in sub_classes.items():
                    sub_value = sub_data.get("value", 0)
                    sub_percentage = sub_data.get("percentage", 0)
                    
                    html_content += f"""
                        <tr>
                            <td>&nbsp;&nbsp;&nbsp;{sub_class}</td>
                            <td>${sub_value:,.2f}</td>
                            <td>{sub_percentage:.2f}%</td>
                        </tr>
                    """
            
            html_content += f"""
                </table>
            """
        
        # Add bonds
        if self.extracted_data["bonds"]:
            html_content += f"""
                <h2>Bonds</h2>
                <table>
                    <tr>
                        <th>Description</th>
                        <th>ISIN</th>
                        <th>Currency</th>
                        <th>Nominal</th>
                        <th>Valuation</th>
                    </tr>
            """
            
            # Sort bonds by valuation
            sorted_bonds = sorted(self.extracted_data["bonds"], key=lambda x: x.get("valuation", 0), reverse=True)
            
            for bond in sorted_bonds:
                description = bond.get("description", "Unknown")
                isin = bond.get("isin", "N/A")
                currency = bond.get("currency", "N/A")
                nominal = bond.get("nominal", 0)
                valuation = bond.get("valuation", 0)
                
                html_content += f"""
                    <tr>
                        <td>{description}</td>
                        <td>{isin}</td>
                        <td>{currency}</td>
                        <td>{nominal:,.2f}</td>
                        <td>${valuation:,.2f}</td>
                    </tr>
                """
            
            html_content += f"""
                </table>
            """
        
        # Add footer
        html_content += f"""
                <div class="footer">
                    <p>This report is generated based on the document processed with ZeroX.</p>
                    <p>Generated on {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save the report if output_dir is specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            report_path = os.path.join(output_dir, "financial_report.html")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Financial report saved to: {report_path}")
            return report_path
        
        # If no output_dir, save to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as f:
            f.write(html_content)
            report_path = f.name
            print(f"Financial report saved to temporary file: {report_path}")
            return report_path

def main():
    """Main function."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Process financial documents with ZeroX.")
    parser.add_argument("file_path", help="Path to the financial document")
    parser.add_argument("--api-key", help="OpenAI API key or other provider API key")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model to use for processing")
    parser.add_argument("--output-dir", help="Directory to save output files")
    
    args = parser.parse_args()
    
    processor = ZeroXDocumentProcessor(api_key=args.api_key, model=args.model)
    processor.process_document(args.file_path, output_dir=args.output_dir)
    report_path = processor.generate_financial_report(output_dir=args.output_dir)
    
    # Open the report in the default browser
    if report_path:
        import webbrowser
        webbrowser.open(f"file://{os.path.abspath(report_path)}")
    
    return 0

if __name__ == "__main__":
    main()
