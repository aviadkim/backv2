"""
Financial Data Analyzer Agent for FinDoc Analyzer v1.0

This agent analyzes financial data extracted from documents.
"""
import re
import logging
import json
from typing import Dict, Any, List, Optional
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialDataAnalyzerAgent:
    """
    Agent for analyzing financial data extracted from documents.
    """
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the FinancialDataAnalyzerAgent.
        
        Args:
            api_key: OpenRouter API key for AI-enhanced analysis
            **kwargs: Additional arguments
        """
        self.api_key = api_key
        logger.info("FinancialDataAnalyzerAgent initialized")
    
    def process(self, text: str, tables: Optional[List[Dict[str, Any]]] = None, **kwargs) -> Dict[str, Any]:
        """
        Analyze financial data from text and tables.
        
        Args:
            text: Text to analyze
            tables: Tables extracted from the document
            **kwargs: Additional arguments
            
        Returns:
            Dictionary with analysis results
        """
        logger.info("Analyzing financial data")
        
        # Extract basic information
        client_info = self._extract_client_info(text)
        document_date = self._extract_document_date(text)
        portfolio_value = self._extract_portfolio_value(text)
        
        # Extract asset allocation
        asset_allocation = self._extract_asset_allocation(text, tables)
        
        # Extract securities
        securities = self._extract_securities(text, tables)
        
        # Use AI to enhance analysis if API key is provided
        if self.api_key:
            enhanced_analysis = self._enhance_analysis_with_ai(text, tables, {
                "client_info": client_info,
                "document_date": document_date,
                "portfolio_value": portfolio_value,
                "asset_allocation": asset_allocation,
                "securities": securities
            })
            
            # Update with enhanced analysis
            client_info = enhanced_analysis.get("client_info", client_info)
            document_date = enhanced_analysis.get("document_date", document_date)
            portfolio_value = enhanced_analysis.get("portfolio_value", portfolio_value)
            asset_allocation = enhanced_analysis.get("asset_allocation", asset_allocation)
            securities = enhanced_analysis.get("securities", securities)
        
        return {
            "status": "success",
            "client_info": client_info,
            "document_date": document_date,
            "portfolio_value": portfolio_value,
            "asset_allocation": asset_allocation,
            "securities": securities
        }
    
    def _extract_client_info(self, text: str) -> Dict[str, Any]:
        """
        Extract client information from text.
        
        Args:
            text: Text to extract client information from
            
        Returns:
            Dictionary with client information
        """
        # Extract client name
        client_name_pattern = r'(?:Client|Customer|Account Holder|Name)(?:\s*:|\s+)([A-Z\s\.]+(?:LTD\.?|INC\.?|LLC\.?|CORP\.?|SA\.?|AG\.?|GMBH\.?|PLC\.?)?)'
        client_name_match = re.search(client_name_pattern, text, re.IGNORECASE)
        client_name = client_name_match.group(1).strip() if client_name_match else ""
        
        # Extract client number
        client_number_pattern = r'(?:Client|Customer|Account)(?:\s+Number|\s+ID|\s+#|\s*:)(?:\s*//|\s*:|\s+)(\d+)'
        client_number_match = re.search(client_number_pattern, text, re.IGNORECASE)
        client_number = client_number_match.group(1).strip() if client_number_match else ""
        
        return {
            "name": client_name,
            "number": client_number
        }
    
    def _extract_document_date(self, text: str) -> str:
        """
        Extract document date from text.
        
        Args:
            text: Text to extract document date from
            
        Returns:
            Document date as string
        """
        # Look for common date formats
        date_patterns = [
            r'(?:as of|dated|date:?|valuation date)\s+(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
            r'(?:as of|dated|date:?|valuation date)\s+(\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{2,4})',
            r'(\d{1,2}\.\d{1,2}\.\d{2,4})'
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, text, re.IGNORECASE)
            if date_match:
                return date_match.group(1).strip()
        
        return ""
    
    def _extract_portfolio_value(self, text: str) -> float:
        """
        Extract portfolio value from text.
        
        Args:
            text: Text to extract portfolio value from
            
        Returns:
            Portfolio value as float
        """
        # Look for portfolio value patterns
        value_patterns = [
            r'(?:Portfolio|Total|Assets)(?:\s+Value|\s+Amount|\s+Sum)(?:\s*:|\s+)(?:USD|EUR|CHF|GBP)?\s*([\d,\'\.]+)',
            r'(?:Portfolio|Total|Assets)(?:\s+Value|\s+Amount|\s+Sum)(?:\s*:|\s+)([\d,\'\.]+)\s*(?:USD|EUR|CHF|GBP)',
            r'Total\s+(?:USD|EUR|CHF|GBP)\s*([\d,\'\.]+)'
        ]
        
        for pattern in value_patterns:
            value_match = re.search(pattern, text, re.IGNORECASE)
            if value_match:
                value_str = value_match.group(1).replace(",", "").replace("'", "")
                try:
                    return float(value_str)
                except ValueError:
                    pass
        
        return 0.0
    
    def _extract_asset_allocation(self, text: str, tables: Optional[List[Dict[str, Any]]]) -> Dict[str, float]:
        """
        Extract asset allocation from text and tables.
        
        Args:
            text: Text to extract asset allocation from
            tables: Tables extracted from the document
            
        Returns:
            Dictionary with asset allocation percentages
        """
        asset_allocation = {}
        
        # Look for asset allocation in text
        allocation_pattern = r'(?:Total|Asset Class)\s+([A-Za-z\s/]+)\s+(?:USD|EUR|CHF|GBP)?\s*[\d,\'\.]+\s+(\d+\.\d+)%'
        allocation_matches = re.finditer(allocation_pattern, text, re.IGNORECASE)
        
        for match in allocation_matches:
            asset_class = match.group(1).strip()
            percentage = float(match.group(2))
            asset_allocation[asset_class] = percentage
        
        # Look for asset allocation in tables
        if tables:
            for table in tables:
                # Check if this looks like an asset allocation table
                headers = table.get("headers", [])
                if any(header.lower() in ["asset class", "allocation", "weight", "%"] for header in headers):
                    for row in table.get("data", []):
                        # Try to find asset class and percentage columns
                        asset_class = None
                        percentage = None
                        
                        for key, value in row.items():
                            if key.lower() in ["asset class", "asset", "class", "type"]:
                                asset_class = value
                            elif key.lower() in ["allocation", "weight", "%", "percentage"]:
                                try:
                                    percentage = float(value.replace("%", ""))
                                except (ValueError, AttributeError):
                                    pass
                        
                        if asset_class and percentage is not None:
                            asset_allocation[asset_class] = percentage
        
        return asset_allocation
    
    def _extract_securities(self, text: str, tables: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Extract securities from text and tables.
        
        Args:
            text: Text to extract securities from
            tables: Tables extracted from the document
            
        Returns:
            List of securities
        """
        securities = []
        
        # Extract ISINs
        isin_pattern = r'(?:ISIN:|ISIN\s+|ISIN=|ISIN\s*:\s*|^|\s)([A-Z]{2}[A-Z0-9]{10})(?:\s|$|,|\.|;|//)'
        isin_matches = re.finditer(isin_pattern, text, re.MULTILINE)
        
        for match in isin_matches:
            isin = match.group(1)
            
            # Get context around the ISIN
            context_start = max(0, match.start() - 200)
            context_end = min(len(text), match.end() + 200)
            context = text[context_start:context_end]
            
            # Extract security details
            security = {
                "isin": isin,
                "description": self._extract_security_description(isin, context),
                "valuation": self._extract_security_valuation(isin, context),
                "currency": self._extract_security_currency(isin, context),
                "quantity": self._extract_security_quantity(isin, context),
                "price": self._extract_security_price(isin, context)
            }
            
            securities.append(security)
        
        return securities
    
    def _extract_security_description(self, isin: str, context: str) -> Optional[str]:
        """
        Extract security description for an ISIN.
        
        Args:
            isin: ISIN to extract description for
            context: Text context around the ISIN
            
        Returns:
            Security description if found, None otherwise
        """
        # Look for patterns like "SECURITY NAME (ISIN: XX0000000000)"
        pattern1 = r'([^()\n]{5,100})\s*\([^\)]*' + re.escape(isin) + r'[^\)]*\)'
        match1 = re.search(pattern1, context)
        if match1:
            return match1.group(1).strip()
        
        # Look for patterns like "ISIN: XX0000000000 SECURITY NAME"
        pattern2 = r'ISIN\s*:\s*' + re.escape(isin) + r'\s*//\s*Valorn\.[^//]*//\s*([^//\n]{5,100})'
        match2 = re.search(pattern2, context)
        if match2:
            return match2.group(1).strip()
        
        # Look for patterns like "USD X'XXX'XXX SECURITY NAME"
        pattern3 = r'(?:USD|EUR|CHF|GBP)\s+[\d,\'\.]+\s+([A-Z0-9\s\.\-\(\)]+)(?:\d|\s|$)'
        match3 = re.search(pattern3, context)
        if match3:
            return match3.group(1).strip()
        
        return None
    
    def _extract_security_valuation(self, isin: str, context: str) -> Optional[float]:
        """
        Extract security valuation for an ISIN.
        
        Args:
            isin: ISIN to extract valuation for
            context: Text context around the ISIN
            
        Returns:
            Security valuation if found, None otherwise
        """
        # Look for patterns like "VALUATION: 1,234,567.89" near the ISIN
        value_pattern = r'(\d+[\'|\,]?\d*[\'|\,]?\d*)\s+(\d+\.\d+)%'
        value_match = re.search(value_pattern, context)
        
        if value_match:
            value_str = value_match.group(1).replace("'", "").replace(",", "")
            try:
                return float(value_str)
            except ValueError:
                pass
        
        return None
    
    def _extract_security_currency(self, isin: str, context: str) -> Optional[str]:
        """
        Extract security currency for an ISIN.
        
        Args:
            isin: ISIN to extract currency for
            context: Text context around the ISIN
            
        Returns:
            Security currency if found, None otherwise
        """
        # Look for currency codes
        currency_pattern = r'(USD|EUR|CHF|GBP)\s+[\d,\'\.]+\s+'
        currency_match = re.search(currency_pattern, context)
        
        if currency_match:
            return currency_match.group(1)
        
        return "USD"  # Default to USD
    
    def _extract_security_quantity(self, isin: str, context: str) -> Optional[float]:
        """
        Extract security quantity for an ISIN.
        
        Args:
            isin: ISIN to extract quantity for
            context: Text context around the ISIN
            
        Returns:
            Security quantity if found, None otherwise
        """
        # Look for patterns like "QUANTITY: 1,234"
        quantity_pattern = r'(?:USD|EUR|CHF|GBP)\s+([\d,\'\.]+)\s+'
        quantity_match = re.search(quantity_pattern, context)
        
        if quantity_match:
            quantity_str = quantity_match.group(1).replace("'", "").replace(",", "")
            try:
                return float(quantity_str)
            except ValueError:
                pass
        
        return None
    
    def _extract_security_price(self, isin: str, context: str) -> Optional[float]:
        """
        Extract security price for an ISIN.
        
        Args:
            isin: ISIN to extract price for
            context: Text context around the ISIN
            
        Returns:
            Security price if found, None otherwise
        """
        # Look for patterns like "PRICE: 123.45"
        price_pattern = r'(\d+\.\d+)\s+(\d+\.\d+)\s+'
        price_match = re.search(price_pattern, context)
        
        if price_match:
            try:
                return float(price_match.group(2))
            except ValueError:
                pass
        
        return None
    
    def _enhance_analysis_with_ai(self, text: str, tables: Optional[List[Dict[str, Any]]], 
                                 initial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance analysis with AI.
        
        Args:
            text: Text to analyze
            tables: Tables extracted from the document
            initial_analysis: Initial analysis results
            
        Returns:
            Enhanced analysis results
        """
        if not self.api_key:
            return initial_analysis
        
        logger.info("Enhancing analysis with AI")
        
        try:
            # Prepare the prompt
            prompt = f"""
            You are a financial document analysis expert. I need you to analyze the following financial document data and provide a comprehensive understanding of the document.
            
            EXTRACTED TEXT SAMPLE (first 1000 characters):
            {text[:1000]}...
            
            INITIAL ANALYSIS:
            {json.dumps(initial_analysis, indent=2)}
            
            Please provide an enhanced analysis of this financial document, including:
            
            1. Client Information: Who is the client? What is their client number?
            2. Document Date: When was this document created?
            3. Portfolio Value: What is the total portfolio value?
            4. Asset Allocation: What is the asset allocation of the portfolio?
            5. Securities: What securities are in the portfolio?
            
            Format your response as a JSON object with the following structure:
            {{
                "client_info": {{
                    "name": "Client name",
                    "number": "Client number"
                }},
                "document_date": "Document date",
                "portfolio_value": "Total portfolio value",
                "asset_allocation": {{
                    "asset_class": "Percentage"
                }},
                "securities": [
                    {{
                        "isin": "ISIN code",
                        "description": "Security description",
                        "valuation": "Security value",
                        "currency": "Security currency",
                        "quantity": "Security quantity",
                        "price": "Security price"
                    }}
                ]
            }}
            """
            
            # Call OpenRouter API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/aviadkim/backv2",
                "X-Title": "Financial Document Analysis",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "anthropic/claude-3-haiku",
                "messages": [
                    {"role": "system", "content": "You are a financial document analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 2000
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                response_json = response.json()
                analysis_text = response_json["choices"][0]["message"]["content"]
                
                # Extract JSON from response
                try:
                    # Find JSON part in the response
                    json_start = analysis_text.find("{")
                    json_end = analysis_text.rfind("}")
                    
                    if json_start >= 0 and json_end >= 0:
                        json_str = analysis_text[json_start:json_end+1]
                        enhanced_analysis = json.loads(json_str)
                        
                        # Merge with initial analysis
                        merged_analysis = initial_analysis.copy()
                        
                        # Update with enhanced analysis if values are present
                        if enhanced_analysis.get("client_info"):
                            merged_analysis["client_info"] = enhanced_analysis["client_info"]
                        
                        if enhanced_analysis.get("document_date"):
                            merged_analysis["document_date"] = enhanced_analysis["document_date"]
                        
                        if enhanced_analysis.get("portfolio_value"):
                            try:
                                merged_analysis["portfolio_value"] = float(enhanced_analysis["portfolio_value"])
                            except (ValueError, TypeError):
                                pass
                        
                        if enhanced_analysis.get("asset_allocation"):
                            merged_analysis["asset_allocation"] = enhanced_analysis["asset_allocation"]
                        
                        if enhanced_analysis.get("securities"):
                            # Merge securities by ISIN
                            isin_to_security = {s["isin"]: s for s in merged_analysis["securities"] if "isin" in s}
                            
                            for security in enhanced_analysis["securities"]:
                                if "isin" in security:
                                    if security["isin"] in isin_to_security:
                                        # Update existing security
                                        for key, value in security.items():
                                            if value and key != "isin":
                                                isin_to_security[security["isin"]][key] = value
                                    else:
                                        # Add new security
                                        isin_to_security[security["isin"]] = security
                            
                            merged_analysis["securities"] = list(isin_to_security.values())
                        
                        return merged_analysis
                except Exception as e:
                    logger.error(f"Error parsing AI response: {e}")
        
        except Exception as e:
            logger.error(f"Error enhancing analysis with AI: {e}")
        
        return initial_analysis
