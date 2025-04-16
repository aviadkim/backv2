"""
FastAPI web application for the Financial Document Processor.
"""
import os
import logging
from typing import Dict, List, Any, Optional
import json
from fastapi import FastAPI, Request, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import database
from financial_document_processor.database.supabase_db import SupabaseDB

# Import document processor
from financial_document_processor.processor import DocumentProcessor
from financial_document_processor.extractors.pdf_extractor import PDFExtractor

# Import OpenRouter agent
from financial_document_processor.agents.openrouter_agent import OpenRouterAgent

# Create FastAPI app
app = FastAPI(
    title="Financial Document Processor",
    description="Web interface for processing financial documents",
    version="1.0.0"
)

# Create templates
templates = Jinja2Templates(directory="financial_document_processor/web/templates")

# Create static files
app.mount("/static", StaticFiles(directory="financial_document_processor/web/static"), name="static")

# Create uploads directory
uploads_dir = os.environ.get("UPLOAD_DIR", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Database dependency
def get_database():
    """Get database connection."""
    db = SupabaseDB(
        url=os.environ.get("SUPABASE_URL", "https://dnjnsotemnfrjlotgved.supabase.co"),
        key=os.environ.get("SUPABASE_KEY")
    )
    return db

# OpenRouter agent dependency
def get_openrouter_agent():
    """Get OpenRouter agent."""
    return OpenRouterAgent(
        api_key=os.environ.get("OPENROUTER_API_KEY", "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"),
        model=os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3-opus")
    )

# Document processor dependency
def get_document_processor(db: SupabaseDB = Depends(get_database)):
    """Get document processor."""
    extractor = PDFExtractor()
    return DocumentProcessor(db, extractor)

# Models
class QueryRequest(BaseModel):
    """Query request model."""
    question: str
    document_id: int

class AnalysisRequest(BaseModel):
    """Analysis request model."""
    request: str
    document_id: int

class TableRequest(BaseModel):
    """Table request model."""
    request: str
    document_id: int
    format: str = "markdown"

# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: SupabaseDB = Depends(get_database)):
    """Index page."""
    # Get all documents
    documents = db.get_all_documents()
    
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "documents": documents}
    )

@app.get("/documents", response_class=HTMLResponse)
async def documents_page(request: Request, db: SupabaseDB = Depends(get_database)):
    """Documents page."""
    # Get all documents
    documents = db.get_all_documents()
    
    return templates.TemplateResponse(
        "documents.html",
        {"request": request, "documents": documents}
    )

@app.get("/documents/{document_id}", response_class=HTMLResponse)
async def document_page(request: Request, document_id: int, db: SupabaseDB = Depends(get_database)):
    """Document page."""
    # Get document
    document = db.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get document summary
    summary = db.get_document_summary(document_id)
    
    # Get securities
    securities = db.get_securities(document_id)
    
    # Get portfolio value
    portfolio_value = db.get_portfolio_value(document_id)
    
    # Get asset allocations
    asset_allocations = db.get_asset_allocations(document_id)
    
    return templates.TemplateResponse(
        "document.html",
        {
            "request": request,
            "document": document,
            "summary": summary,
            "securities": securities,
            "portfolio_value": portfolio_value,
            "asset_allocations": asset_allocations
        }
    )

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """Upload page."""
    return templates.TemplateResponse(
        "upload.html",
        {"request": request}
    )

@app.post("/upload")
async def upload_document(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type: str = Form(None),
    db: SupabaseDB = Depends(get_database),
    processor: DocumentProcessor = Depends(get_document_processor)
):
    """Upload a document."""
    # Save uploaded file
    file_path = os.path.join(uploads_dir, file.filename)
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
            # Process document
            result = processor.process_document(file_path, document_type=document_type)
            logger.info(f"Document processed: {result}")
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            db.update_document_status(document_id, "failed")
    
    background_tasks.add_task(process_document_task, document["id"], file_path, document_type)
    
    # Redirect to document page
    return RedirectResponse(url=f"/documents/{document['id']}", status_code=303)

