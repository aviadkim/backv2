"""
Multi-Document Processor - Processes and compares multiple financial documents.
"""
import os
import re
import json
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from simple_pdf_processor import SimplePDFProcessor

try:
    from report_generator import ReportGenerator
    REPORT_GENERATOR_AVAILABLE = True
except ImportError:
    REPORT_GENERATOR_AVAILABLE = False
    print("Report generator not available. Install required dependencies for report generation.")

class MultiDocumentProcessor:
    """
    Processor for multiple financial documents that can compare and analyze changes over time.
    """

    def __init__(self, use_ocr: bool = False, ocr_lang: str = 'en', use_llm: bool = False, api_key: Optional[str] = None):
        """
        Initialize the multi-document processor.

        Args:
            use_ocr: Whether to use OCR for text extraction (default: False)
            ocr_lang: Language code for OCR (default: 'en')
            use_llm: Whether to use LLM for question answering (default: False)
            api_key: API key for LLM service (default: None, uses environment variable)
        """
        self.documents = {}  # Dictionary to store processed documents
        self.document_dates = {}  # Dictionary to map document IDs to dates
        self.securities_db = {}  # Database of all securities across documents

        # Settings for the document processor
        self.use_ocr = use_ocr
        self.ocr_lang = ocr_lang
        self.use_llm = use_llm
        self.api_key = api_key

        # Create a document processor
        self.processor = SimplePDFProcessor(
            use_ocr=use_ocr,
            ocr_lang=ocr_lang,
            use_llm=use_llm,
            api_key=api_key
        )

    def add_document(self, doc_path: str, doc_id: Optional[str] = None, doc_date: Optional[str] = None,
                   output_dir: Optional[str] = None, force_ocr: bool = False) -> str:
        """
        Add a document to the processor.

        Args:
            doc_path: Path to the document
            doc_id: Optional ID for the document (default: None, uses filename)
            doc_date: Optional date for the document (default: None, extracted from document)
            output_dir: Optional directory to save output files (default: None)
            force_ocr: Whether to force OCR even if text extraction is possible (default: False)

        Returns:
            Document ID
        """
        # Generate document ID if not provided
        if doc_id is None:
            doc_id = os.path.basename(doc_path)

        # Create document-specific output directory if needed
        doc_output_dir = None
        if output_dir:
            doc_output_dir = os.path.join(output_dir, f"doc_{doc_id}")
            os.makedirs(doc_output_dir, exist_ok=True)

        # Process the document
        print(f"Processing document: {doc_path} (ID: {doc_id})")
        self.processor.process(doc_path, output_dir=doc_output_dir, force_ocr=force_ocr)

        # Store the processed data
        self.documents[doc_id] = self.processor.extracted_data.copy()

        # Store the full text for later use
        self.documents[doc_id]["full_text"] = self.processor.full_text

        # Get document date
        if doc_date is None:
            doc_date = self.processor.extracted_data.get("document_date")

        # Try to parse the date into a standard format
        parsed_date = self._parse_document_date(doc_date)

        # Store document date and metadata
        self.document_dates[doc_id] = parsed_date

        # Store additional metadata
        self.documents[doc_id]["metadata"] = {
            "file_path": doc_path,
            "file_name": os.path.basename(doc_path),
            "file_size": os.path.getsize(doc_path) if os.path.exists(doc_path) else None,
            "processing_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "client_info": self.processor.extracted_data.get("client_info", {}),
            "document_date": parsed_date,
            "original_date_string": doc_date
        }

        # Update securities database
        self._update_securities_db(doc_id)

        print(f"Document added: {doc_id} (Date: {parsed_date})")
        return doc_id

    def _parse_document_date(self, date_str: Optional[str]) -> Optional[str]:
        """
        Parse a document date string into a standard format (YYYY-MM-DD).

        Args:
            date_str: Date string to parse

        Returns:
            Parsed date string in YYYY-MM-DD format, or None if parsing fails
        """
        if not date_str:
            return None

        # Try different date formats
        date_formats = [
            "%d.%m.%Y",  # 31.12.2023
            "%Y-%m-%d",  # 2023-12-31
            "%m/%d/%Y",  # 12/31/2023
            "%d/%m/%Y",  # 31/12/2023
            "%Y/%m/%d",  # 2023/12/31
            "%b %d, %Y",  # Dec 31, 2023
            "%d %b %Y",  # 31 Dec 2023
            "%B %d, %Y",  # December 31, 2023
            "%d %B %Y"   # 31 December 2023
        ]

        for date_format in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, date_format)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

        # If all parsing attempts fail, return the original string
        return date_str

    def _update_securities_db(self, doc_id: str):
        """
        Update the securities database with data from a document.

        Args:
            doc_id: Document ID
        """
        if doc_id not in self.documents:
            return

        doc_data = self.documents[doc_id]
        doc_date = self.document_dates.get(doc_id)

        # Process bonds/securities
        for bond in doc_data.get("bonds", []):
            # Get ISIN and description
            isin = bond.get("isin")
            description = bond.get("description", "Unknown")

            # Try to find an existing security by ISIN or description
            security_id = self._find_matching_security(isin, description)

            # If no match found, create a new security ID
            if security_id is None:
                security_id = isin if isin else f"DESC:{self._normalize_description(description)}"

            # Initialize security in database if not exists
            if security_id not in self.securities_db:
                self.securities_db[security_id] = {
                    "isin": isin,
                    "description": description,
                    "values": {},
                    "currency": bond.get("currency"),
                    "maturity_date": bond.get("maturity_date"),
                    "alternative_descriptions": set([description]) if description else set(),
                    "first_seen": doc_date,
                    "last_seen": doc_date
                }
            else:
                # Update existing security
                security = self.securities_db[security_id]

                # Update alternative descriptions
                if description and description not in security["alternative_descriptions"]:
                    security["alternative_descriptions"].add(description)

                # Update last seen date
                if doc_date and (not security["last_seen"] or doc_date > security["last_seen"]):
                    security["last_seen"] = doc_date

            # Update security data for this document
            self.securities_db[security_id]["values"][doc_id] = {
                "date": doc_date,
                "nominal": bond.get("nominal"),
                "price": bond.get("price"),
                "valuation": bond.get("valuation"),
                "currency": bond.get("currency"),
                "maturity_date": bond.get("maturity_date")
            }

    def _find_matching_security(self, isin: Optional[str], description: Optional[str]) -> Optional[str]:
        """
        Find a matching security in the database by ISIN or description.

        Args:
            isin: ISIN of the security
            description: Description of the security

        Returns:
            Security ID if a match is found, None otherwise
        """
        # First, try to match by ISIN (most reliable)
        if isin:
            for security_id, security in self.securities_db.items():
                if security["isin"] == isin:
                    return security_id

        # If no ISIN match, try to match by description
        if description:
            normalized_desc = self._normalize_description(description)

            # Try exact match first
            for security_id, security in self.securities_db.items():
                if security["description"] == description:
                    return security_id

            # Try alternative descriptions
            for security_id, security in self.securities_db.items():
                if description in security["alternative_descriptions"]:
                    return security_id

            # Try normalized description match
            for security_id, security in self.securities_db.items():
                sec_desc = security["description"]
                if sec_desc and self._normalize_description(sec_desc) == normalized_desc:
                    return security_id

            # Try fuzzy matching if no exact match found
            best_match = None
            best_score = 0.7  # Minimum similarity threshold

            for security_id, security in self.securities_db.items():
                sec_desc = security["description"]
                if not sec_desc:
                    continue

                # Calculate similarity score
                score = self._description_similarity(normalized_desc, self._normalize_description(sec_desc))

                if score > best_score:
                    best_score = score
                    best_match = security_id

            return best_match

        return None

    def _normalize_description(self, description: str) -> str:
        """
        Normalize a security description for better matching.

        Args:
            description: Description to normalize

        Returns:
            Normalized description
        """
        if not description:
            return ""

        # Convert to uppercase
        normalized = description.upper()

        # Remove common words and characters that don't help with matching
        for word in ["LTD", "INC", "CORP", "CORPORATION", "COMPANY", "CO", "PLC", "AG", "SA", "NV", "BOND", "NOTE"]:
            normalized = re.sub(r'\b' + word + r'\b', "", normalized)

        # Remove punctuation and extra whitespace
        normalized = re.sub(r'[\.,\-\(\)\[\]\{\}\'\"\/\\]', " ", normalized)
        normalized = re.sub(r'\s+', " ", normalized).strip()

        return normalized

    def _description_similarity(self, desc1: str, desc2: str) -> float:
        """
        Calculate similarity between two security descriptions.

        Args:
            desc1: First description
            desc2: Second description

        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Simple word overlap similarity
        if not desc1 or not desc2:
            return 0.0

        words1 = set(desc1.split())
        words2 = set(desc2.split())

        if not words1 or not words2:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    def get_document_ids(self) -> List[str]:
        """
        Get a list of all document IDs.

        Returns:
            List of document IDs
        """
        return list(self.documents.keys())

    def get_document_dates(self) -> Dict[str, str]:
        """
        Get a dictionary mapping document IDs to dates.

        Returns:
            Dictionary mapping document IDs to dates
        """
        return self.document_dates.copy()

    def get_document_data(self, doc_id: str) -> Dict[str, Any]:
        """
        Get data for a specific document.

        Args:
            doc_id: Document ID

        Returns:
            Document data
        """
        return self.documents.get(doc_id, {}).copy()

    def get_securities(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the securities database.

        Returns:
            Securities database
        """
        return self.securities_db.copy()

    def compare_documents(self, doc_id1: str, doc_id2: str) -> Dict[str, Any]:
        """
        Compare two documents and return the differences.

        Args:
            doc_id1: First document ID
            doc_id2: Second document ID

        Returns:
            Dictionary containing the comparison results
        """
        # Check if both documents exist
        if doc_id1 not in self.documents or doc_id2 not in self.documents:
            return {"error": "One or both documents not found"}

        # Get document data
        doc1 = self.documents[doc_id1]
        doc2 = self.documents[doc_id2]

        # Get document dates
        date1 = self.document_dates.get(doc_id1, "Unknown")
        date2 = self.document_dates.get(doc_id2, "Unknown")

        # Initialize comparison results
        comparison = {
            "doc1_id": doc_id1,
            "doc2_id": doc_id2,
            "doc1_date": date1,
            "doc2_date": date2,
            "portfolio_value_change": {
                "value1": doc1.get("portfolio_value"),
                "value2": doc2.get("portfolio_value"),
                "absolute_change": None,
                "percentage_change": None
            },
            "asset_allocation_changes": {},
            "security_changes": []
        }

        # Calculate portfolio value change
        pv1 = doc1.get("portfolio_value")
        pv2 = doc2.get("portfolio_value")

        if pv1 is not None and pv2 is not None:
            absolute_change = pv2 - pv1
            percentage_change = (absolute_change / pv1) * 100 if pv1 != 0 else None

            comparison["portfolio_value_change"]["absolute_change"] = absolute_change
            comparison["portfolio_value_change"]["percentage_change"] = percentage_change

        # Compare asset allocation
        aa1 = doc1.get("asset_allocation", {})
        aa2 = doc2.get("asset_allocation", {})

        # Get all asset classes from both documents
        all_asset_classes = set(aa1.keys()) | set(aa2.keys())

        for asset_class in all_asset_classes:
            # Get asset class data
            ac1 = aa1.get(asset_class, {})
            ac2 = aa2.get(asset_class, {})

            # Get values and percentages
            value1 = ac1.get("value", 0)
            value2 = ac2.get("value", 0)
            percentage1 = ac1.get("percentage", 0)
            percentage2 = ac2.get("percentage", 0)

            # Calculate changes
            value_change = value2 - value1
            percentage_point_change = percentage2 - percentage1

            # Add to comparison results
            comparison["asset_allocation_changes"][asset_class] = {
                "value1": value1,
                "value2": value2,
                "value_change": value_change,
                "percentage1": percentage1,
                "percentage2": percentage2,
                "percentage_point_change": percentage_point_change
            }

        # Compare securities
        # Get all securities from both documents
        securities1 = {bond.get("isin", f"DESC:{bond.get('description')}"): bond for bond in doc1.get("bonds", [])}
        securities2 = {bond.get("isin", f"DESC:{bond.get('description')}"): bond for bond in doc2.get("bonds", [])}

        all_security_ids = set(securities1.keys()) | set(securities2.keys())

        for security_id in all_security_ids:
            # Get security data
            sec1 = securities1.get(security_id)
            sec2 = securities2.get(security_id)

            # Initialize security change
            security_change = {
                "security_id": security_id,
                "description": None,
                "isin": None,
                "in_doc1": sec1 is not None,
                "in_doc2": sec2 is not None,
                "valuation1": None,
                "valuation2": None,
                "valuation_change": None,
                "percentage_change": None
            }

            # Update security information
            if sec1:
                security_change["description"] = sec1.get("description")
                security_change["isin"] = sec1.get("isin")
                security_change["valuation1"] = sec1.get("valuation")

            if sec2:
                security_change["description"] = security_change["description"] or sec2.get("description")
                security_change["isin"] = security_change["isin"] or sec2.get("isin")
                security_change["valuation2"] = sec2.get("valuation")

            # Calculate valuation change
            val1 = security_change["valuation1"] or 0
            val2 = security_change["valuation2"] or 0

            security_change["valuation_change"] = val2 - val1
            security_change["percentage_change"] = (val2 - val1) / val1 * 100 if val1 != 0 else None

            # Add to comparison results
            comparison["security_changes"].append(security_change)

        # Sort security changes by absolute valuation change
        comparison["security_changes"].sort(key=lambda x: abs(x["valuation_change"] or 0), reverse=True)

        return comparison

    def _determine_chronological_order(self, date1: str, date2: str) -> str:
        """
        Determine the chronological order of two documents.

        Args:
            date1: Date of first document
            date2: Date of second document

        Returns:
            String indicating chronological order ('chronological', 'reverse_chronological', or 'unknown')
        """
        if date1 and date2:
            try:
                # Try to parse dates
                d1 = datetime.strptime(date1, "%Y-%m-%d") if isinstance(date1, str) else date1
                d2 = datetime.strptime(date2, "%Y-%m-%d") if isinstance(date2, str) else date2

                if d1 < d2:
                    return "chronological"
                elif d1 > d2:
                    return "reverse_chronological"
                else:
                    return "same_date"
            except (ValueError, TypeError):
                pass

        return "unknown"

    def _calculate_time_between(self, date1: str, date2: str) -> Optional[Dict[str, Any]]:
        """
        Calculate the time between two document dates.

        Args:
            date1: Date of first document
            date2: Date of second document

        Returns:
            Dictionary with time difference information, or None if dates can't be parsed
        """
        if date1 and date2:
            try:
                # Try to parse dates
                d1 = datetime.strptime(date1, "%Y-%m-%d") if isinstance(date1, str) else date1
                d2 = datetime.strptime(date2, "%Y-%m-%d") if isinstance(date2, str) else date2

                # Calculate difference
                diff = abs((d2 - d1).days)

                return {
                    "days": diff,
                    "months": round(diff / 30.44, 1),  # Approximate months
                    "years": round(diff / 365.25, 2)   # Approximate years
                }
            except (ValueError, TypeError):
                pass

        return None

    def _compare_portfolio_summary(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare portfolio summary between two documents.

        Args:
            doc1: First document data
            doc2: Second document data

        Returns:
            Dictionary with portfolio summary comparison
        """
        # Get portfolio values
        pv1 = doc1.get("portfolio_value")
        pv2 = doc2.get("portfolio_value")

        summary = {
            "value1": pv1,
            "value2": pv2,
            "absolute_change": None,
            "percentage_change": None,
            "annualized_return": None
        }

        if pv1 is not None and pv2 is not None:
            absolute_change = pv2 - pv1
            percentage_change = (absolute_change / pv1) * 100 if pv1 != 0 else None

            summary["absolute_change"] = absolute_change
            summary["percentage_change"] = percentage_change

            # Calculate annualized return if we have dates
            date1 = doc1.get("metadata", {}).get("document_date")
            date2 = doc2.get("metadata", {}).get("document_date")

            if date1 and date2 and percentage_change is not None:
                time_between = self._calculate_time_between(date1, date2)
                if time_between and time_between["years"] > 0:
                    years = time_between["years"]
                    annualized_return = ((1 + percentage_change/100) ** (1/years) - 1) * 100
                    summary["annualized_return"] = annualized_return

        return summary

    def _compare_asset_allocation(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare asset allocation between two documents.

        Args:
            doc1: First document data
            doc2: Second document data

        Returns:
            Dictionary with asset allocation comparison
        """
        # Get asset allocations
        aa1 = doc1.get("asset_allocation", {})
        aa2 = doc2.get("asset_allocation", {})

        # Get all asset classes from both documents
        all_asset_classes = set(aa1.keys()) | set(aa2.keys())

        # Initialize result
        result = {}

        for asset_class in all_asset_classes:
            # Get asset class data
            ac1 = aa1.get(asset_class, {})
            ac2 = aa2.get(asset_class, {})

            # Get values and percentages
            value1 = ac1.get("value", 0) or 0
            value2 = ac2.get("value", 0) or 0
            percentage1 = ac1.get("percentage", 0) or 0
            percentage2 = ac2.get("percentage", 0) or 0

            # Calculate changes
            value_change = value2 - value1
            percentage_point_change = percentage2 - percentage1
            value_percentage_change = (value_change / value1 * 100) if value1 != 0 else None

            # Add to result
            result[asset_class] = {
                "value1": value1,
                "value2": value2,
                "value_change": value_change,
                "value_percentage_change": value_percentage_change,
                "percentage1": percentage1,
                "percentage2": percentage2,
                "percentage_point_change": percentage_point_change,
                "sub_classes": {}
            }

            # Compare sub-classes
            sub_classes1 = ac1.get("sub_classes", {})
            sub_classes2 = ac2.get("sub_classes", {})

            all_sub_classes = set(sub_classes1.keys()) | set(sub_classes2.keys())

            for sub_class in all_sub_classes:
                sc1 = sub_classes1.get(sub_class, {})
                sc2 = sub_classes2.get(sub_class, {})

                sub_value1 = sc1.get("value", 0) or 0
                sub_value2 = sc2.get("value", 0) or 0
                sub_percentage1 = sc1.get("percentage", 0) or 0
                sub_percentage2 = sc2.get("percentage", 0) or 0

                sub_value_change = sub_value2 - sub_value1
                sub_percentage_point_change = sub_percentage2 - sub_percentage1
                sub_value_percentage_change = (sub_value_change / sub_value1 * 100) if sub_value1 != 0 else None

                result[asset_class]["sub_classes"][sub_class] = {
                    "value1": sub_value1,
                    "value2": sub_value2,
                    "value_change": sub_value_change,
                    "value_percentage_change": sub_value_percentage_change,
                    "percentage1": sub_percentage1,
                    "percentage2": sub_percentage2,
                    "percentage_point_change": sub_percentage_point_change
                }

        return result

    def _compare_securities(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Compare securities between two documents.

        Args:
            doc1: First document data
            doc2: Second document data

        Returns:
            List of dictionaries with security comparisons
        """
        # Get securities from both documents
        bonds1 = doc1.get("bonds", [])
        bonds2 = doc2.get("bonds", [])

        # Create dictionaries for easier lookup
        securities1 = {}
        securities2 = {}

        # Process securities from document 1
        for bond in bonds1:
            isin = bond.get("isin")
            description = bond.get("description")

            # Create a unique identifier
            if isin:
                security_id = isin
            elif description:
                security_id = f"DESC:{self._normalize_description(description)}"
            else:
                continue  # Skip securities without ISIN or description

            securities1[security_id] = bond

        # Process securities from document 2
        for bond in bonds2:
            isin = bond.get("isin")
            description = bond.get("description")

            # Create a unique identifier
            if isin:
                security_id = isin
            elif description:
                security_id = f"DESC:{self._normalize_description(description)}"
            else:
                continue  # Skip securities without ISIN or description

            securities2[security_id] = bond

        # Get all security IDs
        all_security_ids = set(securities1.keys()) | set(securities2.keys())

        # Compare securities
        result = []

        for security_id in all_security_ids:
            sec1 = securities1.get(security_id)
            sec2 = securities2.get(security_id)

            # Initialize security change
            security_change = {
                "security_id": security_id,
                "description": None,
                "isin": None,
                "in_doc1": sec1 is not None,
                "in_doc2": sec2 is not None,
                "valuation1": None,
                "valuation2": None,
                "nominal1": None,
                "nominal2": None,
                "price1": None,
                "price2": None,
                "currency": None,
                "maturity_date": None,
                "valuation_change": None,
                "percentage_change": None,
                "nominal_change": None,
                "price_change": None
            }

            # Update security information
            if sec1:
                security_change["description"] = sec1.get("description")
                security_change["isin"] = sec1.get("isin")
                security_change["valuation1"] = sec1.get("valuation")
                security_change["nominal1"] = sec1.get("nominal")
                security_change["price1"] = sec1.get("price")
                security_change["currency"] = sec1.get("currency")
                security_change["maturity_date"] = sec1.get("maturity_date")

            if sec2:
                security_change["description"] = security_change["description"] or sec2.get("description")
                security_change["isin"] = security_change["isin"] or sec2.get("isin")
                security_change["valuation2"] = sec2.get("valuation")
                security_change["nominal2"] = sec2.get("nominal")
                security_change["price2"] = sec2.get("price")
                security_change["currency"] = security_change["currency"] or sec2.get("currency")
                security_change["maturity_date"] = security_change["maturity_date"] or sec2.get("maturity_date")

            # Calculate changes
            val1 = security_change["valuation1"] or 0
            val2 = security_change["valuation2"] or 0
            nom1 = security_change["nominal1"] or 0
            nom2 = security_change["nominal2"] or 0
            price1 = security_change["price1"] or 0
            price2 = security_change["price2"] or 0

            security_change["valuation_change"] = val2 - val1
            security_change["percentage_change"] = (val2 - val1) / val1 * 100 if val1 != 0 else None
            security_change["nominal_change"] = nom2 - nom1
            security_change["price_change"] = price2 - price1
            security_change["price_percentage_change"] = (price2 - price1) / price1 * 100 if price1 != 0 else None

            # Add to result
            result.append(security_change)

        # Sort by absolute valuation change
        result.sort(key=lambda x: abs(x["valuation_change"] or 0), reverse=True)

        return result

    def _calculate_performance_metrics(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate performance metrics between two documents.

        Args:
            doc1: First document data
            doc2: Second document data

        Returns:
            Dictionary with performance metrics
        """
        # Get portfolio values
        pv1 = doc1.get("portfolio_value")
        pv2 = doc2.get("portfolio_value")

        # Initialize metrics
        metrics = {
            "total_return": None,
            "annualized_return": None,
            "volatility": None,
            "sharpe_ratio": None,
            "asset_class_contribution": {},
            "risk_metrics": {
                "max_drawdown": None,
                "value_at_risk": None
            }
        }

        # Calculate total return
        if pv1 is not None and pv2 is not None and pv1 != 0:
            total_return = (pv2 - pv1) / pv1 * 100
            metrics["total_return"] = total_return

            # Calculate annualized return if we have dates
            date1 = doc1.get("metadata", {}).get("document_date")
            date2 = doc2.get("metadata", {}).get("document_date")

            if date1 and date2:
                time_between = self._calculate_time_between(date1, date2)
                if time_between and time_between["years"] > 0:
                    years = time_between["years"]
                    annualized_return = ((1 + total_return/100) ** (1/years) - 1) * 100
                    metrics["annualized_return"] = annualized_return

        # Calculate asset class contribution to return
        aa1 = doc1.get("asset_allocation", {})
        aa2 = doc2.get("asset_allocation", {})

        for asset_class in set(aa1.keys()) | set(aa2.keys()):
            ac1 = aa1.get(asset_class, {})
            ac2 = aa2.get(asset_class, {})

            value1 = ac1.get("value", 0)
            value2 = ac2.get("value", 0)

            if pv1 and value1:
                # Calculate contribution to total return
                weight1 = value1 / pv1
                if value1 != 0:
                    asset_return = (value2 - value1) / value1 * 100
                    contribution = weight1 * asset_return / 100

                    metrics["asset_class_contribution"][asset_class] = {
                        "weight": weight1 * 100,  # as percentage
                        "return": asset_return,
                        "contribution": contribution * 100  # as percentage points
                    }

        return metrics

    def enhanced_compare_documents(self, doc_id1: str, doc_id2: str) -> Dict[str, Any]:
        """
        Compare two documents and return the differences with enhanced analytics.

        Args:
            doc_id1: First document ID
            doc_id2: Second document ID

        Returns:
            Dictionary containing the comparison results
        """
        # Check if both documents exist
        if doc_id1 not in self.documents or doc_id2 not in self.documents:
            return {"error": "One or both documents not found"}

        # Get document data
        doc1 = self.documents[doc_id1]
        doc2 = self.documents[doc_id2]

        # Get document dates
        date1 = self.document_dates.get(doc_id1, "Unknown")
        date2 = self.document_dates.get(doc_id2, "Unknown")

        # Determine chronological order
        chronological_order = self._determine_chronological_order(date1, date2)

        # Initialize comparison results
        comparison = {
            "doc1_id": doc_id1,
            "doc2_id": doc_id2,
            "doc1_date": date1,
            "doc2_date": date2,
            "chronological_order": chronological_order,
            "time_between_documents": self._calculate_time_between(date1, date2),
            "portfolio_summary": self._compare_portfolio_summary(doc1, doc2),
            "asset_allocation_changes": self._compare_asset_allocation(doc1, doc2),
            "security_changes": self._compare_securities(doc1, doc2),
            "new_securities": [],
            "removed_securities": [],
            "top_gainers": [],
            "top_losers": []
        }

        # Extract new and removed securities
        for security in comparison["security_changes"]:
            if security["in_doc1"] and not security["in_doc2"]:
                comparison["removed_securities"].append(security)
            elif not security["in_doc1"] and security["in_doc2"]:
                comparison["new_securities"].append(security)

        # Extract top gainers and losers (only securities present in both documents)
        both_docs_securities = [s for s in comparison["security_changes"] if s["in_doc1"] and s["in_doc2"]]

        # Sort by percentage change
        gainers = sorted([s for s in both_docs_securities if (s["percentage_change"] or 0) > 0],
                         key=lambda x: x["percentage_change"] or 0, reverse=True)
        losers = sorted([s for s in both_docs_securities if (s["percentage_change"] or 0) < 0],
                        key=lambda x: x["percentage_change"] or 0)

        comparison["top_gainers"] = gainers[:10]  # Top 10 gainers
        comparison["top_losers"] = losers[:10]    # Top 10 losers

        # Calculate performance metrics
        comparison["performance_metrics"] = self._calculate_performance_metrics(doc1, doc2)

        return comparison

    def generate_comparison_report(self, doc_id1: str, doc_id2: str, output_dir: str,
                                 format: str = "html") -> Dict[str, str]:
        """
        Generate a report from comparison data.

        Args:
            doc_id1: First document ID
            doc_id2: Second document ID
            output_dir: Directory to save the report
            format: Report format ("html", "csv", or "all")

        Returns:
            Dictionary mapping report types to file paths
        """
        # Check if report generator is available
        if not REPORT_GENERATOR_AVAILABLE:
            print("Report generator not available. Install required dependencies for report generation.")
            return {}

        # Check if both documents exist
        if doc_id1 not in self.documents or doc_id2 not in self.documents:
            print("Error: One or both documents not found")
            return {}

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Generate comparison data
        comparison = self.enhanced_compare_documents(doc_id1, doc_id2)

        # Save comparison data to JSON
        comparison_path = os.path.join(output_dir, f"comparison_{doc_id1}_vs_{doc_id2}.json")
        with open(comparison_path, "w", encoding="utf-8") as f:
            json.dump(comparison, f, indent=2)

        # Create report generator
        generator = ReportGenerator()

        # Generate reports
        report_paths = {"json": comparison_path}

        if format in ["html", "all"]:
            html_path = os.path.join(output_dir, f"comparison_{doc_id1}_vs_{doc_id2}.html")
            generator.generate_html_report(comparison, html_path)
            report_paths["html"] = html_path

        if format in ["csv", "all"]:
            csv_dir = os.path.join(output_dir, f"csv_{doc_id1}_vs_{doc_id2}")
            csv_paths = generator.export_to_csv(comparison, csv_dir)
            report_paths["csv"] = csv_paths

        if format in ["pdf", "all"] and hasattr(generator, "generate_pdf_report"):
            pdf_path = os.path.join(output_dir, f"comparison_{doc_id1}_vs_{doc_id2}.pdf")
            pdf_result = generator.generate_pdf_report(comparison, pdf_path)
            if pdf_result:
                report_paths["pdf"] = pdf_result

        print(f"Reports generated in: {output_dir}")
        return report_paths

    def save_to_json(self, output_path: str):
        """
        Save all document data to a JSON file.

        Args:
            output_path: Path to save the JSON file
        """
        # Convert sets to lists for JSON serialization
        documents_copy = {}
        for doc_id, doc_data in self.documents.items():
            documents_copy[doc_id] = self._prepare_for_json(doc_data)

        securities_db_copy = {}
        for sec_id, sec_data in self.securities_db.items():
            securities_db_copy[sec_id] = self._prepare_for_json(sec_data)

        data = {
            "documents": documents_copy,
            "document_dates": self.document_dates,
            "securities_db": securities_db_copy
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"Data saved to: {output_path}")

    def _prepare_for_json(self, obj):
        """
        Prepare an object for JSON serialization by converting sets to lists.

        Args:
            obj: Object to prepare

        Returns:
            JSON-serializable object
        """
        if isinstance(obj, dict):
            return {k: self._prepare_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._prepare_for_json(item) for item in obj]
        elif isinstance(obj, set):
            return list(obj)
        else:
            return obj

    def load_from_json(self, input_path: str):
        """
        Load document data from a JSON file.

        Args:
            input_path: Path to the JSON file
        """
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.documents = data.get("documents", {})
        self.document_dates = data.get("document_dates", {})
        self.securities_db = data.get("securities_db", {})

        print(f"Data loaded from: {input_path}")

def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Process and compare multiple financial documents.")
    parser.add_argument("--documents", nargs="+", help="Paths to financial documents")
    parser.add_argument("--output-dir", help="Directory to save output files")
    parser.add_argument("--compare", nargs=2, help="Compare two documents (provide document IDs)")
    parser.add_argument("--save-json", help="Save data to JSON file")
    parser.add_argument("--load-json", help="Load data from JSON file")
    parser.add_argument("--use-ocr", action="store_true", help="Use OCR for text extraction")
    parser.add_argument("--ocr-lang", default="en", help="Language code for OCR (default: en)")
    parser.add_argument("--use-llm", action="store_true", help="Use LLM for question answering")
    parser.add_argument("--api-key", help="API key for LLM service")
    parser.add_argument("--generate-report", action="store_true", help="Generate a report from comparison data")
    parser.add_argument("--report-format", choices=["html", "csv", "pdf", "all"], default="all", help="Report format")

    args = parser.parse_args()

    # Create output directory if specified
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)

    # Create processor
    processor = MultiDocumentProcessor(
        use_ocr=args.use_ocr,
        ocr_lang=args.ocr_lang,
        use_llm=args.use_llm,
        api_key=args.api_key
    )

    # Load data from JSON if specified
    if args.load_json:
        processor.load_from_json(args.load_json)

    # Process documents if specified
    if args.documents:
        for doc_path in args.documents:
            if os.path.exists(doc_path):
                processor.add_document(doc_path)
            else:
                print(f"Error: Document not found: {doc_path}")

    # Save data to JSON if specified
    if args.save_json:
        processor.save_to_json(args.save_json)

    # Compare documents if specified
    if args.compare and len(args.compare) == 2:
        doc_id1, doc_id2 = args.compare

        if doc_id1 in processor.get_document_ids() and doc_id2 in processor.get_document_ids():
            comparison = processor.enhanced_compare_documents(doc_id1, doc_id2)

            # Print comparison results
            print("\nDocument Comparison:")
            print(f"Document 1: {doc_id1} ({comparison['doc1_date']})")
            print(f"Document 2: {doc_id2} ({comparison['doc2_date']})")

            # Time between documents
            time_between = comparison.get("time_between_documents")
            if time_between:
                print(f"Time between documents: {time_between['days']} days ({time_between['months']} months, {time_between['years']:.2f} years)")

            # Chronological order
            order = comparison.get("chronological_order")
            if order and order != "unknown":
                if order == "chronological":
                    print("Documents are in chronological order (Document 1 is older)")
                elif order == "reverse_chronological":
                    print("Documents are in reverse chronological order (Document 2 is older)")
                elif order == "same_date":
                    print("Documents have the same date")

            # Portfolio summary
            portfolio = comparison.get("portfolio_summary", {})
            print("\nPortfolio Summary:")
            print(f"Document 1: ${portfolio.get('value1', 0):,.2f}")
            print(f"Document 2: ${portfolio.get('value2', 0):,.2f}")

            if portfolio.get("absolute_change") is not None:
                print(f"Absolute Change: ${portfolio['absolute_change']:,.2f}")

                if portfolio.get("percentage_change") is not None:
                    print(f"Percentage Change: {portfolio['percentage_change']:.2f}%")

                if portfolio.get("annualized_return") is not None:
                    print(f"Annualized Return: {portfolio['annualized_return']:.2f}%")

            # Performance metrics
            metrics = comparison.get("performance_metrics", {})
            if metrics:
                print("\nPerformance Metrics:")
                if metrics.get("total_return") is not None:
                    print(f"Total Return: {metrics['total_return']:.2f}%")
                if metrics.get("annualized_return") is not None:
                    print(f"Annualized Return: {metrics['annualized_return']:.2f}%")

                # Asset class contribution
                contributions = metrics.get("asset_class_contribution", {})
                if contributions:
                    print("\nAsset Class Contribution to Return:")
                    for asset_class, data in contributions.items():
                        print(f"{asset_class}:")
                        print(f"  Weight: {data.get('weight', 0):.2f}%")
                        print(f"  Return: {data.get('return', 0):.2f}%")
                        print(f"  Contribution: {data.get('contribution', 0):.2f}%")

            # Asset allocation changes
            print("\nAsset Allocation Changes:")
            for asset_class, change in comparison["asset_allocation_changes"].items():
                print(f"{asset_class}:")
                print(f"  Document 1: ${change['value1']:,.2f} ({change['percentage1']:.2f}%)")
                print(f"  Document 2: ${change['value2']:,.2f} ({change['percentage2']:.2f}%)")
                print(f"  Value Change: ${change['value_change']:,.2f}")

                if change.get("value_percentage_change") is not None:
                    print(f"  Value Percentage Change: {change['value_percentage_change']:.2f}%")

                print(f"  Percentage Point Change: {change['percentage_point_change']:.2f}%")

            # New securities
            if comparison["new_securities"]:
                print("\nNew Securities:")
                for i, security in enumerate(comparison["new_securities"][:5], 1):
                    print(f"{i}. {security['description']} ({security['isin'] or 'No ISIN'}):")
                    print(f"  Valuation: ${security['valuation2']:,.2f}")

            # Removed securities
            if comparison["removed_securities"]:
                print("\nRemoved Securities:")
                for i, security in enumerate(comparison["removed_securities"][:5], 1):
                    print(f"{i}. {security['description']} ({security['isin'] or 'No ISIN'}):")
                    print(f"  Valuation: ${security['valuation1']:,.2f}")

            # Top gainers
            if comparison["top_gainers"]:
                print("\nTop Gainers:")
                for i, security in enumerate(comparison["top_gainers"][:5], 1):
                    print(f"{i}. {security['description']} ({security['isin'] or 'No ISIN'}):")
                    print(f"  Document 1: ${security['valuation1']:,.2f}")
                    print(f"  Document 2: ${security['valuation2']:,.2f}")
                    print(f"  Change: ${security['valuation_change']:,.2f} ({security['percentage_change']:.2f}%)")

            # Top losers
            if comparison["top_losers"]:
                print("\nTop Losers:")
                for i, security in enumerate(comparison["top_losers"][:5], 1):
                    print(f"{i}. {security['description']} ({security['isin'] or 'No ISIN'}):")
                    print(f"  Document 1: ${security['valuation1']:,.2f}")
                    print(f"  Document 2: ${security['valuation2']:,.2f}")
                    print(f"  Change: ${security['valuation_change']:,.2f} ({security['percentage_change']:.2f}%)")

            # Generate report if requested
            if args.generate_report and args.output_dir:
                report_dir = os.path.join(args.output_dir, f"reports_{doc_id1}_vs_{doc_id2}")
                report_paths = processor.generate_comparison_report(
                    doc_id1, doc_id2, report_dir, format=args.report_format
                )

                # Print report paths
                print("\nGenerated reports:")
                for report_type, path in report_paths.items():
                    if isinstance(path, list):
                        print(f"  {report_type.upper()} reports:")
                        for p in path:
                            print(f"    - {p}")
                    else:
                        print(f"  {report_type.upper()} report: {path}")
            # Save comparison results if output directory is specified and report not generated
            elif args.output_dir:
                comparison_path = os.path.join(args.output_dir, f"comparison_{doc_id1}_vs_{doc_id2}.json")
                with open(comparison_path, "w", encoding="utf-8") as f:
                    json.dump(comparison, f, indent=2)
                print(f"\nComparison results saved to: {comparison_path}")
        else:
            print("Error: One or both document IDs not found")

    return 0

if __name__ == "__main__":
    main()
