"""
Document Integration Agent for combining all extracted data from a document into a unified structure.
"""
import json
from datetime import datetime
import pandas as pd
import uuid
from typing import Dict, Any, List, Optional, Union
from .base_agent import BaseAgent

class DocumentIntegrationAgent(BaseAgent):
    """Agent for integrating all extracted data from a document into a unified structure."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the document integration agent.
        
        Args:
            api_key: OpenRouter API key
            **kwargs: Additional parameters for the base agent
        """
        super().__init__(name="Document Integration Agent")
        self.api_key = api_key
        self.description = "I integrate all extracted data from a document into a unified structure."
        self.document_id = str(uuid.uuid4())
        self.processing_date = datetime.now().isoformat()
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task to integrate document data.
        
        Args:
            task: Task dictionary with the following keys:
                - extracted_text: Text extracted from the document
                - tables_data: Table data detected in the document
                - financial_data: Financial data extracted from the document
                - isin_entities: ISIN entities detected in the document (optional)
                
        Returns:
            Dictionary with integrated document data
        """
        # Get the required data
        extracted_text = task.get('extracted_text', '')
        tables_data = task.get('tables_data', [])
        financial_data = task.get('financial_data', {})
        isin_entities = task.get('isin_entities', [])
        
        # Integrate the data
        integrated_data = self.integrate_document_data(
            extracted_text=extracted_text,
            tables_data=tables_data,
            financial_data=financial_data,
            isin_entities=isin_entities
        )
        
        # Generate output
        if task.get('output_format') == 'json':
            return {
                'integrated_data': integrated_data,
                'json_output': self.generate_output_json(integrated_data)
            }
        
        # Save to file if requested
        if 'output_path' in task:
            output_path = task['output_path']
            self.save_to_json(integrated_data, output_path)
            integrated_data['output_path'] = output_path
        
        return {
            'integrated_data': integrated_data
        }
    
    def integrate_document_data(self, extracted_text, tables_data, financial_data, isin_entities=None):
        """
        Integrate all extracted data into a unified structure.
        
        Args:
            extracted_text: Text extracted from the document
            tables_data: Table data detected in the document
            financial_data: Financial data extracted from the document
            isin_entities: ISIN entities detected in the document
            
        Returns:
            Dictionary with integrated data
        """
        # Create basic data structure
        integrated_data = {
            "document_id": self.document_id,
            "processing_date": self.processing_date,
            "metadata": self._extract_metadata(extracted_text),
            "tables": self._process_tables(tables_data),
            "financial_data": financial_data,
            "entities": {
                "isin": isin_entities or []
            },
            "summary": self._generate_summary(financial_data, tables_data, isin_entities)
        }
        
        return integrated_data
    
    def _extract_metadata(self, text):
        """Extract metadata from the document text."""
        metadata = {
            "text_length": len(text),
            "language": self._detect_language(text),
            "document_date": self._find_document_date(text),
            "document_type": self._identify_document_type(text),
            "document_text": text[:1000] if len(text) > 1000 else text  # Store a preview of the text
        }
        
        return metadata
    
    def _detect_language(self, text):
        """Detect the language of the document."""
        # Simple check - count Hebrew vs. English characters
        hebrew_chars = sum(1 for char in text if '\u0590' <= char <= '\u05FF')
        english_chars = sum(1 for char in text if 'a' <= char.lower() <= 'z')
        
        if hebrew_chars > english_chars:
            return "hebrew"
        else:
            return "english"
    
    def _find_document_date(self, text):
        """Find the document date in the text."""
        # Common date patterns
        date_patterns = [
            # DD/MM/YYYY
            r'(\d{1,2})[/\.](\d{1,2})[/\.](\d{2,4})',
            # Hebrew month
            r'(\d{1,2})?\s?ב?(ינואר|פברואר|מרץ|אפריל|מאי|יוני|יולי|אוגוסט|ספטמבר|אוקטובר|נובמבר|דצמבר)\s?(\d{2,4})?',
            # English date
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:[a-z]{2})?,?\s+(\d{2,4})'
        ]
        
        import re
        
        # Check each pattern for a match
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Take the first match - assuming the date is at the beginning of the document
                # Here we need to handle the specific pattern that matched
                return str(matches[0])  # Return the date as a string
        
        return None
    
    def _identify_document_type(self, text):
        """Identify the document type based on keywords."""
        text_lower = text.lower()
        
        # Keywords for identifying document types
        keywords = {
            "portfolio_statement": ["תיק השקעות", "דו\"ח תיק", "portfolio statement", "investment portfolio"],
            "balance_sheet": ["מאזן", "דו\"ח מאזן", "balance sheet"],
            "income_statement": ["רווח והפסד", "דו\"ח רווח", "income statement", "profit and loss"],
            "bank_statement": ["חשבון בנק", "דף חשבון", "bank statement", "account statement"]
        }
        
        # Search for a match for each document type
        for doc_type, type_keywords in keywords.items():
            for keyword in type_keywords:
                if keyword in text_lower:
                    return doc_type
        
        # Default - general financial document
        return "financial_document"
    
    def _process_tables(self, tables_data):
        """Process table data into a unified format."""
        processed_tables = []
        
        for i, table in enumerate(tables_data):
            table_info = {
                "id": f"table_{i+1}",
                "type": table.get("type", "unknown"),
            }
            
            # Convert DataFrame to JSON format
            df = table.get("data")
            if isinstance(df, pd.DataFrame):
                # Handle NaN values
                df = df.fillna("")
                # Convert to list of dictionaries
                table_info["data"] = df.to_dict(orient="records")
                table_info["columns"] = df.columns.tolist()
                table_info["row_count"] = len(df)
                table_info["column_count"] = len(df.columns)
            
            processed_tables.append(table_info)
        
        return processed_tables
    
    def _generate_summary(self, financial_data, tables_data, isin_entities):
        """Generate a general summary of the document."""
        summary = {
            "table_count": len(tables_data),
            "isin_count": len(isin_entities) if isin_entities else 0
        }
        
        # If it's a portfolio, add a summary of the portfolio value
        if financial_data and "portfolio" in financial_data:
            portfolio_data = financial_data["portfolio"]
            if "securities" in portfolio_data and portfolio_data["securities"]:
                summary["security_count"] = len(portfolio_data["securities"])
            
            if "summary" in portfolio_data and "total_value" in portfolio_data["summary"]:
                summary["total_portfolio_value"] = portfolio_data["summary"]["total_value"]
        
        return summary
    
    def generate_output_json(self, integrated_data):
        """Generate JSON from the integrated data."""
        return json.dumps(integrated_data, ensure_ascii=False, indent=2)
    
    def save_to_json(self, integrated_data, output_path):
        """Save the integrated data as a JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(integrated_data, f, ensure_ascii=False, indent=2)
        
        return output_path
