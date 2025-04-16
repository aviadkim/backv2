"""
Financial Document Processor - Extracts all data from financial PDFs using Unstructured.
"""
import os
import re
import json
import pandas as pd
from typing import Dict, List, Any, Optional
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import (
    Table, Text, Title, NarrativeText, ListItem
)

class FinancialDocumentProcessor:
    """
    Comprehensive processor for financial documents that extracts all data
    and makes it available for analysis and querying.
    """
    
    def __init__(self):
        """Initialize the financial document processor."""
        self.elements = []
        self.tables = []
        self.text_blocks = []
        self.extracted_data = {
            "bonds": [],
            "asset_allocation": {},
            "portfolio_value": None,
            "client_info": {},
            "document_date": None
        }
        self.full_text = ""
    
    def process(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a financial document to extract all data.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save output files (default: None)
        
        Returns:
            Dict containing extracted data
        """
        print(f"Processing document: {pdf_path}")
        
        # Reset data
        self.elements = []
        self.tables = []
        self.text_blocks = []
        self.extracted_data = {
            "bonds": [],
            "asset_allocation": {},
            "portfolio_value": None,
            "client_info": {},
            "document_date": None
        }
        self.full_text = ""
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Extract elements from PDF using Unstructured
            self.elements = partition_pdf(
                pdf_path,
                extract_images_in_pdf=False,
                infer_table_structure=True,
                strategy="hi_res"
            )
            
            # Process elements
            self._process_elements()
            
            # Extract structured data
            self._extract_client_info()
            self._extract_document_date()
            self._extract_portfolio_value()
            self._extract_bonds()
            self._extract_asset_allocation()
            
            # Save results if output_dir is specified
            if output_dir:
                self._save_results(output_dir)
            
            print("Document processing completed.")
            return self.extracted_data
            
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            return self.extracted_data
    
    def _process_elements(self):
        """Process extracted elements."""
        # Separate tables and text blocks
        for element in self.elements:
            if isinstance(element, Table):
                self.tables.append(element)
            elif isinstance(element, (Text, Title, NarrativeText, ListItem)):
                self.text_blocks.append(element)
                self.full_text += str(element) + "\n"
        
        print(f"Extracted {len(self.tables)} tables and {len(self.text_blocks)} text blocks")
    
    def _extract_client_info(self):
        """Extract client information."""
        # Look for client name
        client_match = re.search(r'([A-Z\s]+LTD\.)', self.full_text)
        if client_match:
            self.extracted_data["client_info"]["name"] = client_match.group(1).strip()
        
        # Look for client number
        client_num_match = re.search(r'Client\s+Number[:\s]+(\d+)', self.full_text)
        if client_num_match:
            self.extracted_data["client_info"]["number"] = client_num_match.group(1).strip()
        
        print(f"Client info: {self.extracted_data['client_info']}")
    
    def _extract_document_date(self):
        """Extract document date."""
        date_match = re.search(r'Valuation\s+as\s+of\s+(\d{2}\.\d{2}\.\d{4})', self.full_text)
        if date_match:
            self.extracted_data["document_date"] = date_match.group(1).strip()
            print(f"Document date: {self.extracted_data['document_date']}")
    
    def _extract_portfolio_value(self):
        """Extract portfolio value."""
        # Look for portfolio value in text
        portfolio_value_patterns = [
            r'Total\s+assets\s*[:\s]+(\d[\d,.\']*)',
            r'Portfolio\s+Total\s*[:\s]+(\d[\d,.\']*)',
            r'Total\s+assets\s*[\|\:]?\s*(\d[\d,.\']*)',
            r'Portfolio\s+Value\s*[\|\:]?\s*(\d[\d,.\']*)'
        ]
        
        for pattern in portfolio_value_patterns:
            match = re.search(pattern, self.full_text)
            if match:
                value_str = match.group(1).strip()
                value = self._clean_number(value_str)
                if value:
                    self.extracted_data["portfolio_value"] = value
                    print(f"Portfolio value: {value}")
                    break
        
        # If not found in text, look in tables
        if not self.extracted_data["portfolio_value"]:
            for table in self.tables:
                table_str = str(table)
                for pattern in portfolio_value_patterns:
                    match = re.search(pattern, table_str)
                    if match:
                        value_str = match.group(1).strip()
                        value = self._clean_number(value_str)
                        if value:
                            self.extracted_data["portfolio_value"] = value
                            print(f"Portfolio value (from table): {value}")
                            break
    
    def _extract_bonds(self):
        """Extract bonds from tables."""
        for table in self.tables:
            table_str = str(table)
            
            # Check if this is a bonds table
            if "ISIN" in table_str or ("Nominal" in table_str and "Description" in table_str):
                # Convert table to DataFrame
                df = self._table_to_dataframe(table)
                if df is None or df.empty:
                    continue
                
                # Clean column names
                df.columns = [str(col).strip().lower() for col in df.columns]
                
                # Identify relevant columns
                description_col = next((col for col in df.columns if "description" in col or "security" in col), None)
                isin_col = next((col for col in df.columns if "isin" in col), None)
                currency_col = next((col for col in df.columns if "currency" in col), None)
                nominal_col = next((col for col in df.columns if "nominal" in col or "quantity" in col), None)
                price_col = next((col for col in df.columns if "price" in col), None)
                valuation_col = next((col for col in df.columns if "valuation" in col or "value" in col), None)
                
                # Skip if essential columns are missing
                if not description_col or not valuation_col:
                    continue
                
                # Process each row
                for _, row in df.iterrows():
                    # Skip rows with empty description or valuation
                    if pd.isna(row[description_col]) or pd.isna(row[valuation_col]):
                        continue
                    
                    # Create bond object
                    bond = {
                        "description": str(row[description_col]).strip()
                    }
                    
                    # Add ISIN if available
                    if isin_col and not pd.isna(row[isin_col]):
                        bond["isin"] = str(row[isin_col]).strip()
                    else:
                        # Try to extract ISIN from description
                        isin_match = re.search(r'ISIN:\s*([A-Z0-9]+)', bond["description"])
                        if isin_match:
                            bond["isin"] = isin_match.group(1).strip()
                    
                    # Add currency if available
                    if currency_col and not pd.isna(row[currency_col]):
                        bond["currency"] = str(row[currency_col]).strip()
                    
                    # Add nominal if available
                    if nominal_col and not pd.isna(row[nominal_col]):
                        bond["nominal"] = self._clean_number(row[nominal_col])
                    
                    # Add price if available
                    if price_col and not pd.isna(row[price_col]):
                        bond["price"] = self._clean_number(row[price_col])
                    
                    # Add valuation
                    bond["valuation"] = self._clean_number(row[valuation_col])
                    if not bond["valuation"]:
                        continue
                    
                    # Add the bond to the list
                    self.extracted_data["bonds"].append(bond)
        
        print(f"Extracted {len(self.extracted_data['bonds'])} bonds")
    
    def _extract_asset_allocation(self):
        """Extract asset allocation from tables."""
        for table in self.tables:
            table_str = str(table)
            
            # Check if this is an asset allocation table
            if "Asset Allocation" in table_str or "Asset Class" in table_str:
                # Convert table to DataFrame
                df = self._table_to_dataframe(table)
                if df is None or df.empty:
                    continue
                
                # Clean column names
                df.columns = [str(col).strip().lower() for col in df.columns]
                
                # Identify relevant columns
                asset_class_col = 0  # Usually the first column
                value_col = next((i for i, col in enumerate(df.columns) if "value" in col or "amount" in col), 1)
                percentage_col = next((i for i, col in enumerate(df.columns) if "%" in col or "percent" in col or "weight" in col), 2)
                
                # Process each row
                current_asset_class = None
                
                for _, row in df.iterrows():
                    asset_class = str(row.iloc[asset_class_col]).strip()
                    
                    # Skip empty rows
                    if not asset_class:
                        continue
                    
                    # Check if this is a main asset class (usually starts with uppercase)
                    if asset_class and asset_class[0].isupper():
                        current_asset_class = asset_class
                        
                        # Extract value and percentage
                        value = self._clean_number(row.iloc[value_col])
                        percentage = self._clean_number(row.iloc[percentage_col])
                        
                        if value is not None:
                            self.extracted_data["asset_allocation"][current_asset_class] = {
                                "value": value,
                                "percentage": percentage,
                                "sub_classes": {}
                            }
                    
                    # Check if this is a sub-asset class
                    elif current_asset_class and asset_class:
                        # This is a sub-asset class
                        sub_class = asset_class
                        
                        # Extract value and percentage
                        value = self._clean_number(row.iloc[value_col])
                        percentage = self._clean_number(row.iloc[percentage_col])
                        
                        if value is not None and current_asset_class in self.extracted_data["asset_allocation"]:
                            self.extracted_data["asset_allocation"][current_asset_class]["sub_classes"][sub_class] = {
                                "value": value,
                                "percentage": percentage
                            }
        
        print(f"Extracted asset allocation with {len(self.extracted_data['asset_allocation'])} asset classes")
    
    def _table_to_dataframe(self, table):
        """Convert a table element to a pandas DataFrame."""
        try:
            # Get table data
            data = []
            for row in table.metadata.text_as_html.split("<tr>")[1:]:  # Skip the first empty element
                row_data = []
                for cell in re.findall(r"<td>(.*?)</td>", row):
                    row_data.append(cell.strip())
                if row_data:
                    data.append(row_data)
            
            # Create DataFrame
            if data:
                # Use the first row as header if it looks like a header
                if len(data) > 1:
                    df = pd.DataFrame(data[1:], columns=data[0])
                else:
                    df = pd.DataFrame(data)
                return df
            return None
        except Exception as e:
            print(f"Error converting table to DataFrame: {str(e)}")
            return None
    
    def _clean_number(self, value):
        """Clean a number by removing quotes, commas, etc."""
        if pd.isna(value):
            return None
        
        value_str = str(value)
        
        # Replace single quotes with nothing (European number format)
        cleaned = value_str.replace("'", "")
        
        # Replace commas with nothing (US number format)
        cleaned = cleaned.replace(",", "")
        
        # Remove any non-numeric characters except decimal point and negative sign
        cleaned = re.sub(r'[^\d.-]', '', cleaned)
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def _save_results(self, output_dir):
        """Save extraction results."""
        # Save full text
        text_path = os.path.join(output_dir, "full_text.txt")
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(self.full_text)
        
        # Save extracted data as JSON
        json_path = os.path.join(output_dir, "extracted_data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.extracted_data, f, indent=2)
        
        # Save bonds as CSV
        if self.extracted_data["bonds"]:
            bonds_df = pd.DataFrame(self.extracted_data["bonds"])
            bonds_path = os.path.join(output_dir, "bonds.csv")
            bonds_df.to_csv(bonds_path, index=False)
        
        print(f"Results saved to {output_dir}")
    
    def answer_question(self, question: str) -> str:
        """
        Answer a question about the financial document.
        
        Args:
            question: Question to answer
        
        Returns:
            Answer to the question
        """
        question_lower = question.lower()
        
        # Portfolio value questions
        if "portfolio value" in question_lower or "total value" in question_lower:
            if self.extracted_data["portfolio_value"]:
                return f"The portfolio value is ${self.extracted_data['portfolio_value']:,.2f}."
            else:
                return "I couldn't find the portfolio value in the document."
        
        # Top holdings questions
        elif "top" in question_lower and ("holdings" in question_lower or "bonds" in question_lower):
            # Extract the number from the question (default to 5 if not found)
            match = re.search(r'top (\d+)', question_lower)
            n = int(match.group(1)) if match else 5
            
            if self.extracted_data["bonds"]:
                # Sort bonds by valuation
                sorted_bonds = sorted(self.extracted_data["bonds"], key=lambda x: x.get("valuation", 0), reverse=True)
                top_bonds = sorted_bonds[:n]
                
                response = f"The top {len(top_bonds)} holdings by value are:\n"
                for i, bond in enumerate(top_bonds, 1):
                    description = bond.get("description", "Unknown")
                    valuation = bond.get("valuation", 0)
                    
                    response += f"{i}. {description}: ${valuation:,.2f}\n"
                
                return response
            else:
                return "I couldn't find any holdings in the document."
        
        # Asset allocation questions
        elif "asset allocation" in question_lower or "asset classes" in question_lower:
            if self.extracted_data["asset_allocation"]:
                response = "Asset Allocation:\n"
                
                for asset_class, data in self.extracted_data["asset_allocation"].items():
                    value = data.get("value", 0)
                    percentage = data.get("percentage", 0)
                    
                    response += f"{asset_class}: ${value:,.2f} ({percentage:.2f}%)\n"
                
                return response
            else:
                return "I couldn't find asset allocation information in the document."
        
        # Client information questions
        elif "client" in question_lower:
            if self.extracted_data["client_info"]:
                client_name = self.extracted_data["client_info"].get("name", "Unknown")
                client_number = self.extracted_data["client_info"].get("number", "Unknown")
                
                return f"Client: {client_name}, Client Number: {client_number}"
            else:
                return "I couldn't find client information in the document."
        
        # Document date questions
        elif "date" in question_lower:
            if self.extracted_data["document_date"]:
                return f"The document date is {self.extracted_data['document_date']}."
            else:
                return "I couldn't find the document date."
        
        # General questions - search in full text
        else:
            # Look for relevant sections in the full text
            sentences = re.split(r'[.!?]\s+', self.full_text)
            relevant_sentences = []
            
            # Extract keywords from the question
            keywords = re.findall(r'\b\w{3,}\b', question_lower)
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(keyword in sentence_lower for keyword in keywords):
                    relevant_sentences.append(sentence)
            
            if relevant_sentences:
                return " ".join(relevant_sentences[:3]) + "."
            else:
                return "I couldn't find information related to your question in the document."
    
    def generate_report(self, output_dir: Optional[str] = None) -> str:
        """
        Generate a comprehensive report based on the extracted data.
        
        Args:
            output_dir: Directory to save the report
        
        Returns:
            Path to the generated report
        """
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
                    <p>This report is generated based on the extracted financial data.</p>
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
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as f:
            f.write(html_content)
            report_path = f.name
            print(f"Financial report saved to temporary file: {report_path}")
            return report_path

def main():
    """Main function."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Process financial documents.")
    parser.add_argument("file_path", help="Path to the financial document")
    parser.add_argument("--output-dir", help="Directory to save output files")
    parser.add_argument("--question", help="Question to answer (if provided, skips interactive mode)")
    parser.add_argument("--report", action="store_true", help="Generate a report")
    
    args = parser.parse_args()
    
    # Check if the file exists
    if not os.path.exists(args.file_path):
        print(f"Error: File not found: {args.file_path}")
        return 1
    
    # Process the document
    processor = FinancialDocumentProcessor()
    processor.process(args.file_path, output_dir=args.output_dir)
    
    # Generate a report if requested
    if args.report:
        report_path = processor.generate_report(output_dir=args.output_dir)
        if report_path:
            print(f"Report generated: {report_path}")
            # Open the report in the default browser
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(report_path)}")
    
    # Answer a specific question if provided
    if args.question:
        answer = processor.answer_question(args.question)
        print(f"\nQuestion: {args.question}")
        print(f"Answer: {answer}\n")
    # Otherwise, start interactive session
    else:
        print("\nFinancial Document Processor")
        print("===========================")
        print("I can answer questions about the financial document.")
        print("Type 'exit' to end the session.")
        print("Type 'help' to see example questions.")
        print("Type 'report' to generate a report.")
        print()
        
        while True:
            user_input = input("Ask a question: ").strip()
            
            if user_input.lower() == 'exit':
                print("Ending session. Goodbye!")
                break
            
            elif user_input.lower() == 'help':
                print("\nExample questions:")
                print("- What is the total portfolio value?")
                print("- What is the asset allocation?")
                print("- What are the top 5 holdings?")
                print("- What are the top 10 bonds?")
                print("- What is the client information?")
                print("- What is the document date?")
                print()
                continue
            
            elif user_input.lower() == 'report':
                report_path = processor.generate_report(output_dir=args.output_dir)
                if report_path:
                    print(f"Report generated: {report_path}")
                    # Open the report in the default browser
                    import webbrowser
                    webbrowser.open(f"file://{os.path.abspath(report_path)}")
                continue
            
            answer = processor.answer_question(user_input)
            print(f"\n{answer}\n")
    
    return 0

if __name__ == "__main__":
    main()
