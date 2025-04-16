"""
ISIN Extractor Agent for FinDoc Analyzer v1.0

This agent extracts and validates International Securities Identification Numbers (ISINs) from text.
"""
import re
import logging
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ISINExtractorAgent:
    """
    Agent for extracting and validating ISINs from text.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the ISINExtractorAgent.
        """
        logger.info("ISINExtractorAgent initialized")
    
    def process(self, text: str, validate: bool = True, with_metadata: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Extract ISINs from text.
        
        Args:
            text: Text to extract ISINs from
            validate: Whether to validate the extracted ISINs
            with_metadata: Whether to include metadata about each ISIN
            **kwargs: Additional arguments
            
        Returns:
            Dictionary with extraction results
        """
        logger.info("Extracting ISINs from text")
        
        # Extract ISINs
        isins = self._extract_isins(text)
        
        # Validate ISINs if requested
        if validate:
            isins = [isin for isin in isins if self._validate_isin(isin)]
        
        # Get metadata if requested
        if with_metadata:
            isin_data = [self._get_isin_metadata(isin, text) for isin in isins]
            return {
                "status": "success",
                "isins": isins,
                "count": len(isins),
                "isin_data": isin_data
            }
        
        return {
            "status": "success",
            "isins": isins,
            "count": len(isins)
        }
    
    def _extract_isins(self, text: str) -> List[str]:
        """
        Extract ISINs from text using regex.
        
        Args:
            text: Text to extract ISINs from
            
        Returns:
            List of extracted ISINs
        """
        # ISIN pattern: 2 letters followed by 10 alphanumeric characters
        isin_pattern = r'(?:ISIN:|ISIN\s+|ISIN=|ISIN\s*:\s*|^|\s)([A-Z]{2}[A-Z0-9]{10})(?:\s|$|,|\.|;|//)'
        matches = re.finditer(isin_pattern, text, re.MULTILINE)
        
        # Extract unique ISINs
        isins = set()
        for match in matches:
            isins.add(match.group(1))
        
        return list(isins)
    
    def _validate_isin(self, isin: str) -> bool:
        """
        Validate an ISIN using the checksum algorithm.
        
        Args:
            isin: ISIN to validate
            
        Returns:
            True if the ISIN is valid, False otherwise
        """
        if not re.match(r'^[A-Z]{2}[A-Z0-9]{10}$', isin):
            return False
        
        # Convert letters to numbers (A=10, B=11, ..., Z=35)
        digits = []
        for char in isin:
            if char.isdigit():
                digits.append(int(char))
            else:
                digits.append(ord(char) - ord('A') + 10)
        
        # Apply the Luhn algorithm
        total = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 0:
                total += digit
            else:
                doubled = digit * 2
                total += doubled if doubled < 10 else doubled - 9
        
        return total % 10 == 0
    
    def _get_isin_metadata(self, isin: str, text: str) -> Dict[str, Any]:
        """
        Get metadata about an ISIN from the text.
        
        Args:
            isin: ISIN to get metadata for
            text: Text to extract metadata from
            
        Returns:
            Dictionary with ISIN metadata
        """
        # Find the context around the ISIN
        context_pattern = r'(.{0,100}' + re.escape(isin) + r'.{0,100})'
        context_match = re.search(context_pattern, text, re.DOTALL)
        context = context_match.group(1).strip() if context_match else ""
        
        # Try to extract security name
        security_name = self._extract_security_name(isin, text)
        
        # Try to extract valuation
        valuation = self._extract_valuation(isin, text)
        
        return {
            "isin": isin,
            "context": context,
            "security_name": security_name,
            "valuation": valuation,
            "country_code": isin[:2]
        }
    
    def _extract_security_name(self, isin: str, text: str) -> Optional[str]:
        """
        Extract the security name for an ISIN.
        
        Args:
            isin: ISIN to extract security name for
            text: Text to extract security name from
            
        Returns:
            Security name if found, None otherwise
        """
        # Look for patterns like "SECURITY NAME (ISIN: XX0000000000)"
        pattern1 = r'([^()\n]{5,100})\s*\([^\)]*' + re.escape(isin) + r'[^\)]*\)'
        match1 = re.search(pattern1, text)
        if match1:
            return match1.group(1).strip()
        
        # Look for patterns like "ISIN: XX0000000000 SECURITY NAME"
        pattern2 = r'ISIN\s*:\s*' + re.escape(isin) + r'\s*//\s*Valorn\.[^//]*//\s*([^//\n]{5,100})'
        match2 = re.search(pattern2, text)
        if match2:
            return match2.group(1).strip()
        
        return None
    
    def _extract_valuation(self, isin: str, text: str) -> Optional[float]:
        """
        Extract the valuation for an ISIN.
        
        Args:
            isin: ISIN to extract valuation for
            text: Text to extract valuation from
            
        Returns:
            Valuation if found, None otherwise
        """
        # Look for patterns like "VALUATION: 1,234,567.89" near the ISIN
        context_pattern = r'(.{0,500}' + re.escape(isin) + r'.{0,500})'
        context_match = re.search(context_pattern, text, re.DOTALL)
        
        if not context_match:
            return None
        
        context = context_match.group(1)
        
        # Look for currency values
        value_pattern = r'(\d+[\'|\,]?\d*[\'|\,]?\d*)\s+(\d+\.\d+)%'
        value_match = re.search(value_pattern, context)
        
        if value_match:
            value_str = value_match.group(1).replace("'", "").replace(",", "")
            try:
                return float(value_str)
            except ValueError:
                pass
        
        return None
