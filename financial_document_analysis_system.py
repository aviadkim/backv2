"""
Comprehensive Financial Document Analysis System.

This system combines multiple specialized agents to extract, analyze, and answer questions
about financial documents.
"""
import os
import sys
import argparse
import json
import pandas as pd
from typing import Optional, Dict, Any, List

# Import our specialized agents
try:
    from financial_table_extractor import FinancialTableExtractor
    TABLE_EXTRACTOR_AVAILABLE = True
except ImportError:
    TABLE_EXTRACTOR_AVAILABLE = False
    print("Financial Table Extractor not available.")

try:
    from financial_data_analyzer import FinancialDataAnalyzer
    DATA_ANALYZER_AVAILABLE = True
except ImportError:
    DATA_ANALYZER_AVAILABLE = False
    print("Financial Data Analyzer not available.")

try:
    from zerox_document_processor import ZeroXDocumentProcessor
    ZEROX_PROCESSOR_AVAILABLE = True
except ImportError:
    ZEROX_PROCESSOR_AVAILABLE = False
    print("ZeroX Document Processor not available.")

class FinancialDocumentAnalysisSystem:
    """
    Comprehensive system for analyzing financial documents.
    
    This system combines multiple specialized agents to extract, analyze, and answer
    questions about financial documents.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the financial document analysis system.
        
        Args:
            api_key: API key for AI services
            model: Model to use for AI processing
        """
        self.api_key = api_key
        self.model = model
        
        # Initialize specialized agents
        self.table_extractor = FinancialTableExtractor() if TABLE_EXTRACTOR_AVAILABLE else None
        self.data_analyzer = FinancialDataAnalyzer() if DATA_ANALYZER_AVAILABLE else None
        self.zerox_processor = ZeroXDocumentProcessor(api_key=api_key, model=model) if ZEROX_PROCESSOR_AVAILABLE else None
        
        # Store extracted data
        self.extracted_data = {
            "bonds": [],
            "asset_allocation": {},
            "portfolio_value": None,
            "client_info": {},
            "document_date": None
        }
        
        # Store processing results from each agent
        self.agent_results = {}
    
    def process_document(self, file_path: str, output_dir: Optional[str] = None, use_zerox: bool = True) -> Dict[str, Any]:
        """
        Process a financial document using all available agents.
        
        Args:
            file_path: Path to the document file
            output_dir: Directory to save output files
            use_zerox: Whether to use ZeroX for processing
        
        Returns:
            Dict containing extracted data
        """
        print(f"Processing document: {file_path}")
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Process with ZeroX if available and requested
        if use_zerox and self.zerox_processor:
            print("Processing with ZeroX Document Processor...")
            zerox_results = self.zerox_processor.process_document(file_path, output_dir=output_dir)
            self.agent_results["zerox"] = zerox_results
            
            # Update extracted data with ZeroX results
            self._update_extracted_data(zerox_results)
        
        # Process with Financial Table Extractor
        if self.table_extractor:
            print("Processing with Financial Table Extractor...")
            table_results = self.table_extractor.process(file_path)
            self.agent_results["table_extractor"] = table_results
            
            # Update extracted data with table extractor results
            self._update_extracted_data(table_results)
        
        # Process with Financial Data Analyzer
        if self.data_analyzer:
            print("Processing with Financial Data Analyzer...")
            self.data_analyzer.process_document(file_path)
            
            # Store the analyzer for later use in answering questions
            self.agent_results["data_analyzer"] = self.data_analyzer
        
        # Save the combined extracted data if output_dir is specified
        if output_dir:
            json_path = os.path.join(output_dir, "combined_data.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(self.extracted_data, f, indent=2)
            print(f"Combined data saved to: {json_path}")
        
        print("Document processing completed.")
        return self.extracted_data
    
    def _update_extracted_data(self, new_data: Dict[str, Any]):
        """
        Update the extracted data with new data from an agent.
        
        Args:
            new_data: New data to incorporate
        """
        # Update bonds
        if "bonds" in new_data and new_data["bonds"]:
            # If we already have bonds, merge them
            if self.extracted_data["bonds"]:
                # Create a set of existing ISINs
                existing_isins = {bond.get("isin") for bond in self.extracted_data["bonds"] if "isin" in bond}
                
                # Add new bonds that don't already exist
                for bond in new_data["bonds"]:
                    if "isin" in bond and bond["isin"] not in existing_isins:
                        self.extracted_data["bonds"].append(bond)
                        existing_isins.add(bond["isin"])
            else:
                # If we don't have bonds yet, use the new ones
                self.extracted_data["bonds"] = new_data["bonds"]
        
        # Update asset allocation
        if "asset_allocation" in new_data and new_data["asset_allocation"]:
            # If we already have asset allocation, merge it
            if self.extracted_data["asset_allocation"]:
                for asset_class, data in new_data["asset_allocation"].items():
                    if asset_class not in self.extracted_data["asset_allocation"]:
                        self.extracted_data["asset_allocation"][asset_class] = data
            else:
                # If we don't have asset allocation yet, use the new one
                self.extracted_data["asset_allocation"] = new_data["asset_allocation"]
        
        # Update portfolio value
        if "portfolio_value" in new_data and new_data["portfolio_value"]:
            # Use the new portfolio value if we don't have one yet or if it's more precise
            if not self.extracted_data["portfolio_value"]:
                self.extracted_data["portfolio_value"] = new_data["portfolio_value"]
        
        # Update client info
        if "client_info" in new_data and new_data["client_info"]:
            # Merge client info
            for key, value in new_data["client_info"].items():
                if key not in self.extracted_data["client_info"] or not self.extracted_data["client_info"][key]:
                    self.extracted_data["client_info"][key] = value
        
        # Update document date
        if "document_date" in new_data and new_data["document_date"]:
            # Use the new document date if we don't have one yet
            if not self.extracted_data["document_date"]:
                self.extracted_data["document_date"] = new_data["document_date"]
    
    def answer_question(self, question: str) -> str:
        """
        Answer a question about the financial document.
        
        Args:
            question: Question to answer
        
        Returns:
            Answer to the question
        """
        # If we have the data analyzer, use it to answer the question
        if "data_analyzer" in self.agent_results and self.agent_results["data_analyzer"]:
            return self.agent_results["data_analyzer"].answer_question(question)
        
        # If we have ZeroX, use it to answer the question
        if "zerox" in self.agent_results and self.agent_results["zerox"]:
            # This is a simplified approach - in a real implementation, we would use
            # the ZeroX processor to answer the question more intelligently
            
            # For now, just provide basic answers based on the extracted data
            question_lower = question.lower()
            
            if "portfolio value" in question_lower:
                if self.extracted_data["portfolio_value"]:
                    return f"The portfolio value is ${self.extracted_data['portfolio_value']:,.2f}."
                else:
                    return "I couldn't find the portfolio value in the document."
            
            elif "top" in question_lower and ("holdings" in question_lower or "bonds" in question_lower):
                # Extract the number from the question (default to 5 if not found)
                import re
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
            
            elif "client" in question_lower:
                if self.extracted_data["client_info"]:
                    client_name = self.extracted_data["client_info"].get("name", "Unknown")
                    client_number = self.extracted_data["client_info"].get("number", "Unknown")
                    
                    return f"Client: {client_name}, Client Number: {client_number}"
                else:
                    return "I couldn't find client information in the document."
            
            elif "date" in question_lower:
                if self.extracted_data["document_date"]:
                    return f"The document date is {self.extracted_data['document_date']}."
                else:
                    return "I couldn't find the document date."
            
            else:
                return "I don't understand that question. Please ask about portfolio value, top holdings, asset allocation, client information, or document date."
        
        # If we don't have any agents that can answer questions, return a generic response
        return "I don't have enough information to answer that question. Please process a document first."
    
    def generate_report(self, output_dir: Optional[str] = None) -> str:
        """
        Generate a comprehensive report based on the extracted data.
        
        Args:
            output_dir: Directory to save the report
        
        Returns:
            Path to the generated report
        """
        # If we have ZeroX, use it to generate a report
        if self.zerox_processor:
            return self.zerox_processor.generate_financial_report(output_dir=output_dir)
        
        # If we don't have ZeroX, generate a basic report
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
                <table>
                    <tr>
                        <th>Asset Class</th>
                        <th>Value</th>
                        <th>Percentage</th>
                    </tr>
            """
            
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
        
        # Add top holdings
        if self.extracted_data["bonds"]:
            # Sort bonds by valuation
            sorted_bonds = sorted(self.extracted_data["bonds"], key=lambda x: x.get("valuation", 0), reverse=True)
            top_bonds = sorted_bonds[:10]  # Show top 10 holdings
            
            html_content += f"""
                <h2>Top Holdings</h2>
                <table>
                    <tr>
                        <th>Description</th>
                        <th>ISIN</th>
                        <th>Currency</th>
                        <th>Valuation</th>
                        <th>% of Portfolio</th>
                    </tr>
            """
            
            for bond in top_bonds:
                description = bond.get("description", "Unknown")
                isin = bond.get("isin", "N/A")
                currency = bond.get("currency", "N/A")
                valuation = bond.get("valuation", 0)
                
                # Calculate percentage of portfolio
                percentage = 0
                if self.extracted_data["portfolio_value"] and self.extracted_data["portfolio_value"] > 0:
                    percentage = (valuation / self.extracted_data["portfolio_value"]) * 100
                
                html_content += f"""
                    <tr>
                        <td>{description}</td>
                        <td>{isin}</td>
                        <td>{currency}</td>
                        <td>${valuation:,.2f}</td>
                        <td>{percentage:.2f}%</td>
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
    
    def start_interactive_session(self):
        """Start an interactive Q&A session."""
        print("\nFinancial Document Analysis System")
        print("=================================")
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
                self._show_help()
                continue
            
            elif user_input.lower() == 'report':
                report_path = self.generate_report()
                if report_path:
                    print(f"Report generated: {report_path}")
                    # Open the report in the default browser
                    import webbrowser
                    webbrowser.open(f"file://{os.path.abspath(report_path)}")
                continue
            
            answer = self.answer_question(user_input)
            print(f"\n{answer}\n")
    
    def _show_help(self):
        """Show help information."""
        print("\nExample questions:")
        print("- What is the total portfolio value?")
        print("- What is the asset allocation?")
        print("- What are the top 5 holdings?")
        print("- What are the top 10 bonds?")
        print("- What is the bond allocation?")
        print("- What are the bond maturities?")
        print("- What currencies are used in the portfolio?")
        print("- What is the client information?")
        print("- What is the document date?")
        print()
        print("Commands:")
        print("- 'report': Generate a financial report")
        print("- 'help': Show this help message")
        print("- 'exit': End the session")
        print()

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Analyze financial documents.")
    parser.add_argument("file_path", help="Path to the financial document")
    parser.add_argument("--api-key", help="API key for AI services")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model to use for AI processing")
    parser.add_argument("--output-dir", help="Directory to save output files")
    parser.add_argument("--no-zerox", action="store_true", help="Disable ZeroX processing")
    
    args = parser.parse_args()
    
    system = FinancialDocumentAnalysisSystem(api_key=args.api_key, model=args.model)
    system.process_document(args.file_path, output_dir=args.output_dir, use_zerox=not args.no_zerox)
    system.start_interactive_session()
    
    return 0

if __name__ == "__main__":
    main()
