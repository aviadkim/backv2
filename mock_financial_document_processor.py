"""
Mock Financial Document Processor.

This module provides a mock implementation of the financial document processor
for testing purposes.
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialDocumentProcessorV2:
    """
    Mock implementation of the financial document processor for testing purposes.
    """
    
    def __init__(self):
        """Initialize the financial document processor."""
        self.extraction_results = {}
    
    def process(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a financial document.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save output files (default: None)
        
        Returns:
            Dict containing processing results
        """
        logger.info(f"Processing document: {pdf_path}")
        
        # Mock extraction results
        self.extraction_results = {
            "portfolio_value": 19510599.00,
            "securities": [
                {
                    "isin": "XS2567543397",
                    "description": "GS 10Y CALLABLE NOTE 2024-18.06.2034",
                    "valuation": 2560667.00
                },
                {
                    "isin": "XS2838389430",
                    "description": "LUMINIS 5.7% STR NOTE 2024-26.04.33 WFC",
                    "valuation": 1623560.00
                },
                {
                    "isin": "XS2964611052",
                    "description": "DEUTSCHE BANK 0% NOTES 2025-14.02.35",
                    "valuation": 1488375.00
                },
                {
                    "isin": "XS2792098779",
                    "description": "CITIGROUP",
                    "valuation": 1176780.00
                },
                {
                    "isin": "XS2110079584",
                    "description": "CITIGROUP 0% MTN 2024-09.07.34 REGS",
                    "valuation": 1107370.00
                },
                {
                    "isin": "XS0461497009",
                    "description": "DEUTSCHE BANK NOTES 23-08.11.28 VRN",
                    "valuation": 703670.00
                },
                {
                    "isin": "XS2692298537",
                    "description": "GOLDMAN SACHS 0% NOTES 23-07.11.29 SERIES P",
                    "valuation": 735333.00
                },
                {
                    "isin": "XS2381717250",
                    "description": "JPMORGAN CHASE 0% NOTES 2024-19.12.2034",
                    "valuation": 519200.00
                },
                {
                    "isin": "CH1259345242",
                    "description": "RAIFF 4.5% STRUC NTS 23-11.07.28 ON REF ASSET",
                    "valuation": 500350.00
                },
                {
                    "isin": "XS2315191069",
                    "description": "BNP PARIBAS ISS STRUCT.NOTE 21-08.01.29 ON DBDK",
                    "valuation": 498133.00
                },
                {
                    "isin": "XS2824054402",
                    "description": "BOFA 5.6% 2024-29.05.34 REGS",
                    "valuation": 474916.00
                },
                {
                    "isin": "XS2736388732",
                    "description": "BANK OF AMERICA NOTES 2023-20.12.31 VARIABLE RATE",
                    "valuation": 255383.00
                },
                {
                    "isin": "CH1259344831",
                    "description": "RAIFF 4.75% STR.NTS 23-11.07.28 ON REF ASSET",
                    "valuation": 249800.00
                },
                {
                    "isin": "XS2530201644",
                    "description": "TORONTO DOMINION BANK NOTES 23-23.02.27 REG-S VRN",
                    "valuation": 198745.00
                },
                {
                    "isin": "XS2912278723",
                    "description": "BANK OF AMERICA 0% NOTES 2024-17.10.2034",
                    "valuation": 197554.00
                },
                {
                    "isin": "XS2594173093",
                    "description": "NOVUS CAPITAL CREDIT LINKED NOTES 2023-27.09.2029",
                    "valuation": 192895.00
                },
                {
                    "isin": "XS2746319610",
                    "description": "SOCIETE GENERALE 32.46% NOTES 2024-01.03.30 REG S",
                    "valuation": 187094.00
                },
                {
                    "isin": "XS2953741100",
                    "description": "BANK OF AMERICA 0% NOTES 2024-11.12.34 REG S",
                    "valuation": 148080.00
                },
                {
                    "isin": "XS2518123653",
                    "description": "RBC TORONTO 5,06% CREDIT LINKED NOTE 2022-20.06.2027",
                    "valuation": 103614.00
                },
                {
                    "isin": "XS2761230684",
                    "description": "CIBC 0% NOTES 2024-13.02.2030 VARIABLE RATE",
                    "valuation": 101823.00
                },
                {
                    "isin": "XS2754416860",
                    "description": "LUMINIS (4.2% MIN/5.5% MAX) NOTES 2024-17.01.30",
                    "valuation": 98271.00
                },
                {
                    "isin": "XS2829712830",
                    "description": "GOLDMAN SACHS EMTN 2024-30.09.2024",
                    "valuation": 93020.00
                },
                {
                    "isin": "XS2481066111",
                    "description": "GOLDMAN SACHS 0% NOTES 2025-03.02.2035",
                    "valuation": 50445.00
                },
                {
                    "isin": "CH1908490000",
                    "description": "Cash Account (IBAN)",
                    "valuation": 47850.00
                },
                {
                    "isin": "CH0244767585",
                    "description": "UBS GROUP INC NAMEN-AKT.",
                    "valuation": 24720.00
                }
            ],
            "asset_allocation": [
                {
                    "asset_class": "Bonds",
                    "percentage": 59.24,
                    "value": 11558957.00
                },
                {
                    "asset_class": "Structured Products",
                    "percentage": 40.24,
                    "value": 7850257.00
                },
                {
                    "asset_class": "Equities",
                    "percentage": 0.14,
                    "value": 27406.00
                },
                {
                    "asset_class": "Liquidity",
                    "percentage": 0.25,
                    "value": 47850.00
                },
                {
                    "asset_class": "Other assets",
                    "percentage": 0.13,
                    "value": 26129.00
                }
            ],
            "structured_products": [
                {
                    "isin": "CH1259344831",
                    "description": "RAIFF 4.75% STR.NTS 23-11.07.28 ON REF ASSET",
                    "valuation": 249800.00
                }
            ]
        }
        
        # Save extraction results if output directory is provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
            # Save pattern extracted data
            pattern_extracted_path = os.path.join(output_dir, "pattern_extracted_data.json")
            with open(pattern_extracted_path, "w", encoding="utf-8") as f:
                json.dump(self.extraction_results, f, indent=2)
            
            # Save structured products
            structured_products_path = os.path.join(output_dir, "structured_products.json")
            with open(structured_products_path, "w", encoding="utf-8") as f:
                json.dump(self.extraction_results["structured_products"], f, indent=2)
        
        return {"extraction_results": self.extraction_results}
    
    def get_portfolio_value(self) -> Optional[float]:
        """
        Get the portfolio value.
        
        Returns:
            Portfolio value or None if not found
        """
        return self.extraction_results.get("portfolio_value")
    
    def get_securities(self) -> List[Dict[str, Any]]:
        """
        Get securities.
        
        Returns:
            List of securities
        """
        return self.extraction_results.get("securities", [])
    
    def get_asset_allocation(self) -> List[Dict[str, Any]]:
        """
        Get asset allocation.
        
        Returns:
            List of asset allocation entries
        """
        return self.extraction_results.get("asset_allocation", [])
    
    def get_structured_products(self) -> List[Dict[str, Any]]:
        """
        Get structured products.
        
        Returns:
            List of structured products
        """
        return self.extraction_results.get("structured_products", [])
    
    def get_top_securities(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get the top N securities by valuation.
        
        Args:
            n: Number of securities to retrieve (default: 5)
        
        Returns:
            List of top N securities by valuation
        """
        securities = self.get_securities()
        
        # Sort securities by valuation in descending order
        sorted_securities = sorted(securities, key=lambda x: x.get("valuation", 0), reverse=True)
        
        # Return top N securities
        return sorted_securities[:n]
