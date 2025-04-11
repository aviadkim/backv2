import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from .report_base import ReportGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialStatementReportGenerator(ReportGenerator):
    """Specialized report generator for financial statements."""
    
    def _generate_profit_loss_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a profit and loss report."""
        # Extract relevant data
        period = data.get("period", "")
        revenue_items = data.get("revenue_items", [])
        expense_items = data.get("expense_items", [])
        
        # Calculate totals
        total_revenue = sum(item.get("amount", 0) for item in revenue_items)
        total_expenses = sum(item.get("amount", 0) for item in expense_items)
        net_income = total_revenue - total_expenses
        
        # Format the report
        report = {
            "title": "Profit and Loss Statement",
            "period": period,
            "summary": {
                "total_revenue": self._format_currency(total_revenue),
                "total_expenses": self._format_currency(total_expenses),
                "net_income": self._format_currency(net_income),
                "profit_margin": self._format_percentage((net_income / total_revenue * 100) if total_revenue else 0)
            },
            "details": {
                "revenue_items": self._format_financial_items(revenue_items),
                "expense_items": self._format_financial_items(expense_items)
            }
        }
        
        return report
    
    def _generate_balance_sheet_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a balance sheet report."""
        # Extract relevant data
        as_of_date = data.get("as_of_date", datetime.now().isoformat())
        assets = data.get("assets", {})
        liabilities = data.get("liabilities", {})
        equity = data.get("equity", {})
        
        # Calculate totals
        total_assets = self._calculate_category_total(assets)
        total_liabilities = self._calculate_category_total(liabilities)
        total_equity = self._calculate_category_total(equity)
        
        # Format the report
        report = {
            "title": "Balance Sheet",
            "as_of_date": as_of_date,
            "summary": {
                "total_assets": self._format_currency(total_assets),
                "total_liabilities": self._format_currency(total_liabilities),
                "total_equity": self._format_currency(total_equity),
                "debt_to_equity_ratio": self._format_ratio(total_liabilities / total_equity if total_equity else 0)
            },
            "details": {
                "assets": self._format_balance_sheet_category(assets),
                "liabilities": self._format_balance_sheet_category(liabilities),
                "equity": self._format_balance_sheet_category(equity)
            }
        }
        
        return report
    
    def _generate_cash_flow_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a cash flow report."""
        # Extract relevant data
        period = data.get("period", "")
        operating = data.get("operating", {})
        investing = data.get("investing", {})
        financing = data.get("financing", {})
        
        # Calculate totals
        net_operating = self._calculate_category_total(operating)
        net_investing = self._calculate_category_total(investing)
        net_financing = self._calculate_category_total(financing)
        net_change = net_operating + net_investing + net_financing
        
        # Format the report
        report = {
            "title": "Cash Flow Statement",
            "period": period,
            "summary": {
                "net_operating_cash_flow": self._format_currency(net_operating),
                "net_investing_cash_flow": self._format_currency(net_investing),
                "net_financing_cash_flow": self._format_currency(net_financing),
                "net_change_in_cash": self._format_currency(net_change)
            },
            "details": {
                "operating": self._format_cash_flow_category(operating),
                "investing": self._format_cash_flow_category(investing),
                "financing": self._format_cash_flow_category(financing)
            }
        }
        
        return report
    
    def _format_financial_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format financial statement line items."""
        formatted_items = []
        
        for item in items:
            formatted_item = {
                "name": item.get("name", "Unknown"),
                "amount": self._format_currency(item.get("amount", 0)),
                "raw_amount": item.get("amount", 0),
                "notes": item.get("notes", "")
            }
            
            formatted_items.append(formatted_item)
        
        return formatted_items
    
    def _format_balance_sheet_category(self, category: Dict[str, Any]) -> Dict[str, Any]:
        """Format a balance sheet category (assets, liabilities, equity)."""
        formatted_category = {}
        
        for subcategory, items in category.items():
            formatted_items = self._format_financial_items(items)
            subcategory_total = sum(item.get("amount", 0) for item in items)
            
            formatted_category[subcategory] = {
                "items": formatted_items,
                "total": self._format_currency(subcategory_total)
            }
        
        return formatted_category
    
    def _format_cash_flow_category(self, category: Dict[str, Any]) -> Dict[str, Any]:
        """Format a cash flow category (operating, investing, financing)."""
        formatted_category = {}
        
        for subcategory, items in category.items():
            formatted_items = self._format_financial_items(items)
            subcategory_total = sum(item.get("amount", 0) for item in items)
            
            formatted_category[subcategory] = {
                "items": formatted_items,
                "total": self._format_currency(subcategory_total)
            }
        
        return formatted_category
    
    def _calculate_category_total(self, category: Dict[str, Any]) -> float:
        """Calculate the total for a financial statement category."""
        total = 0
        
        for subcategory, items in category.items():
            if isinstance(items, list):
                subcategory_total = sum(item.get("amount", 0) for item in items)
                total += subcategory_total
        
        return total
    
    def _profit_loss_to_html(self, data: Dict[str, Any]) -> str:
        """Convert profit and loss report data to HTML."""
        html = "<div class='profit-loss-report'>"
        
        # Header
        html += f"<h2>{data.get('title', 'Profit and Loss Statement')}</h2>"
        html += f"<p class='period'>Period: {data.get('period', '')}</p>"
        
        # Summary
        summary = data.get("summary", {})
        html += "<div class='summary-section'>"
        html += "<h3>Summary</h3>"
        html += "<table class='summary-table'>"
        html += f"<tr><td>Total Revenue</td><td>{summary.get('total_revenue', '$0.00')}</td></tr>"
        html += f"<tr><td>Total Expenses</td><td>{summary.get('total_expenses', '$0.00')}</td></tr>"
        html += f"<tr class='net-income'><td>Net Income</td><td>{summary.get('net_income', '$0.00')}</td></tr>"
        html += f"<tr><td>Profit Margin</td><td>{summary.get('profit_margin', '0.00%')}</td></tr>"
        html += "</table>"
        html += "</div>"
        
        # Revenue details
        details = data.get("details", {})
        revenue_items = details.get("revenue_items", [])
        
        if revenue_items:
            html += "<div class='revenue-section'>"
            html += "<h3>Revenue</h3>"
            html += "<table class='items-table'>"
            html += "<thead><tr><th>Item</th><th>Amount</th><th>Notes</th></tr></thead>"
            html += "<tbody>"
            
            for item in revenue_items:
                html += f"<tr><td>{item.get('name', 'Unknown')}</td><td>{item.get('amount', '$0.00')}</td><td>{item.get('notes', '')}</td></tr>"
            
            html += "</tbody>"
            html += "</table>"
            html += "</div>"
        
        # Expense details
        expense_items = details.get("expense_items", [])
        
        if expense_items:
            html += "<div class='expense-section'>"
            html += "<h3>Expenses</h3>"
            html += "<table class='items-table'>"
            html += "<thead><tr><th>Item</th><th>Amount</th><th>Notes</th></tr></thead>"
            html += "<tbody>"
            
            for item in expense_items:
                html += f"<tr><td>{item.get('name', 'Unknown')}</td><td>{item.get('amount', '$0.00')}</td><td>{item.get('notes', '')}</td></tr>"
            
            html += "</tbody>"
            html += "</table>"
            html += "</div>"
        
        html += "</div>"
        return html
    
    def _balance_sheet_to_html(self, data: Dict[str, Any]) -> str:
        """Convert balance sheet report data to HTML."""
        html = "<div class='balance-sheet-report'>"
        
        # Header
        html += f"<h2>{data.get('title', 'Balance Sheet')}</h2>"
        html += f"<p class='as-of-date'>As of: {data.get('as_of_date', '')}</p>"
        
        # Summary
        summary = data.get("summary", {})
        html += "<div class='summary-section'>"
        html += "<h3>Summary</h3>"
        html += "<table class='summary-table'>"
        html += f"<tr><td>Total Assets</td><td>{summary.get('total_assets', '$0.00')}</td></tr>"
        html += f"<tr><td>Total Liabilities</td><td>{summary.get('total_liabilities', '$0.00')}</td></tr>"
        html += f"<tr><td>Total Equity</td><td>{summary.get('total_equity', '$0.00')}</td></tr>"
        html += f"<tr><td>Debt to Equity Ratio</td><td>{summary.get('debt_to_equity_ratio', '0.00')}</td></tr>"
        html += "</table>"
        html += "</div>"
        
        # Assets
        details = data.get("details", {})
        assets = details.get("assets", {})
        
        if assets:
            html += "<div class='assets-section'>"
            html += "<h3>Assets</h3>"
            
            for subcategory, subcategory_data in assets.items():
                html += f"<h4>{subcategory}</h4>"
                html += "<table class='items-table'>"
                html += "<thead><tr><th>Item</th><th>Amount</th><th>Notes</th></tr></thead>"
                html += "<tbody>"
                
                for item in subcategory_data.get("items", []):
                    html += f"<tr><td>{item.get('name', 'Unknown')}</td><td>{item.get('amount', '$0.00')}</td><td>{item.get('notes', '')}</td></tr>"
                
                html += f"<tr class='subtotal'><td>Total {subcategory}</td><td>{subcategory_data.get('total', '$0.00')}</td><td></td></tr>"
                html += "</tbody>"
                html += "</table>"
            
            html += "</div>"
        
        # Liabilities
        liabilities = details.get("liabilities", {})
        
        if liabilities:
            html += "<div class='liabilities-section'>"
            html += "<h3>Liabilities</h3>"
            
            for subcategory, subcategory_data in liabilities.items():
                html += f"<h4>{subcategory}</h4>"
                html += "<table class='items-table'>"
                html += "<thead><tr><th>Item</th><th>Amount</th><th>Notes</th></tr></thead>"
                html += "<tbody>"
                
                for item in subcategory_data.get("items", []):
                    html += f"<tr><td>{item.get('name', 'Unknown')}</td><td>{item.get('amount', '$0.00')}</td><td>{item.get('notes', '')}</td></tr>"
                
                html += f"<tr class='subtotal'><td>Total {subcategory}</td><td>{subcategory_data.get('total', '$0.00')}</td><td></td></tr>"
                html += "</tbody>"
                html += "</table>"
            
            html += "</div>"
        
        # Equity
        equity = details.get("equity", {})
        
        if equity:
            html += "<div class='equity-section'>"
            html += "<h3>Equity</h3>"
            
            for subcategory, subcategory_data in equity.items():
                html += f"<h4>{subcategory}</h4>"
                html += "<table class='items-table'>"
                html += "<thead><tr><th>Item</th><th>Amount</th><th>Notes</th></tr></thead>"
                html += "<tbody>"
                
                for item in subcategory_data.get("items", []):
                    html += f"<tr><td>{item.get('name', 'Unknown')}</td><td>{item.get('amount', '$0.00')}</td><td>{item.get('notes', '')}</td></tr>"
                
                html += f"<tr class='subtotal'><td>Total {subcategory}</td><td>{subcategory_data.get('total', '$0.00')}</td><td></td></tr>"
                html += "</tbody>"
                html += "</table>"
            
            html += "</div>"
        
        html += "</div>"
        return html
    
    def _cash_flow_to_html(self, data: Dict[str, Any]) -> str:
        """Convert cash flow report data to HTML."""
        html = "<div class='cash-flow-report'>"
        
        # Header
        html += f"<h2>{data.get('title', 'Cash Flow Statement')}</h2>"
        html += f"<p class='period'>Period: {data.get('period', '')}</p>"
        
        # Summary
        summary = data.get("summary", {})
        html += "<div class='summary-section'>"
        html += "<h3>Summary</h3>"
        html += "<table class='summary-table'>"
        html += f"<tr><td>Net Operating Cash Flow</td><td>{summary.get('net_operating_cash_flow', '$0.00')}</td></tr>"
        html += f"<tr><td>Net Investing Cash Flow</td><td>{summary.get('net_investing_cash_flow', '$0.00')}</td></tr>"
        html += f"<tr><td>Net Financing Cash Flow</td><td>{summary.get('net_financing_cash_flow', '$0.00')}</td></tr>"
        html += f"<tr class='net-change'><td>Net Change in Cash</td><td>{summary.get('net_change_in_cash', '$0.00')}</td></tr>"
        html += "</table>"
        html += "</div>"
        
        # Operating Cash Flow
        details = data.get("details", {})
        operating = details.get("operating", {})
        
        if operating:
            html += "<div class='operating-section'>"
            html += "<h3>Operating Activities</h3>"
            
            for subcategory, subcategory_data in operating.items():
                html += f"<h4>{subcategory}</h4>"
                html += "<table class='items-table'>"
                html += "<thead><tr><th>Item</th><th>Amount</th><th>Notes</th></tr></thead>"
                html += "<tbody>"
                
                for item in subcategory_data.get("items", []):
                    html += f"<tr><td>{item.get('name', 'Unknown')}</td><td>{item.get('amount', '$0.00')}</td><td>{item.get('notes', '')}</td></tr>"
                
                html += f"<tr class='subtotal'><td>Total {subcategory}</td><td>{subcategory_data.get('total', '$0.00')}</td><td></td></tr>"
                html += "</tbody>"
                html += "</table>"
            
            html += "</div>"
        
        # Investing Cash Flow
        investing = details.get("investing", {})
        
        if investing:
            html += "<div class='investing-section'>"
            html += "<h3>Investing Activities</h3>"
            
            for subcategory, subcategory_data in investing.items():
                html += f"<h4>{subcategory}</h4>"
                html += "<table class='items-table'>"
                html += "<thead><tr><th>Item</th><th>Amount</th><th>Notes</th></tr></thead>"
                html += "<tbody>"
                
                for item in subcategory_data.get("items", []):
                    html += f"<tr><td>{item.get('name', 'Unknown')}</td><td>{item.get('amount', '$0.00')}</td><td>{item.get('notes', '')}</td></tr>"
                
                html += f"<tr class='subtotal'><td>Total {subcategory}</td><td>{subcategory_data.get('total', '$0.00')}</td><td></td></tr>"
                html += "</tbody>"
                html += "</table>"
            
            html += "</div>"
        
        # Financing Cash Flow
        financing = details.get("financing", {})
        
        if financing:
            html += "<div class='financing-section'>"
            html += "<h3>Financing Activities</h3>"
            
            for subcategory, subcategory_data in financing.items():
                html += f"<h4>{subcategory}</h4>"
                html += "<table class='items-table'>"
                html += "<thead><tr><th>Item</th><th>Amount</th><th>Notes</th></tr></thead>"
                html += "<tbody>"
                
                for item in subcategory_data.get("items", []):
                    html += f"<tr><td>{item.get('name', 'Unknown')}</td><td>{item.get('amount', '$0.00')}</td><td>{item.get('notes', '')}</td></tr>"
                
                html += f"<tr class='subtotal'><td>Total {subcategory}</td><td>{subcategory_data.get('total', '$0.00')}</td><td></td></tr>"
                html += "</tbody>"
                html += "</table>"
            
            html += "</div>"
        
        html += "</div>"
        return html
    
    # Helper methods for formatting values
    def _format_currency(self, value: float) -> str:
        """Format a value as currency."""
        if value >= 0:
            return f"${value:,.2f}"
        else:
            return f"-${abs(value):,.2f}"
    
    def _format_percentage(self, value: float) -> str:
        """Format a value as percentage."""
        return f"{value:.2f}%"
    
    def _format_ratio(self, value: float) -> str:
        """Format a value as a ratio."""
        return f"{value:.2f}"
