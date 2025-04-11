import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
import pandas as pd
import numpy as np
from datetime import datetime
import json
from .financial_entity_recognizer import FinancialEntityRecognizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialDataExtractor:
    """
    Financial Data Extractor for extracting structured financial data from documents.
    """
    
    def __init__(self):
        """
        Initialize the Financial Data Extractor.
        """
        self.entity_recognizer = FinancialEntityRecognizer()
        
        # Load financial statement templates
        self._load_statement_templates()
    
    def _load_statement_templates(self):
        """Load templates for common financial statements."""
        # Income Statement template
        self.income_statement_template = {
            "line_items": [
                {"name": "Revenue", "aliases": ["sales", "total revenue", "net revenue", "net sales"]},
                {"name": "Cost of Revenue", "aliases": ["cost of sales", "cost of goods sold", "cogs"]},
                {"name": "Gross Profit", "aliases": ["gross margin", "gross income"]},
                {"name": "Operating Expenses", "aliases": ["opex", "total operating expenses"]},
                {"name": "Research and Development", "aliases": ["r&d", "research & development"]},
                {"name": "Selling, General and Administrative", "aliases": ["sg&a", "sga", "selling and administrative"]},
                {"name": "Operating Income", "aliases": ["operating profit", "operating earnings", "income from operations"]},
                {"name": "Interest Expense", "aliases": ["interest costs", "interest charges"]},
                {"name": "Interest Income", "aliases": ["interest revenue"]},
                {"name": "Other Income/Expense", "aliases": ["other income", "other expense", "other income (expense)"]},
                {"name": "Income Before Tax", "aliases": ["earnings before tax", "ebt", "profit before tax", "pre-tax income"]},
                {"name": "Income Tax Expense", "aliases": ["tax expense", "provision for income taxes", "income taxes"]},
                {"name": "Net Income", "aliases": ["net earnings", "net profit", "bottom line"]},
                {"name": "EPS Basic", "aliases": ["basic eps", "basic earnings per share"]},
                {"name": "EPS Diluted", "aliases": ["diluted eps", "diluted earnings per share"]}
            ]
        }
        
        # Balance Sheet template
        self.balance_sheet_template = {
            "line_items": [
                # Assets
                {"name": "Cash and Cash Equivalents", "aliases": ["cash", "cash equivalents"]},
                {"name": "Short-term Investments", "aliases": ["short term investments", "marketable securities"]},
                {"name": "Accounts Receivable", "aliases": ["receivables", "trade receivables"]},
                {"name": "Inventory", "aliases": ["inventories", "stock"]},
                {"name": "Other Current Assets", "aliases": ["prepaid expenses", "other current"]},
                {"name": "Total Current Assets", "aliases": ["current assets"]},
                {"name": "Property, Plant and Equipment", "aliases": ["ppe", "fixed assets", "property and equipment"]},
                {"name": "Goodwill", "aliases": []},
                {"name": "Intangible Assets", "aliases": ["intangibles"]},
                {"name": "Long-term Investments", "aliases": ["long term investments", "investments"]},
                {"name": "Other Non-current Assets", "aliases": ["other assets", "other non-current"]},
                {"name": "Total Non-current Assets", "aliases": ["non-current assets", "non current assets"]},
                {"name": "Total Assets", "aliases": ["assets"]},
                
                # Liabilities
                {"name": "Accounts Payable", "aliases": ["payables", "trade payables"]},
                {"name": "Short-term Debt", "aliases": ["short term debt", "current portion of long term debt"]},
                {"name": "Other Current Liabilities", "aliases": ["accrued liabilities", "accrued expenses"]},
                {"name": "Total Current Liabilities", "aliases": ["current liabilities"]},
                {"name": "Long-term Debt", "aliases": ["long term debt", "long-term borrowings"]},
                {"name": "Other Non-current Liabilities", "aliases": ["other liabilities", "other non-current"]},
                {"name": "Total Non-current Liabilities", "aliases": ["non-current liabilities", "non current liabilities"]},
                {"name": "Total Liabilities", "aliases": ["liabilities"]},
                
                # Equity
                {"name": "Common Stock", "aliases": ["share capital", "capital stock"]},
                {"name": "Retained Earnings", "aliases": ["accumulated earnings", "accumulated deficit"]},
                {"name": "Treasury Stock", "aliases": ["treasury shares"]},
                {"name": "Additional Paid-in Capital", "aliases": ["apic", "paid in capital", "share premium"]},
                {"name": "Total Shareholders' Equity", "aliases": ["shareholders equity", "stockholders equity", "equity"]}
            ]
        }
        
        # Cash Flow Statement template
        self.cash_flow_template = {
            "line_items": [
                # Operating Activities
                {"name": "Net Income", "aliases": ["net earnings", "net profit"]},
                {"name": "Depreciation and Amortization", "aliases": ["depreciation", "amortization", "d&a"]},
                {"name": "Changes in Working Capital", "aliases": ["working capital changes", "change in working capital"]},
                {"name": "Accounts Receivable", "aliases": ["change in accounts receivable", "receivables"]},
                {"name": "Inventory", "aliases": ["change in inventory", "inventories"]},
                {"name": "Accounts Payable", "aliases": ["change in accounts payable", "payables"]},
                {"name": "Other Operating Activities", "aliases": ["other operating"]},
                {"name": "Net Cash from Operating Activities", "aliases": ["cash from operations", "operating cash flow"]},
                
                # Investing Activities
                {"name": "Capital Expenditures", "aliases": ["capex", "purchase of property and equipment"]},
                {"name": "Acquisitions", "aliases": ["business acquisitions", "acquisition of businesses"]},
                {"name": "Purchases of Investments", "aliases": ["investment purchases", "purchase of investments"]},
                {"name": "Sales of Investments", "aliases": ["investment sales", "sale of investments"]},
                {"name": "Other Investing Activities", "aliases": ["other investing"]},
                {"name": "Net Cash from Investing Activities", "aliases": ["cash from investing", "investing cash flow"]},
                
                # Financing Activities
                {"name": "Debt Repayment", "aliases": ["repayment of debt", "debt repayments"]},
                {"name": "Debt Issuance", "aliases": ["issuance of debt", "borrowings"]},
                {"name": "Dividends Paid", "aliases": ["dividend payments", "payment of dividends"]},
                {"name": "Share Repurchases", "aliases": ["stock buybacks", "repurchase of shares"]},
                {"name": "Other Financing Activities", "aliases": ["other financing"]},
                {"name": "Net Cash from Financing Activities", "aliases": ["cash from financing", "financing cash flow"]},
                
                {"name": "Net Change in Cash", "aliases": ["change in cash", "net increase in cash"]},
                {"name": "Cash at Beginning of Period", "aliases": ["beginning cash", "cash at beginning"]},
                {"name": "Cash at End of Period", "aliases": ["ending cash", "cash at end"]}
            ]
        }
    
    def extract_financial_data(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured financial data from a document.
        
        Args:
            document: Document dictionary containing text and tables
            
        Returns:
            Dictionary of extracted financial data
        """
        logger.info(f"Extracting financial data from document: {document.get('file_name', 'unknown')}")
        
        try:
            # Initialize results
            results = {
                "document_info": {
                    "file_name": document.get("file_name", ""),
                    "file_path": document.get("file_path", ""),
                    "title": document.get("structure", {}).get("title", "")
                },
                "financial_statements": [],
                "financial_metrics": [],
                "entities": {
                    "currencies": [],
                    "percentages": [],
                    "dates": [],
                    "numbers": [],
                    "organizations": []
                },
                "time_periods": []
            }
            
            # Extract entities from text
            text_entities = self.entity_recognizer.extract_entities(document.get("text", ""))
            
            # Add entities to results
            for entity_type in ["currencies", "percentages", "dates", "numbers", "organizations"]:
                results["entities"][entity_type].extend(text_entities[entity_type])
            
            # Extract time periods
            time_periods = self.entity_recognizer.extract_time_periods(document.get("text", ""))
            results["time_periods"] = time_periods
            
            # Process tables
            for table in document.get("tables", []):
                # Convert table data to DataFrame
                df = pd.DataFrame(table["data"], columns=table.get("headers", []))
                
                # Identify financial statement type
                statement_type = self._identify_statement_type(df)
                
                if statement_type:
                    # Extract financial statement data
                    statement_data = self._extract_statement_data(df, statement_type)
                    
                    if statement_data:
                        results["financial_statements"].append({
                            "type": statement_type,
                            "page": table.get("page", 0),
                            "data": statement_data
                        })
                
                # Extract financial metrics from table
                table_metrics = self._extract_metrics_from_table(df)
                results["financial_metrics"].extend(table_metrics)
            
            # Extract financial metrics from text
            text_metrics = self._extract_metrics_from_text(document.get("text", ""))
            results["financial_metrics"].extend(text_metrics)
            
            return results
        except Exception as e:
            logger.error(f"Error extracting financial data: {e}")
            raise
    
    def _identify_statement_type(self, df: pd.DataFrame) -> Optional[str]:
        """
        Identify the type of financial statement in a table.
        
        Args:
            df: DataFrame containing table data
            
        Returns:
            Statement type or None if not identified
        """
        # Convert DataFrame to string for analysis
        table_text = ' '.join([' '.join(map(str, df.columns))] + 
                             [' '.join(map(str, row)) for _, row in df.iterrows()])
        
        # Get confidence scores for each statement type
        scores = self.entity_recognizer.identify_financial_statement_type(table_text, df)
        
        # Find the statement type with the highest score
        max_score = max(scores.values())
        max_type = max(scores.items(), key=lambda x: x[1])[0]
        
        # Return the statement type if the score is high enough
        if max_score > 0.5:
            return max_type
        
        return None
    
    def _extract_statement_data(self, df: pd.DataFrame, statement_type: str) -> List[Dict[str, Any]]:
        """
        Extract data from a financial statement table.
        
        Args:
            df: DataFrame containing table data
            statement_type: Type of financial statement
            
        Returns:
            List of extracted line items
        """
        # Get the appropriate template
        if statement_type == "income_statement":
            template = self.income_statement_template
        elif statement_type == "balance_sheet":
            template = self.balance_sheet_template
        elif statement_type == "cash_flow":
            template = self.cash_flow_template
        else:
            return []
        
        # Extract time periods from column headers
        time_periods = []
        for col in df.columns[1:]:  # Skip first column (usually line item names)
            if isinstance(col, str):
                periods = self.entity_recognizer.extract_time_periods(col)
                if periods:
                    time_periods.append({
                        "column": col,
                        "period": periods[0]["text"] if periods else col
                    })
        
        # Extract line items
        line_items = []
        
        for template_item in template["line_items"]:
            item_name = template_item["name"]
            aliases = template_item["aliases"] + [item_name.lower()]
            
            # Look for the line item in the first column
            for idx, row_label in enumerate(df.iloc[:, 0]):
                if isinstance(row_label, str) and any(alias in row_label.lower() for alias in aliases):
                    # Found a matching line item
                    values = []
                    
                    # Extract values for each time period
                    for col_idx, col in enumerate(df.columns[1:], 1):
                        if col_idx < len(df.columns):
                            value = df.iloc[idx, col_idx]
                            
                            # Try to convert to float
                            try:
                                if isinstance(value, str):
                                    # Remove currency symbols, commas, and parentheses
                                    value = value.replace('$', '').replace(',', '')
                                    value = value.replace('(', '-').replace(')', '')
                                    value = float(value)
                                else:
                                    value = float(value)
                            except:
                                value = None
                            
                            period_info = time_periods[col_idx-1] if col_idx-1 < len(time_periods) else {"column": col, "period": str(col)}
                            
                            values.append({
                                "period": period_info["period"],
                                "value": value
                            })
                    
                    line_items.append({
                        "name": item_name,
                        "row_label": row_label,
                        "values": values
                    })
                    
                    break
        
        return line_items
    
    def _extract_metrics_from_table(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Extract financial metrics from a table.
        
        Args:
            df: DataFrame containing table data
            
        Returns:
            List of extracted metrics
        """
        metrics = []
        
        # Common financial metrics to look for
        financial_metrics = {
            "revenue": ["revenue", "sales", "net revenue", "total revenue"],
            "net_income": ["net income", "net earnings", "net profit", "bottom line"],
            "ebitda": ["ebitda", "earnings before interest taxes depreciation and amortization"],
            "eps": ["eps", "earnings per share"],
            "operating_income": ["operating income", "operating profit", "income from operations"],
            "gross_profit": ["gross profit", "gross margin"],
            "total_assets": ["total assets", "assets"],
            "total_liabilities": ["total liabilities", "liabilities"],
            "shareholders_equity": ["shareholders equity", "stockholders equity", "equity"],
            "operating_cash_flow": ["operating cash flow", "cash from operations", "net cash from operating activities"],
            "free_cash_flow": ["free cash flow", "fcf"]
        }
        
        # Look for metrics in row labels (first column)
        for idx, row_label in enumerate(df.iloc[:, 0]):
            if not isinstance(row_label, str):
                continue
                
            row_label_lower = row_label.lower()
            
            # Check if row label matches any metric
            for metric_name, aliases in financial_metrics.items():
                if any(alias in row_label_lower for alias in aliases):
                    # Found a matching metric
                    for col_idx, col in enumerate(df.columns[1:], 1):
                        if col_idx < len(df.columns):
                            value = df.iloc[idx, col_idx]
                            
                            # Try to convert to float
                            try:
                                if isinstance(value, str):
                                    # Remove currency symbols, commas, and parentheses
                                    value = value.replace('$', '').replace(',', '')
                                    value = value.replace('(', '-').replace(')', '')
                                    value = float(value)
                                else:
                                    value = float(value)
                            except:
                                continue
                            
                            # Extract period from column header
                            period = str(col)
                            period_entities = self.entity_recognizer.extract_time_periods(period)
                            if period_entities:
                                period = period_entities[0]["text"]
                            
                            metrics.append({
                                "name": metric_name,
                                "display_name": row_label,
                                "value": value,
                                "period": period,
                                "source": "table"
                            })
        
        return metrics
    
    def _extract_metrics_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract financial metrics from text.
        
        Args:
            text: Document text
            
        Returns:
            List of extracted metrics
        """
        metrics = []
        
        # Common financial metrics to look for
        financial_metrics = {
            "revenue": ["revenue", "sales", "net revenue", "total revenue"],
            "net_income": ["net income", "net earnings", "net profit"],
            "ebitda": ["ebitda", "earnings before interest taxes depreciation and amortization"],
            "eps": ["eps", "earnings per share"],
            "operating_income": ["operating income", "operating profit", "income from operations"],
            "gross_profit": ["gross profit", "gross margin"],
            "total_assets": ["total assets"],
            "total_liabilities": ["total liabilities"],
            "shareholders_equity": ["shareholders equity", "stockholders equity", "equity"],
            "operating_cash_flow": ["operating cash flow", "cash from operations"],
            "free_cash_flow": ["free cash flow", "fcf"]
        }
        
        # Extract entities
        entities = self.entity_recognizer.extract_entities(text)
        
        # Look for patterns like "Revenue of $100 million"
        for metric_name, aliases in financial_metrics.items():
            for alias in aliases:
                # Look for the metric name followed by a value
                pattern = rf'{alias}\s+(?:was|of|at|is|reached|totaled|amounted to)\s+([$€£¥]?\d+(?:[.,]\d+)?(?:\s*(?:million|billion|trillion|m|b|t))?)'
                
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    # Extract the value
                    value_text = match.group(1)
                    
                    # Normalize the value
                    value = self.entity_recognizer._normalize_entity_value(value_text, "NUMBER")
                    
                    # Look for a period near the metric
                    context = text[max(0, match.start() - 100):min(len(text), match.end() + 100)]
                    period_entities = self.entity_recognizer.extract_time_periods(context)
                    
                    period = "unknown"
                    if period_entities:
                        period = period_entities[0]["text"]
                    
                    metrics.append({
                        "name": metric_name,
                        "display_name": match.group(0),
                        "value": value,
                        "period": period,
                        "source": "text"
                    })
        
        return metrics
    
    def extract_financial_ratios(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract financial ratios from a document.
        
        Args:
            document: Document dictionary containing text and tables
            
        Returns:
            List of extracted financial ratios
        """
        ratios = []
        
        # Common financial ratios to look for
        financial_ratios = {
            "pe_ratio": ["p/e ratio", "price to earnings", "price-to-earnings"],
            "pb_ratio": ["p/b ratio", "price to book", "price-to-book"],
            "ps_ratio": ["p/s ratio", "price to sales", "price-to-sales"],
            "ev_ebitda": ["ev/ebitda", "enterprise value to ebitda"],
            "roe": ["roe", "return on equity"],
            "roa": ["roa", "return on assets"],
            "roi": ["roi", "return on investment"],
            "gross_margin": ["gross margin", "gross profit margin"],
            "operating_margin": ["operating margin", "operating profit margin"],
            "net_margin": ["net margin", "net profit margin", "profit margin"],
            "debt_to_equity": ["debt to equity", "debt-to-equity", "d/e ratio"],
            "current_ratio": ["current ratio"],
            "quick_ratio": ["quick ratio", "acid-test ratio"],
            "dividend_yield": ["dividend yield"],
            "payout_ratio": ["payout ratio", "dividend payout ratio"],
            "beta": ["beta", "beta coefficient"]
        }
        
        # Extract ratios from text
        text = document.get("text", "")
        
        for ratio_name, aliases in financial_ratios.items():
            for alias in aliases:
                # Look for the ratio name followed by a value
                pattern = rf'{alias}\s+(?:was|of|at|is|reached|totaled|amounted to)?\s*([\d.]+%?|[\d.]+\s*x)'
                
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    # Extract the value
                    value_text = match.group(1)
                    
                    # Normalize the value
                    if '%' in value_text:
                        value = self.entity_recognizer._normalize_entity_value(value_text, "PERCENTAGE")
                    elif 'x' in value_text.lower():
                        value = float(value_text.lower().replace('x', '').strip())
                    else:
                        value = float(value_text)
                    
                    # Look for a period near the ratio
                    context = text[max(0, match.start() - 100):min(len(text), match.end() + 100)]
                    period_entities = self.entity_recognizer.extract_time_periods(context)
                    
                    period = "unknown"
                    if period_entities:
                        period = period_entities[0]["text"]
                    
                    ratios.append({
                        "name": ratio_name,
                        "display_name": match.group(0),
                        "value": value,
                        "period": period,
                        "source": "text"
                    })
        
        # Extract ratios from tables
        for table in document.get("tables", []):
            # Convert table data to DataFrame
            df = pd.DataFrame(table["data"], columns=table.get("headers", []))
            
            # Look for ratios in row labels (first column)
            for idx, row_label in enumerate(df.iloc[:, 0]):
                if not isinstance(row_label, str):
                    continue
                    
                row_label_lower = row_label.lower()
                
                # Check if row label matches any ratio
                for ratio_name, aliases in financial_ratios.items():
                    if any(alias in row_label_lower for alias in aliases):
                        # Found a matching ratio
                        for col_idx, col in enumerate(df.columns[1:], 1):
                            if col_idx < len(df.columns):
                                value = df.iloc[idx, col_idx]
                                
                                # Try to convert to float
                                try:
                                    if isinstance(value, str):
                                        if '%' in value:
                                            value = float(value.replace('%', '')) / 100
                                        elif 'x' in value.lower():
                                            value = float(value.lower().replace('x', '').strip())
                                        else:
                                            value = float(value)
                                    else:
                                        value = float(value)
                                except:
                                    continue
                                
                                # Extract period from column header
                                period = str(col)
                                period_entities = self.entity_recognizer.extract_time_periods(period)
                                if period_entities:
                                    period = period_entities[0]["text"]
                                
                                ratios.append({
                                    "name": ratio_name,
                                    "display_name": row_label,
                                    "value": value,
                                    "period": period,
                                    "source": "table"
                                })
        
        return ratios
    
    def extract_company_information(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract company information from a document.
        
        Args:
            document: Document dictionary containing text and tables
            
        Returns:
            Dictionary of extracted company information
        """
        company_info = {
            "name": None,
            "ticker": None,
            "industry": None,
            "sector": None,
            "description": None,
            "headquarters": None,
            "website": None,
            "executives": []
        }
        
        text = document.get("text", "")
        
        # Extract company name
        # Look for patterns like "Company Name, Inc." or "About Company Name"
        company_patterns = [
            r'([A-Z][A-Za-z0-9\s,\.]+(?:Inc\.|Corporation|Corp\.|Company|Co\.|Ltd\.|Limited|LLC|LLP))',
            r'About\s+([A-Z][A-Za-z0-9\s,\.]+)',
            r'([A-Z][A-Za-z0-9\s,\.]+)(?:\s+is\s+a|\s+operates\s+in|\s+provides)'
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text)
            if match:
                company_info["name"] = match.group(1).strip()
                break
        
        # Extract ticker symbol
        # Look for patterns like "Ticker: AAPL" or "Symbol: AAPL" or "NASDAQ: AAPL"
        ticker_patterns = [
            r'Ticker:\s*([A-Z]{1,5})',
            r'Symbol:\s*([A-Z]{1,5})',
            r'([A-Z]{1,5})(?:\s+on\s+the\s+(?:NYSE|NASDAQ|AMEX))',
            r'(?:NYSE|NASDAQ|AMEX):\s*([A-Z]{1,5})'
        ]
        
        for pattern in ticker_patterns:
            match = re.search(pattern, text)
            if match:
                company_info["ticker"] = match.group(1).strip()
                break
        
        # Extract industry and sector
        industry_patterns = [
            r'Industry:\s*([A-Za-z0-9\s,\.]+)',
            r'Sector:\s*([A-Za-z0-9\s,\.]+)',
            r'operates\s+in\s+the\s+([A-Za-z0-9\s,\.]+)\s+industry',
            r'operates\s+in\s+the\s+([A-Za-z0-9\s,\.]+)\s+sector'
        ]
        
        for pattern in industry_patterns:
            match = re.search(pattern, text)
            if match:
                value = match.group(1).strip()
                if "industry" in pattern.lower():
                    company_info["industry"] = value
                else:
                    company_info["sector"] = value
        
        # Extract company description
        # Look for a paragraph after "About" or at the beginning of the document
        description_patterns = [
            r'About(?:\s+[A-Za-z0-9\s,\.]+)?\n\n([A-Za-z0-9\s,\.\(\)]+)',
            r'([A-Za-z0-9\s,\.]+\s+is\s+a\s+[A-Za-z0-9\s,\.]+\s+that\s+[A-Za-z0-9\s,\.]+)'
        ]
        
        for pattern in description_patterns:
            match = re.search(pattern, text)
            if match:
                company_info["description"] = match.group(1).strip()
                break
        
        # Extract headquarters location
        hq_patterns = [
            r'Headquarters:\s*([A-Za-z0-9\s,\.]+)',
            r'headquartered\s+in\s+([A-Za-z0-9\s,\.]+)',
            r'based\s+in\s+([A-Za-z0-9\s,\.]+)'
        ]
        
        for pattern in hq_patterns:
            match = re.search(pattern, text)
            if match:
                company_info["headquarters"] = match.group(1).strip()
                break
        
        # Extract website
        website_pattern = r'(?:Website|URL):\s*((?:https?://)?(?:www\.)?[A-Za-z0-9\.-]+\.[A-Za-z]{2,})'
        match = re.search(website_pattern, text)
        if match:
            company_info["website"] = match.group(1).strip()
        
        # Extract executives
        executive_patterns = [
            r'([A-Z][A-Za-z\s\.]+),\s+(Chief\s+[A-Za-z\s]+|CEO|CFO|COO|CTO|President|Chairman)',
            r'(Chief\s+[A-Za-z\s]+|CEO|CFO|COO|CTO|President|Chairman)(?:\s+and\s+[A-Za-z\s]+)?:\s*([A-Z][A-Za-z\s\.]+)'
        ]
        
        for pattern in executive_patterns:
            for match in re.finditer(pattern, text):
                if len(match.groups()) == 2:
                    if "Chief" in match.group(1) or "CEO" in match.group(1):
                        # Pattern 2: Title: Name
                        title = match.group(1).strip()
                        name = match.group(2).strip()
                    else:
                        # Pattern 1: Name, Title
                        name = match.group(1).strip()
                        title = match.group(2).strip()
                    
                    company_info["executives"].append({
                        "name": name,
                        "title": title
                    })
        
        return company_info
