"""
Query Engine Agent for answering natural language questions about financial documents.
"""
import re
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from .base_agent import BaseAgent

class QueryEngineAgent(BaseAgent):
    """Agent for answering natural language questions about financial documents."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the query engine agent.
        
        Args:
            api_key: OpenRouter API key
            **kwargs: Additional parameters for the base agent
        """
        super().__init__(name="Query Engine Agent")
        self.api_key = api_key
        self.description = "I answer natural language questions about financial documents."
        
        # Keywords for identifying query types
        self.query_patterns = {
            "portfolio_value": [
                r'(?:מה|כמה|מהו)[^?]*(?:שווי|ערך)[^?]*(?:תיק|כולל)[^?]*',
                r'(?:what|how much)[^?]*(?:value|worth)[^?]*(?:portfolio|total)[^?]*'
            ],
            "securities_list": [
                r'(?:מה|אילו|איזה|הצג)[^?]*(?:ניירות ערך|מניות|אג"ח|ני"ע)[^?]*(?:כולל|מכיל|יש ב)[^?]*',
                r'(?:what|which|list)[^?]*(?:securities|stocks|bonds)[^?]*(?:in|contains|has)[^?]*'
            ],
            "isin_info": [
                r'(?:מה|מהו|איזה)[^?]*(?:פרטים|מידע)[^?]*(?:isin|איסין)[^?]*([A-Z]{2}[A-Z0-9]{9}\d)',
                r'(?:what|show|give)[^?]*(?:information|details)[^?]*(?:isin|security)[^?]*([A-Z]{2}[A-Z0-9]{9}\d)'
            ],
            "return_info": [
                r'(?:מה|מהי|כמה)[^?]*(?:תשואה|תשואת|ביצועים)[^?]*',
                r'(?:what|how much)[^?]*(?:return|performance|yield)[^?]*'
            ],
            "date_info": [
                r'(?:מה|מהו|מתי)[^?]*(?:תאריך|מועד)[^?]*(?:דו"ח|דוח|מסמך)[^?]*',
                r'(?:what|when)[^?]*(?:date|time)[^?]*(?:document|report|statement)[^?]*'
            ]
        }
        
        # Keywords for identifying entities
        self.entity_patterns = {
            "isin": r'[A-Z]{2}[A-Z0-9]{9}\d',
            "company": r'(?:חברת|חב\'|ח\.?ברה|company|corp|inc|ltd) ([א-ת\w\s\.]{2,30})',
            "date": r'(\d{1,2})[/\.-](\d{1,2})[/\.-](\d{2,4})',
            "amount": r'([\d,.]+)(?:\s*(?:₪|שקל|ש"ח|ש״ח|דולר|\$|USD|ILS|EUR|יורו|€))'
        }
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task to answer a query about a document.
        
        Args:
            task: Task dictionary with the following keys:
                - query: Natural language query
                - document_data: Processed document data
                
        Returns:
            Dictionary with the answer and relevant data
        """
        # Get the required data
        query = task.get('query', '')
        document_data = task.get('document_data', {})
        
        # Process the query
        result = self.process_query(query, document_data)
        
        return result
    
    def process_query(self, query: str, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a natural language query and return an answer from the document.
        
        Args:
            query: Natural language query
            document_data: Processed document data
            
        Returns:
            Dictionary with the answer and relevant data
        """
        # Identify the query type
        query_type, extracted_entities = self._identify_query_type(query)
        
        # Execute the query based on its type
        if query_type == "portfolio_value":
            return self._get_portfolio_value(document_data)
        elif query_type == "securities_list":
            return self._get_securities_list(document_data, extracted_entities)
        elif query_type == "isin_info":
            return self._get_isin_info(document_data, extracted_entities)
        elif query_type == "return_info":
            return self._get_return_info(document_data, extracted_entities)
        elif query_type == "date_info":
            return self._get_date_info(document_data)
        else:
            # Try to answer a general query
            return self._general_query(query, document_data)
    
    def _identify_query_type(self, query: str) -> tuple:
        """Identify the query type and extract entities."""
        query_lower = query.lower()
        
        # Identify the query type
        identified_type = None
        for q_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query_lower)
                if match:
                    identified_type = q_type
                    break
            if identified_type:
                break
        
        # Extract entities from the query
        entities = {}
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, query)
            if matches:
                entities[entity_type] = matches
        
        return identified_type or "general", entities
    
    def _get_portfolio_value(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about the portfolio value."""
        response = {
            "query_type": "portfolio_value",
            "answer": "No information about portfolio value was found in the document.",
            "data": {}
        }
        
        # Search for data in a specific path
        if "financial_data" in document_data:
            financial_data = document_data["financial_data"]
            if "portfolio" in financial_data:
                portfolio = financial_data["portfolio"]
                if "summary" in portfolio and "total_value" in portfolio["summary"]:
                    total_value = portfolio["summary"]["total_value"]
                    response["answer"] = f"The portfolio value is {total_value:,.2f}."
                    response["data"]["total_value"] = total_value
                    
                    # Add information about portfolio distribution, if available
                    if "type_distribution" in portfolio["summary"]:
                        distribution = portfolio["summary"]["type_distribution"]
                        response["data"]["type_distribution"] = distribution
        
        # Search in tables
        if "answer" not in response and "tables" in document_data:
            for table in document_data["tables"]:
                if table["type"] == "portfolio":
                    # Look for a summary or calculate the total
                    total_found = False
                    
                    if "data" in table:
                        values = []
                        for row in table["data"]:
                            for key, value in row.items():
                                if "שווי" in key.lower() or "ערך" in key.lower() or "value" in key.lower() or "total" in key.lower():
                                    if isinstance(value, (int, float)):
                                        values.append(value)
                                    elif isinstance(value, str):
                                        try:
                                            # Try to convert to a number
                                            values.append(float(value.replace(',', '')))
                                        except:
                                            pass
                        
                        if values:
                            total_value = sum(values)
                            response["answer"] = f"The portfolio value is {total_value:,.2f} (calculated from the table)."
                            response["data"]["total_value"] = total_value
                            total_found = True
                
                if total_found:
                    break
        
        return response
    
    def _get_securities_list(self, document_data: Dict[str, Any], entities: Dict[str, List]) -> Dict[str, Any]:
        """Get a list of securities from the document."""
        response = {
            "query_type": "securities_list",
            "answer": "No securities were found in the document.",
            "data": {"securities": []}
        }
        
        securities = []
        
        # Search in financial data
        if "financial_data" in document_data:
            financial_data = document_data["financial_data"]
            if "portfolio" in financial_data and "securities" in financial_data["portfolio"]:
                securities = financial_data["portfolio"]["securities"]
        
        # If none found, search in ISIN entities
        if not securities and "entities" in document_data and "isin" in document_data["entities"]:
            securities = document_data["entities"]["isin"]
        
        # Search in tables
        if not securities and "tables" in document_data:
            for table in document_data["tables"]:
                if table["type"] == "portfolio" and "data" in table:
                    # Look for security names in the table
                    for row in table["data"]:
                        security = {}
                        for key, value in row.items():
                            key_lower = key.lower()
                            if "שם" in key_lower or "name" in key_lower or "תיאור" in key_lower or "description" in key_lower:
                                security["name"] = value
                            elif "isin" in key_lower:
                                security["isin"] = value
                        
                        if security:
                            securities.append(security)
        
        # Filter by entities if any
        filtered_securities = securities
        if entities:
            if "company" in entities:
                company_names = entities["company"]
                filtered_securities = [
                    sec for sec in securities 
                    if any(company.lower() in str(sec.get("name", "")).lower() for company in company_names)
                ]
        
        if filtered_securities:
            # Limit to a reasonable number of results
            displayed_securities = filtered_securities[:10]
            response["answer"] = f"Found {len(filtered_securities)} securities in the document."
            
            if len(filtered_securities) > 10:
                response["answer"] += f" (showing the first 10)"
            
            response["data"]["securities"] = displayed_securities
            response["data"]["total_count"] = len(filtered_securities)
        
        return response
    
    def _get_isin_info(self, document_data: Dict[str, Any], entities: Dict[str, List]) -> Dict[str, Any]:
        """Get information about a specific security by ISIN."""
        response = {
            "query_type": "isin_info",
            "answer": "No information was found about the requested security.",
            "data": {}
        }
        
        isin_to_find = None
        
        # Get the ISIN from the query
        if "isin" in entities and entities["isin"]:
            isin_to_find = entities["isin"][0]
        
        if not isin_to_find:
            return response
        
        # Search in financial data
        if "financial_data" in document_data:
            financial_data = document_data["financial_data"]
            if "portfolio" in financial_data and "securities" in financial_data["portfolio"]:
                for security in financial_data["portfolio"]["securities"]:
                    if security.get("isin") == isin_to_find:
                        response["answer"] = f"Found information about security with ISIN {isin_to_find}."
                        response["data"]["security"] = security
                        return response
        
        # Search in ISIN entities
        if "entities" in document_data and "isin" in document_data["entities"]:
            for isin_entity in document_data["entities"]["isin"]:
                if isin_entity.get("isin") == isin_to_find:
                    response["answer"] = f"Found basic information about security with ISIN {isin_to_find}."
                    response["data"]["security"] = isin_entity
                    return response
        
        # Search in tables
        if "tables" in document_data:
            for table in document_data["tables"]:
                if "data" in table:
                    for row in table["data"]:
                        for key, value in row.items():
                            if value == isin_to_find or (isinstance(value, str) and isin_to_find in value):
                                response["answer"] = f"Found information about security with ISIN {isin_to_find} in a table."
                                response["data"]["security"] = row
                                return response
        
        return response
    
    def _get_return_info(self, document_data: Dict[str, Any], entities: Dict[str, List]) -> Dict[str, Any]:
        """Get information about returns."""
        response = {
            "query_type": "return_info",
            "answer": "No information about returns was found in the document.",
            "data": {"returns": []}
        }
        
        returns_data = []
        
        # Search in financial data
        if "financial_data" in document_data:
            financial_data = document_data["financial_data"]
            if "portfolio" in financial_data and "securities" in financial_data["portfolio"]:
                for security in financial_data["portfolio"]["securities"]:
                    if "return" in security:
                        returns_data.append({
                            "security": security.get("security_name", ""),
                            "isin": security.get("isin", ""),
                            "return": security["return"]
                        })
        
        # Search in tables
        if not returns_data and "tables" in document_data:
            for table in document_data["tables"]:
                if "data" in table:
                    has_return = False
                    return_col = None
                    
                    # Look for a return column
                    if "columns" in table:
                        for col in table["columns"]:
                            col_lower = str(col).lower()
                            if "תשואה" in col_lower or "return" in col_lower or "%" in col:
                                return_col = col
                                has_return = True
                                break
                    
                    if has_return and return_col:
                        for row in table["data"]:
                            if return_col in row:
                                return_value = row[return_col]
                                
                                # Find the security name or ISIN
                                security_name = ""
                                isin = ""
                                
                                for key, value in row.items():
                                    key_lower = str(key).lower()
                                    if "שם" in key_lower or "name" in key_lower or "תיאור" in key_lower:
                                        security_name = value
                                    elif "isin" in key_lower:
                                        isin = value
                                
                                returns_data.append({
                                    "security": security_name,
                                    "isin": isin,
                                    "return": return_value
                                })
        
        # Filter by entities if any
        filtered_returns = returns_data
        if entities:
            if "company" in entities:
                company_names = entities["company"]
                filtered_returns = [
                    ret for ret in returns_data 
                    if any(company.lower() in str(ret.get("security", "")).lower() for company in company_names)
                ]
            elif "isin" in entities:
                isin_codes = entities["isin"]
                filtered_returns = [
                    ret for ret in returns_data 
                    if any(ret.get("isin", "") == isin for isin in isin_codes)
                ]
        
        if filtered_returns:
            response["answer"] = f"Found return information for {len(filtered_returns)} securities."
            response["data"]["returns"] = filtered_returns
        
        return response
    
    def _get_date_info(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about the document date."""
        response = {
            "query_type": "date_info",
            "answer": "No information about the document date was found.",
            "data": {}
        }
        
        # Search for date in metadata
        if "metadata" in document_data and "document_date" in document_data["metadata"]:
            doc_date = document_data["metadata"]["document_date"]
            if doc_date:
                response["answer"] = f"The document date is {doc_date}."
                response["data"]["document_date"] = doc_date
                return response
        
        # Search for date in document text (assuming we have access to the full text)
        date_patterns = [
            r'(?:תאריך|מועד)[:\s]+(\d{1,2})[/\.-](\d{1,2})[/\.-](\d{2,4})',
            r'(?:Date)[:\s]+(\d{1,2})[/\.-](\d{1,2})[/\.-](\d{2,4})'
        ]
        
        if "metadata" in document_data and "document_text" in document_data["metadata"]:
            doc_text = document_data["metadata"]["document_text"]
            for pattern in date_patterns:
                match = re.search(pattern, doc_text)
                if match:
                    date_str = match.group(0).split(':', 1)[1].strip()
                    response["answer"] = f"The document date is {date_str}."
                    response["data"]["document_date"] = date_str
                    return response
        
        return response
    
    def _general_query(self, query: str, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Try to answer a general query."""
        response = {
            "query_type": "general",
            "answer": "There is not enough information in the document to answer the query.",
            "data": {}
        }
        
        # Break down into possible topics
        query_lower = query.lower()
        topics = {
            "portfolio": ["תיק", "השקעות", "ניירות ערך", "מניות", "אג\"ח", "portfolio", "investments", "securities"],
            "balance": ["מאזן", "נכסים", "התחייבויות", "הון", "balance sheet", "assets", "liabilities"],
            "income": ["רווח", "הפסד", "הכנסות", "הוצאות", "income", "profit", "loss", "revenue", "expenses"],
            "bank": ["בנק", "חשבון", "משיכה", "הפקדה", "bank", "account", "deposit", "withdrawal"]
        }
        
        detected_topics = []
        for topic, keywords in topics.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_topics.append(topic)
        
        # If no specific topics were detected, return a general summary
        if not detected_topics:
            return self._get_document_summary(document_data)
        
        # Handle based on the primary topic
        primary_topic = detected_topics[0]
        
        if primary_topic == "portfolio":
            # Return basic information about the portfolio
            return self._get_portfolio_value(document_data)
        elif primary_topic == "balance":
            # Return information about the balance sheet
            return self._get_balance_info(document_data)
        elif primary_topic == "income":
            # Return information about the income statement
            return self._get_income_info(document_data)
        elif primary_topic == "bank":
            # Return information about the bank account
            return self._get_bank_info(document_data)
        
        return response
    
    def _get_document_summary(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return a general summary of the document."""
        response = {
            "query_type": "summary",
            "answer": "Here is a summary of the document:",
            "data": {}
        }
        
        summary_parts = []
        
        # Document type
        if "metadata" in document_data and "document_type" in document_data["metadata"]:
            doc_type = document_data["metadata"]["document_type"]
            summary_parts.append(f"Document type: {doc_type}")
            response["data"]["document_type"] = doc_type
        
        # Document date
        if "metadata" in document_data and "document_date" in document_data["metadata"]:
            doc_date = document_data["metadata"]["document_date"]
            if doc_date:
                summary_parts.append(f"Document date: {doc_date}")
                response["data"]["document_date"] = doc_date
        
        # Number of tables
        if "tables" in document_data:
            table_count = len(document_data["tables"])
            summary_parts.append(f"Number of tables: {table_count}")
            response["data"]["table_count"] = table_count
        
        # Number of securities/ISINs
        if "entities" in document_data and "isin" in document_data["entities"]:
            isin_count = len(document_data["entities"]["isin"])
            summary_parts.append(f"Number of securities identified: {isin_count}")
            response["data"]["isin_count"] = isin_count
        
        # Financial summary
        if "summary" in document_data:
            doc_summary = document_data["summary"]
            
            if "total_portfolio_value" in doc_summary:
                value = doc_summary["total_portfolio_value"]
                summary_parts.append(f"Total portfolio value: {value:,.2f}")
                response["data"]["total_portfolio_value"] = value
        
        # Construct the final answer
        if summary_parts:
            response["answer"] += "\n" + "\n".join(summary_parts)
        else:
            response["answer"] = "Not enough information was found to summarize the document."
        
        return response
    
    def _get_balance_info(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return information about the balance sheet."""
        response = {
            "query_type": "balance_info",
            "answer": "No information about the balance sheet was found in the document.",
            "data": {}
        }
        
        # Search in financial data
        if "financial_data" in document_data:
            financial_data = document_data["financial_data"]
            if "balance_sheet" in financial_data:
                balance_data = financial_data["balance_sheet"]
                
                summary_parts = []
                
                # Assets summary
                if "assets" in balance_data:
                    assets = balance_data["assets"]
                    if assets:
                        response["data"]["assets"] = assets
                        if "summary" in balance_data and "total_assets" in balance_data["summary"]:
                            total_assets = balance_data["summary"]["total_assets"]
                            summary_parts.append(f"Total assets: {total_assets:,.2f}")
                            response["data"]["total_assets"] = total_assets
                
                # Liabilities summary
                if "liabilities" in balance_data:
                    liabilities = balance_data["liabilities"]
                    if liabilities:
                        response["data"]["liabilities"] = liabilities
                        if "summary" in balance_data and "total_liabilities" in balance_data["summary"]:
                            total_liabilities = balance_data["summary"]["total_liabilities"]
                            summary_parts.append(f"Total liabilities: {total_liabilities:,.2f}")
                            response["data"]["total_liabilities"] = total_liabilities
                
                # Equity summary
                if "equity" in balance_data:
                    equity = balance_data["equity"]
                    if equity:
                        response["data"]["equity"] = equity
                        if "summary" in balance_data and "total_equity" in balance_data["summary"]:
                            total_equity = balance_data["summary"]["total_equity"]
                            summary_parts.append(f"Total equity: {total_equity:,.2f}")
                            response["data"]["total_equity"] = total_equity
                
                if summary_parts:
                    response["answer"] = "Balance sheet information:\n" + "\n".join(summary_parts)
        
        return response
    
    def _get_income_info(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return information about the income statement."""
        response = {
            "query_type": "income_info",
            "answer": "No information about the income statement was found in the document.",
            "data": {}
        }
        
        # Search in financial data
        if "financial_data" in document_data:
            financial_data = document_data["financial_data"]
            if "income_statement" in financial_data:
                income_data = financial_data["income_statement"]
                
                summary_parts = []
                
                # Revenues summary
                if "revenues" in income_data:
                    revenues = income_data["revenues"]
                    if revenues:
                        response["data"]["revenues"] = revenues
                        if "summary" in income_data and "total_revenue" in income_data["summary"]:
                            total_revenue = income_data["summary"]["total_revenue"]
                            summary_parts.append(f"Total revenue: {total_revenue:,.2f}")
                            response["data"]["total_revenue"] = total_revenue
                
                # Expenses summary
                if "expenses" in income_data:
                    expenses = income_data["expenses"]
                    if expenses:
                        response["data"]["expenses"] = expenses
                        if "summary" in income_data and "total_expenses" in income_data["summary"]:
                            total_expenses = income_data["summary"]["total_expenses"]
                            summary_parts.append(f"Total expenses: {total_expenses:,.2f}")
                            response["data"]["total_expenses"] = total_expenses
                
                # Net profit
                if "summary" in income_data and "net_profit" in income_data["summary"]:
                    net_profit = income_data["summary"]["net_profit"]
                    summary_parts.append(f"Net profit: {net_profit:,.2f}")
                    response["data"]["net_profit"] = net_profit
                
                if summary_parts:
                    response["answer"] = "Income statement information:\n" + "\n".join(summary_parts)
        
        return response
    
    def _get_bank_info(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return information about the bank account."""
        response = {
            "query_type": "bank_info",
            "answer": "No information about a bank account was found in the document.",
            "data": {}
        }
        
        # Search in tables
        if "tables" in document_data:
            for table in document_data["tables"]:
                # Check if it's a bank statement table
                if "type" in table and table["type"] == "bank_statement":
                    response["answer"] = "Found information about a bank account."
                    
                    # Look for balance
                    if "data" in table:
                        for row in table["data"]:
                            for key, value in row.items():
                                key_lower = str(key).lower()
                                if "יתרה" in key_lower or "balance" in key_lower:
                                    response["data"]["balance"] = value
                                    response["answer"] += f"\nBalance: {value}"
                                    break
                    
                    return response
        
        return response
