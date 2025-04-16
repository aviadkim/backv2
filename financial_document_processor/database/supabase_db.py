"""
Supabase database integration for the Financial Document Processor.
"""
import os
import logging
from typing import Dict, List, Any, Optional
import json
import datetime

# Try to import Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning("Supabase library not available. Install with: pip install supabase")

class SupabaseDB:
    """Supabase database integration."""

    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Initialize the Supabase database connection.

        Args:
            url: Supabase URL
            key: Supabase API key
        """
        if not SUPABASE_AVAILABLE:
            raise ImportError("Supabase library not available. Install with: pip install supabase")

        self.url = url or os.environ.get("SUPABASE_URL", "https://dnjnsotemnfrjlotgved.supabase.co")
        self.key = key or os.environ.get("SUPABASE_KEY")

        if not self.url or not self.key:
            raise ValueError("Supabase URL and key must be provided or set as environment variables")

        self.client = create_client(self.url, self.key)
        logging.info(f"Connected to Supabase at {self.url}")

    def create_tables(self):
        """Create tables if they don't exist."""
        logging.info("Creating tables in Supabase")

        # Execute SQL to create tables
        # Note: Supabase doesn't have a direct way to create tables via the Python client
        # We would typically use migrations or the Supabase dashboard for this
        # For this implementation, we'll assume the tables already exist

        logging.info("Tables should be created via Supabase dashboard or migrations")

        # For reference, here's the SQL that would create the tables:
        """
        -- Documents table
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            filename TEXT NOT NULL,
            file_path TEXT,
            file_size INTEGER,
            content_type TEXT,
            page_count INTEGER,
            title TEXT,
            author TEXT,
            creation_date TIMESTAMP,
            modification_date TIMESTAMP,
            document_date TIMESTAMP,
            document_type TEXT,
            processing_status TEXT DEFAULT 'pending',
            extraction_date TIMESTAMP DEFAULT NOW(),
            extraction_method TEXT,
            extraction_version TEXT,
            risk_profile TEXT,
            currency TEXT
        );

        -- Securities table
        CREATE TABLE IF NOT EXISTS securities (
            id SERIAL PRIMARY KEY,
            document_id INTEGER REFERENCES documents(id),
            isin TEXT,
            cusip TEXT,
            ticker TEXT,
            name TEXT,
            description TEXT,
            security_type TEXT,
            asset_class TEXT,
            valuation FLOAT,
            price FLOAT,
            quantity FLOAT,
            currency TEXT,
            coupon_rate FLOAT,
            maturity_date TIMESTAMP,
            extraction_method TEXT,
            confidence_score FLOAT
        );

        -- Portfolio values table
        CREATE TABLE IF NOT EXISTS portfolio_values (
            id SERIAL PRIMARY KEY,
            document_id INTEGER REFERENCES documents(id),
            value FLOAT NOT NULL,
            currency TEXT,
            value_date TIMESTAMP,
            extraction_method TEXT,
            confidence_score FLOAT
        );

        -- Asset allocations table
        CREATE TABLE IF NOT EXISTS asset_allocations (
            id SERIAL PRIMARY KEY,
            document_id INTEGER REFERENCES documents(id),
            asset_class TEXT NOT NULL,
            value FLOAT,
            percentage FLOAT,
            currency TEXT,
            parent_id INTEGER REFERENCES asset_allocations(id),
            extraction_method TEXT,
            confidence_score FLOAT
        );

        -- Raw text table
        CREATE TABLE IF NOT EXISTS raw_texts (
            id SERIAL PRIMARY KEY,
            document_id INTEGER REFERENCES documents(id) UNIQUE,
            content TEXT,
            extraction_method TEXT
        );

        -- Document tables table
        CREATE TABLE IF NOT EXISTS document_tables (
            id SERIAL PRIMARY KEY,
            document_id INTEGER REFERENCES documents(id),
            page_number INTEGER,
            table_number INTEGER,
            extraction_method TEXT,
            headers JSONB,
            data JSONB,
            accuracy FLOAT
        );
        """

    def store_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store a document in the database.

        Args:
            document_data: Document data

        Returns:
            Document object
        """
        logging.info(f"Storing document: {document_data.get('filename')}")

        # Convert dates to ISO format if they exist
        for date_field in ['creation_date', 'modification_date', 'document_date', 'extraction_date']:
            if date_field in document_data and document_data[date_field] and isinstance(document_data[date_field], datetime.datetime):
                document_data[date_field] = document_data[date_field].isoformat()

        # Insert document
        result = self.client.table('documents').insert(document_data).execute()

        if not result.data:
            raise ValueError(f"Failed to store document: {result.error}")

        return result.data[0]

    def store_securities(self, document_id: int, securities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Store securities in the database.

        Args:
            document_id: Document ID
            securities: List of securities data

        Returns:
            List of Security objects
        """
        logging.info(f"Storing {len(securities)} securities for document ID {document_id}")

        # Add document_id to each security
        for security in securities:
            security['document_id'] = document_id

            # Convert dates to ISO format if they exist
            if 'maturity_date' in security and security['maturity_date'] and isinstance(security['maturity_date'], datetime.datetime):
                security['maturity_date'] = security['maturity_date'].isoformat()

        # Insert securities
        result = self.client.table('securities').insert(securities).execute()

        if not result.data:
            raise ValueError(f"Failed to store securities: {result.error}")

        return result.data

    def store_portfolio_value(self, document_id: int, portfolio_value_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store a portfolio value in the database.

        Args:
            document_id: Document ID
            portfolio_value_data: Portfolio value data

        Returns:
            PortfolioValue object
        """
        logging.info(f"Storing portfolio value for document ID {document_id}")

        # Add document_id to portfolio value data
        portfolio_value_data['document_id'] = document_id

        # Convert dates to ISO format if they exist
        if 'value_date' in portfolio_value_data and portfolio_value_data['value_date'] and isinstance(portfolio_value_data['value_date'], datetime.datetime):
            portfolio_value_data['value_date'] = portfolio_value_data['value_date'].isoformat()

        # Insert portfolio value
        result = self.client.table('portfolio_values').insert(portfolio_value_data).execute()

        if not result.data:
            raise ValueError(f"Failed to store portfolio value: {result.error}")

        return result.data[0]

    def store_asset_allocations(self, document_id: int, asset_allocations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Store asset allocations in the database.

        Args:
            document_id: Document ID
            asset_allocations: List of asset allocation data

        Returns:
            List of AssetAllocation objects
        """
        logging.info(f"Storing {len(asset_allocations)} asset allocations for document ID {document_id}")

        # Add document_id to each asset allocation
        for allocation in asset_allocations:
            allocation['document_id'] = document_id

        # Insert asset allocations
        result = self.client.table('asset_allocations').insert(asset_allocations).execute()

        if not result.data:
            raise ValueError(f"Failed to store asset allocations: {result.error}")

        return result.data

    def store_raw_text(self, document_id: int, content: str, extraction_method: Optional[str] = None) -> Dict[str, Any]:
        """
        Store raw text in the database.

        Args:
            document_id: Document ID
            content: Raw text content
            extraction_method: Extraction method

        Returns:
            RawText object
        """
        logging.info(f"Storing raw text for document ID {document_id}")

        # Create raw text data
        raw_text_data = {
            'document_id': document_id,
            'content': content,
            'extraction_method': extraction_method
        }

        # Check if raw text already exists for this document
        existing = self.client.table('raw_texts').select('id').eq('document_id', document_id).execute()

        if existing.data:
            # Update existing raw text
            result = self.client.table('raw_texts').update(raw_text_data).eq('document_id', document_id).execute()
        else:
            # Insert new raw text
            result = self.client.table('raw_texts').insert(raw_text_data).execute()

        if not result.data:
            raise ValueError(f"Failed to store raw text: {result.error}")

        return result.data[0]

    def store_tables(self, document_id: int, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Store tables in the database.

        Args:
            document_id: Document ID
            tables: List of table data

        Returns:
            List of DocumentTable objects
        """
        logging.info(f"Storing {len(tables)} tables for document ID {document_id}")

        # Add document_id to each table and convert data to JSON
        table_data = []
        for table in tables:
            table_data.append({
                'document_id': document_id,
                'page_number': table.get('page'),
                'table_number': table.get('table_number'),
                'extraction_method': table.get('extraction_method'),
                'headers': json.dumps(table.get('headers', [])),
                'data': json.dumps(table.get('data', [])),
                'accuracy': table.get('accuracy')
            })

        # Insert tables
        result = self.client.table('document_tables').insert(table_data).execute()

        if not result.data:
            raise ValueError(f"Failed to store tables: {result.error}")

        return result.data

    def get_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document object or None if not found
        """
        logging.info(f"Getting document ID {document_id}")

        result = self.client.table('documents').select('*').eq('id', document_id).execute()

        if not result.data:
            return None

        return result.data[0]

    def get_securities(self, document_id: int) -> List[Dict[str, Any]]:
        """
        Get securities for a document.

        Args:
            document_id: Document ID

        Returns:
            List of Security objects
        """
        logging.info(f"Getting securities for document ID {document_id}")

        result = self.client.table('securities').select('*').eq('document_id', document_id).execute()

        return result.data

    def get_portfolio_value(self, document_id: int) -> Optional[Dict[str, Any]]:
        """
        Get portfolio value for a document.

        Args:
            document_id: Document ID

        Returns:
            PortfolioValue object or None if not found
        """
        logging.info(f"Getting portfolio value for document ID {document_id}")

        result = self.client.table('portfolio_values').select('*').eq('document_id', document_id).execute()

        if not result.data:
            return None

        return result.data[0]

    def get_asset_allocations(self, document_id: int) -> List[Dict[str, Any]]:
        """
        Get asset allocations for a document.

        Args:
            document_id: Document ID

        Returns:
            List of AssetAllocation objects
        """
        logging.info(f"Getting asset allocations for document ID {document_id}")

        result = self.client.table('asset_allocations').select('*').eq('document_id', document_id).execute()

        return result.data

    def get_raw_text(self, document_id: int) -> Optional[Dict[str, Any]]:
        """
        Get raw text for a document.

        Args:
            document_id: Document ID

        Returns:
            RawText object or None if not found
        """
        logging.info(f"Getting raw text for document ID {document_id}")

        result = self.client.table('raw_texts').select('*').eq('document_id', document_id).execute()

        if not result.data:
            return None

        return result.data[0]

    def get_tables(self, document_id: int) -> List[Dict[str, Any]]:
        """
        Get tables for a document.

        Args:
            document_id: Document ID

        Returns:
            List of DocumentTable objects
        """
        logging.info(f"Getting tables for document ID {document_id}")

        result = self.client.table('document_tables').select('*').eq('document_id', document_id).execute()

        return result.data

    def update_document_status(self, document_id: int, status: str) -> Optional[Dict[str, Any]]:
        """
        Update document processing status.

        Args:
            document_id: Document ID
            status: Processing status

        Returns:
            Updated Document object or None if not found
        """
        logging.info(f"Updating status to '{status}' for document ID {document_id}")

        result = self.client.table('documents').update({'processing_status': status}).eq('id', document_id).execute()

        if not result.data:
            return None

        return result.data[0]

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Get all documents.

        Returns:
            List of Document objects
        """
        logging.info("Getting all documents")

        result = self.client.table('documents').select('*').execute()

        return result.data

    def get_documents_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get documents by status.

        Args:
            status: Processing status

        Returns:
            List of Document objects
        """
        logging.info(f"Getting documents with status '{status}'")

        result = self.client.table('documents').select('*').eq('processing_status', status).execute()

        return result.data

    def update_document(self, document_id: int, document_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a document in the database.

        Args:
            document_id: Document ID
            document_data: Document data to update

        Returns:
            Updated Document object or None if not found
        """
        logging.info(f"Updating document ID {document_id}")

        # Convert dates to ISO format if they exist
        for date_field in ['creation_date', 'modification_date', 'document_date', 'extraction_date']:
            if date_field in document_data and document_data[date_field] and isinstance(document_data[date_field], datetime.datetime):
                document_data[date_field] = document_data[date_field].isoformat()

        # Update document
        result = self.client.table('documents').update(document_data).eq('id', document_id).execute()

        if not result.data:
            return None

        return result.data[0]

    def store_financial_entities(self, document_id: int, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Store financial entities in the database.

        Args:
            document_id: Document ID
            entities: List of financial entity data

        Returns:
            List of FinancialEntity objects
        """
        logging.info(f"Storing {len(entities)} financial entities for document ID {document_id}")

        # Add document_id to each entity
        for entity in entities:
            entity['document_id'] = document_id

        # Insert entities
        result = self.client.table('financial_entities').insert(entities).execute()

        if not result.data:
            raise ValueError(f"Failed to store financial entities: {result.error}")

        return result.data

    def store_validation_result(self, document_id: int, validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store a validation result in the database.

        Args:
            document_id: Document ID
            validation_data: Validation data

        Returns:
            ValidationResult object
        """
        logging.info(f"Storing validation result for document ID {document_id}")

        # Add document_id to validation data
        validation_data['document_id'] = document_id

        # Convert dates to ISO format if they exist
        if 'validation_date' in validation_data and validation_data['validation_date'] and isinstance(validation_data['validation_date'], datetime.datetime):
            validation_data['validation_date'] = validation_data['validation_date'].isoformat()

        # Insert validation result
        result = self.client.table('validation_results').insert(validation_data).execute()

        if not result.data:
            raise ValueError(f"Failed to store validation result: {result.error}")

        return result.data[0]

    def store_document_comparison(self, document_id_1: int, document_id_2: int, comparison_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store a document comparison in the database.

        Args:
            document_id_1: First document ID
            document_id_2: Second document ID
            comparison_data: Comparison data

        Returns:
            DocumentComparison object
        """
        logging.info(f"Storing document comparison for documents {document_id_1} and {document_id_2}")

        # Add document IDs to comparison data
        comparison_data['document_id_1'] = document_id_1
        comparison_data['document_id_2'] = document_id_2

        # Convert dates to ISO format if they exist
        if 'comparison_date' in comparison_data and comparison_data['comparison_date'] and isinstance(comparison_data['comparison_date'], datetime.datetime):
            comparison_data['comparison_date'] = comparison_data['comparison_date'].isoformat()

        # Insert comparison
        result = self.client.table('document_comparisons').insert(comparison_data).execute()

        if not result.data:
            raise ValueError(f"Failed to store document comparison: {result.error}")

        return result.data[0]

    def store_document_query(self, document_id: int, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store a document query in the database.

        Args:
            document_id: Document ID
            query_data: Query data

        Returns:
            DocumentQuery object
        """
        logging.info(f"Storing document query for document ID {document_id}")

        # Add document ID to query data
        query_data['document_id'] = document_id

        # Convert dates to ISO format if they exist
        if 'query_date' in query_data and query_data['query_date'] and isinstance(query_data['query_date'], datetime.datetime):
            query_data['query_date'] = query_data['query_date'].isoformat()

        # Insert query
        result = self.client.table('document_queries').insert(query_data).execute()

        if not result.data:
            raise ValueError(f"Failed to store document query: {result.error}")

        return result.data[0]

    def get_financial_entities(self, document_id: int, entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get financial entities for a document.

        Args:
            document_id: Document ID
            entity_type: Entity type to filter by (optional)

        Returns:
            List of FinancialEntity objects
        """
        logging.info(f"Getting financial entities for document ID {document_id}")

        query = self.client.table('financial_entities').select('*').eq('document_id', document_id)

        if entity_type:
            query = query.eq('entity_type', entity_type)

        result = query.execute()

        return result.data

    def get_validation_results(self, document_id: int) -> List[Dict[str, Any]]:
        """
        Get validation results for a document.

        Args:
            document_id: Document ID

        Returns:
            List of ValidationResult objects
        """
        logging.info(f"Getting validation results for document ID {document_id}")

        result = self.client.table('validation_results').select('*').eq('document_id', document_id).execute()

        return result.data

    def get_document_comparisons(self, document_id: int) -> List[Dict[str, Any]]:
        """
        Get document comparisons for a document.

        Args:
            document_id: Document ID

        Returns:
            List of DocumentComparison objects
        """
        logging.info(f"Getting document comparisons for document ID {document_id}")

        # Get comparisons where document is either the first or second document
        result1 = self.client.table('document_comparisons').select('*').eq('document_id_1', document_id).execute()
        result2 = self.client.table('document_comparisons').select('*').eq('document_id_2', document_id).execute()

        return result1.data + result2.data

    def get_document_queries(self, document_id: int) -> List[Dict[str, Any]]:
        """
        Get document queries for a document.

        Args:
            document_id: Document ID

        Returns:
            List of DocumentQuery objects
        """
        logging.info(f"Getting document queries for document ID {document_id}")

        result = self.client.table('document_queries').select('*').eq('document_id', document_id).execute()

        return result.data

    def get_document_summary(self, document_id: int) -> Dict[str, Any]:
        """
        Get a summary of a document.

        Args:
            document_id: Document ID

        Returns:
            Document summary
        """
        logging.info(f"Getting summary for document ID {document_id}")

        # Get document
        document = self.get_document(document_id)
        if not document:
            raise ValueError(f"Document not found: {document_id}")

        # Get securities count
        securities = self.get_securities(document_id)
        securities_count = len(securities)

        # Get portfolio value
        portfolio_value = self.get_portfolio_value(document_id)

        # Get asset allocations count
        asset_allocations = self.get_asset_allocations(document_id)
        asset_allocations_count = len(asset_allocations)

        # Get validation results
        validation_results = self.get_validation_results(document_id)
        validation_valid = validation_results[0].get("valid") if validation_results else None
        validation_issues = validation_results[0].get("issues") if validation_results else None

        # Create summary
        summary = {
            "id": document_id,
            "filename": document.get("filename"),
            "document_type": document.get("document_type"),
            "processing_status": document.get("processing_status"),
            "extraction_date": document.get("extraction_date"),
            "page_count": document.get("page_count"),
            "securities_count": securities_count,
            "portfolio_value": portfolio_value.get("value") if portfolio_value else None,
            "asset_allocations_count": asset_allocations_count,
            "risk_profile": document.get("risk_profile"),
            "currency": document.get("currency"),
            "validation_valid": validation_valid,
            "validation_issues": validation_issues
        }

        return summary
