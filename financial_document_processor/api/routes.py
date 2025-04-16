"""
API routes for the Financial Document Processor.
"""
import os
import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse

from financial_document_processor.database.db import Database
from financial_document_processor.extractors.pdf_extractor import PDFExtractor
from financial_document_processor.processor import DocumentProcessor
from financial_document_processor.agents.config import AIConfig
from financial_document_processor.agents.document_index import DocumentIndex
from financial_document_processor.agents.financial_agents import FinancialQueryAgent, TableGenerationAgent, FinancialAnalysisAgent
from financial_document_processor.api.models import (
    Document, DocumentCreate, DocumentSummary, Security, PortfolioValue, AssetAllocation,
    ProcessingResult, QueryRequest, QueryResponse, TableGenerationRequest, TableGenerationResponse,
    AnalysisRequest, AnalysisResponse
)

# Create router
router = APIRouter(prefix="/api", tags=["Financial Document Processor"])

# Database dependency
def get_database():
    """Get database connection."""
    db = Database(os.environ.get("DATABASE_URL"))
    try:
        yield db
    finally:
        db.close()

# AI config dependency
def get_ai_config():
    """Get AI configuration."""
    return AIConfig(
        api_key=os.environ.get("OPENAI_API_KEY") or os.environ.get("GOOGLE_API_KEY"),
        model_provider=os.environ.get("MODEL_PROVIDER", "openai"),
        model_name=os.environ.get("MODEL_NAME")
    )

# Document index dependency
def get_document_index(db: Database = Depends(get_database), ai_config: AIConfig = Depends(get_ai_config)):
    """Get document index."""
    persist_dir = os.environ.get("INDEX_PERSIST_DIR")
    return DocumentIndex(db, ai_config, persist_dir)

# Financial query agent dependency
def get_query_agent(db: Database = Depends(get_database), 
                   ai_config: AIConfig = Depends(get_ai_config),
                   document_index: DocumentIndex = Depends(get_document_index)):
    """Get financial query agent."""
    return FinancialQueryAgent(db, ai_config, document_index)

# Table generation agent dependency
def get_table_agent(db: Database = Depends(get_database), 
                   ai_config: AIConfig = Depends(get_ai_config),
                   document_index: DocumentIndex = Depends(get_document_index)):
    """Get table generation agent."""
    return TableGenerationAgent(db, ai_config, document_index)

# Financial analysis agent dependency
def get_analysis_agent(db: Database = Depends(get_database), 
                      ai_config: AIConfig = Depends(get_ai_config),
                      document_index: DocumentIndex = Depends(get_document_index)):
    """Get financial analysis agent."""
    return FinancialAnalysisAgent(db, ai_config, document_index)

# Document routes
@router.post("/documents", response_model=Document)
async def create_document(document: DocumentCreate, db: Database = Depends(get_database)):
    """Create a new document."""
    document_data = document.dict()
    db_document = db.store_document(document_data)
    return db_document

@router.get("/documents", response_model=List[DocumentSummary])
async def get_documents(db: Database = Depends(get_database)):
    """Get all documents."""
    with db.get_session() as session:
        from financial_document_processor.database.models import Document, Security, PortfolioValue, AssetAllocation
        from sqlalchemy import func
        
        # Query documents with counts
        documents = []
        
        for doc in session.query(Document).all():
            # Get securities count
            securities_count = session.query(func.count(Security.id)).filter(Security.document_id == doc.id).scalar() or 0
            
            # Get portfolio value
            portfolio_value = session.query(PortfolioValue).filter(PortfolioValue.document_id == doc.id).first()
            
            # Get asset allocations count
            asset_allocations_count = session.query(func.count(AssetAllocation.id)).filter(AssetAllocation.document_id == doc.id).scalar() or 0
            
            # Create document summary
            document_summary = DocumentSummary(
                id=doc.id,
                filename=doc.filename,
                document_type=doc.document_type,
                processing_status=doc.processing_status,
                extraction_date=doc.extraction_date,
                page_count=doc.page_count,
                securities_count=securities_count,
                portfolio_value=portfolio_value.value if portfolio_value else None,
                asset_allocations_count=asset_allocations_count
            )
            
            documents.append(document_summary)
        
        return documents

@router.get("/documents/{document_id}", response_model=Document)
async def get_document(document_id: int, db: Database = Depends(get_database)):
    """Get a document by ID."""
    document = db.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.get("/documents/{document_id}/securities", response_model=List[Security])
