"""
Database connection and session management.
"""
import os
from typing import Optional, Dict, Any, List
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from financial_document_processor.database.models import Base, Document, Security, PortfolioValue, AssetAllocation, RawText, DocumentTable

class Database:
    """Database connection and session management."""
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize the database connection.
        
        Args:
            connection_string: SQLAlchemy connection string. If None, uses environment variable.
        """
        if connection_string is None:
            connection_string = os.environ.get("DATABASE_URL")
            
            # Handle SQLAlchemy 1.4+ PostgreSQL URL format change
            if connection_string and connection_string.startswith("postgres://"):
                connection_string = connection_string.replace("postgres://", "postgresql://", 1)
        
        if not connection_string:
            raise ValueError("Database connection string not provided and DATABASE_URL environment variable not set")
        
        self.engine = create_engine(connection_string)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    def close(self):
        """Close the database connection."""
        self.engine.dispose()
    
    def store_document(self, document_data: Dict[str, Any]) -> Document:
        """
        Store a document in the database.
        
        Args:
            document_data: Document data
        
        Returns:
            Document object
        """
        with self.get_session() as session:
            document = Document(
                filename=document_data.get("filename"),
                file_path=document_data.get("file_path"),
                file_size=document_data.get("file_size"),
                content_type=document_data.get("content_type"),
                page_count=document_data.get("page_count"),
                title=document_data.get("title"),
                author=document_data.get("author"),
                creation_date=document_data.get("creation_date"),
                modification_date=document_data.get("modification_date"),
                document_date=document_data.get("document_date"),
                document_type=document_data.get("document_type"),
                processing_status=document_data.get("processing_status", "pending"),
                extraction_method=document_data.get("extraction_method"),
                extraction_version=document_data.get("extraction_version")
            )
            
            session.add(document)
            session.commit()
            session.refresh(document)
            
            return document
    
    def store_securities(self, document_id: int, securities: List[Dict[str, Any]]) -> List[Security]:
        """
        Store securities in the database.
        
        Args:
            document_id: Document ID
            securities: List of securities data
        
        Returns:
            List of Security objects
        """
        with self.get_session() as session:
            security_objects = []
            
            for security_data in securities:
                security = Security(
                    document_id=document_id,
                    isin=security_data.get("isin"),
                    cusip=security_data.get("cusip"),
                    ticker=security_data.get("ticker"),
                    name=security_data.get("name"),
                    description=security_data.get("description"),
                    security_type=security_data.get("security_type"),
                    asset_class=security_data.get("asset_class"),
                    valuation=security_data.get("valuation"),
                    price=security_data.get("price"),
                    quantity=security_data.get("quantity"),
                    currency=security_data.get("currency"),
                    coupon_rate=security_data.get("coupon_rate"),
                    maturity_date=security_data.get("maturity_date"),
                    extraction_method=security_data.get("extraction_method"),
                    confidence_score=security_data.get("confidence_score")
                )
                
                session.add(security)
                security_objects.append(security)
            
            session.commit()
            
            # Refresh all securities to get their IDs
            for security in security_objects:
                session.refresh(security)
            
            return security_objects
    
    def store_portfolio_value(self, document_id: int, portfolio_value_data: Dict[str, Any]) -> PortfolioValue:
        """
        Store a portfolio value in the database.
        
        Args:
            document_id: Document ID
            portfolio_value_data: Portfolio value data
        
        Returns:
            PortfolioValue object
        """
        with self.get_session() as session:
            portfolio_value = PortfolioValue(
                document_id=document_id,
                value=portfolio_value_data.get("value"),
                currency=portfolio_value_data.get("currency"),
                value_date=portfolio_value_data.get("value_date"),
                extraction_method=portfolio_value_data.get("extraction_method"),
                confidence_score=portfolio_value_data.get("confidence_score")
            )
            
            session.add(portfolio_value)
            session.commit()
            session.refresh(portfolio_value)
            
            return portfolio_value
    
    def store_asset_allocations(self, document_id: int, asset_allocations: List[Dict[str, Any]]) -> List[AssetAllocation]:
        """
        Store asset allocations in the database.
        
        Args:
            document_id: Document ID
            asset_allocations: List of asset allocation data
        
        Returns:
            List of AssetAllocation objects
        """
        with self.get_session() as session:
            allocation_objects = []
            
            for allocation_data in asset_allocations:
                allocation = AssetAllocation(
                    document_id=document_id,
                    asset_class=allocation_data.get("asset_class"),
                    value=allocation_data.get("value"),
                    percentage=allocation_data.get("percentage"),
                    currency=allocation_data.get("currency"),
                    parent_id=allocation_data.get("parent_id"),
                    extraction_method=allocation_data.get("extraction_method"),
                    confidence_score=allocation_data.get("confidence_score")
                )
                
                session.add(allocation)
                allocation_objects.append(allocation)
            
            session.commit()
            
            # Refresh all allocations to get their IDs
            for allocation in allocation_objects:
                session.refresh(allocation)
            
            return allocation_objects
    
    def store_raw_text(self, document_id: int, content: str, extraction_method: Optional[str] = None) -> RawText:
        """
        Store raw text in the database.
        
        Args:
            document_id: Document ID
            content: Raw text content
            extraction_method: Extraction method
        
        Returns:
            RawText object
        """
        with self.get_session() as session:
            # Check if raw text already exists for this document
            existing = session.query(RawText).filter(RawText.document_id == document_id).first()
            
            if existing:
                existing.content = content
                existing.extraction_method = extraction_method
                raw_text = existing
            else:
                raw_text = RawText(
                    document_id=document_id,
                    content=content,
                    extraction_method=extraction_method
                )
                session.add(raw_text)
            
            session.commit()
            session.refresh(raw_text)
            
            return raw_text
    
    def store_tables(self, document_id: int, tables: List[Dict[str, Any]]) -> List[DocumentTable]:
        """
        Store tables in the database.
        
        Args:
            document_id: Document ID
            tables: List of table data
        
        Returns:
            List of DocumentTable objects
        """
        with self.get_session() as session:
            table_objects = []
            
            for table_data in tables:
                table = DocumentTable(
                    document_id=document_id,
                    page_number=table_data.get("page"),
                    table_number=table_data.get("table_number"),
                    extraction_method=table_data.get("extraction_method"),
                    headers=table_data.get("headers"),
                    data=table_data.get("data"),
                    accuracy=table_data.get("accuracy")
                )
                
                session.add(table)
                table_objects.append(table)
            
            session.commit()
            
            # Refresh all tables to get their IDs
            for table in table_objects:
                session.refresh(table)
            
            return table_objects
    
    def get_document(self, document_id: int) -> Optional[Document]:
        """
        Get a document by ID.
        
        Args:
            document_id: Document ID
        
        Returns:
            Document object or None if not found
        """
        with self.get_session() as session:
            return session.query(Document).filter(Document.id == document_id).first()
    
    def get_securities(self, document_id: int) -> List[Security]:
        """
        Get securities for a document.
        
        Args:
            document_id: Document ID
        
        Returns:
            List of Security objects
        """
        with self.get_session() as session:
            return session.query(Security).filter(Security.document_id == document_id).all()
    
    def get_portfolio_value(self, document_id: int) -> Optional[PortfolioValue]:
        """
        Get portfolio value for a document.
        
        Args:
            document_id: Document ID
        
        Returns:
            PortfolioValue object or None if not found
        """
        with self.get_session() as session:
            return session.query(PortfolioValue).filter(PortfolioValue.document_id == document_id).first()
    
    def get_asset_allocations(self, document_id: int) -> List[AssetAllocation]:
        """
        Get asset allocations for a document.
        
        Args:
            document_id: Document ID
        
        Returns:
            List of AssetAllocation objects
        """
        with self.get_session() as session:
            return session.query(AssetAllocation).filter(AssetAllocation.document_id == document_id).all()
    
    def get_raw_text(self, document_id: int) -> Optional[RawText]:
        """
        Get raw text for a document.
        
        Args:
            document_id: Document ID
        
        Returns:
            RawText object or None if not found
        """
        with self.get_session() as session:
            return session.query(RawText).filter(RawText.document_id == document_id).first()
    
    def get_tables(self, document_id: int) -> List[DocumentTable]:
        """
        Get tables for a document.
        
        Args:
            document_id: Document ID
        
        Returns:
            List of DocumentTable objects
        """
        with self.get_session() as session:
            return session.query(DocumentTable).filter(DocumentTable.document_id == document_id).all()
    
    def update_document_status(self, document_id: int, status: str) -> Optional[Document]:
        """
        Update document processing status.
        
        Args:
            document_id: Document ID
            status: Processing status
        
        Returns:
            Updated Document object or None if not found
        """
        with self.get_session() as session:
            document = session.query(Document).filter(Document.id == document_id).first()
            
            if document:
                document.processing_status = status
                session.commit()
                session.refresh(document)
            
            return document
