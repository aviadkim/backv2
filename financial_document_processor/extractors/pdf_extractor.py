"""
PDF extraction module using Unstructured, Camelot, and pdfplumber.
"""
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
import json

# Import extraction libraries
try:
    from unstructured.partition.pdf import partition_pdf
    from unstructured.staging.base import elements_to_json
    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    UNSTRUCTURED_AVAILABLE = False
    logging.warning("Unstructured library not available. Install with: pip install unstructured")

try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False
    logging.warning("Camelot library not available. Install with: pip install camelot-py")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logging.warning("pdfplumber library not available. Install with: pip install pdfplumber")

class PDFExtractor:
    """
    Comprehensive PDF extraction using multiple libraries.
    """
    
    def __init__(self, use_unstructured: bool = True, use_camelot: bool = True, 
                 use_pdfplumber: bool = True, ocr_languages: str = "eng"):
        """
        Initialize the PDF extractor.
        
        Args:
            use_unstructured: Whether to use Unstructured for extraction
            use_camelot: Whether to use Camelot for table extraction
            use_pdfplumber: Whether to use pdfplumber for extraction
            ocr_languages: Languages to use for OCR (e.g., "eng+heb" for English and Hebrew)
        """
        self.use_unstructured = use_unstructured and UNSTRUCTURED_AVAILABLE
        self.use_camelot = use_camelot and CAMELOT_AVAILABLE
        self.use_pdfplumber = use_pdfplumber and PDFPLUMBER_AVAILABLE
        self.ocr_languages = ocr_languages
        
        if not any([self.use_unstructured, self.use_camelot, self.use_pdfplumber]):
            raise ValueError("At least one extraction library must be enabled")
    
    def extract(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract content from a PDF using all available methods.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save extracted data (optional)
        
        Returns:
            Dictionary containing extracted content
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        result = {
            "metadata": self._extract_metadata(pdf_path),
            "text": {},
            "tables": [],
            "elements": []
        }
        
        # Extract using Unstructured
        if self.use_unstructured:
            unstructured_result = self._extract_with_unstructured(pdf_path)
            result["elements"] = unstructured_result.get("elements", [])
            result["text"]["unstructured"] = unstructured_result.get("text", "")
        
        # Extract tables using Camelot
        if self.use_camelot:
            result["tables"].extend(self._extract_tables_with_camelot(pdf_path))
        
        # Extract using pdfplumber
        if self.use_pdfplumber:
            pdfplumber_result = self._extract_with_pdfplumber(pdf_path)
            result["text"]["pdfplumber"] = pdfplumber_result.get("text", "")
            result["tables"].extend(pdfplumber_result.get("tables", []))
        
        # Save results if output directory is provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{os.path.basename(pdf_path)}.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        
        return result
    
    def _extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract metadata from the PDF."""
        metadata = {
            "filename": os.path.basename(pdf_path),
            "path": pdf_path,
            "size_bytes": os.path.getsize(pdf_path)
        }
        
        # Try to extract more metadata using pdfplumber
        if self.use_pdfplumber:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    metadata.update({
                        "page_count": len(pdf.pages),
                        "pdf_info": pdf.metadata
                    })
            except Exception as e:
                logging.warning(f"Error extracting metadata with pdfplumber: {e}")
        
        return metadata
    
    def _extract_with_unstructured(self, pdf_path: str) -> Dict[str, Any]:
        """Extract content using Unstructured."""
        if not self.use_unstructured:
            return {"elements": [], "text": ""}
        
        try:
            # Extract elements from PDF
            elements = partition_pdf(
                pdf_path,
                strategy="auto",
                languages=[self.ocr_languages],
                ocr_enabled=True
            )
            
            # Convert elements to structured format
            elements_json = elements_to_json(elements)
            
            # Extract full text
            full_text = "\n\n".join([elem.get("text", "") for elem in elements_json])
            
            return {
                "elements": elements_json,
                "text": full_text
            }
        except Exception as e:
            logging.error(f"Error extracting with Unstructured: {e}")
            return {"elements": [], "text": ""}
    
    def _extract_tables_with_camelot(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract tables using Camelot."""
        if not self.use_camelot:
            return []
        
        tables = []
        try:
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
        except Exception as e:
            logging.error(f"Error extracting tables with Camelot: {e}")
        
        return tables
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Dict[str, Any]:
        """Extract content using pdfplumber."""
        if not self.use_pdfplumber:
            return {"text": "", "tables": []}
        
        result = {"text": "", "tables": []}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                tables = []
                
                for i, page in enumerate(pdf.pages):
                    # Extract text
                    page_text = page.extract_text() or ""
                    full_text += f"\n\n--- Page {i+1} ---\n\n{page_text}"
                    
                    # Extract tables
                    page_tables = page.extract_tables()
                    for j, table_data in enumerate(page_tables):
                        tables.append({
                            "page": i + 1,
                            "extraction_method": "pdfplumber",
                            "table_number": j + 1,
                            "data": table_data,
                            "headers": table_data[0] if table_data and len(table_data) > 0 else [],
                            "rows": table_data[1:] if table_data and len(table_data) > 1 else []
                        })
                
                result["text"] = full_text
                result["tables"] = tables
        except Exception as e:
            logging.error(f"Error extracting with pdfplumber: {e}")
        
        return result
    
    def extract_securities(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract securities information from a financial document.
        
        Args:
            pdf_path: Path to the PDF file
        
        Returns:
            List of dictionaries containing securities information
        """
        # Extract all content from the PDF
        extraction_result = self.extract(pdf_path)
        
        # Process the extracted content to identify securities
        securities = []
        
        # Process tables for securities information
        for table in extraction_result["tables"]:
            securities.extend(self._extract_securities_from_table(table))
        
        # Process text for securities information
        if "unstructured" in extraction_result["text"]:
            securities.extend(self._extract_securities_from_text(extraction_result["text"]["unstructured"]))
        
        if "pdfplumber" in extraction_result["text"]:
            securities.extend(self._extract_securities_from_text(extraction_result["text"]["pdfplumber"]))
        
        # Deduplicate securities based on ISIN
        deduplicated = {}
        for security in securities:
            isin = security.get("isin")
            if isin and isin not in deduplicated:
                deduplicated[isin] = security
            elif isin and isin in deduplicated:
                # Merge information if we have multiple entries for the same security
                for key, value in security.items():
                    if value and not deduplicated[isin].get(key):
                        deduplicated[isin][key] = value
        
        return list(deduplicated.values())
    
    def _extract_securities_from_table(self, table: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract securities information from a table."""
        securities = []
        
        # Skip tables with no data
        if not table.get("data") or len(table["data"]) <= 1:
            return securities
        
        # Check if this looks like a securities table
        headers = [str(h).lower() for h in table.get("headers", [])]
        
        # Look for common securities table headers
        securities_table = any(keyword in " ".join(headers) for keyword in 
                              ["isin", "security", "bond", "equity", "stock", "fund", 
                               "valuation", "value", "price", "quantity"])
        
        if not securities_table:
            return securities
        
        # Find column indices for relevant information
        isin_col = next((i for i, h in enumerate(headers) if "isin" in h), None)
        name_col = next((i for i, h in enumerate(headers) if any(k in h for k in ["name", "description", "security"])), None)
        value_col = next((i for i, h in enumerate(headers) if any(k in h for k in ["value", "valuation", "amount"])), None)
        price_col = next((i for i, h in enumerate(headers) if "price" in h), None)
        quantity_col = next((i for i, h in enumerate(headers) if any(k in h for k in ["quantity", "shares", "units"])), None)
        
        # Process rows
        for row in table.get("rows", []):
            if len(row) < max(filter(None, [isin_col, name_col, value_col, price_col, quantity_col])) + 1:
                continue
            
            security = {"extraction_method": f"table_{table.get('extraction_method', 'unknown')}"}
            
            # Extract ISIN
            if isin_col is not None and row[isin_col]:
                # Clean and validate ISIN
                isin_text = str(row[isin_col]).strip()
                # ISIN is typically 12 characters: 2 letters followed by 10 alphanumeric characters
                import re
                isin_match = re.search(r'[A-Z]{2}[A-Z0-9]{9}[0-9]', isin_text)
                if isin_match:
                    security["isin"] = isin_match.group(0)
            
            # Extract name/description
            if name_col is not None and row[name_col]:
                security["description"] = str(row[name_col]).strip()
            
            # Extract valuation
            if value_col is not None and row[value_col]:
                try:
                    # Clean and convert to float
                    value_text = str(row[value_col]).strip()
                    value_text = value_text.replace(",", "").replace("'", "")
                    security["valuation"] = float(value_text)
                except (ValueError, TypeError):
                    pass
            
            # Extract price
            if price_col is not None and row[price_col]:
                try:
                    price_text = str(row[price_col]).strip()
                    price_text = price_text.replace(",", "").replace("'", "")
                    security["price"] = float(price_text)
                except (ValueError, TypeError):
                    pass
            
            # Extract quantity
            if quantity_col is not None and row[quantity_col]:
                try:
                    quantity_text = str(row[quantity_col]).strip()
                    quantity_text = quantity_text.replace(",", "").replace("'", "")
                    security["quantity"] = float(quantity_text)
                except (ValueError, TypeError):
                    pass
            
            # Only add if we have at least ISIN or description
            if security.get("isin") or security.get("description"):
                securities.append(security)
        
        return securities
    
    def _extract_securities_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract securities information from text."""
        securities = []
        
        # Look for ISIN patterns in the text
        import re
        isin_pattern = r'ISIN:?\s*([A-Z]{2}[A-Z0-9]{9}[0-9])'
        isin_matches = re.finditer(isin_pattern, text)
        
        for match in isin_matches:
            isin = match.group(1)
            
            # Get context around the ISIN (500 characters before and after)
            context_start = max(0, match.start() - 500)
            context_end = min(len(text), match.end() + 500)
            context = text[context_start:context_end]
            
            # Try to extract description
            desc_pattern = r'([A-Z][A-Z0-9\s\.\-\(\)]{5,50})'
            desc_match = re.search(desc_pattern, context[:match.start() - context_start])
            description = desc_match.group(1).strip() if desc_match else None
            
            # Try to extract valuation
            valuation_pattern = r'(\d{1,3}(?:[\',]\d{3})*(?:\.\d{1,2})?)'
            
            # Look for valuation in the context after the ISIN
            after_isin = context[match.end() - context_start:]
            valuation_matches = list(re.finditer(valuation_pattern, after_isin))
            
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
            
            # Create security object
            security = {
                "isin": isin,
                "description": description,
                "valuation": valuation,
                "extraction_method": "text_pattern"
            }
            
            # Only add if we have at least ISIN
            if security.get("isin"):
                securities.append(security)
        
        return securities
    
    def extract_portfolio_value(self, pdf_path: str) -> Optional[float]:
        """
        Extract the portfolio value from a financial document.
        
        Args:
            pdf_path: Path to the PDF file
        
        Returns:
            Portfolio value as a float, or None if not found
        """
        # Extract all content from the PDF
        extraction_result = self.extract(pdf_path)
        
        # Combine all text
        all_text = ""
        for source, text in extraction_result["text"].items():
            all_text += text + "\n\n"
        
        # Look for portfolio value patterns
        import re
        portfolio_value_patterns = [
            r'Portfolio\s+Total\s+(\d[\d,.\']*)',
            r'Total\s+assets\s+(\d[\d,.\']*)',
            r'Portfolio\s+Value\s*[:\s]+(\d[\d,.\']*)',
            r'Total\s+Value\s*[:\s]+(\d[\d,.\']*)',
            r'Total\s+Portfolio\s+Value\s*[:\s]+(\d[\d,.\']*)'
        ]
        
        for pattern in portfolio_value_patterns:
            match = re.search(pattern, all_text)
            if match:
                value_str = match.group(1).strip()
                value_str = value_str.replace("'", "").replace(",", "")
                try:
                    return float(value_str)
                except ValueError:
                    continue
        
        # If no match found, try to find it in tables
        for table in extraction_result["tables"]:
            for row in table.get("rows", []):
                for cell in row:
                    cell_text = str(cell).lower()
                    if any(term in cell_text for term in ["portfolio total", "total assets", "portfolio value"]):
                        # Look for a number in this row
                        for cell in row:
                            try:
                                value_str = str(cell).strip()
                                value_str = value_str.replace("'", "").replace(",", "")
                                value = float(value_str)
                                if value > 10000:  # Likely a portfolio value
                                    return value
                            except ValueError:
                                continue
        
        return None