async def get_document_securities(document_id: int, db: Database = Depends(get_database)):
    """Get securities for a document."""
    document = db.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    securities = db.get_securities(document_id)
    return securities

@router.get("/documents/{document_id}/portfolio-value", response_model=Optional[PortfolioValue])
async def get_document_portfolio_value(document_id: int, db: Database = Depends(get_database)):
    """Get portfolio value for a document."""
    document = db.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    portfolio_value = db.get_portfolio_value(document_id)
    return portfolio_value

@router.get("/documents/{document_id}/asset-allocations", response_model=List[AssetAllocation])
async def get_document_asset_allocations(document_id: int, db: Database = Depends(get_database)):
    """Get asset allocations for a document."""
    document = db.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    asset_allocations = db.get_asset_allocations(document_id)
    return asset_allocations

# Processing routes
@router.post("/process", response_model=ProcessingResult)
async def process_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None),
    db: Database = Depends(get_database)
):
    """Process a document."""
    # Save uploaded file
    upload_dir = os.environ.get("UPLOAD_DIR", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Create document
    document_data = {
        "filename": file.filename,
        "file_path": file_path,
        "file_size": os.path.getsize(file_path),
        "content_type": file.content_type,
        "document_type": document_type,
        "processing_status": "pending"
    }
    
    document = db.store_document(document_data)
    
    # Process document in background
    def process_document_task(document_id: int, file_path: str, document_type: Optional[str]):
        try:
            # Create processor
            extractor = PDFExtractor()
            processor = DocumentProcessor(db, extractor)
            
            # Process document
            result = processor.process_document(file_path, document_type=document_type)
            
            # Index document
            ai_config = get_ai_config()
            document_index = DocumentIndex(db, ai_config, os.environ.get("INDEX_PERSIST_DIR"))
            document_index.index_document(document_id)
        except Exception as e:
            logging.error(f"Error processing document: {e}")
            db.update_document_status(document_id, "failed")
    
    background_tasks.add_task(process_document_task, document.id, file_path, document_type)
    
    return ProcessingResult(
        document_id=document.id,
        status="processing"
    )

@router.post("/process/{document_id}", response_model=ProcessingResult)
async def process_existing_document(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Database = Depends(get_database)
):
    """Process an existing document."""
    document = db.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update document status
    db.update_document_status(document_id, "processing")
    
    # Process document in background
    def process_document_task(document_id: int, file_path: str, document_type: Optional[str]):
        try:
            # Create processor
            extractor = PDFExtractor()
            processor = DocumentProcessor(db, extractor)
            
            # Process document
            result = processor.process_document(file_path, document_type=document_type)
            
            # Index document
            ai_config = get_ai_config()
            document_index = DocumentIndex(db, ai_config, os.environ.get("INDEX_PERSIST_DIR"))
            document_index.index_document(document_id)
        except Exception as e:
            logging.error(f"Error processing document: {e}")
            db.update_document_status(document_id, "failed")
    
    background_tasks.add_task(process_document_task, document.id, document.file_path, document.document_type)
    
    return ProcessingResult(
        document_id=document.id,
        status="processing"
    )

# AI agent routes
@router.post("/query", response_model=QueryResponse)
async def query_document(
    query_request: QueryRequest,
    query_agent: FinancialQueryAgent = Depends(get_query_agent)
):
    """Query a document."""
    result = query_agent.query(query_request.query, query_request.document_id)
    
    return QueryResponse(
        query=result["query"],
        document_id=result["document_id"],
        response=result["response"],
        sources=result.get("sources")
    )

@router.post("/generate-table", response_model=TableGenerationResponse)
async def generate_table(
    table_request: TableGenerationRequest,
    table_agent: TableGenerationAgent = Depends(get_table_agent)
):
    """Generate a table."""
    result = table_agent.generate_table(
        table_request.request,
        table_request.document_id,
        table_request.format
    )
    
    return TableGenerationResponse(
        request=result["request"],
        document_id=result["document_id"],
        format=result["format"],
        table=result["table"]
    )

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_document(
    analysis_request: AnalysisRequest,
    analysis_agent: FinancialAnalysisAgent = Depends(get_analysis_agent)
):
    """Analyze a document."""
    result = analysis_agent.analyze(
        analysis_request.request,
        analysis_request.document_id
    )
    
    return AnalysisResponse(
        request=result["request"],
        document_id=result["document_id"],
        analysis=result["analysis"]
    )
