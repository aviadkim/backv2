"""
Financial Table Extractor - Extracts structured data from financial tables in PDFs.
"""
import os
import re
import json
import pandas as pd
import pdfplumber
from collections import defaultdict

class FinancialTableExtractor:
    """Agent that extracts structured data from financial tables."""
    
    def __init__(self):
        self.bonds = []
        self.asset_allocation = {}
        self.portfolio_value = None
        self.client_info = {}
        self.document_date = None
    
    def process(self, pdf_path):
        """Process a financial document to extract structured data."""
        print(f"Processing financial document: {pdf_path}")
        
        # Create output directory
        output_dir = 'extraction_results'
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract tables from PDF
        tables_by_page = self._extract_tables(pdf_path)
        
        # Extract client information
        self._extract_client_info(tables_by_page)
        
        # Extract bonds
        self._extract_bonds(tables_by_page)
        
        # Extract asset allocation
        self._extract_asset_allocation(tables_by_page)
        
        # Extract portfolio value
        self._extract_portfolio_value(tables_by_page)
        
        # Save results
        self._save_results(output_dir)
        
        print(f"Extraction completed. Results saved to {output_dir}")
        print(f"Client: {self.client_info.get('name', 'Unknown')}")
        print(f"Document Date: {self.document_date}")
        print(f"Portfolio Value: ${self.portfolio_value:,.2f}" if self.portfolio_value else "Portfolio Value not found")
        print(f"Bonds found: {len(self.bonds)}")
        print(f"Asset Classes: {', '.join(self.asset_allocation.keys())}")
        
        return {
            'bonds': self.bonds,
            'asset_allocation': self.asset_allocation,
            'portfolio_value': self.portfolio_value,
            'client_info': self.client_info,
            'document_date': self.document_date
        }
    
    def _extract_tables(self, pdf_path):
        """Extract tables from PDF."""
        tables_by_page = {}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        tables_by_page[page_num] = tables
                        print(f"Page {page_num}: {len(tables)} tables extracted")
        except Exception as e:
            print(f"Error extracting tables: {str(e)}")
        
        return tables_by_page
    
    def _extract_client_info(self, tables_by_page):
        """Extract client information."""
        for page_num, tables in tables_by_page.items():
            for table in tables:
                # Skip empty tables
                if not table or len(table) == 0:
                    continue
                
                # Look for client information in the header
                for row in table[:3]:  # Check first few rows
                    for cell in row:
                        if not cell:
                            continue
                        
                        # Look for client name
                        client_match = re.search(r'([A-Z\s]+LTD\.)', str(cell))
                        if client_match:
                            self.client_info['name'] = client_match.group(1).strip()
                        
                        # Look for client number
                        client_num_match = re.search(r'Client\s+Number[:\s]+(\d+)', str(cell))
                        if client_num_match:
                            self.client_info['number'] = client_num_match.group(1).strip()
                        
                        # Look for document date
                        date_match = re.search(r'Valuation\s+as\s+of\s+(\d{2}\.\d{2}\.\d{4})', str(cell))
                        if date_match:
                            self.document_date = date_match.group(1).strip()
    
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
    
    def _extract_bonds(self, tables_by_page):
        """Extract bonds from tables."""
        for page_num, tables in tables_by_page.items():
            for table_idx, table in enumerate(tables):
                # Skip empty tables
                if not table or len(table) <= 1:
                    continue
                
                # Check if this is a bonds table
                is_bonds_table = False
                for row in table[:3]:  # Check first few rows
                    for cell in row:
                        if cell and 'Bonds' in str(cell):
                            is_bonds_table = True
                            break
                    if is_bonds_table:
                        break
                
                if not is_bonds_table:
                    # Also check for bond-related column headers
                    header_row = table[0] if table else []
                    bond_headers = ['Currency', 'Nominal', 'Description', 'ISIN', 'Maturity']
                    if header_row and any(header in str(cell) for cell in header_row for header in bond_headers):
                        is_bonds_table = True
                
                if is_bonds_table:
                    # This is a bonds table, extract bonds
                    self._extract_bonds_from_table(table, page_num, table_idx)
    
    def _extract_bonds_from_table(self, table, page_num, table_idx):
        """Extract bonds from a bonds table."""
        # Identify the header row
        header_row = table[0]
        
        # Map column indices to their meanings
        column_indices = {}
        for i, cell in enumerate(header_row):
            if not cell:
                continue
            
            cell_lower = str(cell).lower()
            
            if 'currency' in cell_lower:
                column_indices['currency'] = i
            elif 'nominal' in cell_lower or 'quantity' in cell_lower:
                column_indices['nominal'] = i
            elif 'description' in cell_lower:
                column_indices['description'] = i
            elif 'price' in cell_lower and 'actual' in cell_lower:
                column_indices['price'] = i
            elif 'valuation' in cell_lower:
                column_indices['valuation'] = i
            elif '%' in cell_lower and 'assets' in cell_lower:
                column_indices['percentage'] = i
        
        # Extract bonds from data rows
        for row_idx, row in enumerate(table[1:], 1):
            # Skip empty rows or header rows
            if not row or all(not cell for cell in row) or 'Currency' in str(row[0]):
                continue
            
            # Extract bond data
            bond = {
                'page': page_num,
                'table_idx': table_idx,
                'row_idx': row_idx
            }
            
            # Extract data from mapped columns
            for field, col_idx in column_indices.items():
                if col_idx < len(row) and row[col_idx]:
                    if field in ['nominal', 'price', 'valuation', 'percentage']:
                        bond[field] = self._clean_number(row[col_idx])
                    else:
                        bond[field] = str(row[col_idx]).strip()
            
            # Extract ISIN from description
            if 'description' in bond:
                isin_match = re.search(r'ISIN:\s*([A-Z0-9]+)', bond['description'])
                if isin_match:
                    bond['isin'] = isin_match.group(1).strip()
                
                # Extract maturity date
                maturity_match = re.search(r'Maturity:\s*(\d{2}\.\d{2}\.\d{4})', bond['description'])
                if maturity_match:
                    bond['maturity_date'] = maturity_match.group(1).strip()
            
            # Only add bonds with at least currency, description, and valuation
            if 'currency' in bond and 'description' in bond and 'valuation' in bond:
                self.bonds.append(bond)
    
    def _extract_asset_allocation(self, tables_by_page):
        """Extract asset allocation from tables."""
        for page_num, tables in tables_by_page.items():
            for table_idx, table in enumerate(tables):
                # Skip empty tables
                if not table or len(table) <= 1:
                    continue
                
                # Check if this is an asset allocation table
                is_asset_table = False
                for row in table[:3]:  # Check first few rows
                    for cell in row:
                        if cell and 'Asset Allocation' in str(cell):
                            is_asset_table = True
                            break
                    if is_asset_table:
                        break
                
                if is_asset_table:
                    # This is an asset allocation table, extract asset allocation
                    self._extract_asset_allocation_from_table(table, page_num, table_idx)
    
    def _extract_asset_allocation_from_table(self, table, page_num, table_idx):
        """Extract asset allocation from an asset allocation table."""
        # Extract asset classes and their values
        current_asset_class = None
        
        for row in table:
            # Skip empty rows
            if not row or all(not cell for cell in row):
                continue
            
            # Check if this is a main asset class row
            first_cell = str(row[0]).strip() if row[0] else ""
            if first_cell and first_cell[0].isupper() and len(row) >= 3:
                # This is a main asset class
                current_asset_class = first_cell
                
                # Extract value and percentage if available
                if len(row) >= 3 and row[1] and row[2]:
                    value = self._clean_number(row[1])
                    percentage = self._clean_number(row[2])
                    
                    if value is not None:
                        self.asset_allocation[current_asset_class] = {
                            'value': value,
                            'percentage': percentage,
                            'sub_classes': {}
                        }
            
            # Check if this is a sub-asset class row
            elif current_asset_class and first_cell and not first_cell[0].isupper() and len(row) >= 3:
                # This is a sub-asset class
                sub_class = first_cell
                
                # Extract value and percentage if available
                if len(row) >= 3 and row[1] and row[2]:
                    value = self._clean_number(row[1])
                    percentage = self._clean_number(row[2])
                    
                    if value is not None and current_asset_class in self.asset_allocation:
                        self.asset_allocation[current_asset_class]['sub_classes'][sub_class] = {
                            'value': value,
                            'percentage': percentage
                        }
    
    def _extract_portfolio_value(self, tables_by_page):
        """Extract portfolio value from tables."""
        for page_num, tables in tables_by_page.items():
            for table in tables:
                # Skip empty tables
                if not table or len(table) == 0:
                    continue
                
                # Look for portfolio value
                for row in table:
                    if not row or len(row) < 2:
                        continue
                    
                    first_cell = str(row[0]).strip() if row[0] else ""
                    if first_cell in ['Total assets', 'Portfolio Total']:
                        # This is the portfolio value row
                        if len(row) >= 2 and row[1]:
                            value = self._clean_number(row[1])
                            if value is not None:
                                self.portfolio_value = value
                                return
    
    def _save_results(self, output_dir):
        """Save extraction results."""
        # Save bonds to CSV
        bonds_df = pd.DataFrame(self.bonds)
        bonds_path = os.path.join(output_dir, 'bonds.csv')
        bonds_df.to_csv(bonds_path, index=False)
        
        # Save asset allocation to JSON
        asset_allocation_path = os.path.join(output_dir, 'asset_allocation.json')
        with open(asset_allocation_path, 'w', encoding='utf-8') as f:
            json.dump(self.asset_allocation, f, indent=2)
        
        # Save client info and portfolio value to JSON
        summary_path = os.path.join(output_dir, 'summary.json')
        summary = {
            'client_info': self.client_info,
            'document_date': self.document_date,
            'portfolio_value': self.portfolio_value
        }
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

def main():
    """Main function."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python financial_table_extractor.py <pdf_path>")
        return 1
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return 1
    
    extractor = FinancialTableExtractor()
    extractor.process(pdf_path)
    
    return 0

if __name__ == "__main__":
    main()