@app.get("/query", response_class=HTMLResponse)
async def query_page(request: Request, db: SupabaseDB = Depends(get_database)):
    """Query page."""
    # Get all documents
    documents = db.get_all_documents()
    
    return templates.TemplateResponse(
        "query.html",
        {"request": request, "documents": documents}
    )

@app.post("/api/query")
async def query_document(
    query_request: QueryRequest,
    db: SupabaseDB = Depends(get_database),
    agent: OpenRouterAgent = Depends(get_openrouter_agent)
):
    """Query a document."""
    # Get document
    document = db.get_document(query_request.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get raw text
    raw_text = db.get_raw_text(query_request.document_id)
    if not raw_text:
        raise HTTPException(status_code=404, detail="Raw text not found")
    
    # Query document
    answer = agent.query(raw_text["content"], query_request.question)
    
    return {"question": query_request.question, "answer": answer}

@app.post("/api/analyze")
async def analyze_document(
    analysis_request: AnalysisRequest,
    db: SupabaseDB = Depends(get_database),
    agent: OpenRouterAgent = Depends(get_openrouter_agent)
):
    """Analyze a document."""
    # Get document
    document = db.get_document(analysis_request.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get raw text
    raw_text = db.get_raw_text(analysis_request.document_id)
    if not raw_text:
        raise HTTPException(status_code=404, detail="Raw text not found")
    
    # Analyze document
    analysis = agent.analyze(raw_text["content"], analysis_request.request)
    
    return {"request": analysis_request.request, "analysis": analysis}

@app.post("/api/generate-table")
async def generate_table(
    table_request: TableRequest,
    db: SupabaseDB = Depends(get_database),
    agent: OpenRouterAgent = Depends(get_openrouter_agent)
):
    """Generate a table."""
    # Get document
    document = db.get_document(table_request.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get raw text
    raw_text = db.get_raw_text(table_request.document_id)
    if not raw_text:
        raise HTTPException(status_code=404, detail="Raw text not found")
    
    # Generate table
    table = agent.generate_table(raw_text["content"], table_request.request, table_request.format)
    
    return {"request": table_request.request, "table": table, "format": table_request.format}

@app.get("/api/documents")
async def get_documents(db: SupabaseDB = Depends(get_database)):
    """Get all documents."""
    documents = db.get_all_documents()
    return {"documents": documents}

@app.get("/api/documents/{document_id}")
async def get_document(document_id: int, db: SupabaseDB = Depends(get_database)):
    """Get a document."""
    document = db.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"document": document}

@app.get("/api/documents/{document_id}/summary")
async def get_document_summary(document_id: int, db: SupabaseDB = Depends(get_database)):
    """Get a document summary."""
    summary = db.get_document_summary(document_id)
    return {"summary": summary}

@app.get("/api/documents/{document_id}/securities")
async def get_document_securities(document_id: int, db: SupabaseDB = Depends(get_database)):
    """Get securities for a document."""
    securities = db.get_securities(document_id)
    return {"securities": securities}

@app.get("/api/documents/{document_id}/portfolio-value")
async def get_document_portfolio_value(document_id: int, db: SupabaseDB = Depends(get_database)):
    """Get portfolio value for a document."""
    portfolio_value = db.get_portfolio_value(document_id)
    return {"portfolio_value": portfolio_value}

@app.get("/api/documents/{document_id}/asset-allocations")
async def get_document_asset_allocations(document_id: int, db: SupabaseDB = Depends(get_database)):
    """Get asset allocations for a document."""
    asset_allocations = db.get_asset_allocations(document_id)
    return {"asset_allocations": asset_allocations}

@app.get("/api/insights/{document_id}")
async def get_document_insights(
    document_id: int,
    db: SupabaseDB = Depends(get_database),
    agent: OpenRouterAgent = Depends(get_openrouter_agent)
):
    """Get insights for a document."""
    # Get document
    document = db.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get raw text
    raw_text = db.get_raw_text(document_id)
    if not raw_text:
        raise HTTPException(status_code=404, detail="Raw text not found")
    
    # Extract insights
    insights = agent.extract_insights(raw_text["content"])
    
    return {"insights": insights}
