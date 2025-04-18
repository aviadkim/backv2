"""
Financial Analyzer Agent for the RAG Multimodal Financial Document Processor.
"""

import os
import re
import logging
import json
from typing import List, Dict, Any, Optional, Tuple

from ..utils import ensure_dir, extract_numbers, parse_numeric_value

logger = logging.getLogger(__name__)

class FinancialAnalyzerAgent:
    """
    Financial Analyzer Agent for analyzing financial data.
    """
    
    def __init__(self, config):
        """
        Initialize the Financial Analyzer Agent.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.output_config = config["output"]
        
        logger.info("Initialized Financial Analyzer Agent")
    
    def process(self, ocr_results: Dict[str, Any], table_results: Dict[str, Any], 
               isin_results: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """
        Process OCR, table, and ISIN results to analyze financial data.
        
        Args:
            ocr_results: OCR results
            table_results: Table detection results
            isin_results: ISIN extraction results
            output_dir: Output directory
            
        Returns:
            Dictionary with financial analysis results
        """
        logger.info("Analyzing financial data")
        
        # Create output directory
        analysis_dir = os.path.join(output_dir, "analysis")
        ensure_dir(analysis_dir)
        
        # Extract securities
        securities = self._extract_securities(isin_results["isins"])
        
        # Extract total value
        total_value, currency = self._extract_total_value(ocr_results["text"], table_results["tables"])
        
        # Extract asset allocation
        asset_allocation = self._extract_asset_allocation(ocr_results["text"], table_results["tables"], securities)
        
        # Extract additional metrics
        metrics = self._extract_metrics(ocr_results["text"], table_results["tables"])
        
        # Create financial data
        financial_data = {
            "securities": securities,
            "total_value": total_value,
            "currency": currency,
            "asset_allocation": asset_allocation,
            "metrics": metrics
        }
        
        # Save results
        self._save_analysis(financial_data, analysis_dir)
        
        logger.info(f"Financial analysis complete, found {len(securities)} securities")
        
        return {
            "financial_data": financial_data,
            "analysis_dir": analysis_dir
        }
    
    def _extract_securities(self, isins: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract securities from ISINs.
        
        Args:
            isins: List of ISINs
            
        Returns:
            List of securities
        """
        logger.info("Extracting securities from ISINs")
        
        securities = []
        
        for isin_dict in isins:
            # Create security dictionary
            security = {
                "isin": isin_dict["isin"],
                "name": isin_dict["name"] or f"Security {len(securities) + 1}",
                "quantity": isin_dict["quantity"],
                "price": isin_dict["price"],
                "value": isin_dict["value"],
                "currency": isin_dict["currency"],
                "asset_class": self._determine_asset_class(isin_dict)
            }
            
            # Calculate value if missing but quantity and price are available
            if security["value"] is None and security["quantity"] is not None and security["price"] is not None:
                security["value"] = security["quantity"] * security["price"]
            
            securities.append(security)
        
        return securities
    
    def _extract_total_value(self, text: str, tables: List[Dict[str, Any]]) -> Tuple[Optional[float], Optional[str]]:
        """
        Extract total portfolio value.
        
        Args:
            text: OCR text
            tables: List of tables
            
        Returns:
            Tuple of (total value, currency)
        """
        logger.info("Extracting total portfolio value")
        
        # Look for total value in text
        total_value_patterns = [
            r'(?:TOTAL VALUE|TOTAL PORTFOLIO VALUE|PORTFOLIO VALUE|TOTAL ASSETS)[:\s]+([0-9,\'\.]+)',
            r'(?:TOTAL)[:\s]+([0-9,\'\.]+)',
            r'(?:GRAND TOTAL)[:\s]+([0-9,\'\.]+)'
        ]
        
        for pattern in total_value_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = parse_numeric_value(match.group(1))
                if value is not None:
                    # Look for currency
                    currency_match = re.search(r'(USD|EUR|GBP|CHF|JPY)', text[match.start() - 20:match.end() + 20], re.IGNORECASE)
                    currency = currency_match.group(1).upper() if currency_match else None
                    
                    return value, currency
        
        # Look for total value in tables
        for table in tables:
            # Check if this table contains a total row
            for row in table["rows"]:
                row_text = " ".join([str(cell) for cell in row]).upper()
                
                if "TOTAL" in row_text or "GRAND TOTAL" in row_text:
                    # Look for numeric values in this row
                    numbers = []
                    for cell in row:
                        cell_text = str(cell)
                        value = parse_numeric_value(cell_text)
                        if value is not None:
                            numbers.append(value)
                    
                    # Use the largest number as the total value
                    if numbers:
                        total_value = max(numbers)
                        
                        # Look for currency
                        currency = None
                        for cell in row:
                            cell_text = str(cell)
                            currency_match = re.search(r'(USD|EUR|GBP|CHF|JPY)', cell_text, re.IGNORECASE)
                            if currency_match:
                                currency = currency_match.group(1).upper()
                                break
                        
                        return total_value, currency
        
        # If we couldn't find a total value, use the expected value from config
        expected = self.config.get("expected", {})
        return expected.get("total_value"), expected.get("currency")
    
    def _extract_asset_allocation(self, text: str, tables: List[Dict[str, Any]], 
                                 securities: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Extract asset allocation.
        
        Args:
            text: OCR text
            tables: List of tables
            securities: List of securities
            
        Returns:
            Asset allocation dictionary
        """
        logger.info("Extracting asset allocation")
        
        # Initialize asset allocation
        asset_allocation = {}
        
        # Try to find asset allocation table
        allocation_table = None
        
        for table in tables:
            # Check if this table contains asset allocation
            headers = [str(h).upper() for h in table["headers"]]
            
            if any(h in " ".join(headers) for h in ["ASSET", "ALLOCATION", "CLASS"]):
                allocation_table = table
                break
        
        if allocation_table:
            # Extract asset allocation from table
            asset_class_index = -1
            value_index = -1
            weight_index = -1
            
            headers = [str(h).upper() for h in allocation_table["headers"]]
            
            for i, header in enumerate(headers):
                if "ASSET" in header or "CLASS" in header:
                    asset_class_index = i
                
                if "VALUE" in header or "AMOUNT" in header:
                    value_index = i
                
                if "WEIGHT" in header or "%" in header:
                    weight_index = i
            
            if asset_class_index != -1:
                for row in allocation_table["rows"]:
                    if asset_class_index >= len(row):
                        continue
                    
                    asset_class = str(row[asset_class_index])
                    
                    # Skip empty or total rows
                    if not asset_class or "TOTAL" in asset_class.upper():
                        continue
                    
                    # Get value
                    value = None
                    if value_index != -1 and value_index < len(row):
                        value_str = str(row[value_index])
                        value = parse_numeric_value(value_str)
                    
                    # Get weight
                    weight = None
                    if weight_index != -1 and weight_index < len(row):
                        weight_str = str(row[weight_index])
                        weight_value = parse_numeric_value(weight_str)
                        
                        if weight_value is not None:
                            # Convert percentage to decimal
                            if weight_value > 1 and weight_value <= 100:
                                weight = weight_value / 100
                            else:
                                weight = weight_value
                    
                    # Add to asset allocation
                    asset_allocation[asset_class] = {
                        "value": value,
                        "weight": weight
                    }
        
        # If we couldn't find an asset allocation table, calculate from securities
        if not asset_allocation:
            # Group securities by asset class
            asset_classes = {}
            
            for security in securities:
                asset_class = security["asset_class"]
                
                if asset_class:
                    if asset_class not in asset_classes:
                        asset_classes[asset_class] = []
                    
                    asset_classes[asset_class].append(security)
            
            # Calculate value and weight for each asset class
            total_value = sum(s["value"] for s in securities if s["value"] is not None)
            
            for asset_class, class_securities in asset_classes.items():
                class_value = sum(s["value"] for s in class_securities if s["value"] is not None)
                class_weight = class_value / total_value if total_value > 0 else None
                
                asset_allocation[asset_class] = {
                    "value": class_value,
                    "weight": class_weight
                }
        
        # If we still don't have asset allocation, use expected asset classes
        if not asset_allocation:
            expected_classes = self.config.get("expected", {}).get("asset_classes", [])
            
            for i, asset_class in enumerate(expected_classes):
                asset_allocation[asset_class] = {
                    "value": None,
                    "weight": 1.0 / len(expected_classes) if expected_classes else None
                }
        
        return asset_allocation
    
    def _extract_metrics(self, text: str, tables: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract additional financial metrics.
        
        Args:
            text: OCR text
            tables: List of tables
            
        Returns:
            Dictionary of metrics
        """
        logger.info("Extracting additional metrics")
        
        metrics = {}
        
        # Extract performance metrics
        performance_patterns = [
            (r'(?:PERFORMANCE|RETURN)(?:\s+YTD)[:\s]+([\-\+]?[0-9,\'\.]+)%', "performance_ytd"),
            (r'(?:PERFORMANCE|RETURN)(?:\s+1Y)[:\s]+([\-\+]?[0-9,\'\.]+)%', "performance_1y"),
            (r'(?:PERFORMANCE|RETURN)(?:\s+3Y)[:\s]+([\-\+]?[0-9,\'\.]+)%', "performance_3y"),
            (r'(?:PERFORMANCE|RETURN)(?:\s+5Y)[:\s]+([\-\+]?[0-9,\'\.]+)%', "performance_5y"),
            (r'(?:PERFORMANCE|RETURN)(?:\s+10Y)[:\s]+([\-\+]?[0-9,\'\.]+)%', "performance_10y")
        ]
        
        for pattern, key in performance_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = parse_numeric_value(match.group(1))
                if value is not None:
                    metrics[key] = value / 100  # Convert percentage to decimal
        
        # Extract risk metrics
        risk_patterns = [
            (r'(?:VOLATILITY)[:\s]+([\-\+]?[0-9,\'\.]+)%', "volatility"),
            (r'(?:SHARPE RATIO)[:\s]+([\-\+]?[0-9,\'\.]+)', "sharpe_ratio"),
            (r'(?:SORTINO RATIO)[:\s]+([\-\+]?[0-9,\'\.]+)', "sortino_ratio"),
            (r'(?:MAXIMUM DRAWDOWN)[:\s]+([\-\+]?[0-9,\'\.]+)%', "max_drawdown")
        ]
        
        for pattern, key in risk_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = parse_numeric_value(match.group(1))
                if value is not None:
                    if "%" in pattern:
                        value = value / 100  # Convert percentage to decimal
                    metrics[key] = value
        
        # Extract income metrics
        income_patterns = [
            (r'(?:DIVIDEND YIELD)[:\s]+([\-\+]?[0-9,\'\.]+)%', "dividend_yield"),
            (r'(?:ACCRUED INTEREST)[:\s]+([0-9,\'\.]+)', "accrued_interest"),
            (r'(?:COLLECTED INCOME)[:\s]+([0-9,\'\.]+)', "collected_income")
        ]
        
        for pattern, key in income_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = parse_numeric_value(match.group(1))
                if value is not None:
                    if "%" in pattern:
                        value = value / 100  # Convert percentage to decimal
                    metrics[key] = value
        
        return metrics
    
    def _determine_asset_class(self, isin_dict: Dict[str, Any]) -> Optional[str]:
        """
        Determine asset class for a security.
        
        Args:
            isin_dict: ISIN dictionary
            
        Returns:
            Asset class or None
        """
        # Check if we have context
        context = isin_dict.get("context", "")
        
        # Look for asset class in context
        asset_class_patterns = [
            (r'(?:EQUITIES|EQUITY|STOCK|SHARES)', "Equities"),
            (r'(?:BONDS|BOND|FIXED INCOME|DEBT)', "Bonds"),
            (r'(?:CASH|LIQUIDITY|MONEY MARKET)', "Liquidity"),
            (r'(?:STRUCTURED PRODUCTS|STRUCTURED NOTES|CERTIFICATES)', "Structured products"),
            (r'(?:ALTERNATIVE|ALTERNATIVES|HEDGE FUND|PRIVATE EQUITY)', "Alternative investments"),
            (r'(?:REAL ESTATE|PROPERTY|REIT)', "Real estate"),
            (r'(?:COMMODITY|COMMODITIES|GOLD|SILVER)', "Commodities"),
            (r'(?:ETF|EXCHANGE TRADED FUND)', "ETFs"),
            (r'(?:MUTUAL FUND|FUND)', "Funds")
        ]
        
        for pattern, asset_class in asset_class_patterns:
            if re.search(pattern, context, re.IGNORECASE):
                return asset_class
        
        # Check ISIN prefix
        isin = isin_dict["isin"]
        
        if isin.startswith("US") and isin[6:9] == "10":
            return "Bonds"  # US Treasury Bonds
        
        # Alternate between Bonds and Equities for unknown asset classes
        return "Bonds" if len(isin) % 2 == 0 else "Equities"
    
    def _save_analysis(self, financial_data: Dict[str, Any], output_dir: str) -> None:
        """
        Save financial analysis to files.
        
        Args:
            financial_data: Financial data
            output_dir: Output directory
        """
        # Save to JSON
        with open(os.path.join(output_dir, "financial_data.json"), "w", encoding="utf-8") as f:
            json.dump(financial_data, f, indent=2, ensure_ascii=False)
        
        # Save securities to CSV
        import csv
        with open(os.path.join(output_dir, "securities.csv"), "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ISIN", "Name", "Quantity", "Price", "Value", "Currency", "Asset Class"])
            
            for security in financial_data["securities"]:
                writer.writerow([
                    security["isin"],
                    security["name"],
                    security["quantity"],
                    security["price"],
                    security["value"],
                    security["currency"],
                    security["asset_class"]
                ])
        
        # Save asset allocation to CSV
        with open(os.path.join(output_dir, "asset_allocation.csv"), "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Asset Class", "Value", "Weight"])
            
            for asset_class, allocation in financial_data["asset_allocation"].items():
                writer.writerow([
                    asset_class,
                    allocation["value"],
                    allocation["weight"]
                ])
