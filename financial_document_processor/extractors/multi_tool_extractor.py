"""
Multi-tool extractor for financial documents with reconciliation.
"""
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
import json
import tempfile
import re
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import enhanced preprocessor
from financial_document_processor.extractors.enhanced_preprocessor import EnhancedPreprocessor

class MultiToolExtractor:
    """Multi-tool extractor for financial documents with reconciliation."""
    
    def __init__(self, ocr_languages: str = "eng"):
        """
        Initialize the extractor.
        
        Args:
            ocr_languages: Languages to use for OCR (e.g., "eng+heb" for English and Hebrew)
        """
        self.preprocessor = EnhancedPreprocessor(ocr_languages=ocr_languages)
        logger.info(f"Initialized multi-tool extractor with OCR languages: {ocr_languages}")
        
        # Try to import extraction libraries
        try:
            import camelot
            self.camelot_available = True
        except ImportError:
            self.camelot_available = False
            logger.warning("Camelot not available. Install with: pip install camelot-py")
        
        try:
            import tabula
            self.tabula_available = True
        except ImportError:
            self.tabula_available = False
            logger.warning("Tabula not available. Install with: pip install tabula-py")
    
    def extract(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract data from a PDF file using multiple tools.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save extracted data (optional)
        
        Returns:
            Dictionary with extraction results
        """
        logger.info(f"Extracting data from {pdf_path} using multiple tools")
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Preprocess PDF
        preprocessed = self.preprocessor.preprocess(pdf_path, output_dir=output_dir)
        
        # Extract tables with multiple tools
        tables = self._extract_tables_with_multiple_tools(pdf_path)
        
        # Extract financial entities
        entities = self._extract_financial_entities(preprocessed["text"])
        
        # Extract portfolio value
        portfolio_value = self._extract_portfolio_value(preprocessed["text"], tables)
        
        # Extract securities
        securities = self._extract_securities(preprocessed["text"], tables, entities)
        
        # Extract asset allocation
        asset_allocation = self._extract_asset_allocation(preprocessed["text"], tables, entities)
        
        # Extract risk profile
        risk_profile = self._extract_risk_profile(preprocessed["text"])
        
        # Extract currency
        currency = self._extract_currency(preprocessed["text"], entities)
        
        # Combine results
        result = {
            "metadata": preprocessed["metadata"],
            "portfolio_value": portfolio_value,
            "securities": securities,
            "asset_allocation": asset_allocation,
            "risk_profile": risk_profile,
            "currency": currency,
            "entities": entities,
            "tables": tables,
            "text": preprocessed["text"]
        }
        
        # Save results if output directory is specified
        if output_dir:
            with open(os.path.join(output_dir, "extraction_result.json"), "w", encoding="utf-8") as f:
                # Convert result to JSON-serializable format
                json_result = self._make_json_serializable(result)
                json.dump(json_result, f, indent=2)
        
        logger.info(f"Extraction completed for {pdf_path}")
        return result
    
    def _make_json_serializable(self, obj: Any) -> Any:
        """Convert an object to a JSON-serializable format."""
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            return str(obj)
    
    def _extract_tables_with_multiple_tools(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract tables from PDF using multiple tools."""
        logger.info(f"Extracting tables from {pdf_path} using multiple tools")
        
        tables = []
        
        # Extract tables with pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    for j, table_data in enumerate(page_tables):
                        tables.append({
                            "page": i + 1,
                            "table_number": j + 1,
                            "extraction_method": "pdfplumber",
                            "data": table_data
                        })
            
            logger.info(f"Extracted {len(tables)} tables with pdfplumber")
        except Exception as e:
            logger.warning(f"Error extracting tables with pdfplumber: {e}")
        
        # Extract tables with camelot
        if self.camelot_available:
            try:
                import camelot
                
                # Try lattice mode first (for tables with borders)
                lattice_tables = camelot.read_pdf(pdf_path, pages="all", flavor="lattice")
                
                # Then try stream mode (for tables without borders)
                stream_tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")
                
                # Process lattice tables
                for i, table in enumerate(lattice_tables):
                    tables.append({
                        "page": table.page,
                        "extraction_method": "camelot_lattice",
                        "table_number": i + 1,
                        "data": table.data,
                        "headers": table.data[0] if len(table.data) > 0 else [],
                        "rows": table.data[1:] if len(table.data) > 1 else [],
                        "accuracy": table.accuracy
                    })
                
                # Process stream tables
                for i, table in enumerate(stream_tables):
                    tables.append({
                        "page": table.page,
                        "extraction_method": "camelot_stream",
                        "table_number": i + 1,
                        "data": table.data,
                        "headers": table.data[0] if len(table.data) > 0 else [],
                        "rows": table.data[1:] if len(table.data) > 1 else [],
                        "accuracy": table.accuracy
                    })
                
                logger.info(f"Extracted {len(lattice_tables) + len(stream_tables)} tables with camelot")
            except Exception as e:
                logger.warning(f"Error extracting tables with camelot: {e}")
        
        # Extract tables with tabula
        if self.tabula_available:
            try:
                import tabula
                
                # Extract tables
                tabula_tables = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True)
                
                for i, table in enumerate(tabula_tables):
                    tables.append({
                        "extraction_method": "tabula",
                        "table_number": i + 1,
                        "data": table.values.tolist(),
                        "headers": table.columns.tolist()
                    })
                
                logger.info(f"Extracted {len(tabula_tables)} tables with tabula")
            except Exception as e:
                logger.warning(f"Error extracting tables with tabula: {e}")
        
        return tables
    
    def _extract_financial_entities(self, text_dict: Dict[str, str]) -> Dict[str, List[Dict[str, Any]]]:
        """Extract financial entities from text."""
        logger.info("Extracting financial entities from text")
        
        # Combine text from different extraction methods
        combined_text = ""
        for method, text in text_dict.items():
            combined_text += f"\n\n--- {method.upper()} ---\n\n{text}"
        
        # Detect financial entities
        entities = self.preprocessor.detect_financial_entities(combined_text)
        
        return entities
    
    def _extract_portfolio_value(self, text_dict: Dict[str, str], tables: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract portfolio value from text and tables.
        
        Args:
            text_dict: Dictionary with text from different extraction methods
            tables: List of extracted tables
        
        Returns:
            Dictionary with portfolio value information
        """
        logger.info("Extracting portfolio value")
        
        # Combine text from different extraction methods
        combined_text = ""
        for method, text in text_dict.items():
            combined_text += f"\n\n--- {method.upper()} ---\n\n{text}"
        
        # Define patterns to match portfolio value
        patterns = [
            r'Portfolio\s+Total\s+(\d[\d,.\']*)',
            r'Total\s+assets\s+(\d[\d,.\']*)',
            r'Portfolio\s+Total\s*[:\s]+(\d[\d,.\']*)',
            r'Total\s+assets\s*[:\s]+(\d[\d,.\']*)',
            r'Portfolio\s+Value\s*[:\s]+(\d[\d,.\']*)',
            r'Total\s+Value\s*[:\s]+(\d[\d,.\']*)',
            r'Total\s+Portfolio\s+Value\s*[:\s]+(\d[\d,.\']*)'
        ]
        
        # Search for portfolio value in text
        text_values = []
        for pattern in patterns:
            matches = re.finditer(pattern, combined_text)
            for match in matches:
                value_str = match.group(1).strip()
                value_str = value_str.replace("'", "").replace(",", "")
                try:
                    value = float(value_str)
                    text_values.append({
                        "value": value,
                        "source": "text",
                        "pattern": pattern,
                        "match": match.group(0)
                    })
                except ValueError:
                    continue
        
        # Search for portfolio value in tables
        table_values = []
        for table in tables:
            # Skip tables without data
            if not table.get("data"):
                continue
            
            # Check if table contains portfolio value
            for row in table["data"]:
                for i, cell in enumerate(row):
                    if not cell:
                        continue
                    
                    # Check if cell contains portfolio value keywords
                    if any(keyword in str(cell).lower() for keyword in ["portfolio total", "total assets", "portfolio value", "total value"]):
                        # Look for value in the same row
                        for j, value_cell in enumerate(row):
                            if j == i:
                                continue
                            
                            if not value_cell:
                                continue
                            
                            # Try to extract value
                            value_str = str(value_cell).strip()
                            value_str = re.sub(r'[^\d.]', '', value_str)
                            
                            try:
                                value = float(value_str)
                                if value > 1000:  # Minimum threshold for portfolio value
                                    table_values.append({
                                        "value": value,
                                        "source": "table",
                                        "extraction_method": table.get("extraction_method"),
                                        "table_number": table.get("table_number"),
                                        "page": table.get("page")
                                    })
                            except ValueError:
                                continue
        
        # Combine values from text and tables
        all_values = text_values + table_values
        
        if not all_values:
            logger.warning("No portfolio value found")
            return {"value": None, "confidence": 0, "sources": []}
        
        # Group values by value
        value_groups = defaultdict(list)
        for value_info in all_values:
            value_groups[value_info["value"]].append(value_info)
        
        # Find the most common value
        most_common_value = max(value_groups.items(), key=lambda x: len(x[1]))
        value = most_common_value[0]
        sources = most_common_value[1]
        confidence = len(sources) / len(all_values)
        
        logger.info(f"Found portfolio value: {value} (confidence: {confidence:.2f})")
        
        return {
            "value": value,
            "confidence": confidence,
            "sources": sources
        }
    
    def _extract_securities(self, text_dict: Dict[str, str], tables: List[Dict[str, Any]], entities: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Extract securities from text, tables, and entities.
        
        Args:
            text_dict: Dictionary with text from different extraction methods
            tables: List of extracted tables
            entities: Dictionary with extracted entities
        
        Returns:
            List of securities
        """
        logger.info("Extracting securities")
        
        securities = []
        
        # Extract securities from entities
        for security in entities["securities"]:
            # Get ISIN
            isin = security["value"]
            
            # Get context
            context = security["context"]
            
            # Try to extract description
            desc_pattern = r'([A-Z][A-Z0-9\s\.\-\(\)]{5,50})'
            desc_match = re.search(desc_pattern, context)
            description = desc_match.group(1).strip() if desc_match else "Unknown"
            
            # Try to extract valuation
            valuation_pattern = r'(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)'
            valuation_matches = list(re.finditer(valuation_pattern, context))
            
            valuation = None
            if valuation_matches:
                # Look for large values that might be valuations
                for val_match in valuation_matches:
                    val_str = val_match.group(1)
                    try:
                        val = float(val_str.replace(',', '').replace("'", ''))
                        if val > 10000:  # Likely a valuation
                            valuation = val
                            break
                    except ValueError:
                        continue
            
            # Try to determine security type
            security_type = "Unknown"
            if "Bond" in context or "bond" in context:
                security_type = "Bond"
            elif "Equity" in context or "equity" in context or "Stock" in context or "stock" in context:
                security_type = "Equity"
            elif "Structured" in context or "structured" in context:
                security_type = "Structured Product"
            elif "Fund" in context or "fund" in context:
                security_type = "Fund"
            
            # Create security object
            security_obj = {
                "isin": isin,
                "description": description,
                "security_type": security_type,
                "valuation": valuation,
                "source": "text"
            }
            
            # Check if this security is already in the list
            if not any(s["isin"] == isin for s in securities):
                securities.append(security_obj)
        
        # Extract securities from tables
        for table in tables:
            # Skip tables without data
            if not table.get("data"):
                continue
            
            # Check if table contains securities
            for row in table["data"]:
                # Skip empty rows
                if not row or all(not cell for cell in row):
                    continue
                
                # Look for ISIN in the row
                isin = None
                for cell in row:
                    if not cell:
                        continue
                    
                    # Check if cell contains ISIN
                    isin_match = re.search(r'([A-Z]{2}[A-Z0-9]{9}[0-9])', str(cell))
                    if isin_match:
                        isin = isin_match.group(1)
                        break
                
                if not isin:
                    continue
                
                # Extract other information from the row
                description = "Unknown"
                security_type = "Unknown"
                valuation = None
                
                for cell in row:
                    if not cell:
                        continue
                    
                    # Try to extract description
                    if len(str(cell)) > 10 and not description or description == "Unknown":
                        description = str(cell)
                    
                    # Try to extract security type
                    cell_lower = str(cell).lower()
                    if "bond" in cell_lower and security_type == "Unknown":
                        security_type = "Bond"
                    elif "equity" in cell_lower or "stock" in cell_lower and security_type == "Unknown":
                        security_type = "Equity"
                    elif "structured" in cell_lower and security_type == "Unknown":
                        security_type = "Structured Product"
                    elif "fund" in cell_lower and security_type == "Unknown":
                        security_type = "Fund"
                    
                    # Try to extract valuation
                    if not valuation:
                        val_match = re.search(r'(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)', str(cell))
                        if val_match:
                            val_str = val_match.group(1)
                            try:
                                val = float(val_str.replace(',', '').replace("'", ''))
                                if val > 10000:  # Likely a valuation
                                    valuation = val
                            except ValueError:
                                continue
                
                # Create security object
                security_obj = {
                    "isin": isin,
                    "description": description,
                    "security_type": security_type,
                    "valuation": valuation,
                    "source": "table",
                    "extraction_method": table.get("extraction_method"),
                    "table_number": table.get("table_number"),
                    "page": table.get("page")
                }
                
                # Check if this security is already in the list
                existing_security = next((s for s in securities if s["isin"] == isin), None)
                if existing_security:
                    # Update existing security with table information if it's more complete
                    if existing_security["description"] == "Unknown" and description != "Unknown":
                        existing_security["description"] = description
                    
                    if existing_security["security_type"] == "Unknown" and security_type != "Unknown":
                        existing_security["security_type"] = security_type
                    
                    if existing_security["valuation"] is None and valuation is not None:
                        existing_security["valuation"] = valuation
                        existing_security["source"] = f"{existing_security['source']}, table"
                else:
                    securities.append(security_obj)
        
        logger.info(f"Found {len(securities)} securities")
        return securities
    
    def _extract_asset_allocation(self, text_dict: Dict[str, str], tables: List[Dict[str, Any]], entities: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Extract asset allocation from text, tables, and entities.
        
        Args:
            text_dict: Dictionary with text from different extraction methods
            tables: List of extracted tables
            entities: Dictionary with extracted entities
        
        Returns:
            List of asset allocations
        """
        logger.info("Extracting asset allocation")
        
        # Combine text from different extraction methods
        combined_text = ""
        for method, text in text_dict.items():
            combined_text += f"\n\n--- {method.upper()} ---\n\n{text}"
        
        asset_allocations = []
        
        # Look for the Asset Allocation section
        asset_allocation_start = combined_text.find("Asset Allocation")
        if asset_allocation_start == -1:
            logger.warning("No Asset Allocation section found in text")
        else:
            # Find the end of the Asset Allocation section
            asset_allocation_end = combined_text.find("Total assets", asset_allocation_start)
            if asset_allocation_end == -1:
                asset_allocation_end = len(combined_text)
            
            asset_allocation_text = combined_text[asset_allocation_start:asset_allocation_end]
            
            # Extract asset classes and their values
            asset_class_pattern = r'([A-Za-z\s]+)\s+(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)\s+(\d{1,3}(?:\.\d{1,2})?)%'
            asset_class_matches = re.finditer(asset_class_pattern, asset_allocation_text)
            
            for match in asset_class_matches:
                asset_class = match.group(1).strip()
                value_str = match.group(2).strip()
                percentage_str = match.group(3).strip()
                
                try:
                    value = float(value_str.replace(',', '').replace("'", ''))
                    percentage = float(percentage_str)
                    
                    asset_allocations.append({
                        "asset_class": asset_class,
                        "value": value,
                        "percentage": percentage,
                        "source": "text"
                    })
                    
                    logger.info(f"Found asset allocation in text: {asset_class} - {value} ({percentage}%)")
                except ValueError:
                    continue
        
        # Extract asset allocation from tables
        for table in tables:
            # Skip tables without data
            if not table.get("data"):
                continue
            
            # Check if table contains asset allocation
            is_asset_allocation_table = False
            for row in table["data"]:
                # Skip empty rows
                if not row or all(not cell for cell in row):
                    continue
                
                # Check if row contains asset allocation keywords
                row_str = " ".join(str(cell) for cell in row if cell)
                if "asset allocation" in row_str.lower() or "asset class" in row_str.lower():
                    is_asset_allocation_table = True
                    break
            
            if not is_asset_allocation_table:
                continue
            
            # Extract asset allocation from table
            for row in table["data"]:
                # Skip empty rows
                if not row or all(not cell for cell in row):
                    continue
                
                # Skip header rows
                row_str = " ".join(str(cell) for cell in row if cell)
                if "asset allocation" in row_str.lower() or "asset class" in row_str.lower():
                    continue
                
                # Extract asset class, value, and percentage
                asset_class = None
                value = None
                percentage = None
                
                for i, cell in enumerate(row):
                    if not cell:
                        continue
                    
                    cell_str = str(cell).strip()
                    
                    # Try to extract asset class
                    if i == 0 and not asset_class:
                        asset_class = cell_str
                    
                    # Try to extract value
                    if not value:
                        val_match = re.search(r'(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)', cell_str)
                        if val_match:
                            val_str = val_match.group(1)
                            try:
                                val = float(val_str.replace(',', '').replace("'", ''))
                                if val > 1000:  # Minimum threshold for asset value
                                    value = val
                            except ValueError:
                                continue
                    
                    # Try to extract percentage
                    if not percentage:
                        pct_match = re.search(r'(\d{1,3}(?:\.\d{1,2})?)%', cell_str)
                        if pct_match:
                            pct_str = pct_match.group(1)
                            try:
                                percentage = float(pct_str)
                            except ValueError:
                                continue
                
                if asset_class and (value or percentage):
                    # Create asset allocation object
                    asset_allocation = {
                        "asset_class": asset_class,
                        "value": value,
                        "percentage": percentage,
                        "source": "table",
                        "extraction_method": table.get("extraction_method"),
                        "table_number": table.get("table_number"),
                        "page": table.get("page")
                    }
                    
                    # Check if this asset class is already in the list
                    existing_allocation = next((a for a in asset_allocations if a["asset_class"] == asset_class), None)
                    if existing_allocation:
                        # Update existing allocation with table information if it's more complete
                        if existing_allocation["value"] is None and value is not None:
                            existing_allocation["value"] = value
                        
                        if existing_allocation["percentage"] is None and percentage is not None:
                            existing_allocation["percentage"] = percentage
                        
                        existing_allocation["source"] = f"{existing_allocation['source']}, table"
                    else:
                        asset_allocations.append(asset_allocation)
                        logger.info(f"Found asset allocation in table: {asset_class} - {value} ({percentage}%)")
        
        # Validate asset allocations
        if asset_allocations:
            # Check if percentages sum to approximately 100%
            total_percentage = sum(a["percentage"] for a in asset_allocations if a["percentage"] is not None)
            if abs(total_percentage - 100) > 5:
                logger.warning(f"Asset allocation percentages sum to {total_percentage}%, which is not close to 100%")
            
            # Check if values sum to approximately the portfolio value
            total_value = sum(a["value"] for a in asset_allocations if a["value"] is not None)
            logger.info(f"Asset allocation total value: {total_value}")
        
        return asset_allocations
    
    def _extract_risk_profile(self, text_dict: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract risk profile from text.
        
        Args:
            text_dict: Dictionary with text from different extraction methods
        
        Returns:
            Dictionary with risk profile information
        """
        logger.info("Extracting risk profile")
        
        # Combine text from different extraction methods
        combined_text = ""
        for method, text in text_dict.items():
            combined_text += f"\n\n--- {method.upper()} ---\n\n{text}"
        
        # Define patterns to match risk profile
        patterns = [
            r'Risk\s+Profile\s*[:\s]+([A-Za-z\-]+)',
            r'Risk\s+profile\s*[:\s]+([A-Za-z\-]+)',
            r'Risk\s+Profile\s*//([A-Za-z\-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, combined_text)
            if match:
                risk_profile = match.group(1).strip()
                logger.info(f"Found risk profile: {risk_profile}")
                return {
                    "value": risk_profile,
                    "confidence": 1.0,
                    "source": "text",
                    "pattern": pattern
                }
        
        logger.warning("No risk profile found")
        return {"value": None, "confidence": 0, "source": None}
    
    def _extract_currency(self, text_dict: Dict[str, str], entities: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Extract currency from text and entities.
        
        Args:
            text_dict: Dictionary with text from different extraction methods
            entities: Dictionary with extracted entities
        
        Returns:
            Dictionary with currency information
        """
        logger.info("Extracting currency")
        
        # Combine text from different extraction methods
        combined_text = ""
        for method, text in text_dict.items():
            combined_text += f"\n\n--- {method.upper()} ---\n\n{text}"
        
        # Define patterns to match currency
        patterns = [
            r'Valuation\s+currency\s*[:\s]+([A-Z]{3})',
            r'Valuation\s+currency\s*//([A-Z]{3})',
            r'Currency\s*[:\s]+([A-Z]{3})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, combined_text)
            if match:
                currency = match.group(1).strip()
                logger.info(f"Found currency: {currency}")
                return {
                    "value": currency,
                    "confidence": 1.0,
                    "source": "text",
                    "pattern": pattern
                }
        
        # Check entities for currencies
        if entities["currencies"]:
            # Count occurrences of each currency
            currency_counts = defaultdict(int)
            for currency in entities["currencies"]:
                currency_counts[currency["value"]] += 1
            
            # Find the most common currency
            most_common_currency = max(currency_counts.items(), key=lambda x: x[1])
            currency = most_common_currency[0]
            count = most_common_currency[1]
            
            logger.info(f"Found currency from entities: {currency} (count: {count})")
            return {
                "value": currency,
                "confidence": 0.8,
                "source": "entities",
                "count": count
            }
        
        logger.warning("No currency found")
        return {"value": None, "confidence": 0, "source": None}
