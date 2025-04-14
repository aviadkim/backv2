"""
Financial Data Analyzer Agent for analyzing and organizing financial information from documents.
"""
import pandas as pd
import numpy as np
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from .base_agent import BaseAgent

class FinancialDataAnalyzerAgent(BaseAgent):
    """Agent for analyzing and organizing financial information from documents."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the financial data analyzer agent.

        Args:
            api_key: OpenRouter API key
            **kwargs: Additional parameters for the base agent
        """
        super().__init__(name="Financial Data Analyzer")
        self.api_key = api_key
        self.description = "I analyze and organize financial information from documents."

        # Keywords for identifying types of financial data
        self.financial_indicators = {
            'values': ['ערך', 'שווי', 'סכום', 'יתרה'],
            'percentages': ['אחוז', '%', 'תשואה', 'תשואת'],
            'rates': ['ריבית', 'תשואה', 'ריבית שנתית']
        }

        # Patterns for identifying monetary values
        self.currency_pattern = r'([\d,.]+)(?:\s*(?:₪|ש"ח|ש״ח|דולר|\$|EUR|יורו|€))'
        self.percentage_pattern = r'([\d,.]+)\s*%'
        self.number_pattern = r'([\d,.]+)'

        # Patterns for identifying dates
        self.date_patterns = [
            r'(\d{1,2}/\d{1,2}/\d{2,4})',
            r'(\d{1,2}\.\d{1,2}\.\d{2,4})',
            r'(\d{1,2}-\d{1,2}-\d{2,4})'
        ]

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task to analyze financial data.

        Args:
            task: Task dictionary with the following keys:
                - table_data: Pandas DataFrame or dictionary with table data
                - table_type: Optional type of the table (portfolio, balance_sheet, income_statement)

        Returns:
            Dictionary with analyzed financial data
        """
        # Get the table data
        if 'table_data' not in task:
            raise ValueError("Task must contain 'table_data'")

        table_data = task['table_data']
        table_type = task.get('table_type', 'unknown')

        # If table_data is a dictionary with a 'data' key, extract the DataFrame
        if isinstance(table_data, dict) and 'data' in table_data:
            df = table_data['data']
            if 'type' in table_data and table_type == 'unknown':
                table_type = table_data['type']
        elif isinstance(table_data, pd.DataFrame):
            df = table_data
        else:
            raise ValueError("table_data must be a DataFrame or a dictionary with a 'data' key")

        # Analyze the table
        result = self.analyze_table(df, table_type)

        return result

    def analyze_table(self, table_data, table_type="unknown"):
        """Analyze a financial table and extract structured information."""
        # Check if we received a DataFrame
        if not isinstance(table_data, pd.DataFrame):
            raise ValueError("Table must be a DataFrame")

        if table_data.empty:
            return {"error": "Empty table"}

        # Clean data
        clean_df = self._clean_table_data(table_data)

        # Process according to table type
        if table_type == "portfolio":
            return self._analyze_portfolio_table(clean_df)
        elif table_type == "balance_sheet":
            return self._analyze_balance_sheet(clean_df)
        elif table_type == "income_statement":
            return self._analyze_income_statement(clean_df)
        else:
            # Try to automatically identify the table type
            detected_type = self._detect_table_type(clean_df)

            if detected_type == "portfolio":
                return self._analyze_portfolio_table(clean_df)
            elif detected_type == "balance_sheet":
                return self._analyze_balance_sheet(clean_df)
            elif detected_type == "income_statement":
                return self._analyze_income_statement(clean_df)
            else:
                # General analysis
                return self._general_table_analysis(clean_df)

    def _clean_table_data(self, df):
        """Clean and process table data."""
        # Copy the table
        clean_df = df.copy()

        # Handle missing values
        clean_df = clean_df.fillna('')

        # Clean cells
        for col in clean_df.columns:
            if clean_df[col].dtype == 'object':
                # Remove extra spaces and newlines
                clean_df[col] = clean_df[col].str.strip().str.replace('\n', ' ')

                # Try to convert numeric columns
                if self._is_numeric_column(clean_df[col]):
                    clean_df[col] = self._convert_to_numeric(clean_df[col])

        return clean_df

    def _is_numeric_column(self, series):
        """Check if a series contains mostly numeric values."""
        # Number of non-empty values
        non_empty = series[series != ''].count()
        if non_empty == 0:
            return False

        # Count values that look like numbers (including commas and dots)
        numeric_pattern = re.compile(r'^[\d.,\-+%₪$€]*$')
        numeric_count = sum(1 for val in series if isinstance(val, str) and
                          numeric_pattern.match(val.strip()))

        # If at least 70% of non-empty values look like numbers
        return numeric_count / non_empty >= 0.7

    def _convert_to_numeric(self, series):
        """Convert a series to numeric values."""
        def convert_value(val):
            if not isinstance(val, str) or val.strip() == '':
                return val

            # Remove currency symbols and other characters
            clean_val = val.replace('₪', '').replace('$', '').replace('€', '')\
                          .replace('%', '').replace(',', '').strip()

            try:
                return float(clean_val)
            except ValueError:
                return val

        return series.apply(convert_value)

    def _detect_table_type(self, df):
        """Automatically detect the table type."""
        # Convert column names and cells to a single text for keyword search
        headers = ' '.join(str(col) for col in df.columns)
        sample_data = ' '.join(str(val) for val in df.iloc[0].values if isinstance(val, str))
        combined_text = (headers + ' ' + sample_data).lower()

        # Search for keywords to identify table type
        portfolio_keywords = ['isin', 'נייר', 'כמות', 'שער', 'שווי', 'תשואה']
        balance_sheet_keywords = ['נכסים', 'התחייבויות', 'הון', 'מאזן']
        income_keywords = ['הכנסות', 'הוצאות', 'רווח', 'הפסד', 'נקי']

        # Count keywords of each type
        portfolio_score = sum(1 for keyword in portfolio_keywords if keyword in combined_text)
        balance_score = sum(1 for keyword in balance_sheet_keywords if keyword in combined_text)
        income_score = sum(1 for keyword in income_keywords if keyword in combined_text)

        # Determine type by highest score
        max_score = max(portfolio_score, balance_score, income_score)

        if max_score == 0:
            return "unknown"
        elif max_score == portfolio_score:
            return "portfolio"
        elif max_score == balance_score:
            return "balance_sheet"
        else:
            return "income_statement"

    def _analyze_portfolio_table(self, df):
        """Analyze an investment portfolio table."""
        result = {
            "table_type": "portfolio",
            "securities": [],
            "summary": {}
        }

        # Identify relevant columns
        col_mapping = self._identify_portfolio_columns(df)

        # Extract data about securities
        securities = []
        for _, row in df.iterrows():
            security = {}

            for field, col_candidates in col_mapping.items():
                for col in col_candidates:
                    if col in df.columns and pd.notna(row[col]) and row[col] != '':
                        security[field] = row[col]
                        break

            # Add only if there's enough meaningful information
            if len(security) >= 3:
                securities.append(security)

        result["securities"] = securities

        # Calculate summaries
        if securities:
            # Total portfolio value
            if "value" in col_mapping:
                values = [sec.get("value", 0) for sec in securities]
                values = [v for v in values if isinstance(v, (int, float))]
                if values:
                    result["summary"]["total_value"] = sum(values)

            # Distribution by type
            if "type" in col_mapping:
                types = {}
                for sec in securities:
                    if "type" in sec and "value" in sec:
                        sec_type = sec["type"]
                        if sec_type not in types:
                            types[sec_type] = 0
                        if isinstance(sec["value"], (int, float)):
                            types[sec_type] += sec["value"]

                if types:
                    result["summary"]["type_distribution"] = types

        return result

    def _identify_portfolio_columns(self, df):
        """Identify columns in a portfolio table."""
        columns = df.columns
        col_texts = [str(col).lower() for col in columns]

        # Keywords for identifying column types
        column_keywords = {
            "security_name": ["שם", "נייר", "ני\"ע", "תיאור"],
            "isin": ["isin", "מספר"],
            "quantity": ["כמות", "יחידות", "יח'"],
            "price": ["שער", "מחיר", "ערך"],
            "value": ["שווי", "ערך נקוב", "סה\"כ", "סך הכל"],
            "return": ["תשואה", "רווח", "שינוי"],
            "type": ["סוג", "ענף", "סקטור", "אפיק"],
            "currency": ["מטבע", "מט\"ח"]
        }

        # Find matches for each column type
        col_mapping = {}

        for field, keywords in column_keywords.items():
            matches = []
            for i, col_text in enumerate(col_texts):
                for keyword in keywords:
                    if keyword in col_text:
                        matches.append(columns[i])
                        break

            if matches:
                col_mapping[field] = matches

        return col_mapping

    def _analyze_balance_sheet(self, df):
        """Analyze a balance sheet table."""
        result = {
            "table_type": "balance_sheet",
            "assets": {},
            "liabilities": {},
            "equity": {},
            "summary": {}
        }

        # Identify asset, liability, and equity rows
        asset_rows = []
        liability_rows = []
        equity_rows = []

        # Keywords for identification
        asset_keywords = ["נכסים", "רכוש", "מזומנים", "השקעות", "חייבים", "מלאי"]
        liability_keywords = ["התחייבויות", "הלוואות", "זכאים", "אשראי"]
        equity_keywords = ["הון", "עצמי", "מניות", "יתרת רווח"]

        # Check first row (usually a header)
        first_row_text = ' '.join(str(val) for val in df.iloc[0].values if isinstance(val, str)).lower()

        # Try to identify if it's a horizontal or vertical balance sheet
        horizontal_balance_sheet = any(keyword in first_row_text for keyword in
                                     asset_keywords + liability_keywords + equity_keywords)

        if horizontal_balance_sheet:
            # Horizontal table - categories appear in rows
            for idx, row in df.iterrows():
                row_text = ' '.join(str(val) for val in row.values if isinstance(val, str)).lower()

                is_asset = any(keyword in row_text for keyword in asset_keywords)
                is_liability = any(keyword in row_text for keyword in liability_keywords)
                is_equity = any(keyword in row_text for keyword in equity_keywords)

                if is_asset:
                    asset_rows.append(idx)
                if is_liability:
                    liability_rows.append(idx)
                if is_equity:
                    equity_rows.append(idx)

            # For each category, try to find rows containing numeric values
            if asset_rows:
                result["assets"] = self._extract_balance_sheet_items(df, asset_rows)

            if liability_rows:
                result["liabilities"] = self._extract_balance_sheet_items(df, liability_rows)

            if equity_rows:
                result["equity"] = self._extract_balance_sheet_items(df, equity_rows)
        else:
            # Vertical table - categories appear in columns
            # Identify relevant columns
            for col in df.columns:
                col_text = str(col).lower()

                is_asset = any(keyword in col_text for keyword in asset_keywords)
                is_liability = any(keyword in col_text for keyword in liability_keywords)
                is_equity = any(keyword in col_text for keyword in equity_keywords)

                if is_asset:
                    result["assets"] = self._extract_column_values(df, col)
                elif is_liability:
                    result["liabilities"] = self._extract_column_values(df, col)
                elif is_equity:
                    result["equity"] = self._extract_column_values(df, col)

        # Calculate summaries
        result["summary"]["total_assets"] = sum(val for val in result["assets"].values()
                                            if isinstance(val, (int, float)))
        result["summary"]["total_liabilities"] = sum(val for val in result["liabilities"].values()
                                                 if isinstance(val, (int, float)))
        result["summary"]["total_equity"] = sum(val for val in result["equity"].values()
                                            if isinstance(val, (int, float)))

        return result

    def _extract_balance_sheet_items(self, df, row_indices):
        """Extract items from a balance sheet."""
        items = {}

        for idx in row_indices:
            row = df.iloc[idx]
            label = str(row.iloc[0])

            # Look for a numeric value in the row
            for val in row.iloc[1:]:
                if isinstance(val, (int, float)) and val != 0:
                    items[label] = val
                    break
                elif isinstance(val, str) and self._try_parse_number(val) is not None:
                    items[label] = self._try_parse_number(val)
                    break

        return items

    def _extract_column_values(self, df, column):
        """Extract values from a column in a vertical balance sheet."""
        items = {}

        for idx, row in df.iterrows():
            if idx == 0:  # Skip header
                continue

            label = str(row.iloc[0])
            value = row[column]

            if isinstance(value, (int, float)):
                items[label] = value
            elif isinstance(value, str) and self._try_parse_number(value) is not None:
                items[label] = self._try_parse_number(value)

        return items

    def _try_parse_number(self, text):
        """Try to convert text to a number."""
        if not isinstance(text, str):
            return None

        # Remove currency symbols and other characters
        clean_val = text.replace('₪', '').replace('$', '').replace('€', '')\
                      .replace('%', '').replace(',', '').strip()

        try:
            return float(clean_val)
        except ValueError:
            return None

    def _analyze_income_statement(self, df):
        """Analyze an income statement."""
        result = {
            "table_type": "income_statement",
            "revenues": {},
            "expenses": {},
            "profits": {},
            "summary": {}
        }

        # Identify revenue, expense, and profit rows
        revenue_rows = []
        expense_rows = []
        profit_rows = []

        # Keywords for identification
        revenue_keywords = ["הכנסות", "מכירות", "שירותים", "תקבולים"]
        expense_keywords = ["הוצאות", "עלות", "תשלומים", "ארנונה", "משכורות"]
        profit_keywords = ["רווח", "הפסד", "נקי", "גולמי", "תפעולי"]

        for idx, row in df.iterrows():
            row_text = ' '.join(str(val) for val in row.values if isinstance(val, str)).lower()

            is_revenue = any(keyword in row_text for keyword in revenue_keywords)
            is_expense = any(keyword in row_text for keyword in expense_keywords)
            is_profit = any(keyword in row_text for keyword in profit_keywords)

            if is_revenue and not is_expense:
                revenue_rows.append(idx)
            if is_expense and not is_revenue:
                expense_rows.append(idx)
            if is_profit:
                profit_rows.append(idx)

        # Extract data
        if revenue_rows:
            result["revenues"] = self._extract_income_statement_items(df, revenue_rows)

        if expense_rows:
            result["expenses"] = self._extract_income_statement_items(df, expense_rows)

        if profit_rows:
            result["profits"] = self._extract_income_statement_items(df, profit_rows)

        # Calculate summaries
        result["summary"]["total_revenue"] = sum(val for val in result["revenues"].values()
                                             if isinstance(val, (int, float)))
        result["summary"]["total_expenses"] = sum(val for val in result["expenses"].values()
                                              if isinstance(val, (int, float)))

        # If there's a net profit value, use it, otherwise calculate
        if result["profits"] and any("נקי" in k.lower() for k in result["profits"].keys()):
            for k, v in result["profits"].items():
                if "נקי" in k.lower() and isinstance(v, (int, float)):
                    result["summary"]["net_profit"] = v
                    break
        else:
            result["summary"]["net_profit"] = result["summary"]["total_revenue"] - \
                                            result["summary"]["total_expenses"]

        return result

    def _extract_income_statement_items(self, df, row_indices):
        """Extract items from an income statement."""
        items = {}

        for idx in row_indices:
            row = df.iloc[idx]
            label = str(row.iloc[0])

            # Look for a numeric value in the row
            for val in row.iloc[1:]:
                if isinstance(val, (int, float)) and val != 0:
                    items[label] = val
                    break
                elif isinstance(val, str) and self._try_parse_number(val) is not None:
                    items[label] = self._try_parse_number(val)
                    break

        return items

    def _general_table_analysis(self, df):
        """General analysis of an unidentified table."""
        result = {
            "table_type": "general",
            "data": {},
            "summary": {
                "dimensions": {
                    "rows": len(df),
                    "columns": len(df.columns)
                }
            }
        }

        # Analyze columns
        numeric_columns = []
        for col in df.columns:
            # Check if the column is numeric
            if df[col].dtype in [np.int64, np.float64] or self._is_numeric_column(df[col]):
                numeric_columns.append(col)

                # Calculate basic statistics
                values = [val for val in df[col] if isinstance(val, (int, float))]
                if values:
                    result["data"][str(col)] = {
                        "mean": np.mean(values),
                        "median": np.median(values),
                        "min": min(values),
                        "max": max(values)
                    }

        # Summarize data
        result["summary"]["numeric_columns"] = len(numeric_columns)

        # If there are many numeric columns, it might be a financial data table
        if len(numeric_columns) > 2:
            result["summary"]["likely_financial"] = True

        return result
