"""
Database models for the Financial Document Processor.
"""
import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Document(Base):
    """Financial document model."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(1024), nullable=True)
    file_size = Column(Integer, nullable=True)
    content_type = Column(String(100), nullable=True)
    page_count = Column(Integer, nullable=True)
    
    # Document metadata
    title = Column(String(255), nullable=True)
    author = Column(String(255), nullable=True)
    creation_date = Column(DateTime, nullable=True)
    modification_date = Column(DateTime, nullable=True)
    document_date = Column(DateTime, nullable=True)
    
    # Document type and status
    document_type = Column(String(50), nullable=True)  # e.g., "bank_statement", "portfolio_report"
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    
    # Extraction metadata
    extraction_date = Column(DateTime, default=datetime.datetime.utcnow)
    extraction_method = Column(String(50), nullable=True)
    extraction_version = Column(String(50), nullable=True)
    
    # Relationships
    securities = relationship("Security", back_populates="document")
    portfolio_values = relationship("PortfolioValue", back_populates="document")
    asset_allocations = relationship("AssetAllocation", back_populates="document")
    raw_text = relationship("RawText", back_populates="document", uselist=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "content_type": self.content_type,
            "page_count": self.page_count,
            "title": self.title,
            "author": self.author,
            "creation_date": self.creation_date.isoformat() if self.creation_date else None,
            "modification_date": self.modification_date.isoformat() if self.modification_date else None,
            "document_date": self.document_date.isoformat() if self.document_date else None,
            "document_type": self.document_type,
            "processing_status": self.processing_status,
            "extraction_date": self.extraction_date.isoformat() if self.extraction_date else None,
            "extraction_method": self.extraction_method,
            "extraction_version": self.extraction_version
        }


class Security(Base):
    """Security model for stocks, bonds, etc."""
    __tablename__ = "securities"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    
    # Security identifiers
    isin = Column(String(12), nullable=True, index=True)
    cusip = Column(String(9), nullable=True)
    ticker = Column(String(20), nullable=True)
    
    # Security details
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    security_type = Column(String(50), nullable=True)  # e.g., "equity", "bond", "fund"
    asset_class = Column(String(50), nullable=True)
    
    # Valuation data
    valuation = Column(Float, nullable=True)
    price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=True)
    currency = Column(String(3), nullable=True)
    
    # Bond-specific fields
    coupon_rate = Column(Float, nullable=True)
    maturity_date = Column(DateTime, nullable=True)
    
    # Extraction metadata
    extraction_method = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="securities")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "isin": self.isin,
            "cusip": self.cusip,
            "ticker": self.ticker,
            "name": self.name,
            "description": self.description,
            "security_type": self.security_type,
            "asset_class": self.asset_class,
            "valuation": self.valuation,
            "price": self.price,
            "quantity": self.quantity,
            "currency": self.currency,
            "coupon_rate": self.coupon_rate,
            "maturity_date": self.maturity_date.isoformat() if self.maturity_date else None,
            "extraction_method": self.extraction_method,
            "confidence_score": self.confidence_score
        }


class PortfolioValue(Base):
    """Portfolio value model."""
    __tablename__ = "portfolio_values"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    
    # Portfolio value data
    value = Column(Float, nullable=False)
    currency = Column(String(3), nullable=True)
    value_date = Column(DateTime, nullable=True)
    
    # Extraction metadata
    extraction_method = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="portfolio_values")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "value": self.value,
            "currency": self.currency,
            "value_date": self.value_date.isoformat() if self.value_date else None,
            "extraction_method": self.extraction_method,
            "confidence_score": self.confidence_score
        }


class AssetAllocation(Base):
    """Asset allocation model."""
    __tablename__ = "asset_allocations"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    
    # Asset allocation data
    asset_class = Column(String(50), nullable=False)
    value = Column(Float, nullable=True)
    percentage = Column(Float, nullable=True)
    currency = Column(String(3), nullable=True)
    
    # Parent-child relationship for hierarchical asset classes
    parent_id = Column(Integer, ForeignKey("asset_allocations.id"), nullable=True)
    children = relationship("AssetAllocation")
    
    # Extraction metadata
    extraction_method = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="asset_allocations")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "asset_class": self.asset_class,
            "value": self.value,
            "percentage": self.percentage,
            "currency": self.currency,
            "parent_id": self.parent_id,
            "extraction_method": self.extraction_method,
            "confidence_score": self.confidence_score
        }


class RawText(Base):
    """Raw text model for full-text search."""
    __tablename__ = "raw_texts"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, unique=True)
    
    # Raw text content
    content = Column(Text, nullable=True)
    
    # Extraction metadata
    extraction_method = Column(String(50), nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="raw_text")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "extraction_method": self.extraction_method,
            # Exclude content as it can be very large
        }


class DocumentTable(Base):
    """Table extracted from a document."""
    __tablename__ = "document_tables"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    
    # Table metadata
    page_number = Column(Integer, nullable=True)
    table_number = Column(Integer, nullable=True)
    extraction_method = Column(String(50), nullable=True)
    
    # Table content
    headers = Column(JSON, nullable=True)
    data = Column(JSON, nullable=True)
    
    # Extraction quality
    accuracy = Column(Float, nullable=True)
    
    # Relationships
    document = relationship("Document")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "page_number": self.page_number,
            "table_number": self.table_number,
            "extraction_method": self.extraction_method,
            "headers": self.headers,
            "data": self.data,
            "accuracy": self.accuracy
        }
