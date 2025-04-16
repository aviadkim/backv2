"""
API models for the Financial Document Processor.
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class DocumentBase(BaseModel):
    """Base document model."""
    filename: str
    document_type: Optional[str] = None

class DocumentCreate(DocumentBase):
    """Document creation model."""
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    content_type: Optional[str] = None

class Document(DocumentBase):
    """Document model."""
    id: int
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    page_count: Optional[int] = None
    title: Optional[str] = None
    author: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    document_date: Optional[datetime] = None
    processing_status: str
    extraction_date: datetime
    extraction_method: Optional[str] = None
    extraction_version: Optional[str] = None
    
    class Config:
        """Pydantic config."""
        from_attributes = True

class SecurityBase(BaseModel):
    """Base security model."""
    isin: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    security_type: Optional[str] = None
    asset_class: Optional[str] = None
    valuation: Optional[float] = None
    price: Optional[float] = None
    quantity: Optional[float] = None
    currency: Optional[str] = None

class Security(SecurityBase):
    """Security model."""
    id: int
    document_id: int
    cusip: Optional[str] = None
    ticker: Optional[str] = None
    coupon_rate: Optional[float] = None
    maturity_date: Optional[datetime] = None
    extraction_method: Optional[str] = None
    confidence_score: Optional[float] = None
    
    class Config:
        """Pydantic config."""
        from_attributes = True

class PortfolioValueBase(BaseModel):
    """Base portfolio value model."""
    value: float
    currency: Optional[str] = None
    value_date: Optional[datetime] = None

class PortfolioValue(PortfolioValueBase):
    """Portfolio value model."""
    id: int
    document_id: int
    extraction_method: Optional[str] = None
    confidence_score: Optional[float] = None
    
    class Config:
        """Pydantic config."""
        from_attributes = True

class AssetAllocationBase(BaseModel):
    """Base asset allocation model."""
    asset_class: str
    value: Optional[float] = None
    percentage: Optional[float] = None
    currency: Optional[str] = None

class AssetAllocation(AssetAllocationBase):
    """Asset allocation model."""
    id: int
    document_id: int
    parent_id: Optional[int] = None
    extraction_method: Optional[str] = None
    confidence_score: Optional[float] = None
    
    class Config:
        """Pydantic config."""
        from_attributes = True

class DocumentSummary(BaseModel):
    """Document summary model."""
    id: int
    filename: str
    document_type: Optional[str] = None
    processing_status: str
    extraction_date: datetime
    page_count: Optional[int] = None
    securities_count: int
    portfolio_value: Optional[float] = None
    asset_allocations_count: int
    
    class Config:
        """Pydantic config."""
        from_attributes = True

class ProcessingResult(BaseModel):
    """Processing result model."""
    document_id: int
    status: str
    securities_count: Optional[int] = None
    portfolio_value: Optional[float] = None
    asset_allocations_count: Optional[int] = None
    tables_count: Optional[int] = None
    error: Optional[str] = None

class QueryRequest(BaseModel):
    """Query request model."""
    query: str
    document_id: Optional[int] = None

class QueryResponse(BaseModel):
    """Query response model."""
    query: str
    document_id: Optional[int] = None
    response: str
    sources: Optional[List[Dict[str, Any]]] = None

class TableGenerationRequest(BaseModel):
    """Table generation request model."""
    request: str
    document_id: int
    format: str = Field(default="markdown", description="Output format (markdown, html, or csv)")

class TableGenerationResponse(BaseModel):
    """Table generation response model."""
    request: str
    document_id: int
    format: str
    table: str

class AnalysisRequest(BaseModel):
    """Analysis request model."""
    request: str
    document_id: int

class AnalysisResponse(BaseModel):
    """Analysis response model."""
    request: str
    document_id: int
    analysis: str
