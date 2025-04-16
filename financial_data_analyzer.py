"""
Financial Data Analyzer - Analyzes financial data and answers questions.
"""
import os
import re
import json
import pandas as pd
import numpy as np
from financial_table_extractor import FinancialTableExtractor

class FinancialDataAnalyzer:
    """Agent that analyzes financial data and answers questions."""
    
    def __init__(self):
        self.extractor = FinancialTableExtractor()
        self.bonds = []
        self.asset_allocation = {}
        self.portfolio_value = None
        self.client_info = {}
        self.document_date = None
        self.data_loaded = False
    
    def process_document(self, pdf_path):
        """Process a financial document to extract and analyze data."""
        print(f"Processing document: {pdf_path}")
        
        # Extract data using the financial table extractor
        extraction_results = self.extractor.process(pdf_path)
        
        # Load the extracted data
        self.bonds = extraction_results['bonds']
        self.asset_allocation = extraction_results['asset_allocation']
        self.portfolio_value = extraction_results['portfolio_value']
        self.client_info = extraction_results['client_info']
        self.document_date = extraction_results['document_date']
        
        # Perform additional analysis
        self._analyze_bonds()
        self._analyze_asset_allocation()
        
        self.data_loaded = True
        
        print("Document processed and analyzed. Ready for queries.")
    
    def _analyze_bonds(self):
        """Perform additional analysis on bonds."""
        if not self.bonds:
            return
        
        # Calculate additional metrics for bonds
        total_bond_value = sum(bond.get('valuation', 0) for bond in self.bonds)
        
        for bond in self.bonds:
            # Calculate percentage of total bond value
            if 'valuation' in bond and total_bond_value > 0:
                bond['percentage_of_bonds'] = (bond['valuation'] / total_bond_value) * 100
            
            # Calculate percentage of total portfolio
            if 'valuation' in bond and self.portfolio_value and self.portfolio_value > 0:
                bond['percentage_of_portfolio'] = (bond['valuation'] / self.portfolio_value) * 100
            
            # Calculate days to maturity if maturity date is available
            if 'maturity_date' in bond and self.document_date:
                try:
                    from datetime import datetime
                    maturity_date = datetime.strptime(bond['maturity_date'], '%d.%m.%Y')
                    document_date = datetime.strptime(self.document_date, '%d.%m.%Y')
                    days_to_maturity = (maturity_date - document_date).days
                    bond['days_to_maturity'] = days_to_maturity
                except Exception:
                    pass
    
    def _analyze_asset_allocation(self):
        """Perform additional analysis on asset allocation."""
        if not self.asset_allocation:
            return
        
        # Calculate total value from asset allocation
        total_value = sum(asset_class.get('value', 0) for asset_class in self.asset_allocation.values())
        
        # Check if total value matches portfolio value
        if self.portfolio_value and abs(total_value - self.portfolio_value) > 1:
            print(f"Warning: Total value from asset allocation ({total_value}) does not match portfolio value ({self.portfolio_value})")
    
    def answer_question(self, question):
        """Answer a question about the financial data."""
        if not self.data_loaded:
            return "Please process a document first."
        
        question_lower = question.lower()
        
        # Portfolio value questions
        if re.search(r'(portfolio|total).*value', question_lower) or re.search(r'value.*(portfolio|total)', question_lower):
            return self._answer_portfolio_value_question()
        
        # Bond questions
        elif 'bond' in question_lower:
            if re.search(r'top (\d+) bonds', question_lower):
                # Top N bonds question
                match = re.search(r'top (\d+)', question_lower)
                n = int(match.group(1)) if match else 5
                return self._answer_top_bonds_question(n)
            elif 'allocation' in question_lower or 'percentage' in question_lower:
                # Bond allocation question
                return self._answer_bond_allocation_question()
            elif 'maturity' in question_lower:
                # Bond maturity question
                return self._answer_bond_maturity_question()
            else:
                # General bond question
                return self._answer_general_bond_question()
        
        # Asset allocation questions
        elif 'asset' in question_lower and ('allocation' in question_lower or 'class' in question_lower):
            return self._answer_asset_allocation_question()
        
        # Top holdings questions
        elif re.search(r'top (\d+) (holdings|positions|securities)', question_lower):
            match = re.search(r'top (\d+)', question_lower)
            n = int(match.group(1)) if match else 5
            return self._answer_top_holdings_question(n)
        
        # Client information questions
        elif 'client' in question_lower or 'customer' in question_lower:
            return self._answer_client_info_question()
        
        # Document date questions
        elif 'date' in question_lower or 'when' in question_lower:
            return self._answer_document_date_question()
        
        # Currency questions
        elif 'currency' in question_lower:
            return self._answer_currency_question()
        
        # Specific security questions
        elif 'isin' in question_lower:
            # Extract ISIN from question
            isin_match = re.search(r'([A-Z0-9]{12})', question)
            if isin_match:
                isin = isin_match.group(1)
                return self._answer_specific_security_question(isin)
        
        # Generate report questions
        elif 'report' in question_lower or 'generate' in question_lower or 'create' in question_lower:
            if 'bond' in question_lower:
                return self._generate_bond_report()
            elif 'asset' in question_lower:
                return self._generate_asset_allocation_report()
            elif 'portfolio' in question_lower:
                return self._generate_portfolio_report()
            else:
                return self._generate_summary_report()
        
        # Fallback
        return "I don't understand that question. Please ask about portfolio value, bonds, asset allocation, top holdings, or client information."
    
    def _answer_portfolio_value_question(self):
        """Answer a question about portfolio value."""
        if self.portfolio_value:
            return f"The total portfolio value is ${self.portfolio_value:,.2f}."
        else:
            return "I couldn't find the portfolio value in the document."
    
    def _answer_top_bonds_question(self, n=5):
        """Answer a question about top N bonds."""
        if not self.bonds:
            return "I couldn't find any bonds in the document."
        
        # Sort bonds by valuation
        sorted_bonds = sorted(self.bonds, key=lambda x: x.get('valuation', 0), reverse=True)
        top_bonds = sorted_bonds[:n]
        
        response = f"The top {len(top_bonds)} bonds by value are:\n"
        for i, bond in enumerate(top_bonds, 1):
            description = bond.get('description', 'Unknown Bond')
            # Extract the bond name from the description
            name_match = re.search(r'^([A-Z\s]+)', description)
            name = name_match.group(1).strip() if name_match else description
            
            valuation = bond.get('valuation', 0)
            percentage = bond.get('percentage_of_portfolio', 0)
            
            response += f"{i}. {name}: ${valuation:,.2f} ({percentage:.2f}% of portfolio)\n"
        
        return response
    
    def _answer_bond_allocation_question(self):
        """Answer a question about bond allocation."""
        if not self.bonds:
            return "I couldn't find any bonds in the document."
        
        total_bond_value = sum(bond.get('valuation', 0) for bond in self.bonds)
        
        if self.portfolio_value and self.portfolio_value > 0:
            bond_percentage = (total_bond_value / self.portfolio_value) * 100
            return f"Bonds make up ${total_bond_value:,.2f} or {bond_percentage:.2f}% of the total portfolio value."
        else:
            return f"The total value of bonds is ${total_bond_value:,.2f}, but I couldn't determine the percentage of the portfolio."
    
    def _answer_bond_maturity_question(self):
        """Answer a question about bond maturities."""
        if not self.bonds:
            return "I couldn't find any bonds in the document."
        
        # Group bonds by maturity year
        bonds_with_maturity = [bond for bond in self.bonds if 'maturity_date' in bond]
        
        if not bonds_with_maturity:
            return "I couldn't find maturity information for the bonds."
        
        # Extract years from maturity dates
        for bond in bonds_with_maturity:
            match = re.search(r'(\d{4})', bond['maturity_date'])
            if match:
                bond['maturity_year'] = int(match.group(1))
        
        # Group by maturity year
        maturity_years = {}
        for bond in bonds_with_maturity:
            if 'maturity_year' in bond:
                year = bond['maturity_year']
                if year not in maturity_years:
                    maturity_years[year] = []
                maturity_years[year].append(bond)
        
        # Sort years
        sorted_years = sorted(maturity_years.keys())
        
        response = "Bond maturity profile:\n"
        for year in sorted_years:
            bonds = maturity_years[year]
            total_value = sum(bond.get('valuation', 0) for bond in bonds)
            response += f"{year}: {len(bonds)} bonds, ${total_value:,.2f}\n"
        
        return response
    
    def _answer_general_bond_question(self):
        """Answer a general question about bonds."""
        if not self.bonds:
            return "I couldn't find any bonds in the document."
        
        total_bond_value = sum(bond.get('valuation', 0) for bond in self.bonds)
        
        response = f"There are {len(self.bonds)} bonds with a total value of ${total_bond_value:,.2f}.\n"
        
        # Add information about bond types if available
        bond_types = {}
        for bond in self.bonds:
            description = bond.get('description', '')
            
            # Try to determine bond type
            bond_type = 'Other'
            if 'Ordinary Bonds' in description:
                bond_type = 'Ordinary Bonds'
            elif 'Zero Bonds' in description:
                bond_type = 'Zero Bonds'
            elif 'Structured Bonds' in description:
                bond_type = 'Structured Bonds'
            elif 'Bond Funds' in description or 'Bond funds' in description:
                bond_type = 'Bond Funds'
            
            if bond_type not in bond_types:
                bond_types[bond_type] = []
            bond_types[bond_type].append(bond)
        
        if bond_types:
            response += "\nBreakdown by bond type:\n"
            for bond_type, bonds in bond_types.items():
                total_value = sum(bond.get('valuation', 0) for bond in bonds)
                percentage = (total_value / total_bond_value) * 100 if total_bond_value > 0 else 0
                response += f"{bond_type}: {len(bonds)} bonds, ${total_value:,.2f} ({percentage:.2f}%)\n"
        
        return response
    
    def _answer_asset_allocation_question(self):
        """Answer a question about asset allocation."""
        if not self.asset_allocation:
            return "I couldn't find asset allocation information in the document."
        
        response = "Asset Allocation:\n"
        
        for asset_class, data in self.asset_allocation.items():
            value = data.get('value', 0)
            percentage = data.get('percentage', 0)
            
            response += f"{asset_class}: ${value:,.2f} ({percentage:.2f}%)\n"
            
            # Add sub-classes if available
            sub_classes = data.get('sub_classes', {})
            if sub_classes:
                for sub_class, sub_data in sub_classes.items():
                    sub_value = sub_data.get('value', 0)
                    sub_percentage = sub_data.get('percentage', 0)
                    
                    response += f"  - {sub_class}: ${sub_value:,.2f} ({sub_percentage:.2f}%)\n"
        
        return response
    
    def _answer_top_holdings_question(self, n=5):
        """Answer a question about top N holdings."""
        # Combine bonds and other securities
        all_securities = self.bonds.copy()
        
        # Sort by valuation
        sorted_securities = sorted(all_securities, key=lambda x: x.get('valuation', 0), reverse=True)
        top_securities = sorted_securities[:n]
        
        if not top_securities:
            return f"I couldn't find information about the top {n} holdings."
        
        response = f"The top {len(top_securities)} holdings by value are:\n"
        for i, security in enumerate(top_securities, 1):
            description = security.get('description', 'Unknown Security')
            # Extract the security name from the description
            name_match = re.search(r'^([A-Z\s]+)', description)
            name = name_match.group(1).strip() if name_match else description
            
            valuation = security.get('valuation', 0)
            percentage = security.get('percentage_of_portfolio', 0)
            
            response += f"{i}. {name}: ${valuation:,.2f} ({percentage:.2f}% of portfolio)\n"
        
        return response
    
    def _answer_client_info_question(self):
        """Answer a question about client information."""
        if not self.client_info:
            return "I couldn't find client information in the document."
        
        client_name = self.client_info.get('name', 'Unknown')
        client_number = self.client_info.get('number', 'Unknown')
        
        return f"Client: {client_name}, Client Number: {client_number}"
    
    def _answer_document_date_question(self):
        """Answer a question about document date."""
        if self.document_date:
            return f"The document date is {self.document_date}."
        else:
            return "I couldn't find the document date."
    
    def _answer_currency_question(self):
        """Answer a question about currencies."""
        if not self.bonds:
            return "I couldn't find any securities to determine currencies."
        
        # Count securities by currency
        currencies = {}
        for bond in self.bonds:
            currency = bond.get('currency')
            if currency:
                if currency not in currencies:
                    currencies[currency] = {
                        'count': 0,
                        'value': 0
                    }
                currencies[currency]['count'] += 1
                currencies[currency]['value'] += bond.get('valuation', 0)
        
        if not currencies:
            return "I couldn't determine the currencies used in the portfolio."
        
        response = "The portfolio contains the following currencies:\n"
        for currency, data in currencies.items():
            count = data['count']
            value = data['value']
            percentage = (value / self.portfolio_value) * 100 if self.portfolio_value and self.portfolio_value > 0 else 0
            
            response += f"{currency}: {count} securities, ${value:,.2f} ({percentage:.2f}% of portfolio)\n"
        
        return response
    
    def _answer_specific_security_question(self, isin):
        """Answer a question about a specific security by ISIN."""
        # Find the security with the given ISIN
        security = None
        for bond in self.bonds:
            if bond.get('isin') == isin:
                security = bond
                break
        
        if not security:
            return f"I couldn't find a security with ISIN {isin}."
        
        # Extract information
        description = security.get('description', 'Unknown Security')
        valuation = security.get('valuation', 0)
        currency = security.get('currency', 'Unknown')
        nominal = security.get('nominal', 0)
        price = security.get('price', 0)
        percentage = security.get('percentage_of_portfolio', 0)
        
        response = f"Security with ISIN {isin}:\n"
        response += f"Description: {description}\n"
        response += f"Valuation: ${valuation:,.2f} ({percentage:.2f}% of portfolio)\n"
        response += f"Currency: {currency}\n"
        response += f"Nominal/Quantity: {nominal:,.2f}\n"
        response += f"Price: {price:,.4f}\n"
        
        # Add maturity information if available
        if 'maturity_date' in security:
            response += f"Maturity Date: {security['maturity_date']}\n"
        
        # Add days to maturity if available
        if 'days_to_maturity' in security:
            response += f"Days to Maturity: {security['days_to_maturity']}\n"
        
        return response
    
    def _generate_bond_report(self):
        """Generate a report about bonds."""
        if not self.bonds:
            return "I couldn't find any bonds in the document."
        
        # Create a DataFrame from bonds
        bonds_df = pd.DataFrame(self.bonds)
        
        # Calculate summary statistics
        total_bond_value = bonds_df['valuation'].sum() if 'valuation' in bonds_df.columns else 0
        bond_count = len(bonds_df)
        
        # Calculate percentage of portfolio
        portfolio_percentage = (total_bond_value / self.portfolio_value) * 100 if self.portfolio_value and self.portfolio_value > 0 else 0
        
        # Group by currency
        currency_groups = bonds_df.groupby('currency')['valuation'].agg(['sum', 'count']) if 'currency' in bonds_df.columns and 'valuation' in bonds_df.columns else None
        
        # Generate report
        report = "Bond Portfolio Report\n"
        report += "====================\n\n"
        
        report += f"Total Bond Value: ${total_bond_value:,.2f}\n"
        report += f"Number of Bonds: {bond_count}\n"
        report += f"Percentage of Portfolio: {portfolio_percentage:.2f}%\n\n"
        
        if currency_groups is not None:
            report += "Breakdown by Currency:\n"
            for currency, data in currency_groups.iterrows():
                value = data['sum']
                count = data['count']
                percentage = (value / total_bond_value) * 100 if total_bond_value > 0 else 0
                
                report += f"{currency}: {count} bonds, ${value:,.2f} ({percentage:.2f}%)\n"
            
            report += "\n"
        
        # Top 5 bonds by value
        if 'valuation' in bonds_df.columns:
            top_bonds = bonds_df.sort_values('valuation', ascending=False).head(5)
            
            report += "Top 5 Bonds by Value:\n"
            for i, (_, bond) in enumerate(top_bonds.iterrows(), 1):
                description = bond.get('description', 'Unknown Bond')
                valuation = bond.get('valuation', 0)
                percentage = (valuation / self.portfolio_value) * 100 if self.portfolio_value and self.portfolio_value > 0 else 0
                
                report += f"{i}. {description}: ${valuation:,.2f} ({percentage:.2f}% of portfolio)\n"
        
        return report
    
    def _generate_asset_allocation_report(self):
        """Generate a report about asset allocation."""
        if not self.asset_allocation:
            return "I couldn't find asset allocation information in the document."
        
        report = "Asset Allocation Report\n"
        report += "======================\n\n"
        
        # Calculate total value
        total_value = sum(asset_class.get('value', 0) for asset_class in self.asset_allocation.values())
        
        report += f"Total Portfolio Value: ${self.portfolio_value:,.2f}\n" if self.portfolio_value else ""
        report += f"Total Value from Asset Classes: ${total_value:,.2f}\n\n"
        
        # Add asset classes
        report += "Asset Classes:\n"
        for asset_class, data in self.asset_allocation.items():
            value = data.get('value', 0)
            percentage = data.get('percentage', 0)
            
            report += f"{asset_class}: ${value:,.2f} ({percentage:.2f}%)\n"
            
            # Add sub-classes if available
            sub_classes = data.get('sub_classes', {})
            if sub_classes:
                for sub_class, sub_data in sub_classes.items():
                    sub_value = sub_data.get('value', 0)
                    sub_percentage = sub_data.get('percentage', 0)
                    
                    report += f"  - {sub_class}: ${sub_value:,.2f} ({sub_percentage:.2f}%)\n"
        
        return report
    
    def _generate_portfolio_report(self):
        """Generate a comprehensive portfolio report."""
        report = "Portfolio Report\n"
        report += "===============\n\n"
        
        # Add client information
        if self.client_info:
            client_name = self.client_info.get('name', 'Unknown')
            client_number = self.client_info.get('number', 'Unknown')
            
            report += f"Client: {client_name}\n"
            report += f"Client Number: {client_number}\n"
        
        # Add document date
        if self.document_date:
            report += f"Document Date: {self.document_date}\n"
        
        report += f"Portfolio Value: ${self.portfolio_value:,.2f}\n\n" if self.portfolio_value else "\n"
        
        # Add asset allocation section
        report += self._generate_asset_allocation_report()
        report += "\n"
        
        # Add bond section
        report += self._generate_bond_report()
        
        return report
    
    def _generate_summary_report(self):
        """Generate a summary report."""
        report = "Portfolio Summary Report\n"
        report += "=======================\n\n"
        
        # Add client information
        if self.client_info:
            client_name = self.client_info.get('name', 'Unknown')
            client_number = self.client_info.get('number', 'Unknown')
            
            report += f"Client: {client_name}\n"
            report += f"Client Number: {client_number}\n"
        
        # Add document date
        if self.document_date:
            report += f"Document Date: {self.document_date}\n"
        
        report += f"Portfolio Value: ${self.portfolio_value:,.2f}\n\n" if self.portfolio_value else "\n"
        
        # Add asset allocation summary
        if self.asset_allocation:
            report += "Asset Allocation Summary:\n"
            for asset_class, data in self.asset_allocation.items():
                value = data.get('value', 0)
                percentage = data.get('percentage', 0)
                
                report += f"{asset_class}: ${value:,.2f} ({percentage:.2f}%)\n"
            
            report += "\n"
        
        # Add top 5 holdings
        all_securities = self.bonds.copy()
        sorted_securities = sorted(all_securities, key=lambda x: x.get('valuation', 0), reverse=True)
        top_securities = sorted_securities[:5]
        
        if top_securities:
            report += "Top 5 Holdings:\n"
            for i, security in enumerate(top_securities, 1):
                description = security.get('description', 'Unknown Security')
                valuation = security.get('valuation', 0)
                percentage = (valuation / self.portfolio_value) * 100 if self.portfolio_value and self.portfolio_value > 0 else 0
                
                report += f"{i}. {description}: ${valuation:,.2f} ({percentage:.2f}% of portfolio)\n"
        
        return report
    
    def start_interactive_session(self):
        """Start an interactive Q&A session."""
        print("\nFinancial Data Analyzer")
        print("======================")
        print("I can answer questions about the financial document.")
        print("Type 'exit' to end the session.")
        print("Type 'help' to see example questions.")
        print()
        
        while True:
            user_input = input("Ask a question: ").strip()
            
            if user_input.lower() == 'exit':
                print("Ending session. Goodbye!")
                break
            
            elif user_input.lower() == 'help':
                self._show_help()
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
        print("- Generate a bond report")
        print("- Generate an asset allocation report")
        print("- Generate a portfolio report")
        print()

def main():
    """Main function."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python financial_data_analyzer.py <pdf_path>")
        return 1
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return 1
    
    analyzer = FinancialDataAnalyzer()
    analyzer.process_document(pdf_path)
    analyzer.start_interactive_session()
    
    return 0

if __name__ == "__main__":
    main()
