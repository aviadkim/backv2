"""
Simple PDF Processor - Extracts text and tables from PDFs using pdfplumber.
"""
import os
import re
import json
import pandas as pd
import pdfplumber
from typing import Dict, List, Any, Optional

try:
    from ocr_processor import OCRProcessor
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("OCR processor not available. Install required dependencies for OCR support.")

try:
    from llm_question_answerer import LLMQuestionAnswerer
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("LLM question answerer not available. Install required dependencies for advanced question answering.")

class SimplePDFProcessor:
    """
    Simple processor for PDF documents that extracts text and tables.
    """

    def __init__(self, use_ocr: bool = False, ocr_lang: str = 'en', use_llm: bool = False, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """Initialize the PDF processor.

        Args:
            use_ocr: Whether to use OCR for text extraction (default: False)
            ocr_lang: Language code for OCR (default: 'en')
            use_llm: Whether to use LLM for question answering (default: False)
            api_key: API key for LLM service (default: None, uses environment variable)
            model: Model to use for LLM (default: gpt-4o-mini)
        """
        self.extracted_data = {
            "bonds": [],
            "asset_allocation": {},
            "portfolio_value": None,
            "client_info": {},
            "document_date": None
        }
        self.full_text = ""
        self.tables = []

        # OCR settings
        self.use_ocr = use_ocr and OCR_AVAILABLE
        self.ocr_lang = ocr_lang
        self.ocr_processor = OCRProcessor(lang=ocr_lang) if self.use_ocr else None

        # LLM settings
        self.use_llm = use_llm and LLM_AVAILABLE
        self.api_key = api_key
        self.model = model
        self.llm_answerer = LLMQuestionAnswerer(api_key=api_key, model=model) if self.use_llm else None

    def process(self, pdf_path: str, output_dir: Optional[str] = None, force_ocr: bool = False) -> Dict[str, Any]:
        """
        Process a PDF document to extract text and tables.

        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save output files (default: None)
            force_ocr: Whether to force OCR even if text extraction is possible (default: False)

        Returns:
            Dict containing extracted data
        """
        print(f"Processing document: {pdf_path}")

        # Reset data
        self.extracted_data = {
            "bonds": [],
            "asset_allocation": {},
            "portfolio_value": None,
            "client_info": {},
            "document_date": None
        }
        self.full_text = ""
        self.tables = []

        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Try standard text extraction first
        use_ocr = force_ocr or self.use_ocr
        standard_extraction_failed = False

        if not use_ocr:
            try:
                self._extract_with_pdfplumber(pdf_path)

                # Check if we got enough text
                if len(self.full_text) < 100:  # If we got very little text, try OCR
                    print("Standard text extraction yielded minimal text. Trying OCR...")
                    standard_extraction_failed = True
                    use_ocr = OCR_AVAILABLE
            except Exception as e:
                print(f"Error with standard text extraction: {str(e)}")
                standard_extraction_failed = True
                use_ocr = OCR_AVAILABLE

        # Use OCR if needed and available
        if use_ocr and OCR_AVAILABLE:
            if self.ocr_processor is None:
                self.ocr_processor = OCRProcessor(lang=self.ocr_lang)

            try:
                print("Using OCR for text extraction...")
                self._extract_with_ocr(pdf_path, output_dir)
            except Exception as e:
                print(f"Error with OCR extraction: {str(e)}")
                # If OCR failed and we haven't tried standard extraction yet, try it now
                if standard_extraction_failed:
                    print("Falling back to standard text extraction...")
                    self._extract_with_pdfplumber(pdf_path)

        # Extract structured data
        self._extract_client_info()
        self._extract_document_date()
        self._extract_portfolio_value()
        self._extract_bonds()
        self._extract_asset_allocation()

        # Save the extracted data if output_dir is specified
        if output_dir:
            self._save_results(output_dir)

        print("Document processing completed.")
        return self.extracted_data

    def _extract_with_pdfplumber(self, pdf_path: str):
        """Extract text and tables using pdfplumber."""
        with pdfplumber.open(pdf_path) as pdf:
            # Process each page
            for i, page in enumerate(pdf.pages):
                print(f"Processing page {i+1}/{len(pdf.pages)} with pdfplumber")

                # Extract text from the page
                text = page.extract_text()
                if text:
                    self.full_text += text + "\n\n"

                # Extract tables from the page
                tables = page.extract_tables()
                if tables:
                    self.tables.extend(tables)

    def _extract_with_ocr(self, pdf_path: str, output_dir: Optional[str] = None):
        """Extract text using OCR."""
        # Process the PDF with OCR
        results = self.ocr_processor.process_pdf(pdf_path, output_dir=output_dir)

        # Combine all pages into a single text
        self.full_text = "\n\n".join(results.values())

        # Extract tables from the OCR text (this is more challenging)
        # For now, we'll rely on pattern matching in the text extraction methods

    def _extract_client_info(self):
        """Extract client information."""
        # Look for client name
        client_match = re.search(r'([A-Z\s]+LTD\.)', self.full_text)
        if client_match:
            self.extracted_data["client_info"]["name"] = client_match.group(1).strip()

        # Look for client number
        client_num_match = re.search(r'Client\s+Number[:\s]+(\d+)', self.full_text)
        if client_num_match:
            self.extracted_data["client_info"]["number"] = client_num_match.group(1).strip()

        print(f"Client info: {self.extracted_data['client_info']}")

    def _extract_document_date(self):
        """Extract document date."""
        date_match = re.search(r'Valuation\s+as\s+of\s+(\d{2}\.\d{2}\.\d{4})', self.full_text)
        if date_match:
            self.extracted_data["document_date"] = date_match.group(1).strip()
            print(f"Document date: {self.extracted_data['document_date']}")

    def _extract_portfolio_value(self):
        """Extract portfolio value."""
        # Look for portfolio value in text
        portfolio_value_patterns = [
            r'Total\s+assets\s*[:\s]+(\d[\d,.\']*)',
            r'Portfolio\s+Total\s*[:\s]+(\d[\d,.\']*)',
            r'Total\s+assets\s*[\|\:]?\s*(\d[\d,.\']*)',
            r'Portfolio\s+Value\s*[\|\:]?\s*(\d[\d,.\']*)'
        ]

        for pattern in portfolio_value_patterns:
            match = re.search(pattern, self.full_text)
            if match:
                value_str = match.group(1).strip()
                value = self._clean_number(value_str)
                if value:
                    self.extracted_data["portfolio_value"] = value
                    print(f"Portfolio value: {value}")
                    break

    def _extract_bonds(self):
        """Extract bonds from tables and text."""
        # First, try to extract bonds from tables
        self._extract_bonds_from_tables()

        # If no bonds were found in tables, try to extract from text
        if not self.extracted_data["bonds"]:
            self._extract_bonds_from_text()

        print(f"Extracted {len(self.extracted_data['bonds'])} bonds")

    def _extract_bonds_from_tables(self):
        """Extract bonds from tables."""
        for table in self.tables:
            # Skip empty tables
            if not table or len(table) <= 1:
                continue

            # Convert table to DataFrame
            df = pd.DataFrame(table)

            # Check if this is a bonds table
            header_row = df.iloc[0] if not df.empty else []
            bond_headers = ['Currency', 'Nominal', 'Description', 'ISIN', 'Maturity', 'Valuation', 'Price']

            # Check if this looks like a bonds table
            is_bond_table = any(any(header in str(cell) for cell in header_row) for header in bond_headers)

            # Also check if the table contains "Bonds" in any cell
            contains_bonds = any("Bonds" in str(cell) for row in df.values for cell in row if cell)

            if is_bond_table or contains_bonds:
                # This is likely a bonds table
                # Clean the DataFrame
                df = self._clean_dataframe(df)

                # Map column indices to their meanings
                column_indices = {}
                for i, cell in enumerate(header_row):
                    if not cell:
                        continue

                    cell_lower = str(cell).lower()

                    if 'currency' in cell_lower:
                        column_indices['currency'] = i
                    elif 'nominal' in cell_lower or 'quantity' in cell_lower:
                        column_indices['nominal'] = i
                    elif 'description' in cell_lower or 'security' in cell_lower:
                        column_indices['description'] = i
                    elif 'price' in cell_lower and 'actual' in cell_lower:
                        column_indices['price'] = i
                    elif 'valuation' in cell_lower or 'value' in cell_lower or 'countervalue' in cell_lower:
                        column_indices['valuation'] = i
                    elif 'isin' in cell_lower:
                        column_indices['isin'] = i
                    elif 'maturity' in cell_lower:
                        column_indices['maturity_date'] = i

                # If we couldn't identify essential columns but this is a bonds section,
                # try to infer column positions based on typical layout
                if not column_indices and contains_bonds and len(df.columns) >= 3:
                    # Typical layout: Currency, Nominal, Description, Price, Valuation
                    if len(df.columns) >= 5:
                        column_indices = {
                            'currency': 0,
                            'nominal': 1,
                            'description': 2,
                            'price': 3,
                            'valuation': 4
                        }

                # Extract bonds from data rows
                for i in range(1, len(df)):
                    row = df.iloc[i]

                    # Skip empty rows
                    if all(pd.isna(cell) or str(cell).strip() == "" for cell in row):
                        continue

                    # Create bond object
                    bond = {}

                    # Check if this row contains an ISIN
                    row_str = " ".join(str(cell) for cell in row if not pd.isna(cell))
                    isin_match = re.search(r'ISIN:\s*([A-Z0-9]{12})', row_str)
                    if isin_match:
                        bond['isin'] = isin_match.group(1).strip()

                    # Extract data from mapped columns
                    for field, col_idx in column_indices.items():
                        if col_idx < len(row) and not pd.isna(row[col_idx]) and str(row[col_idx]).strip() != "":
                            if field in ['nominal', 'price', 'valuation']:
                                bond[field] = self._clean_number(row[col_idx])
                            else:
                                bond[field] = str(row[col_idx]).strip()

                    # If we have a description but no ISIN, try to extract ISIN from description
                    if 'description' in bond and 'isin' not in bond:
                        isin_match = re.search(r'ISIN:\s*([A-Z0-9]{12})', bond['description'])
                        if isin_match:
                            bond['isin'] = isin_match.group(1).strip()

                    # If we have a description with maturity info but no maturity date, extract it
                    if 'description' in bond and 'maturity_date' not in bond:
                        maturity_match = re.search(r'Maturity:\s*(\d{2}\.\d{2}\.\d{4})', bond['description'])
                        if maturity_match:
                            bond['maturity_date'] = maturity_match.group(1).strip()

                    # Only add bonds with at least description and valuation or ISIN
                    has_description = 'description' in bond and bond['description']
                    has_valuation = 'valuation' in bond and bond['valuation'] is not None
                    has_isin = 'isin' in bond and bond['isin']

                    if (has_description and has_valuation) or has_isin:
                        # Check if this bond already exists (by ISIN)
                        if has_isin:
                            existing_bond = next((b for b in self.extracted_data["bonds"] if b.get('isin') == bond['isin']), None)
                            if existing_bond:
                                # Update existing bond with any new information
                                for key, value in bond.items():
                                    if key not in existing_bond or not existing_bond[key]:
                                        existing_bond[key] = value
                            else:
                                self.extracted_data["bonds"].append(bond)
                        else:
                            self.extracted_data["bonds"].append(bond)

    def _extract_bonds_from_text(self):
        """Extract bonds from text using pattern matching."""
        # Look for bond sections in the text
        bond_sections = re.split(r'Bonds|Structured products', self.full_text)

        if len(bond_sections) > 1:
            # Process each bond section
            for section in bond_sections[1:]:  # Skip the first section (before "Bonds")
                # Look for ISIN patterns
                isin_matches = re.finditer(r'ISIN:\s*([A-Z0-9]{12})', section)

                for isin_match in isin_matches:
                    isin = isin_match.group(1).strip()

                    # Find the context around this ISIN (up to 10 lines)
                    start_pos = max(0, isin_match.start() - 500)
                    end_pos = min(len(section), isin_match.end() + 500)
                    context = section[start_pos:end_pos]

                    # Create a bond object
                    bond = {'isin': isin}

                    # Extract description (usually before ISIN)
                    desc_match = re.search(r'([A-Z][A-Z0-9\s\.\-\(\)]+)(?=.*ISIN)', context)
                    if desc_match:
                        bond['description'] = desc_match.group(1).strip()

                    # Extract maturity date
                    maturity_match = re.search(r'Maturity:\s*(\d{2}\.\d{2}\.\d{4})', context)
                    if maturity_match:
                        bond['maturity_date'] = maturity_match.group(1).strip()

                    # Extract currency
                    currency_match = re.search(r'Currency[:\s]+([A-Z]{3})', context)
                    if currency_match:
                        bond['currency'] = currency_match.group(1).strip()

                    # Extract nominal
                    nominal_match = re.search(r'Nominal[:\s]+([\d\',\.]+)', context)
                    if nominal_match:
                        bond['nominal'] = self._clean_number(nominal_match.group(1))

                    # Extract price
                    price_match = re.search(r'Price[:\s]+([\d\',\.]+)', context)
                    if price_match:
                        bond['price'] = self._clean_number(price_match.group(1))

                    # Extract valuation
                    valuation_match = re.search(r'Valuation[:\s]+([\d\',\.]+)', context)
                    if valuation_match:
                        bond['valuation'] = self._clean_number(valuation_match.group(1))

                    # Only add if we have at least ISIN
                    if 'isin' in bond:
                        # Check if this bond already exists
                        existing_bond = next((b for b in self.extracted_data["bonds"] if b.get('isin') == bond['isin']), None)
                        if existing_bond:
                            # Update existing bond with any new information
                            for key, value in bond.items():
                                if key not in existing_bond or not existing_bond[key]:
                                    existing_bond[key] = value
                        else:
                            self.extracted_data["bonds"].append(bond)

        print(f"Extracted {len(self.extracted_data['bonds'])} bonds")

    def _extract_asset_allocation(self):
        """Extract asset allocation from tables and text."""
        # First, try to extract asset allocation from tables
        self._extract_asset_allocation_from_tables()

        # If no asset allocation was found in tables, try to extract from text
        if not self.extracted_data["asset_allocation"]:
            self._extract_asset_allocation_from_text()

        print(f"Extracted asset allocation with {len(self.extracted_data['asset_allocation'])} asset classes")

    def _extract_asset_allocation_from_tables(self):
        """Extract asset allocation from tables."""
        for table in self.tables:
            # Skip empty tables
            if not table or len(table) <= 1:
                continue

            # Convert table to DataFrame
            df = pd.DataFrame(table)

            # Check if this is an asset allocation table
            header_row = df.iloc[0] if not df.empty else []
            asset_headers = ['Asset', 'Allocation', 'Class', 'Weight', 'Value', 'Countervalue']

            # Check if this looks like an asset allocation table
            is_asset_table = any(any(header in str(cell) for cell in header_row) for header in asset_headers)

            # Also check if the table contains "Asset Allocation" in any cell
            contains_asset_allocation = any("Asset Allocation" in str(cell) for row in df.values for cell in row if cell)

            if is_asset_table or contains_asset_allocation:
                # This is likely an asset allocation table
                # Clean the DataFrame
                df = self._clean_dataframe(df)

                # Map column indices to their meanings
                column_indices = {}
                for i, cell in enumerate(header_row):
                    if not cell:
                        continue

                    cell_lower = str(cell).lower()

                    if 'asset' in cell_lower or 'class' in cell_lower:
                        column_indices['asset_class'] = i
                    elif 'value' in cell_lower or 'amount' in cell_lower or 'countervalue' in cell_lower:
                        column_indices['value'] = i
                    elif '%' in cell_lower or 'percent' in cell_lower or 'weight' in cell_lower:
                        column_indices['percentage'] = i

                # If we couldn't identify essential columns but this is an asset allocation section,
                # try to infer column positions based on typical layout
                if not column_indices and contains_asset_allocation and len(df.columns) >= 3:
                    # Typical layout: Asset Class, Value, Percentage
                    column_indices = {
                        'asset_class': 0,
                        'value': 1,
                        'percentage': 2
                    }

                # Process asset allocation
                current_asset_class = None

                for i in range(1, len(df)):
                    row = df.iloc[i]

                    # Skip empty rows
                    if all(pd.isna(cell) or str(cell).strip() == "" for cell in row):
                        continue

                    # Get the asset class name
                    asset_class_idx = column_indices.get('asset_class', 0)  # Default to first column
                    asset_class = str(row[asset_class_idx]).strip() if asset_class_idx < len(row) and not pd.isna(row[asset_class_idx]) else ""

                    # Skip empty asset classes
                    if not asset_class:
                        continue

                    # Get value and percentage
                    value_idx = column_indices.get('value', 1)  # Default to second column
                    percentage_idx = column_indices.get('percentage', 2)  # Default to third column

                    value = self._clean_number(row[value_idx]) if value_idx < len(row) and not pd.isna(row[value_idx]) else None
                    percentage = self._clean_number(row[percentage_idx]) if percentage_idx < len(row) and not pd.isna(row[percentage_idx]) else None

                    # Check if this is a main asset class (usually starts with uppercase)
                    if asset_class and asset_class[0].isupper():
                        current_asset_class = asset_class

                        if value is not None:
                            self.extracted_data["asset_allocation"][current_asset_class] = {
                                "value": value,
                                "percentage": percentage,
                                "sub_classes": {}
                            }

                    # Check if this is a sub-asset class
                    elif current_asset_class and asset_class and not asset_class[0].isupper():
                        # This is a sub-asset class
                        sub_class = asset_class

                        if value is not None and current_asset_class in self.extracted_data["asset_allocation"]:
                            self.extracted_data["asset_allocation"][current_asset_class]["sub_classes"][sub_class] = {
                                "value": value,
                                "percentage": percentage
                            }

    def _extract_asset_allocation_from_text(self):
        """Extract asset allocation from text using pattern matching."""
        # Look for asset allocation sections in the text
        asset_sections = re.split(r'Asset Allocation|Assets and Liabilities Structure', self.full_text)

        if len(asset_sections) > 1:
            # Process each asset allocation section
            for section in asset_sections[1:]:  # Skip the first section (before "Asset Allocation")
                # Look for asset class patterns
                asset_class_matches = re.finditer(r'([A-Z][A-Za-z\s]+)\s+(\d[\d\',\.]+)\s+(\d+\.\d+)%', section)

                for asset_match in asset_class_matches:
                    asset_class = asset_match.group(1).strip()
                    value_str = asset_match.group(2).strip()
                    percentage_str = asset_match.group(3).strip()

                    value = self._clean_number(value_str)
                    percentage = float(percentage_str) if percentage_str else None

                    if value is not None and asset_class:
                        self.extracted_data["asset_allocation"][asset_class] = {
                            "value": value,
                            "percentage": percentage,
                            "sub_classes": {}
                        }

                # Look for sub-class patterns
                sub_class_matches = re.finditer(r'\s+([a-z][A-Za-z\s/]+)\s+(\d[\d\',\.]+)\s+(\d+\.\d+)%', section)

                current_asset_class = next(iter(self.extracted_data["asset_allocation"].keys())) if self.extracted_data["asset_allocation"] else None

                for sub_match in sub_class_matches:
                    sub_class = sub_match.group(1).strip()
                    value_str = sub_match.group(2).strip()
                    percentage_str = sub_match.group(3).strip()

                    value = self._clean_number(value_str)
                    percentage = float(percentage_str) if percentage_str else None

                    if value is not None and sub_class and current_asset_class:
                        self.extracted_data["asset_allocation"][current_asset_class]["sub_classes"][sub_class] = {
                            "value": value,
                            "percentage": percentage
                        }

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean a DataFrame by removing empty rows and columns.

        Args:
            df: DataFrame to clean

        Returns:
            Cleaned DataFrame
        """
        # Remove rows where all values are None or empty string
        df = df.dropna(how="all")
        df = df[~df.apply(lambda row: all(pd.isna(val) or str(val).strip() == "" for val in row), axis=1)]

        # Remove columns where all values are None or empty string
        df = df.dropna(axis=1, how="all")
        df = df.loc[:, ~df.apply(lambda col: all(pd.isna(val) or str(val).strip() == "" for val in col), axis=0)]

        return df

    def _clean_number(self, value):
        """Clean a number by removing quotes, commas, etc."""
        if pd.isna(value):
            return None

        value_str = str(value)

        # Replace single quotes with nothing (European number format)
        cleaned = value_str.replace("'", "")

        # Replace commas with nothing (US number format)
        cleaned = cleaned.replace(",", "")

        # Remove any non-numeric characters except decimal point and negative sign
        cleaned = re.sub(r'[^\d.-]', '', cleaned)

        try:
            return float(cleaned)
        except ValueError:
            return None

    def _save_results(self, output_dir):
        """Save extraction results."""
        # Save full text
        text_path = os.path.join(output_dir, "full_text.txt")
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(self.full_text)

        # Save extracted data as JSON
        json_path = os.path.join(output_dir, "extracted_data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.extracted_data, f, indent=2)

        # Save bonds as CSV
        if self.extracted_data["bonds"]:
            bonds_df = pd.DataFrame(self.extracted_data["bonds"])
            bonds_path = os.path.join(output_dir, "bonds.csv")
            bonds_df.to_csv(bonds_path, index=False)

        print(f"Results saved to {output_dir}")

    def answer_question(self, question: str) -> str:
        """
        Answer a question about the financial document.

        Args:
            question: Question to answer

        Returns:
            Answer to the question
        """
        # If LLM is available and enabled, use it for all questions
        if self.use_llm and self.llm_answerer:
            # Prepare context for the LLM
            context = self._prepare_llm_context(question)

            # Use the LLM to answer the question
            return self.llm_answerer.answer_question(question, context)

        # Otherwise, use rule-based approach
        return self._rule_based_answer(question)

    def _prepare_llm_context(self, question: str) -> str:
        """Prepare context for the LLM based on the question."""
        # Start with basic information
        context = ""

        # Add client information
        if self.extracted_data["client_info"]:
            client_name = self.extracted_data["client_info"].get("name", "Unknown")
            client_number = self.extracted_data["client_info"].get("number", "Unknown")
            context += f"Client: {client_name}, Client Number: {client_number}\n\n"

        # Add document date
        if self.extracted_data["document_date"]:
            context += f"Document Date: {self.extracted_data['document_date']}\n\n"

        # Add portfolio value
        if self.extracted_data["portfolio_value"]:
            context += f"Portfolio Value: ${self.extracted_data['portfolio_value']:,.2f}\n\n"

        # Add asset allocation if the question is about it
        question_lower = question.lower()
        if "asset" in question_lower or "allocation" in question_lower or "class" in question_lower:
            context += "Asset Allocation:\n"
            for asset_class, data in self.extracted_data["asset_allocation"].items():
                value = data.get("value", 0)
                percentage = data.get("percentage", 0)
                context += f"{asset_class}: ${value:,.2f} ({percentage:.2f}%)\n"

                # Add sub-classes
                sub_classes = data.get("sub_classes", {})
                for sub_class, sub_data in sub_classes.items():
                    sub_value = sub_data.get("value", 0)
                    sub_percentage = sub_data.get("percentage", 0)
                    context += f"  - {sub_class}: ${sub_value:,.2f} ({sub_percentage:.2f}%)\n"
            context += "\n"

        # Add bonds if the question is about them
        if "bond" in question_lower or "holding" in question_lower or "security" in question_lower or "isin" in question_lower:
            # Sort bonds by valuation
            sorted_bonds = sorted(self.extracted_data["bonds"], key=lambda x: x.get("valuation", 0), reverse=True)

            # Limit to top 20 bonds to keep context manageable
            top_bonds = sorted_bonds[:20]

            context += f"Top {len(top_bonds)} Bonds/Securities:\n"
            for i, bond in enumerate(top_bonds, 1):
                description = bond.get("description", "Unknown")
                isin = bond.get("isin", "N/A")
                currency = bond.get("currency", "N/A")
                nominal = bond.get("nominal", 0)
                price = bond.get("price", 0)
                valuation = bond.get("valuation", 0)
                maturity_date = bond.get("maturity_date", "N/A")

                context += f"{i}. {description}\n"
                context += f"   ISIN: {isin}\n"
                context += f"   Currency: {currency}\n"
                context += f"   Nominal: {nominal:,.2f}\n"
                context += f"   Price: {price:,.4f}\n"
                context += f"   Valuation: ${valuation:,.2f}\n"
                if maturity_date != "N/A":
                    context += f"   Maturity Date: {maturity_date}\n"
                context += "\n"

        # Add relevant sections from the full text
        if len(context) < 4000:  # Keep context size reasonable
            # Extract keywords from the question
            keywords = re.findall(r'\b\w{3,}\b', question_lower)

            # Find relevant paragraphs
            paragraphs = self.full_text.split("\n\n")
            relevant_paragraphs = []

            for paragraph in paragraphs:
                paragraph_lower = paragraph.lower()
                if any(keyword in paragraph_lower for keyword in keywords):
                    relevant_paragraphs.append(paragraph)

            # Add relevant paragraphs to context
            if relevant_paragraphs:
                context += "Relevant sections from the document:\n\n"
                for paragraph in relevant_paragraphs[:3]:  # Limit to 3 paragraphs
                    context += paragraph + "\n\n"

        return context

    def _rule_based_answer(self, question: str) -> str:
        """Answer a question using rule-based approach."""
        question_lower = question.lower()

        # Portfolio value questions
        if "portfolio value" in question_lower or "total value" in question_lower:
            if self.extracted_data["portfolio_value"]:
                return f"The portfolio value is ${self.extracted_data['portfolio_value']:,.2f}."
            else:
                return "I couldn't find the portfolio value in the document."

        # Top holdings questions
        elif "top" in question_lower and ("holdings" in question_lower or "bonds" in question_lower):
            # Extract the number from the question (default to 5 if not found)
            match = re.search(r'top (\d+)', question_lower)
            n = int(match.group(1)) if match else 5

            if self.extracted_data["bonds"]:
                # Sort bonds by valuation
                sorted_bonds = sorted(self.extracted_data["bonds"], key=lambda x: x.get("valuation", 0), reverse=True)
                top_bonds = sorted_bonds[:n]

                response = f"The top {len(top_bonds)} holdings by value are:\n"
                for i, bond in enumerate(top_bonds, 1):
                    description = bond.get("description", "Unknown")
                    valuation = bond.get("valuation", 0)

                    response += f"{i}. {description}: ${valuation:,.2f}\n"

                return response
            else:
                return "I couldn't find any holdings in the document."

        # Asset allocation questions
        elif "asset allocation" in question_lower or "asset classes" in question_lower:
            if self.extracted_data["asset_allocation"]:
                response = "Asset Allocation:\n"

                for asset_class, data in self.extracted_data["asset_allocation"].items():
                    value = data.get("value", 0)
                    percentage = data.get("percentage", 0)

                    response += f"{asset_class}: ${value:,.2f} ({percentage:.2f}%)\n"

                return response
            else:
                return "I couldn't find asset allocation information in the document."

        # Client information questions
        elif "client" in question_lower:
            if self.extracted_data["client_info"]:
                client_name = self.extracted_data["client_info"].get("name", "Unknown")
                client_number = self.extracted_data["client_info"].get("number", "Unknown")

                return f"Client: {client_name}, Client Number: {client_number}"
            else:
                return "I couldn't find client information in the document."

        # Document date questions
        elif "date" in question_lower:
            if self.extracted_data["document_date"]:
                return f"The document date is {self.extracted_data['document_date']}."
            else:
                return "I couldn't find the document date."

        # General questions - search in full text
        else:
            # Look for relevant sections in the full text
            sentences = re.split(r'[.!?]\s+', self.full_text)
            relevant_sentences = []

            # Extract keywords from the question
            keywords = re.findall(r'\b\w{3,}\b', question_lower)

            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(keyword in sentence_lower for keyword in keywords):
                    relevant_sentences.append(sentence)

            if relevant_sentences:
                return " ".join(relevant_sentences[:3]) + "."
            else:
                return "I couldn't find information related to your question in the document."

    def generate_report(self, output_dir: Optional[str] = None) -> str:
        """
        Generate a comprehensive report based on the extracted data.

        Args:
            output_dir: Directory to save the report

        Returns:
            Path to the generated report
        """
        # Create HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Financial Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    color: #333;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .summary-box {{
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    padding: 15px;
                    margin-bottom: 20px;
                }}
                .value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #28a745;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px 15px;
                    border-bottom: 1px solid #ddd;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
                .chart {{
                    width: 100%;
                    height: 20px;
                    background-color: #e9ecef;
                    margin-bottom: 10px;
                    border-radius: 5px;
                    overflow: hidden;
                }}
                .chart-segment {{
                    height: 100%;
                    float: left;
                    text-align: center;
                    color: white;
                    font-weight: bold;
                }}
                .footer {{
                    margin-top: 30px;
                    text-align: center;
                    font-size: 12px;
                    color: #6c757d;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Financial Report</h1>
        """

        # Add client information
        if self.extracted_data["client_info"]:
            client_name = self.extracted_data["client_info"].get("name", "Unknown")
            client_number = self.extracted_data["client_info"].get("number", "Unknown")

            html_content += f"""
                <div class="summary-box">
                    <h2>Client Information</h2>
                    <p>Client: <span class="value">{client_name}</span></p>
                    <p>Client Number: <span class="value">{client_number}</span></p>
            """

            if self.extracted_data["document_date"]:
                html_content += f"""
                    <p>Document Date: <span class="value">{self.extracted_data["document_date"]}</span></p>
                """

            html_content += f"""
                </div>
            """

        # Add portfolio summary
        if self.extracted_data["portfolio_value"]:
            html_content += f"""
                <div class="summary-box">
                    <h2>Portfolio Summary</h2>
                    <p>Portfolio Value: <span class="value">${self.extracted_data["portfolio_value"]:,.2f}</span></p>
                </div>
            """

        # Add asset allocation
        if self.extracted_data["asset_allocation"]:
            html_content += f"""
                <h2>Asset Allocation</h2>
            """

            # Add chart
            html_content += f"""
                <div class="chart">
            """

            # Define colors for asset classes
            colors = {
                "Liquidity": "#17a2b8",
                "Bonds": "#007bff",
                "Equities": "#28a745",
                "Mixed funds": "#6f42c1",
                "Structured products": "#fd7e14",
                "Metal accounts and precious metals": "#dc3545",
                "Real Estate": "#6c757d",
                "Other assets": "#20c997"
            }

            # Add chart segments
            for asset_class, data in self.extracted_data["asset_allocation"].items():
                percentage = data.get("percentage", 0)
                color = colors.get(asset_class, "#6c757d")

                if percentage > 0:
                    html_content += f"""
                        <div class="chart-segment" style="width: {percentage}%; background-color: {color};">
                            {percentage:.1f}%
                        </div>
                    """

            html_content += f"""
                </div>

                <table>
                    <tr>
                        <th>Asset Class</th>
                        <th>Value</th>
                        <th>Percentage</th>
                    </tr>
            """

            # Add asset classes
            for asset_class, data in self.extracted_data["asset_allocation"].items():
                value = data.get("value", 0)
                percentage = data.get("percentage", 0)

                html_content += f"""
                    <tr>
                        <td>{asset_class}</td>
                        <td>${value:,.2f}</td>
                        <td>{percentage:.2f}%</td>
                    </tr>
                """

                # Add sub-classes
                sub_classes = data.get("sub_classes", {})
                for sub_class, sub_data in sub_classes.items():
                    sub_value = sub_data.get("value", 0)
                    sub_percentage = sub_data.get("percentage", 0)

                    html_content += f"""
                        <tr>
                            <td>&nbsp;&nbsp;&nbsp;{sub_class}</td>
                            <td>${sub_value:,.2f}</td>
                            <td>{sub_percentage:.2f}%</td>
                        </tr>
                    """

            html_content += f"""
                </table>
            """

        # Add bonds
        if self.extracted_data["bonds"]:
            html_content += f"""
                <h2>Bonds</h2>
                <table>
                    <tr>
                        <th>Description</th>
                        <th>ISIN</th>
                        <th>Currency</th>
                        <th>Nominal</th>
                        <th>Valuation</th>
                    </tr>
            """

            # Sort bonds by valuation
            sorted_bonds = sorted(self.extracted_data["bonds"], key=lambda x: x.get("valuation", 0), reverse=True)

            for bond in sorted_bonds:
                description = bond.get("description", "Unknown")
                isin = bond.get("isin", "N/A")
                currency = bond.get("currency", "N/A")
                nominal = bond.get("nominal", 0)
                valuation = bond.get("valuation", 0)

                html_content += f"""
                    <tr>
                        <td>{description}</td>
                        <td>{isin}</td>
                        <td>{currency}</td>
                        <td>{nominal:,.2f}</td>
                        <td>${valuation:,.2f}</td>
                    </tr>
                """

            html_content += f"""
                </table>
            """

        # Add footer
        html_content += f"""
                <div class="footer">
                    <p>This report is generated based on the extracted financial data.</p>
                    <p>Generated on {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Save the report if output_dir is specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            report_path = os.path.join(output_dir, "financial_report.html")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Financial report saved to: {report_path}")
            return report_path

        # If no output_dir, save to a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as f:
            f.write(html_content)
            report_path = f.name
            print(f"Financial report saved to temporary file: {report_path}")
            return report_path

def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Process financial documents.")
    parser.add_argument("file_path", help="Path to the financial document")
    parser.add_argument("--output-dir", help="Directory to save output files")
    parser.add_argument("--question", help="Question to answer (if provided, skips interactive mode)")
    parser.add_argument("--report", action="store_true", help="Generate a report")
    parser.add_argument("--use-ocr", action="store_true", help="Use OCR for text extraction")
    parser.add_argument("--ocr-lang", default="en", help="Language code for OCR (default: en)")
    parser.add_argument("--use-llm", action="store_true", help="Use LLM for question answering")
    parser.add_argument("--api-key", help="API key for LLM service")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model to use for LLM (default: gpt-4o-mini)")
    parser.add_argument("--force-ocr", action="store_true", help="Force OCR even if text extraction is possible")

    args = parser.parse_args()

    # Check if the file exists
    if not os.path.exists(args.file_path):
        print(f"Error: File not found: {args.file_path}")
        return 1

    # Process the document
    processor = SimplePDFProcessor(
        use_ocr=args.use_ocr,
        ocr_lang=args.ocr_lang,
        use_llm=args.use_llm,
        api_key=args.api_key,
        model=args.model
    )
    processor.process(args.file_path, output_dir=args.output_dir, force_ocr=args.force_ocr)

    # Generate a report if requested
    if args.report:
        report_path = processor.generate_report(output_dir=args.output_dir)
        if report_path:
            print(f"Report generated: {report_path}")
            # Open the report in the default browser
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(report_path)}")

    # Answer a specific question if provided
    if args.question:
        answer = processor.answer_question(args.question)
        print(f"\nQuestion: {args.question}")
        print(f"Answer: {answer}\n")
    # Otherwise, start interactive session
    else:
        print("\nFinancial Document Processor")
        print("===========================")
        print("I can answer questions about the financial document.")
        print("Type 'exit' to end the session.")
        print("Type 'help' to see example questions.")
        print("Type 'report' to generate a report.")
        print()

        while True:
            user_input = input("Ask a question: ").strip()

            if user_input.lower() == 'exit':
                print("Ending session. Goodbye!")
                break

            elif user_input.lower() == 'help':
                print("\nExample questions:")
                print("- What is the total portfolio value?")
                print("- What is the asset allocation?")
                print("- What are the top 5 holdings?")
                print("- What are the top 10 bonds?")
                print("- What is the client information?")
                print("- What is the document date?")
                print()
                continue

            elif user_input.lower() == 'report':
                report_path = processor.generate_report(output_dir=args.output_dir)
                if report_path:
                    print(f"Report generated: {report_path}")
                    # Open the report in the default browser
                    import webbrowser
                    webbrowser.open(f"file://{os.path.abspath(report_path)}")
                continue

            answer = processor.answer_question(user_input)
            print(f"\n{answer}\n")

    return 0

if __name__ == "__main__":
    main()
