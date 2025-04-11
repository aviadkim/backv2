import os
import re
import json
import logging
import tempfile
from typing import Dict, List, Any, Optional, Tuple, Union
import pandas as pd
import numpy as np
from datetime import datetime
import traceback

# Import the base document processor
from document_processor import DocumentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialDocumentProcessor(DocumentProcessor):
    """Enhanced document processor for financial documents with advanced extraction capabilities."""

    def __init__(self, upload_dir: str = "uploads"):
        """Initialize the financial document processor."""
        super().__init__(upload_dir)
        
        # Enhanced financial keywords
        self.financial_keywords.extend([
            # Income statement terms
            'revenue', 'sales', 'turnover', 'income', 'profit', 'loss', 'ebitda', 'ebit',
            'earnings', 'eps', 'cost of goods sold', 'cogs', 'gross margin', 'operating expense',
            'opex', 'depreciation', 'amortization', 'interest expense', 'tax', 'net income',
            
            # Balance sheet terms
            'asset', 'liability', 'equity', 'current asset', 'non-current asset', 'fixed asset',
            'intangible asset', 'goodwill', 'account receivable', 'inventory', 'cash equivalent',
            'current liability', 'non-current liability', 'long-term debt', 'short-term debt',
            'account payable', 'retained earnings', 'share capital', 'shareholder equity',
            
            # Cash flow terms
            'cash flow', 'operating cash flow', 'investing cash flow', 'financing cash flow',
            'capital expenditure', 'capex', 'dividend', 'repurchase', 'buyback',
            
            # Portfolio and investment terms
            'portfolio', 'investment', 'security', 'stock', 'bond', 'fund', 'etf', 'reit',
            'mutual fund', 'hedge fund', 'private equity', 'venture capital', 'allocation',
            'diversification', 'asset class', 'sector', 'industry', 'region', 'market cap',
            
            # Financial ratios
            'pe ratio', 'price to earnings', 'pb ratio', 'price to book', 'roe', 'return on equity',
            'roa', 'return on assets', 'roi', 'return on investment', 'current ratio', 'quick ratio',
            'debt to equity', 'leverage', 'liquidity', 'solvency', 'profitability', 'efficiency',
            
            # Risk metrics
            'volatility', 'standard deviation', 'beta', 'alpha', 'sharpe ratio', 'sortino ratio',
            'var', 'value at risk', 'drawdown', 'maximum drawdown', 'correlation', 'covariance'
        ])
        
        # Financial patterns
        self.currency_pattern = re.compile(r'(?:USD|EUR|GBP|JPY|CHF|CAD|AUD|NZD|€|\$|£|¥)')
        self.amount_pattern = re.compile(r'(?:[\$€£¥])\s*\d+(?:,\d{3})*(?:\.\d+)?|\d+(?:,\d{3})*(?:\.\d+)?\s*(?:USD|EUR|GBP|JPY|CHF|CAD|AUD|NZD|million|billion|m|bn|k)')
        self.percentage_pattern = re.compile(r'\d+(?:\.\d+)?\s*%')
        self.date_pattern = re.compile(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}')
        
        # Financial statement section patterns
        self.income_statement_pattern = re.compile(r'(?:income statement|statement of (?:income|earnings|operations|profit and loss)|profit and loss|p&l)', re.IGNORECASE)
        self.balance_sheet_pattern = re.compile(r'(?:balance sheet|statement of (?:financial position|financial condition))', re.IGNORECASE)
        self.cash_flow_pattern = re.compile(r'(?:cash flow|statement of cash flows)', re.IGNORECASE)
        self.portfolio_pattern = re.compile(r'(?:portfolio|holdings|investments|securities|positions)', re.IGNORECASE)

    def process_document(self, file_path: str, file_type: str, processing_options: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a financial document and extract relevant information."""
        # Call the base class method to get basic processing results
        result = super().process_document(file_path, file_type, processing_options)
        
        # Add enhanced financial processing
        try:
            # Extract text from the result
            text = result.get("text", "")
            
            # Enhanced financial data extraction
            if text:
                # Extract financial data with context
                financial_data = self._extract_enhanced_financial_data(text)
                result["financial_data"] = financial_data
                
                # Extract financial statements
                financial_statements = self._extract_financial_statements(text)
                if financial_statements:
                    result["financial_statements"] = financial_statements
                
                # Extract portfolio data
                portfolio_data = self._extract_portfolio_data(text, result.get("tables", []))
                if portfolio_data:
                    result["portfolio_data"] = portfolio_data
                
                # Extract financial metrics
                financial_metrics = self._extract_financial_metrics(text)
                if financial_metrics:
                    result["financial_metrics"] = financial_metrics
        except Exception as e:
            logger.error(f"Error in enhanced financial processing: {e}", exc_info=True)
            result["financial_processing_error"] = str(e)
            
        return result

    def _extract_enhanced_financial_data(self, text: str) -> Dict[str, Any]:
        """Extract enhanced financial data from text with context."""
        result = {
            "currencies": [],
            "amounts": [],
            "percentages": [],
            "dates": [],
            "financial_terms": [],
            "profit_loss_items": [],
            "balance_sheet_items": [],
            "cash_flow_items": [],
            "portfolio_items": []
        }
        
        if not text:
            return result
        
        # Extract currencies
        result["currencies"] = list(set(self.currency_pattern.findall(text)))
        
        # Extract amounts with currency context
        result["amounts"] = list(set(self.amount_pattern.findall(text)))
        
        # Extract percentages
        result["percentages"] = list(set(self.percentage_pattern.findall(text)))
        
        # Extract dates
        result["dates"] = list(set(self.date_pattern.findall(text)))
        
        # Extract financial terms with context
        for term in self.financial_keywords:
            if term.lower() in text.lower():
                result["financial_terms"].append(term)
        
        # Extract profit and loss items
        pl_pattern = re.compile(r'(?:revenue|sales|income|profit|loss|expense|cost|margin|ebitda|eps|earnings|dividend)', re.IGNORECASE)
        result["profit_loss_items"] = self._extract_financial_context(text, pl_pattern)
        
        # Extract balance sheet items
        bs_pattern = re.compile(r'(?:asset|liability|equity|debt|cash|receivable|payable|inventory|capital)', re.IGNORECASE)
        result["balance_sheet_items"] = self._extract_financial_context(text, bs_pattern)
        
        # Extract cash flow items
        cf_pattern = re.compile(r'(?:cash flow|operating|investing|financing|capex|dividend|repurchase)', re.IGNORECASE)
        result["cash_flow_items"] = self._extract_financial_context(text, cf_pattern)
        
        # Extract portfolio items
        portfolio_pattern = re.compile(r'(?:portfolio|holding|security|stock|bond|fund|etf|investment|allocation)', re.IGNORECASE)
        result["portfolio_items"] = self._extract_financial_context(text, portfolio_pattern)
        
        return result

    def _extract_financial_context(self, text: str, pattern: re.Pattern) -> List[Dict[str, str]]:
        """Extract financial terms with their surrounding context."""
        items = []
        matches = pattern.finditer(text.lower())
        
        for match in matches:
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].strip()
            
            # Try to extract a value associated with this term
            value = self._extract_value_from_context(context)
            
            items.append({
                "term": match.group(0),
                "context": context,
                "value": value
            })
        
        return items

    def _extract_value_from_context(self, context: str) -> str:
        """Extract a financial value from the context."""
        # Look for currency amounts
        amount_matches = self.amount_pattern.findall(context)
        if amount_matches:
            return amount_matches[0]
        
        # Look for percentages
        percentage_matches = self.percentage_pattern.findall(context)
        if percentage_matches:
            return percentage_matches[0]
        
        return ""

    def _extract_financial_statements(self, text: str) -> Dict[str, Any]:
        """Extract financial statements from the document text."""
        statements = {
            "income_statement": {},
            "balance_sheet": {},
            "cash_flow": {}
        }
        
        # Extract income statement
        income_matches = self.income_statement_pattern.finditer(text)
        for match in income_matches:
            section_start = match.start()
            section_end = self._find_section_end(text, section_start)
            section_text = text[section_start:section_end]
            statements["income_statement"] = self._parse_financial_statement(section_text, "income_statement")
        
        # Extract balance sheet
        balance_matches = self.balance_sheet_pattern.finditer(text)
        for match in balance_matches:
            section_start = match.start()
            section_end = self._find_section_end(text, section_start)
            section_text = text[section_start:section_end]
            statements["balance_sheet"] = self._parse_financial_statement(section_text, "balance_sheet")
        
        # Extract cash flow statement
        cash_flow_matches = self.cash_flow_pattern.finditer(text)
        for match in cash_flow_matches:
            section_start = match.start()
            section_end = self._find_section_end(text, section_start)
            section_text = text[section_start:section_end]
            statements["cash_flow"] = self._parse_financial_statement(section_text, "cash_flow")
        
        return statements

    def _find_section_end(self, text: str, section_start: int) -> int:
        """Find the end of a financial statement section."""
        # Look for the next section header or end of text
        section_patterns = [
            self.income_statement_pattern,
            self.balance_sheet_pattern,
            self.cash_flow_pattern,
            self.portfolio_pattern
        ]
        
        min_next_section = len(text)
        
        for pattern in section_patterns:
            matches = pattern.finditer(text[section_start + 100:])  # Skip a bit to avoid matching the current section
            for match in matches:
                next_section_start = section_start + 100 + match.start()
                if next_section_start < min_next_section:
                    min_next_section = next_section_start
        
        return min_next_section

    def _parse_financial_statement(self, section_text: str, statement_type: str) -> Dict[str, Any]:
        """Parse a financial statement section into structured data."""
        result = {
            "line_items": [],
            "period": self._extract_statement_period(section_text),
            "currency": self._extract_statement_currency(section_text)
        }
        
        # Define patterns based on statement type
        if statement_type == "income_statement":
            line_item_patterns = [
                (r'revenue|sales|turnover', 'Revenue'),
                (r'cost of (?:goods sold|sales|revenue)|cogs', 'Cost of Goods Sold'),
                (r'gross profit|gross margin', 'Gross Profit'),
                (r'operating expenses|opex', 'Operating Expenses'),
                (r'research and development|r&d', 'Research and Development'),
                (r'selling, general and administrative|sg&a', 'SG&A'),
                (r'operating income|operating profit', 'Operating Income'),
                (r'interest (?:expense|income)', 'Interest'),
                (r'income before tax|profit before tax|ebt', 'Income Before Tax'),
                (r'tax|income tax expense', 'Tax Expense'),
                (r'net income|net profit|net earnings', 'Net Income'),
                (r'earnings per share|eps', 'EPS'),
                (r'ebitda', 'EBITDA')
            ]
        elif statement_type == "balance_sheet":
            line_item_patterns = [
                (r'total assets', 'Total Assets'),
                (r'current assets', 'Current Assets'),
                (r'cash and (?:cash equivalents|equivalents)', 'Cash and Equivalents'),
                (r'accounts receivable', 'Accounts Receivable'),
                (r'inventory', 'Inventory'),
                (r'non-current assets|long-term assets', 'Non-Current Assets'),
                (r'property, plant and equipment|ppe', 'Property, Plant and Equipment'),
                (r'goodwill', 'Goodwill'),
                (r'intangible assets', 'Intangible Assets'),
                (r'total liabilities', 'Total Liabilities'),
                (r'current liabilities', 'Current Liabilities'),
                (r'accounts payable', 'Accounts Payable'),
                (r'short-term debt', 'Short-Term Debt'),
                (r'non-current liabilities|long-term liabilities', 'Non-Current Liabilities'),
                (r'long-term debt', 'Long-Term Debt'),
                (r'shareholders[\'']? equity|stockholders[\'']? equity|equity', 'Shareholders\' Equity'),
                (r'retained earnings', 'Retained Earnings'),
                (r'share capital|common stock', 'Share Capital')
            ]
        elif statement_type == "cash_flow":
            line_item_patterns = [
                (r'net cash (?:from|provided by) operating activities|operating cash flow', 'Operating Cash Flow'),
                (r'net cash (?:used in|from) investing activities|investing cash flow', 'Investing Cash Flow'),
                (r'net cash (?:used in|from) financing activities|financing cash flow', 'Financing Cash Flow'),
                (r'capital expenditures|capex', 'Capital Expenditures'),
                (r'dividends paid', 'Dividends Paid'),
                (r'share repurchases|stock buyback', 'Share Repurchases'),
                (r'net (?:increase|decrease) in cash', 'Net Change in Cash'),
                (r'free cash flow', 'Free Cash Flow')
            ]
        else:
            line_item_patterns = []
        
        # Extract line items
        for pattern, label in line_item_patterns:
            matches = re.finditer(pattern, section_text, re.IGNORECASE)
            for match in matches:
                context_start = max(0, match.start() - 20)
                context_end = min(len(section_text), match.end() + 50)
                context = section_text[context_start:context_end]
                
                # Extract value
                value = self._extract_value_from_context(context)
                
                if value:
                    result["line_items"].append({
                        "label": label,
                        "value": value,
                        "context": context
                    })
        
        return result

    def _extract_statement_period(self, section_text: str) -> str:
        """Extract the time period for a financial statement."""
        # Look for year patterns
        year_pattern = re.compile(r'(?:year ended|fiscal year|fy|period ended|quarter ended|q[1-4]).*?\b(20\d{2})\b', re.IGNORECASE)
        year_match = year_pattern.search(section_text)
        
        if year_match:
            return year_match.group(0)
        
        # Look for date patterns
        date_matches = self.date_pattern.findall(section_text[:500])  # Check only the beginning of the section
        if date_matches:
            return date_matches[0]
        
        return ""

    def _extract_statement_currency(self, section_text: str) -> str:
        """Extract the currency used in a financial statement."""
        # Look for currency indicators
        currency_indicators = [
            (r'(?:in|thousands of|millions of|billions of)\s+(?:US dollars|USD)', 'USD'),
            (r'(?:in|thousands of|millions of|billions of)\s+(?:euros|EUR)', 'EUR'),
            (r'(?:in|thousands of|millions of|billions of)\s+(?:pounds sterling|GBP)', 'GBP'),
            (r'(?:in|thousands of|millions of|billions of)\s+(?:Japanese yen|JPY)', 'JPY'),
            (r'\$', 'USD'),
            (r'€', 'EUR'),
            (r'£', 'GBP'),
            (r'¥', 'JPY')
        ]
        
        for pattern, currency in currency_indicators:
            if re.search(pattern, section_text, re.IGNORECASE):
                return currency
        
        return ""

    def _extract_portfolio_data(self, text: str, tables: List[Dict]) -> List[Dict[str, Any]]:
        """Extract portfolio data from text and tables."""
        portfolio_items = []
        
        # First, try to extract from tables
        for table in tables:
            if self._is_portfolio_table(table):
                portfolio_items.extend(self._extract_portfolio_from_table(table))
        
        # If no items found in tables, try to extract from text
        if not portfolio_items:
            portfolio_items = self._extract_portfolio_from_text(text)
        
        return portfolio_items

    def _is_portfolio_table(self, table: Dict) -> bool:
        """Determine if a table contains portfolio data."""
        # Check if the table headers suggest portfolio data
        portfolio_headers = ['security', 'holding', 'position', 'stock', 'bond', 'fund', 'etf', 
                            'isin', 'cusip', 'ticker', 'symbol', 'quantity', 'shares', 'units',
                            'price', 'value', 'weight', 'allocation', 'sector', 'industry']
        
        headers = [h.lower() for h in table.get("headers", [])]
        
        # Check if at least 2 portfolio-related headers are present
        matches = sum(1 for h in headers if any(ph in h for ph in portfolio_headers))
        return matches >= 2

    def _extract_portfolio_from_table(self, table: Dict) -> List[Dict[str, Any]]:
        """Extract portfolio items from a table."""
        items = []
        headers = [h.lower() for h in table.get("headers", [])]
        data = table.get("data", [])
        
        # Map common header variations to standardized fields
        header_mapping = {
            'security': ['security', 'name', 'description', 'holding', 'position'],
            'isin': ['isin'],
            'cusip': ['cusip'],
            'ticker': ['ticker', 'symbol', 'code'],
            'quantity': ['quantity', 'shares', 'units', 'amount', 'position size'],
            'price': ['price', 'market price', 'last price', 'current price'],
            'value': ['value', 'market value', 'position value', 'amount'],
            'weight': ['weight', 'allocation', '%', 'percent', 'weighting'],
            'sector': ['sector', 'industry', 'category'],
            'asset_class': ['asset class', 'type', 'asset type', 'security type'],
            'currency': ['currency', 'ccy']
        }
        
        # Create a mapping from actual headers to standardized fields
        field_mapping = {}
        for std_field, variations in header_mapping.items():
            for i, header in enumerate(headers):
                if any(var in header for var in variations):
                    field_mapping[i] = std_field
                    break
        
        # Extract data using the mapping
        for row in data:
            if isinstance(row, dict):
                # Handle dict-style data
                item = {}
                for i, header in enumerate(headers):
                    if i in field_mapping:
                        std_field = field_mapping[i]
                        item[std_field] = row.get(header, "")
                
                # Extract ISIN if present in the security name but not in a dedicated column
                if 'security' in item and 'isin' not in item:
                    isin_match = self.isin_pattern.search(str(item['security']))
                    if isin_match:
                        item['isin'] = isin_match.group(0)
                
                if item:  # Only add non-empty items
                    items.append(item)
            elif isinstance(row, list):
                # Handle list-style data
                item = {}
                for i, value in enumerate(row):
                    if i in field_mapping:
                        std_field = field_mapping[i]
                        item[std_field] = value
                
                if item:  # Only add non-empty items
                    items.append(item)
        
        return items

    def _extract_portfolio_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract portfolio items from text."""
        items = []
        
        # Look for portfolio section
        portfolio_matches = self.portfolio_pattern.finditer(text)
        for match in portfolio_matches:
            section_start = match.start()
            section_end = self._find_section_end(text, section_start)
            section_text = text[section_start:section_end]
            
            # Look for securities with ISINs
            security_pattern = re.compile(r'([^.!?]*?(?:' + '|'.join([
                r'[A-Z]{2}[A-Z0-9]{9}[0-9]',  # ISIN
                r'[A-Z0-9]{6,}',              # CUSIP or ticker
                r'(?:stock|share|bond|fund|etf)'
            ]) + r')[^.!?]*)', re.IGNORECASE)
            
            security_matches = security_pattern.findall(section_text)
            
            for security_text in security_matches:
                item = {}
                
                # Extract security name
                name_match = re.search(r'([A-Za-z0-9\s\.,]+)(?:\(|\s+[A-Z]{2}[A-Z0-9]{9}[0-9])', security_text)
                if name_match:
                    item['security'] = name_match.group(1).strip()
                
                # Extract ISIN
                isin_match = self.isin_pattern.search(security_text)
                if isin_match:
                    item['isin'] = isin_match.group(0)
                
                # Extract quantity
                quantity_match = re.search(r'(\d+(?:,\d{3})*(?:\.\d+)?)\s+(?:shares|units)', security_text, re.IGNORECASE)
                if quantity_match:
                    item['quantity'] = quantity_match.group(1)
                
                # Extract price
                price_match = re.search(r'(?:at|price)\s+(?:of\s+)?([€$£¥]?\s*\d+(?:,\d{3})*(?:\.\d+)?)', security_text, re.IGNORECASE)
                if price_match:
                    item['price'] = price_match.group(1)
                
                # Extract value
                value_match = re.search(r'(?:value|worth)\s+(?:of\s+)?([€$£¥]?\s*\d+(?:,\d{3})*(?:\.\d+)?)', security_text, re.IGNORECASE)
                if value_match:
                    item['value'] = value_match.group(1)
                
                if item:  # Only add non-empty items
                    items.append(item)
        
        return items

    def _extract_financial_metrics(self, text: str) -> Dict[str, Any]:
        """Extract key financial metrics from text."""
        metrics = {
            "profitability": [],
            "liquidity": [],
            "solvency": [],
            "valuation": [],
            "growth": [],
            "efficiency": []
        }
        
        # Profitability metrics
        profitability_patterns = [
            (r'(?:return on equity|roe)[:\s]+([0-9.]+%)', 'Return on Equity'),
            (r'(?:return on assets|roa)[:\s]+([0-9.]+%)', 'Return on Assets'),
            (r'(?:return on invested capital|roic)[:\s]+([0-9.]+%)', 'Return on Invested Capital'),
            (r'(?:net profit margin|profit margin)[:\s]+([0-9.]+%)', 'Net Profit Margin'),
            (r'(?:gross margin)[:\s]+([0-9.]+%)', 'Gross Margin'),
            (r'(?:operating margin)[:\s]+([0-9.]+%)', 'Operating Margin')
        ]
        
        # Liquidity metrics
        liquidity_patterns = [
            (r'(?:current ratio)[:\s]+([0-9.]+)', 'Current Ratio'),
            (r'(?:quick ratio|acid-test ratio)[:\s]+([0-9.]+)', 'Quick Ratio'),
            (r'(?:cash ratio)[:\s]+([0-9.]+)', 'Cash Ratio'),
            (r'(?:working capital)[:\s]+([€$£¥]?\s*\d+(?:,\d{3})*(?:\.\d+)?)', 'Working Capital')
        ]
        
        # Solvency metrics
        solvency_patterns = [
            (r'(?:debt-to-equity|debt to equity)[:\s]+([0-9.]+)', 'Debt to Equity'),
            (r'(?:debt-to-assets|debt to assets)[:\s]+([0-9.]+)', 'Debt to Assets'),
            (r'(?:interest coverage)[:\s]+([0-9.]+)', 'Interest Coverage'),
            (r'(?:debt service coverage)[:\s]+([0-9.]+)', 'Debt Service Coverage')
        ]
        
        # Valuation metrics
        valuation_patterns = [
            (r'(?:price-to-earnings|price to earnings|p/e|pe ratio)[:\s]+([0-9.]+)', 'P/E Ratio'),
            (r'(?:price-to-book|price to book|p/b|pb ratio)[:\s]+([0-9.]+)', 'P/B Ratio'),
            (r'(?:price-to-sales|price to sales|p/s|ps ratio)[:\s]+([0-9.]+)', 'P/S Ratio'),
            (r'(?:enterprise value to ebitda|ev/ebitda)[:\s]+([0-9.]+)', 'EV/EBITDA'),
            (r'(?:dividend yield)[:\s]+([0-9.]+%)', 'Dividend Yield')
        ]
        
        # Growth metrics
        growth_patterns = [
            (r'(?:revenue growth|sales growth)[:\s]+([0-9.]+%)', 'Revenue Growth'),
            (r'(?:earnings growth)[:\s]+([0-9.]+%)', 'Earnings Growth'),
            (r'(?:dividend growth)[:\s]+([0-9.]+%)', 'Dividend Growth'),
            (r'(?:book value growth)[:\s]+([0-9.]+%)', 'Book Value Growth')
        ]
        
        # Efficiency metrics
        efficiency_patterns = [
            (r'(?:asset turnover)[:\s]+([0-9.]+)', 'Asset Turnover'),
            (r'(?:inventory turnover)[:\s]+([0-9.]+)', 'Inventory Turnover'),
            (r'(?:receivables turnover)[:\s]+([0-9.]+)', 'Receivables Turnover'),
            (r'(?:days sales outstanding|dso)[:\s]+([0-9.]+)', 'Days Sales Outstanding'),
            (r'(?:days inventory outstanding|dio)[:\s]+([0-9.]+)', 'Days Inventory Outstanding')
        ]
        
        # Extract metrics for each category
        metrics["profitability"] = self._extract_metrics(text, profitability_patterns)
        metrics["liquidity"] = self._extract_metrics(text, liquidity_patterns)
        metrics["solvency"] = self._extract_metrics(text, solvency_patterns)
        metrics["valuation"] = self._extract_metrics(text, valuation_patterns)
        metrics["growth"] = self._extract_metrics(text, growth_patterns)
        metrics["efficiency"] = self._extract_metrics(text, efficiency_patterns)
        
        return metrics

    def _extract_metrics(self, text: str, patterns: List[Tuple[str, str]]) -> List[Dict[str, str]]:
        """Extract metrics based on patterns."""
        metrics = []
        
        for pattern, label in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) > 0:
                    value = match.group(1)
                    context_start = max(0, match.start() - 30)
                    context_end = min(len(text), match.end() + 30)
                    context = text[context_start:context_end]
                    
                    metrics.append({
                        "label": label,
                        "value": value,
                        "context": context
                    })
        
        return metrics

    def save_uploaded_file(self, file, filename: str) -> str:
        """Save an uploaded file to the upload directory."""
        return super().save_uploaded_file(file, filename)
