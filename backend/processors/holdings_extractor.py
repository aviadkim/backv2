"""
Holdings Extractor for FinDoc Analyzer v1.0

This module extracts holdings information from financial documents.
"""
import os
import logging
import json
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HoldingsExtractor:
    """
    Extractor for holdings information from financial documents.
    """
    
    def __init__(self, output_dir: str = "test_output"):
        """
        Initialize the HoldingsExtractor.
        
        Args:
            output_dir: Directory to save output files
        """
        self.output_dir = output_dir
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info("HoldingsExtractor initialized")
    
    def extract_holdings(self, text: str, document_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract holdings from text.
        
        Args:
            text: Text to extract holdings from
            document_id: Optional identifier for the document
            
        Returns:
            Dictionary with extraction results
        """
        logger.info("Extracting holdings from text")
        
        # Extract security values
        security_values = self._extract_security_values(text)
        
        # Extract top holdings
        top_holdings = self._extract_top_holdings(text, security_values)
        
        # Save the results
        result = {
            "security_values": security_values,
            "top_holdings": top_holdings
        }
        
        if document_id:
            holdings_path = os.path.join(self.output_dir, f"{document_id.replace('.pdf', '')}_holdings.json")
            with open(holdings_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
        
        logger.info(f"Extracted {len(security_values)} securities")
        return result
    
    def extract_comprehensive_holdings(self, text: str, document_id: Optional[str] = None, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Extract comprehensive information for top holdings.
        
        Args:
            text: Text to extract holdings from
            document_id: Optional identifier for the document
            top_n: Number of top holdings to extract
            
        Returns:
            List of top holdings with comprehensive information
        """
        logger.info(f"Extracting comprehensive information for top {top_n} holdings")
        
        # Extract security values
        security_values = self._extract_security_values(text)
        
        # Sort securities by value
        sorted_securities = sorted(security_values.items(), key=lambda x: x[1]["value"], reverse=True)
        
        # Get top N securities
        top_securities = sorted_securities[:top_n]
        
        # Extract comprehensive information for top securities
        top_holdings = []
        for isin, values in top_securities:
            security_details = self._extract_security_details(text, isin)
            if security_details:
                top_holdings.append(security_details)
        
        # Save the results
        if document_id:
            holdings_path = os.path.join(self.output_dir, f"{document_id.replace('.pdf', '')}_top_holdings.json")
            with open(holdings_path, "w", encoding="utf-8") as f:
                json.dump(top_holdings, f, indent=2)
        
        logger.info(f"Extracted comprehensive information for {len(top_holdings)} top holdings")
        return top_holdings
    
    def _extract_security_values(self, text: str) -> Dict[str, Dict[str, Any]]:
        """
        Extract security values from text.
        
        Args:
            text: Text to extract security values from
            
        Returns:
            Dictionary with security values
        """
        security_values = {}
        
        # Extract ISINs and their values
        security_pattern = r'(?:USD|EUR|CHF|GBP)\s+(\d+[\'|\,]?\d*[\'|\,]?\d*)\s+.*?(?:ISIN:\s+([A-Z0-9]{12}).*?(\d+[\'|\,]?\d*[\'|\,]?\d*)\s+(\d+\.\d+)%)'
        security_matches = re.finditer(security_pattern, text, re.DOTALL)
        
        for match in security_matches:
            nominal = match.group(1).replace("'", "").replace(",", "")
            isin = match.group(2)
            value = match.group(3).replace("'", "").replace(",", "")
            percentage = match.group(4)
            
            security_values[isin] = {
                "nominal": float(nominal),
                "value": float(value),
                "percentage": float(percentage)
            }
        
        return security_values
    
    def _extract_top_holdings(self, text: str, security_values: Dict[str, Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Extract top holdings from text.
        
        Args:
            text: Text to extract top holdings from
            security_values: Dictionary with security values
            top_n: Number of top holdings to extract
            
        Returns:
            List of top holdings
        """
        # Sort securities by value
        sorted_securities = sorted(security_values.items(), key=lambda x: x[1]["value"], reverse=True)
        
        # Get top N securities
        top_securities = sorted_securities[:top_n]
        
        # Format top holdings
        top_holdings = []
        for isin, values in top_securities:
            top_holdings.append({
                "isin": isin,
                "nominal": values["nominal"],
                "value": values["value"],
                "percentage": values["percentage"]
            })
        
        return top_holdings
    
    def _extract_security_details(self, text: str, isin: str) -> Optional[Dict[str, Any]]:
        """
        Extract comprehensive details for a specific security by ISIN.
        
        Args:
            text: Text to extract security details from
            isin: ISIN to extract details for
            
        Returns:
            Dictionary with security details if found, None otherwise
        """
        # Find the section containing the ISIN
        isin_pattern = rf'([^I]{{10,500}}ISIN:\s*{isin}[^I]{{10,1000}}?)(?:ISIN:|Total|\n\n)'
        isin_match = re.search(isin_pattern, text, re.DOTALL)
        
        # If not found, try a more relaxed pattern
        if not isin_match:
            isin_pattern = rf'(.*?{isin}.*?)(?:ISIN:|Total|\n\n)'
            isin_match = re.search(isin_pattern, text, re.DOTALL)
        
        if not isin_match:
            return None
        
        security_text = isin_match.group(1)
        
        # Extract description
        description_pattern = r'(?:USD|EUR|CHF|GBP)\s+(\d+[\'|\,]?\d*[\'|\,]?\d*)\s+(.*?)(?:\d+\.\d+\s+\d+\.\d+|\d+\.\d+%)'
        description_match = re.search(description_pattern, security_text)
        
        nominal = None
        description = None
        if description_match:
            nominal_str = description_match.group(1).replace("'", "").replace(",", "")
            nominal = float(nominal_str) if nominal_str else None
            description = description_match.group(2).strip()
        
        # Extract prices and percentages
        prices_pattern = r'(\d+\.\d+)\s+(\d+\.\d+)\s+([-]?\d+\.\d+)%\s+([-]?\d+\.\d+)%\s+(\d+[\'|\,]?\d*[\'|\,]?\d*)\s+(\d+\.\d+)%'
        
        # If not found, try a more relaxed pattern
        if not re.search(prices_pattern, security_text):
            prices_pattern = r'\d+\.\d+\s+\d+\.\d+\s+[-]?\d+\.\d+%\s+[-]?\d+\.\d+%\s+(\d+[\'|\,]?\d*[\'|\,]?\d*)\s+(\d+\.\d+)%'
        
        prices_match = re.search(prices_pattern, security_text)
        
        acquisition_price = None
        current_price = None
        change_1m = None
        change_ytd = None
        valuation = None
        percentage = None
        
        if prices_match:
            # Check if we're using the relaxed pattern
            if len(prices_match.groups()) == 2:
                valuation_str = prices_match.group(1).replace("'", "").replace(",", "")
                valuation = float(valuation_str) if valuation_str else None
                percentage = float(prices_match.group(2))
            else:
                acquisition_price = float(prices_match.group(1))
                current_price = float(prices_match.group(2))
                change_1m = float(prices_match.group(3))
                change_ytd = float(prices_match.group(4))
                valuation_str = prices_match.group(5).replace("'", "").replace(",", "")
                valuation = float(valuation_str) if valuation_str else None
                percentage = float(prices_match.group(6))
        
        # Extract maturity date
        maturity_pattern = r'Maturity:\s+(\d{2}\.\d{2}\.\d{4})'
        maturity_match = re.search(maturity_pattern, security_text)
        maturity_date = maturity_match.group(1) if maturity_match else None
        
        # Extract coupon
        coupon_pattern = r'Coupon:\s+(.*?)(?://|$)'
        coupon_match = re.search(coupon_pattern, security_text)
        coupon = coupon_match.group(1).strip() if coupon_match else None
        
        # Extract security type
        type_pattern = r'(?:Ordinary Bonds|Zero Bonds|Structured Bonds|Structured products equity|Hedge Funds & Private Equity|Ordinary Stocks)'
        type_match = re.search(type_pattern, security_text)
        security_type = type_match.group(0) if type_match else None
        
        # Extract PRC
        prc_pattern = r'PRC:\s+(\d+\.\d+)'
        prc_match = re.search(prc_pattern, security_text)
        prc = float(prc_match.group(1)) if prc_match else None
        
        # Extract YTM
        ytm_pattern = r'YTM:\s+([-]?\d+\.\d+)'
        ytm_match = re.search(ytm_pattern, security_text)
        ytm = float(ytm_match.group(1)) if ytm_match else None
        
        # Extract currency
        currency_pattern = r'^(USD|EUR|CHF|GBP)'
        currency_match = re.search(currency_pattern, security_text.strip())
        currency = currency_match.group(1) if currency_match else "USD"
        
        return {
            "isin": isin,
            "description": description,
            "nominal": nominal,
            "acquisition_price": acquisition_price,
            "current_price": current_price,
            "change_1m": change_1m,
            "change_ytd": change_ytd,
            "valuation": valuation,
            "percentage": percentage,
            "maturity_date": maturity_date,
            "coupon": coupon,
            "security_type": security_type,
            "prc": prc,
            "ytm": ytm,
            "currency": currency
        }
